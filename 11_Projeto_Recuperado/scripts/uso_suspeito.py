"""Mostra o bytecode em volta de cada uso 'suspeito' (texto curto indo para
funcao que nao e de exibicao) para decidir se e identificador."""
import struct
import subprocess
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from sb import textos

SUSP = {"Chi-Chi", "Ox-King", "Krillin", "Goku", "Tien", "Gohan", "Master Roshi", "Dr. Briefs", "West City",
        "Kiwi Volcano", "Turtle", "Yajirobe", "Puar", "Fortuneteller Baba", "Bulma", "Yamcha",
        "All Dragon Balls collected!"}
DISPLAY = {"Msg", "Select", "SetClickPoint", "Box"}
rom = open("/ds/rom/aots.nds", "rb").read()
vistos = set()
for c in sorted(nds_rom.caminhos(rom)):
    if not (c.startswith("script/US/") and c.endswith(".sb")):
        continue
    d = nds_rom.ler(rom, c)
    if d[:4] != b"SB  ":
        continue
    offs = list(struct.unpack_from("<6I", d, 8))
    a4 = offs[4]
    hs, n = struct.unpack_from("<II", d, a4)
    base = a4 + hs + n * 4
    imps = []
    for i in range(n):
        no, _ = struct.unpack_from("<HH", d, a4 + hs + i * 4)
        imps.append(d[base + no:d.index(b"\x00", base + no)].decode())
    code = d[offs[0]:offs[1]]
    for i, t in enumerate(textos(d)):
        s = t.decode("latin-1")
        if s not in SUSP:
            continue
        p = 0
        while (p := code.find(bytes([0x26, i]), p)) != -1:
            q = code.find(b"\x4a", p + 2)
            while q != -1 and q + 1 < len(code) and code[q + 1] >= len(imps):
                q = code.find(b"\x4a", q + 1)
            fn = imps[code[q + 1]] if q != -1 else "?"
            if fn not in DISPLAY and (s, fn) not in vistos:
                vistos.add((s, fn))
                a = offs[0] + p
                r = subprocess.run(["python3", "/ds/scripts/disasm_sb.py", c, f"{a - 24:x}", f"{a + 40:x}"],
                                   capture_output=True, text=True).stdout
                print(f"=== {s!r} -> {fn} em {c.split('/')[-1]} @{a:x}\n{r}")
            p += 2
