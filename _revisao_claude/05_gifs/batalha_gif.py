"""Anda ate uma batalha e grava marcas de horario (epoch) em <marcas>.
uso: python batalha_gif.py <marcas.txt> <pasta_snap> <seg_max> [entrada]
'entrada' = para depois de mostrar o alvo (nome do inimigo); senao confirma o golpe e espera o dano."""
import sys, time, os
import ctl, raw
from PIL import ImageStat
inst = "gif"; MARC, SNAP, DUR = sys.argv[1], sys.argv[2], float(sys.argv[3])
so_entrada = len(sys.argv) > 4 and sys.argv[4] == "entrada"
os.makedirs(SNAP, exist_ok=True)
def marca(r):
    with open(MARC, "a") as f: f.write(f"{r} {time.time():.3f}\n")
    print(r, flush=True)
def snap():
    im = raw.raw(inst); return im.crop((0, im.size[1] - 576, 384, im.size[1]))
def em_batalha(im):
    r, g, b = im.getpixel((15, 330)); return abs(r - 40) < 20 and abs(g - 73) < 20 and abs(b - 186) < 25
def roda(im):
    r, g, b = im.getpixel((15, 470)); return abs(r - 89) < 15 and abs(b - 235) < 15
def laranja(im): return im.getpixel((170, 462))[0] >= 220
PAD = ["left:1200", "down:900", "right:1200", "up:900"]
ctl.seq(inst, "b:100:800 b:100:800")
t_end = time.time() + DUR; i = 0
while time.time() < t_end:
    im = snap()
    if not em_batalha(im):
        p = PAD[i % len(PAD)].split(":"); i += 1
        marca("passo")
        ctl.key(inst, p[0], int(p[1]), 200)
        continue
    marca("detectou")
    ok = False
    for _ in range(80):
        im = snap()
        if roda(im): ok = True; break
        time.sleep(0.3)
    if not ok:
        marca("travou_ou_sem_roda"); snap().save(SNAP + "/travou.png"); sys.exit(2)
    marca("roda"); im.save(SNAP + "/0_roda.png")
    for t in ["left", "right", "right"]:
        if laranja(im): break
        ctl.key(inst, t, 80, 300); im = snap()
    ctl.key(inst, "a", 80, 300); time.sleep(1.5)
    marca("alvo"); snap().save(SNAP + "/1_alvo.png")
    if so_entrada:
        time.sleep(1.5); marca("fim"); sys.exit(0)
    ctl.key(inst, "a", 80, 200); marca("golpe")
    for k in range(5):
        time.sleep(1.2); snap().save(f"{SNAP}/2_golpe{k}.png")
    marca("fim"); sys.exit(0)
marca("sem_batalha"); sys.exit(1)
