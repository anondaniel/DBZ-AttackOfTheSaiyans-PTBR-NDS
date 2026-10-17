"""Gerador e aplicador de patch BPS (formato do byuu/Near, usado pelo
Floating IPS e pelo Rom Patcher JS).

  "BPS1" varint(tam_origem) varint(tam_destino) varint(tam_meta) meta
  acoes: varint(((tamanho-1) << 2) | cmd)
    0 SourceRead  copia origem[pos_saida]
    1 TargetRead  bytes literais em seguida
    2 SourceCopy  varint(|delta|<<1 | sinal) e copia de origem[pos_rel]
    3 TargetCopy  (nao usado aqui)
  crc32(origem) crc32(destino) crc32(patch)

criar(origem, destino, regioes_fonte) -> bytes do patch
  regioes_fonte: faixas da ORIGEM onde procurar trechos que mudaram de
  lugar (ex.: posicao antiga de arquivos realocados), para virar SourceCopy
  em vez de bytes literais.
aplicar(origem, patch) -> destino (confere os 3 CRC32)

uso: bps.py criar <origem> <destino> <patch>
     bps.py aplicar <origem> <patch> <saida>
"""
import struct
import sys
import zlib

import numpy as np


def _vint(n):
    out = bytearray()
    while True:
        x = n & 0x7F
        n >>= 7
        if n == 0:
            out.append(0x80 | x)
            return bytes(out)
        out.append(x)
        n -= 1


def _lvint(p, i):
    n, s = 0, 1
    while True:
        x = p[i]
        i += 1
        n += (x & 0x7F) * s
        if x & 0x80:
            return n, i
        s <<= 7
        n += s


def criar(origem, destino, regioes_fonte=(), meta=b""):
    src = np.frombuffer(origem, dtype=np.uint8)
    tgt = np.frombuffer(destino, dtype=np.uint8)
    n = len(tgt)
    comum = min(len(src), n)
    igual = np.zeros(n, dtype=bool)
    igual[:comum] = src[:comum] == tgt[:comum]

    K = 16  # indice de blocos da origem (so nas regioes indicadas)
    indice = {}
    for a, z in regioes_fonte:
        for p in range(a, z - K + 1):
            indice.setdefault(origem[p:p + K], p)

    out = bytearray(b"BPS1" + _vint(len(origem)) + _vint(n) + _vint(len(meta)) + meta)
    rel = 0  # pos_rel do SourceCopy
    lit = bytearray()

    def solta_literal():
        nonlocal lit
        if lit:
            out.extend(_vint(((len(lit) - 1) << 2) | 1) + lit)
            lit = bytearray()

    # fronteiras entre trechos iguais/diferentes
    mud = np.flatnonzero(np.diff(igual.astype(np.int8))) + 1
    cortes = [0] + mud.tolist() + [n]
    for a, z in zip(cortes, cortes[1:]):
        if igual[a]:
            if z - a < 4 and lit:  # trecho igual curto no meio de literais
                lit.extend(destino[a:z])
                continue
            solta_literal()
            out.extend(_vint(((z - a - 1) << 2) | 0))
            continue
        i = a
        while i < z:
            p = indice.get(destino[i:i + K]) if i + K <= z else None
            if p is not None:
                m = K
                while i + m < z and p + m < len(origem) and origem[p + m] == destino[i + m]:
                    m += 1
                solta_literal()
                delta = p - rel
                out.extend(_vint(((m - 1) << 2) | 2) + _vint((abs(delta) << 1) | (delta < 0)))
                rel = p + m
                i += m
            else:
                lit.append(destino[i])
                i += 1
    solta_literal()
    out += struct.pack("<II", zlib.crc32(origem), zlib.crc32(destino))
    out += struct.pack("<I", zlib.crc32(bytes(out)))
    return bytes(out)


def aplicar(origem, patch):
    assert patch[:4] == b"BPS1", "nao e BPS"
    assert zlib.crc32(patch[:-4]) == struct.unpack_from("<I", patch, len(patch) - 4)[0], "patch corrompido"
    crc_src, crc_tgt = struct.unpack_from("<II", patch, len(patch) - 12)
    assert zlib.crc32(origem) == crc_src, "ROM de origem errada (CRC32 nao bate)"
    i = 4
    ts, i = _lvint(patch, i)
    tt, i = _lvint(patch, i)
    tm, i = _lvint(patch, i)
    assert ts == len(origem)
    i += tm
    out = bytearray(tt)
    o = rs = rt = 0
    fim = len(patch) - 12
    while i < fim:
        v, i = _lvint(patch, i)
        cmd, ln = v & 3, (v >> 2) + 1
        if cmd == 0:
            out[o:o + ln] = origem[o:o + ln]
        elif cmd == 1:
            out[o:o + ln] = patch[i:i + ln]
            i += ln
        elif cmd == 2:
            d, i = _lvint(patch, i)
            rs += -(d >> 1) if d & 1 else (d >> 1)
            out[o:o + ln] = origem[rs:rs + ln]
            rs += ln
        else:
            d, i = _lvint(patch, i)
            rt += -(d >> 1) if d & 1 else (d >> 1)
            for k in range(ln):
                out[o + k] = out[rt]
                rt += 1
        o += ln
    assert o == tt
    assert zlib.crc32(out) == crc_tgt, "resultado com CRC32 errado"
    return bytes(out)


if __name__ == "__main__":
    if sys.argv[1] == "criar":
        sys.path.insert(0, "/ds/scripts")
        import nds_rom
        origem, destino = open(sys.argv[2], "rb").read(), open(sys.argv[3], "rb").read()
        # regioes: posicao ANTIGA dos arquivos que mudaram de lugar
        cam = nds_rom.caminhos(origem)
        reg = []
        for c, fid in cam.items():
            a1, z1 = nds_rom.fat_entrada(origem, fid)
            a2, z2 = nds_rom.fat_entrada(destino, fid)
            if (a1, z1) != (a2, z2) or origem[a1:z1] != destino[a2:z2]:
                reg.append((a1, z1))
        p = criar(origem, destino, reg)
        open(sys.argv[4], "wb").write(p)
        print(f"patch: {len(p):,} bytes ({len(reg)} arquivos alterados usados como fonte)")
    else:
        origem, patch = open(sys.argv[2], "rb").read(), open(sys.argv[3], "rb").read()
        open(sys.argv[4], "wb").write(aplicar(origem, patch))
        print("aplicado, CRC32 conferidos")
