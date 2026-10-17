"""Compara cabecalhos de varios .chr: bytes 0x00-0x08, n de paletas
(hipotese: byte 0x05), tamanho, e procura assinaturas ASCII internas."""
import re
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = open("/ds/rom/aots.nds", "rb").read()
for nome in sys.argv[1:]:
    d = nds_rom.ler(rom, f"btl/ene/{nome}.chr")
    b4, b5, u6 = d[4], d[5], struct.unpack_from("<H", d, 6)[0]
    npal = b5
    fim_pal = 8 + npal * 32
    mags = [(hex(m.start()), m.group().decode()) for m in re.finditer(rb"[a-zA-Z]{4}", d)][:12]
    print(f"{nome}: {len(d)} b | b4={b4} b5={b5} u6=0x{u6:04x} ({u6}) | "
          f"paletas fim em 0x{fim_pal:x}: {d[fim_pal:fim_pal + 24].hex(' ')}")
    print(f"    ascii: {mags}")
    print(f"    u32 apos paletas: {[hex(x) for x in struct.unpack_from('<8I', d, fim_pal)]}")
