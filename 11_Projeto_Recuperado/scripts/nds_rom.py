"""Leitura e REESCRITA de arquivos dentro de uma ROM de DS.

substituir(rom, caminho, dados):
  - se couber no espaco original, grava no lugar e ajusta o fim na FAT
  - se nao couber, grava no fim da area usada (alinhado a 0x200), ajusta
    inicio e fim na FAT e o tamanho usado no cabecalho (0x80)
  - recalcula o CRC16 do cabecalho (0x15E)

lz10_comprimir(dados): compressor LZ10 guloso com janela de 4 KB,
  conferido por ida e volta antes de devolver.
"""
import struct


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def caminhos(rom):
    fnt = u32(rom, 0x40)
    res = {}

    def walk(dir_id, pre):
        base = fnt + (dir_id & 0x0FFF) * 8
        p = fnt + u32(rom, base)
        fid = u16(rom, base + 4)
        while True:
            t = rom[p]
            p += 1
            if t == 0:
                break
            n = t & 0x7F
            nome = rom[p:p + n].decode("ascii", "replace")
            p += n
            if t & 0x80:
                walk(u16(rom, p), pre + nome + "/")
                p += 2
            else:
                res[pre + nome] = fid
                fid += 1

    walk(0xF000, "")
    return res


def fat_entrada(rom, fid):
    fat = u32(rom, 0x48)
    return u32(rom, fat + fid * 8), u32(rom, fat + fid * 8 + 4)


def ler(rom, caminho):
    a, b = fat_entrada(rom, caminhos(rom)[caminho])
    return bytes(rom[a:b])


def crc16(dados):
    crc = 0xFFFF
    for byte in dados:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def substituir(rom, caminho, dados):
    """rom: bytearray. Devolve descricao do que fez."""
    fid = caminhos(rom)[caminho]
    fat = u32(rom, 0x48)
    a, b = fat_entrada(rom, fid)
    if len(dados) <= b - a:
        rom[a:a + len(dados)] = dados
        rom[a + len(dados):b] = b"\xff" * (b - a - len(dados))
        struct.pack_into("<I", rom, fat + fid * 8 + 4, a + len(dados))
        acao = f"no lugar (0x{a:08X}, {len(dados)} de {b - a} bytes)"
    else:
        usado = u32(rom, 0x80)
        novo = (usado + 0x1FF) & ~0x1FF
        fim = novo + len(dados)
        if fim > len(rom):
            raise RuntimeError("nao ha espaco no fim da ROM")
        assert all(x == 0xFF for x in rom[novo:fim]) or all(x == 0 for x in rom[novo:fim]), \
            "area apos o fim usado nao esta livre"
        rom[novo:fim] = dados
        struct.pack_into("<II", rom, fat + fid * 8, novo, fim)
        struct.pack_into("<I", rom, 0x80, fim)
        acao = f"realocado para 0x{novo:08X} ({len(dados)} bytes; antes {b - a})"
    struct.pack_into("<H", rom, 0x15E, crc16(rom[0:0x15E]))
    return acao


def lz10_descomprimir(d):
    tam = d[1] | (d[2] << 8) | (d[3] << 16)
    out = bytearray()
    p = 4
    while len(out) < tam:
        fl = d[p]
        p += 1
        for bit in range(8):
            if len(out) >= tam:
                break
            if fl & (0x80 >> bit):
                b0, b1 = d[p], d[p + 1]
                p += 2
                n = (b0 >> 4) + 3
                disp = (((b0 & 0xF) << 8) | b1) + 1
                for _ in range(n):
                    out.append(out[-disp])
            else:
                out.append(d[p])
                p += 1
    return bytes(out)


def lz10_comprimir(dados):
    n = len(dados)
    out = bytearray([0x10, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF])
    tabela = {}
    i = 0
    while i < n:
        flag_pos = len(out)
        out.append(0)
        flag = 0
        for bit in range(8):
            if i >= n:
                break
            melhor_n, melhor_d = 0, 0
            if i + 3 <= n:
                chave = dados[i:i + 3]
                for j in reversed(tabela.get(chave, [])[-64:]):
                    d = i - j
                    if d > 0x1000:
                        break
                    k = 3
                    while k < 18 and i + k < n and dados[j + k] == dados[i + k]:
                        k += 1
                    if k > melhor_n:
                        melhor_n, melhor_d = k, d
                        if k == 18:
                            break
            if melhor_n >= 3:
                flag |= 0x80 >> bit
                v = ((melhor_n - 3) << 12) | (melhor_d - 1)
                out += bytes([v >> 8, v & 0xFF])
                passo = melhor_n
            else:
                out.append(dados[i])
                passo = 1
            for q in range(i, min(i + passo, n - 2)):
                tabela.setdefault(dados[q:q + 3], []).append(q)
            i += passo
        out[flag_pos] = flag
    while len(out) % 4:
        out.append(0)
    res = bytes(out)
    assert lz10_descomprimir(res) == bytes(dados), "LZ10 nao fez ida e volta"
    return res
