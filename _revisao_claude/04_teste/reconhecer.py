"""Anda pelo mapa; em cada batalha fotografa os inimigos e o NOME de cada alvo,
depois tenta fugir. uso: python reconhecer.py <inst> <prefixo> <iter> "<padrao>" [lutar]"""
import sys, time, contextlib, io, os
import ctl
from PIL import Image

inst, pref, n, padrao = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4].split()
lutar = len(sys.argv) > 5 and sys.argv[5] == "lutar"
CAP = ctl.AQUI / "capturas"


def foto(nome=None):
    p = CAP / (nome or "_tmp")
    p = p.with_suffix(".png")
    with contextlib.redirect_stdout(io.StringIO()):
        ctl.shot(inst, str(p))
    return Image.open(p)


def em_batalha(im):
    r, g, b = im.getpixel((15, 330))
    return abs(r - 40) < 20 and abs(g - 73) < 20 and abs(b - 186) < 25


def roda(im):
    r, g, b = im.getpixel((15, 470))
    return abs(r - 89) < 15 and abs(b - 235) < 15


def atacar_sel(im):
    return im.getpixel((170, 462))[0] >= 220


def ir_para_atacar():
    im = foto()
    for t in ["left", "left", "right", "right", "right", "down", "up", "up"]:
        if atacar_sel(im):
            return True
        ctl.key(inst, t, 80, 300); im = foto()
    return atacar_sel(im)


def segura(d, ms):
    h, _, _ = ctl.principal(inst)
    for t in d.split("+"):
        v = ctl.VK[t]; ctl.u32.PostMessageW(h, 0x100, v, ctl.lparam(v, False))
    time.sleep(ms / 1000)
    for t in d.split("+"):
        v = ctl.VK[t]; ctl.u32.PostMessageW(h, 0x101, v, ctl.lparam(v, True))


nb = 0
ctl.seq(inst, "d:ff")
try:
    for i in range(n):
        im = foto()
        if not em_batalha(im):
            if i % 5 == 4:
                im.save(CAP / f"{pref}_campo_{i:03d}.png")
            if not os.environ.get("SEM_A"):
                ctl.key(inst, "a", 40, 120)
            p = padrao[i % len(padrao)].split(":")
            segura(p[0], int(p[1]))
            continue
        nb += 1
        ctl.seq(inst, "u:ff")
        # espera a roda de comandos
        for _ in range(30):
            im = foto()
            if roda(im) or not em_batalha(im):
                break
            time.sleep(0.3)
        im.save(CAP / f"{pref}_{nb:02d}_a.png")
        if roda(im) and ir_para_atacar():
            ctl.key(inst, "a", 80, 450)
            for k in range(4):
                foto(f"{pref}_{nb:02d}_alvo{k}")
                ctl.key(inst, ["down", "down", "up", "left"][k], 80, 350)
            if not lutar:
                ctl.key(inst, "b", 80, 400)
        # luta ou foge
        ctl.seq(inst, "d:ff")
        k = 0
        while k < 300:
            im = foto()
            if not em_batalha(im):
                break
            k += 1
            if roda(im):
                if lutar:
                    ir_para_atacar()
                else:
                    for t in ["right", "right"]:
                        if im.getpixel((300, 470)) != (0, 0, 0):
                            pass
                    # Fugir = direita duas vezes a partir de Atacar
                    ir_para_atacar(); ctl.key(inst, "right", 80, 300); ctl.key(inst, "right", 80, 300)
                    foto(f"{pref}_{nb:02d}_fuga")
            ctl.key(inst, "a", 50, 300)
        ctl.seq(inst, "u:ff")
        foto(f"{pref}_{nb:02d}_fim")
        for _ in range(4 if lutar else 0):
            ctl.seq(inst, "a:100:1200 right:150:300 right:150:300 a:100:1500 up:150:700 a:100:1500")
        if not lutar:
            ctl.seq(inst, "b:80:400 b:80:400 b:80:400")
        foto(f"{pref}_{nb:02d}_pos")
        print("batalha", nb, "laco", k, flush=True)
        ctl.seq(inst, "d:ff")
finally:
    ctl.seq(inst, "u:ff")
    foto(f"{pref}_fim")
    print("total", nb, flush=True)
