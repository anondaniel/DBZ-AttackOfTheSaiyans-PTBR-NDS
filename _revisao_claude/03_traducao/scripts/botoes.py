"""Testa sequencias de botoes a partir do mesmo estado; painel com as duas
telas depois de cada uma.
uso: botoes.py <rom> <estado> <saida.png> "<seq1>" "<seq2>" ...
  seq: botoes separados por espaco, ex.: "start a" ou "b b"
"""
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/ds/scripts")
from ds import DS

ROM, INI, OUT = sys.argv[1:4]
SEQS = sys.argv[4:]
est = open(INI, "rb").read()
ims = []
with DS(ROM) as ds:
    ds.espera(5)
    ds.carregar(est)
    ds.espera(5)
    ims.append(("inicio", ds.tela()))
    for s in SEQS:
        ds.carregar(est)
        ds.espera(2)
        for bt in s.split():
            if bt.startswith("t") and "," in bt:
                ds.toca(*map(int, bt[1:].split(",")), segura=6, depois=30)
            else:
                ds.aperta(*bt.split("+"), segura=6, depois=30)
        ds.espera(30)
        ims.append((s, ds.tela()))
w, h = 256, 384
cols = min(4, len(ims))
g = Image.new("RGB", (w * cols, h * ((len(ims) + cols - 1) // cols)))
dr = ImageDraw.Draw(g)
for i, (rot, im) in enumerate(ims):
    x, y = (i % cols) * w, (i // cols) * h
    g.paste(im, (x, y))
    dr.rectangle((x, y, x + 120, y + 10), fill=(0, 0, 0))
    dr.text((x + 2, y), rot[:20], fill=(255, 255, 0))
g.save(OUT)
print("ok", OUT)
