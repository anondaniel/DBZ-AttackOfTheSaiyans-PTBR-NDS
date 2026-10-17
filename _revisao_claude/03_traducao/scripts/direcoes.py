"""Testa as 8 direcoes a partir do mesmo estado e monta um painel com o
quadro depois de cada uma (so a tela de cima).
uso: direcoes.py <rom> <estado> <saida.png> [quadros=60]"""
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/ds/scripts")
from ds import DS

ROM, INI, OUT = sys.argv[1:4]
Q = int(sys.argv[4]) if len(sys.argv) > 4 else 60
DIRS = ["up", "up+right", "right", "down+right", "down", "down+left", "left", "up+left"]
est = open(INI, "rb").read()
ims = []
with DS(ROM) as ds:
    ds.espera(5)
    ds.carregar(est)
    ds.espera(5)
    ims.append(("inicio", ds.tela().crop((0, 0, 256, 192))))
    for d in DIRS:
        ds.carregar(est)
        ds.espera(2)
        ds.aperta(*d.split("+"), segura=Q, depois=10)
        ims.append((d, ds.tela().crop((0, 0, 256, 192))))
g = Image.new("RGB", (256 * 3, 192 * 3))
dr = ImageDraw.Draw(g)
for i, (rot, im) in enumerate(ims):
    x, y = (i % 3) * 256, (i // 3) * 192
    g.paste(im, (x, y))
    dr.rectangle((x, y, x + 70, y + 10), fill=(0, 0, 0))
    dr.text((x + 2, y), rot, fill=(255, 255, 0))
g.save(OUT)
print("ok", OUT)
