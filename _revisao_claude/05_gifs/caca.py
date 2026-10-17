"""Anda na caverna (save Switch) e, ao entrar em batalha, fotografa cada etapa:
roda de comandos, lista de alvos (nome do inimigo) e golpe. uso: python caca.py <segundos>"""
import sys, time, os
import ctl, raw
from PIL import Image
inst = "gif"; OUT = os.environ.get("OUT", "capturas/bat2"); os.makedirs(OUT, exist_ok=True)
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 240
def snap():
    im = raw.raw(inst); return im.crop((0, im.size[1] - 576, 384, im.size[1]))
def em_batalha(im):
    r, g, b = im.getpixel((15, 330)); return abs(r - 40) < 20 and abs(g - 73) < 20 and abs(b - 186) < 25
def roda(im):
    r, g, b = im.getpixel((15, 470)); return abs(r - 89) < 15 and abs(b - 235) < 15
def laranja(im): return im.getpixel((170, 462))[0] >= 220
PAD = ["left:1200", "down:900", "right:1200", "up:900"]
ctl.seq(inst, "b:100:800 b:100:800")
t_end = time.time() + DUR; bat = 0; i = 0
while time.time() < t_end:
    im = snap()
    if not em_batalha(im):
        ctl.key(inst, "a", 40, 120)          # fecha RESULTADO/textos e interage se houver algo
        p = PAD[i % len(PAD)].split(":"); i += 1
        ctl.key(inst, p[0], int(p[1]), 200)
        continue
    bat += 1; pre = f"{OUT}/b{bat:02d}"
    print("batalha", bat, flush=True)
    for _ in range(80):
        im = snap()
        if roda(im) or not em_batalha(im): break
        time.sleep(0.3)
    if not em_batalha(im): continue
    im.save(pre + "_0_roda.png")
    for t in ["left", "right", "right"]:
        if laranja(im): break
        ctl.key(inst, t, 80, 300); im = snap()
    ctl.key(inst, "a", 80, 900); time.sleep(1.2)
    snap().save(pre + "_1_alvo.png")
    ctl.key(inst, "a", 80, 1200)
    for k in range(4):
        time.sleep(0.8); snap().save(f"{pre}_2_golpe{k}.png")
    for turno in range(6):
        for _ in range(60):
            im = snap()
            if not em_batalha(im) or roda(im): break
            time.sleep(0.4)
        if not em_batalha(im): break
        ctl.key(inst, "a", 60, 400); time.sleep(0.5); ctl.key(inst, "a", 60, 400)
        time.sleep(2.5)
    snap().save(pre + "_9_fim.png")
print("fim, batalhas", bat, flush=True)
