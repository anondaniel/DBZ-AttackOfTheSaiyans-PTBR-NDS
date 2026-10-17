"""Mostra cabecalho, strings e hexdump inicial de arquivos de mapa/script.
uso: ver_mapa.py <caminho_na_rom> [n_bytes]"""
import re
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = open("/ds/rom/aots.nds", "rb").read()
cam = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 256
d = nds_rom.ler(rom, cam)
if d[:1] in (b"\x10", b"\x11"):
    print("(comeca com", hex(d[0]), "- talvez comprimido)")
    try:
        d2 = nds_rom.lz10_descomprimir(d) if d[0] == 0x10 else None
        if d2:
            print("LZ10 ->", len(d2))
            d = d2
    except Exception as e:
        print("falhou LZ10:", e)
print(cam, len(d), "bytes")
for i in range(0, min(n, len(d)), 16):
    ch = d[i:i + 16]
    print(f"{i:06x}  {ch.hex(' '):48s}  {''.join(chr(c) if 32 <= c < 127 else '.' for c in ch)}")
ss = re.findall(rb"[ -~]{4,}", d)
print("strings:", [s.decode() for s in ss[:60]])
