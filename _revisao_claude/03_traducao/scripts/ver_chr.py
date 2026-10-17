"""Primeira olhada num .chr de inimigo: tamanho, compressao, cabecalho em
u32/u16, e regioes com cara de paleta RGB555 (u16 com bit 15 = 0 e
valores 'suaves' em sequencia).
uso: ver_chr.py <caminho_na_rom> [n_hex]"""
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = open("/ds/rom/aots.nds", "rb").read()
cam = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 256
d = nds_rom.ler(rom, cam)
print(cam, len(d), "bytes; primeiros:", d[:16].hex(" "))
if d[0] in (0x10, 0x11):
    tam = d[1] | d[2] << 8 | d[3] << 16
    print(f"  pode ser LZ{d[0]:02x}, tamanho declarado {tam}")
    if d[0] == 0x10:
        try:
            d = nds_rom.lz10_descomprimir(d)
            print("  LZ10 ok ->", len(d))
        except Exception as e:
            print("  LZ10 falhou", e)
for i in range(0, min(n, len(d)), 16):
    ch = d[i:i + 16]
    print(f"{i:06x}  {ch.hex(' '):48s}  {' '.join(f'{x:08x}' for x in struct.unpack_from('<4I', ch.ljust(16, bytes(1))))}")
# u32 que parecem offsets dentro do arquivo
print("u32 do cabecalho que sao < tamanho:",
      [(hex(i * 4), hex(v)) for i, v in enumerate(struct.unpack_from(f"<{min(64, len(d) // 4)}I", d)) if 0 < v < len(d)][:40])
