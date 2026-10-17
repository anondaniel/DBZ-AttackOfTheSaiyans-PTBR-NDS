"""Mapeia as 16 cores da paleta de um .chr: para cada indice, gera uma ROM
(base: demo_soldado.nds, lobo com sprite do Raditz) com AQUELA cor trocada
por magenta, refaz a batalha de 1 lobo e guarda o quadro do alvo.

Paleta: 16 x u16 RGB555 em 0x08 do .chr (assinatura dCHR).
uso: diag_paleta.py <chr> [base_rom] [saida]
"""
import os
import struct
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/ds/scripts")
import nds_rom

CHR = sys.argv[1] if len(sys.argv) > 1 else "btl/ene/ene220_01.chr"
BASE = sys.argv[2] if len(sys.argv) > 2 else "/ds/rom/demo_soldado.nds"
OUT = sys.argv[3] if len(sys.argv) > 3 else "/ds/saida/diag_paleta"
PAL = 0x08
os.makedirs(OUT, exist_ok=True)
base = open(BASE, "rb").read()
orig = nds_rom.ler(base, CHR)
assert orig[:4] == b"dCHR"
cores = struct.unpack_from("<16H", orig, PAL)


def rgb(c):
    return ((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31)


print("paleta:", " ".join(f"{c:04x}" for c in cores))
ims = []
for idx in [-1] + list(range(16)):
    rom = bytearray(base)
    d = bytearray(orig)
    if idx >= 0:
        struct.pack_into("<H", d, PAL + idx * 2, 0x7C1F)  # magenta
    nds_rom.substituir(rom, CHR, bytes(d))
    nome = f"pal_{idx if idx >= 0 else 'base'}"
    caminho = f"/ds/rom/{nome}.nds"
    open(caminho, "wb").write(rom)
    r = subprocess.run(["python3", "/ds/scripts/ab_batalha.py", "/ds/saida/pz5/p0027_pre.bin",
                        "27", "3", OUT, caminho], capture_output=True, text=True)
    os.remove(caminho)
    im = Image.open(f"{OUT}/{nome}_alvo.png").convert("RGB").crop((10, 40, 140, 170))
    ims.append((idx, im))
    print(nome, "ok" if "ok" in r.stdout else "FALHOU")

w, h = 130, 130
g = Image.new("RGB", (w * 6, (h + 14) * 3), (20, 20, 20))
dr = ImageDraw.Draw(g)
for i, (idx, im) in enumerate(ims):
    x, y = (i % 6) * w, (i // 6) * (h + 14)
    g.paste(im, (x, y + 14))
    if idx >= 0:
        dr.rectangle((x, y, x + 12, y + 12), fill=rgb(cores[idx]))
    dr.text((x + 16, y + 1), "original" if idx < 0 else f"cor {idx} ({cores[idx]:04x})", fill=(255, 255, 0))
g = g.resize((g.width * 2, g.height * 2), Image.NEAREST)
g.save(f"{OUT}/mapa_paleta.png")
print("ok", f"{OUT}/mapa_paleta.png")
