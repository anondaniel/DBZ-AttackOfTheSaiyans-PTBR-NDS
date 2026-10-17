"""Leitura e reescrita dos TEXTOS de scripts .sb, com tamanho livre.

Formato (conferido nos 500 scripts de cada idioma, ver sb_estrutura.py):
  0x00 "SB  " 01 00 01 00;  0x08 u32 offset[6] das secoes (em ordem,
  alinhadas a 4); secoes: 0 codigo, 1 tabela, 2 TEXTOS, 3 funcoes,
  4 imports, 5 nome da cena.
  Secao 2: u32 8, u32 n, u32 off[n] (relativo ao fim da lista), strings C
  em ordem, zeros ate multiplo de 4.
  O codigo pede texto pelo INDICE (opcode 26 <indice>); secoes 3-5 usam
  offsets relativos a si mesmas. Crescer a secao 2 so exige corrigir os
  offsets do cabecalho das secoes seguintes.

textos(d) -> [bytes]      com_textos(d, textos) -> novo .sb
"""
import struct


def _secoes(d):
    assert d[:8] == b"SB  \x01\x00\x01\x00", "nao e .sb"
    return list(struct.unpack_from("<6I", d, 8))


def textos(d):
    offs = _secoes(d)
    a2 = offs[2]
    hs, n = struct.unpack_from("<II", d, a2)
    base = a2 + hs + n * 4
    r = []
    for i in range(n):
        o = base + struct.unpack_from("<I", d, a2 + hs + i * 4)[0]
        r.append(bytes(d[o:d.index(b"\x00", o)]))
    return r


def com_textos(d, novos):
    offs = _secoes(d)
    a2, a3 = offs[2], offs[3]
    hs, n = struct.unpack_from("<II", d, a2)
    assert len(novos) == n, "o numero de textos nao pode mudar (o codigo usa o indice)"
    corpo, lista = bytearray(), []
    for t in novos:
        assert b"\x00" not in t
        lista.append(len(corpo))
        corpo += t + b"\x00"
    sec2 = struct.pack("<II", hs, n) + struct.pack(f"<{n}I", *lista) + bytes(corpo)
    sec2 += b"\x00" * (-len(sec2) % 4)
    delta = len(sec2) - (a3 - a2)
    out = bytearray(d[:a2]) + sec2 + d[a3:]
    for i in range(3, 6):
        struct.pack_into("<I", out, 8 + i * 4, offs[i] + delta)
    return bytes(out)
