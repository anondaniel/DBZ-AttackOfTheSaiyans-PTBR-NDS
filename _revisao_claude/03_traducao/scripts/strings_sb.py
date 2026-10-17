"""Todas as strings (>=3 chars) de um arquivo da ROM, com offset.
uso: strings_sb.py <caminho> [filtro]"""
import re
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = open("/ds/rom/aots.nds", "rb").read()
d = nds_rom.ler(rom, sys.argv[1])
f = sys.argv[2].lower() if len(sys.argv) > 2 else ""
for m in re.finditer(rb"[ -~]{3,}", d):
    s = m.group().decode()
    if f in s.lower():
        print(f"0x{m.start():05x} {s}")
