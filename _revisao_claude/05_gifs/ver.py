"""Mostra os ultimos N quadros (ou os de indice dado) numa faixa para conferir. uso: python ver.py <pasta> <saida> [n|i1,i2,..]"""
import sys, glob, os
from PIL import Image
pasta, saida = sys.argv[1], sys.argv[2]
sel = sys.argv[3] if len(sys.argv) > 3 else "6"
fs = sorted(glob.glob(os.path.join(pasta, "[0-9]*.png")))
if "," in sel:
    fs = [fs[int(i)] for i in sel.split(",")]
else:
    fs = fs[-int(sel):]
sheet = Image.new("RGB", (384 * len(fs), 576), (128, 128, 128))
for i, f in enumerate(fs):
    sheet.paste(Image.open(f), (i * 384, 0))
sheet.resize((384 * len(fs) // 2, 288)).save(saida)
print(len(fs), [os.path.basename(f) for f in fs])
