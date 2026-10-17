"""Anda pelo mapa, detecta batalha pela cor do painel de baixo e registra os inimigos.
uso: python explorar.py <inst> <prefixo> <iteracoes> "<padrao de passos>" [fuga]
padrao ex.: "right:900 left:900" (direcao:ms). Capturas em capturas/<prefixo>_NN_[a|b].png
"""
import sys, time, random
import ctl
from PIL import Image

inst, pref, n, padrao = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4].split()
para = len(sys.argv) > 5 and sys.argv[5] == "para"
CAP = ctl.AQUI / "capturas"


def estado():
    p = CAP / "_tmp.png"
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        ctl.shot(inst, str(p))
    im = Image.open(p)
    r, g, b = im.getpixel((15, 330))
    if abs(r - 40) < 20 and abs(g - 73) < 20 and abs(b - 186) < 25:
        return "batalha", im
    return "campo", im


def segura(d, ms):
    h, _, _ = ctl.principal(inst)
    for t in d.split("+"):
        v = ctl.VK[t]; ctl.u32.PostMessageW(h, 0x100, v, ctl.lparam(v, False))
    time.sleep(ms / 1000)
    for t in d.split("+"):
        v = ctl.VK[t]; ctl.u32.PostMessageW(h, 0x101, v, ctl.lparam(v, True))


ctl.seq(inst, "d:ff")
nb = 0
try:
    for i in range(n):
        e, im = estado()
        if e == "batalha":
            nb += 1
            if para:
                ctl.seq(inst, "u:ff"); time.sleep(1.5)
                ctl.shot(inst, str(CAP / f"{pref}_{nb:02d}_a.png")); break
            ctl.seq(inst, "u:ff")
            time.sleep(0.6)
            ctl.shot(inst, str(CAP / f"{pref}_{nb:02d}_a.png"))
            ctl.key(inst, "a", 60, 350)
            ctl.shot(inst, str(CAP / f"{pref}_{nb:02d}_b.png"))
            ctl.key(inst, "down", 60, 250)
            ctl.shot(inst, str(CAP / f"{pref}_{nb:02d}_c.png"))
            ctl.seq(inst, "d:ff")
            k = 0
            while k < 300:
                e2, im2 = estado()
                if e2 != "batalha":
                    break
                k += 1
                roda = im2.getpixel((15, 470))
                if abs(roda[0] - 89) < 15 and abs(roda[2] - 235) < 15:
                    tent = ["left", "left", "right", "right", "right", "down", "up", "up"]
                    while im2.getpixel((170, 462))[0] < 220 and tent:
                        ctl.key(inst, tent.pop(0), 80, 300)
                        im2 = estado()[1]
                ctl.key(inst, "a", 50, 250)
            ctl.shot(inst, str(CAP / f"{pref}_{nb:02d}_d.png"))
            print("batalha", nb, "apertos", k, flush=True)
            ctl.seq(inst, "u:ff")
            for _ in range(5):
                ctl.seq(inst, "a:100:1200 right:150:300 right:150:300 a:100:1500 up:150:700 a:100:1500")
            ctl.shot(inst, str(CAP / f"{pref}_{nb:02d}_e.png"))
            ctl.seq(inst, "d:ff")
            continue
        if i % 5 == 4:
            import shutil; shutil.copy(CAP / "_tmp.png", CAP / f"{pref}_campo_{i:03d}.png")
        ctl.key(inst, "a", 40, 120)
        p = padrao[i % len(padrao)].split(":")
        if p[0] == "w":
            time.sleep(int(p[1]) / 1000)
        else:
            segura(p[0], int(p[1]))
finally:
    ctl.seq(inst, "u:ff")
    ctl.shot(inst, str(CAP / f"{pref}_fim.png"))
    print("total batalhas", nb, flush=True)
