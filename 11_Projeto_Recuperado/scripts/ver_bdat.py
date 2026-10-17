"""Mostra o cabecalho, as colunas e as strings de uma tabela BDAT."""
import re
import struct
import sys

src = open("/ds/scripts/analisar_bdat.py").read()
exec(src[src.index("ROM = "):src.index(
    "# ---------------------------------------------------------------------------\n# 1) bdat.bin")])

LANG = sys.argv[1] if len(sys.argv) > 1 else "EN"
SEC_INI = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x94
SEC_FIM = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x40C4
N_LINHAS = int(sys.argv[4]) if len(sys.argv) > 4 else 20

b = lz10(arquivo(f"btl/bdat/{LANG}/bdat.bin"))
s = b[SEC_INI:SEC_FIM]

print("cabecalho (u16 a partir de 0x04):")
print("  " + " ".join(f"{struct.unpack_from('<H', s, o)[0]:04X}" for o in range(4, 0x28, 2)))
print("cabecalho (u32 a partir de 0x20):")
print("  " + " ".join(f"{struct.unpack_from('<I', s, o)[0]:08X}" for o in range(0x20, 0x30, 4)))
print()
for o in range(0, N_LINHAS * 16, 16):
    lin = s[o:o + 16]
    txt = "".join(chr(c) if 32 <= c < 127 else "." for c in lin)
    print(f"{o:04X}  {lin.hex(' ')}  {txt}")

print("\nstrings (primeiras 45):")
for m in list(re.finditer(rb"[\x20-\x7E]{2,}", s))[:45]:
    print(f"  0x{m.start():04X} {m.group().decode()!r}")
