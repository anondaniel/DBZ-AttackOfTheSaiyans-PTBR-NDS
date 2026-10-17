"""Anda ate a 1a batalha; diz se a batalha abriu (e fotografa os alvos) ou se travou
(tela escura parada). uso: python uma_batalha.py <inst> <prefixo> [max_iter] [lutar_turnos]"""
import sys, time, contextlib, io
import ctl
from PIL import Image, ImageStat

inst, pref = sys.argv[1], sys.argv[2]
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 80
turnos = int(sys.argv[4]) if len(sys.argv) > 4 else 0
CAP = ctl.AQUI / "capturas"
PAD = ["left:1200", "down:900", "right:1200", "up:900"]


def foto(nome="_tmp"):
    p = CAP / f"{nome}.png"
    with contextlib.redirect_stdout(io.StringIO()):
        ctl.shot(inst, str(p))
    return Image.open(p)


def em_batalha(im):
    r, g, b = im.getpixel((15, 330))
    return abs(r - 40) < 20 and abs(g - 73) < 20 and abs(b - 186) < 25


def roda(im):
    r, g, b = im.getpixel((15, 470))
    return abs(r - 89) < 15 and abs(b - 235) < 15


def escuro(im):
    return sum(ImageStat.Stat(im).mean) / 3 < 12


def segura(d, ms):
    h, _, _ = ctl.principal(inst)
    for t in d.split("+"):
        v = ctl.VK[t]; ctl.u32.PostMessageW(h, 0x100, v, ctl.lparam(v, False))
    time.sleep(ms / 1000)
    for t in d.split("+"):
        v = ctl.VK[t]; ctl.u32.PostMessageW(h, 0x101, v, ctl.lparam(v, True))


esc = 0
for i in range(mx):
    im = foto()
    if escuro(im):
        esc += 1
        if esc >= 6:
            foto(f"{pref}_TRAVOU")
            print("RESULTADO: TRAVOU (tela escura parada) iter", i); sys.exit(2)
        time.sleep(1.5); continue
    esc = 0
    if em_batalha(im):
        for _ in range(40):
            im = foto()
            if roda(im):
                break
            time.sleep(0.4)
        foto(f"{pref}_bat")
        # alvos
        for t in ["left", "left", "right", "right", "right"]:
            if im.getpixel((170, 462))[0] >= 220: break
            ctl.key(inst, t, 80, 300); im = foto()
        ctl.key(inst, "a", 80, 500)
        foto(f"{pref}_alvo0"); ctl.key(inst, "down", 80, 350)
        foto(f"{pref}_alvo1"); ctl.key(inst, "up", 80, 350); ctl.key(inst, "up", 80, 350)
        foto(f"{pref}_alvo2"); ctl.key(inst, "b", 80, 400)
        # luta alguns turnos (para ver invocacao) com Defender, depois foge
        n = 0; k = 0
        while n < turnos and k < 400:
            im = foto(); k += 1
            if not em_batalha(im): break
            if roda(im):
                n += 1
                foto(f"{pref}_turno{n:02d}")
                # Defender = baixo a partir de Atacar
                ctl.key(inst, "down", 80, 300); ctl.key(inst, "a", 80, 300)
            else:
                ctl.key(inst, "a", 50, 300)
        foto(f"{pref}_antes_fuga")
        print("RESULTADO: BATALHA OK, turnos", n, flush=True); sys.exit(0)
    p = PAD[i % len(PAD)].split(":")
    segura(p[0], int(p[1]))
print("RESULTADO: SEM BATALHA")
