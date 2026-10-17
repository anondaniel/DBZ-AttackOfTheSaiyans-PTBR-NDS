"""Tenta ler as secoes 1-4 do .sb como tabela: u32 hsize, u32 n, n
entradas de 4 bytes, e um bloco de strings depois. Mostra entrada->nome.
uso: sb_tabelas.py <caminho> <secao> [max]"""
import re
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = open("/ds/rom/aots.nds", "rb").read()
d = nds_rom.ler(rom, sys.argv[1])
sec = int(sys.argv[2])
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 100
offs = list(struct.unpack_from("<6I", d, 8)) + [len(d)]
a, z = offs[sec], offs[sec + 1]
hs, n = struct.unpack_from("<II", d, a)
print(f"secao {sec}: hsize={hs} n={n} ({z - a} b)")


def cstr(p):
    e = d.index(b"\x00", p)
    return d[p:e].decode("latin-1")


for tam in (4, 8):
    base_str = a + hs + n * tam
    if base_str >= z:
        continue
    print(f"--- entradas de {tam} bytes; strings a partir de 0x{base_str:x}: "
          f"{d[base_str:base_str + 40]!r}")
    for i in range(min(n, mx)):
        e = d[a + hs + i * tam:a + hs + (i + 1) * tam]
        vals = struct.unpack("<" + "H" * (tam // 2), e)
        nome = ""
        if base_str + vals[0] < z:
            try:
                nome = cstr(base_str + vals[0])
            except ValueError:
                pass
        print(f"  {i:3d} {e.hex(' ')}  {vals}  {nome!r}")
    break
