"""Junta as capturas de uma pasta numa grade (so a tela de cima), para
ver um trajeto inteiro numa imagem so.

uso: montagem.py <pasta> [colunas] [so_cima=1]
"""
import glob
import os
import sys

from PIL import Image, ImageDraw

pasta = sys.argv[1]
cols = int(sys.argv[2]) if len(sys.argv) > 2 else 4
so_cima = (sys.argv[3] if len(sys.argv) > 3 else "1") == "1"
pref = os.environ.get("PREF", "q")  # prefixo dos quadros (q, p, bat...)
arqs = sorted(glob.glob(f"{pasta}/{pref}*.png")) + [f"{pasta}/final.png"]
arqs = [a for a in arqs if os.path.exists(a)]
ims = []
for a in arqs:
    im = Image.open(a).convert("RGB")
    if so_cima:
        im = im.crop((0, 0, 256, 192))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 60, 10), fill=(0, 0, 0))
    d.text((2, 0), os.path.basename(a)[:-4], fill=(255, 255, 0))
    ims.append(im)
w, h = ims[0].size
linhas = (len(ims) + cols - 1) // cols
grade = Image.new("RGB", (w * cols, h * linhas), (40, 40, 40))
for i, im in enumerate(ims):
    grade.paste(im, ((i % cols) * w, (i // cols) * h))
grade.save(f"{pasta}/montagem.png")
print(f"{len(ims)} quadros -> {pasta}/montagem.png")
