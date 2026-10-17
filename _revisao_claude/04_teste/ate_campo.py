"""Aperta A ate voltar ao campo (botoes vermelho/verde da tela de baixo). uso: ate_campo.py <inst> [max]"""
import sys, contextlib, io, time
import ctl
from PIL import Image
inst = sys.argv[1]; mx = int(sys.argv[2]) if len(sys.argv) > 2 else 60
def campo():
    p = ctl.AQUI / "capturas" / "_tmp.png"
    with contextlib.redirect_stdout(io.StringIO()):
        ctl.shot(inst, str(p))
    im = Image.open(p)
    r1 = im.getpixel((192, 380)); r2 = im.getpixel((192, 475))
    return r1[0] > 180 and r1[1] < 130 and r2[1] > 140 and r2[0] < 140
for i in range(mx):
    if campo():
        print("campo apos", i); break
    if i % 4 == 3: ctl.key(inst, "up", 50, 200)
    ctl.key(inst, "a", 50, 250)
else:
    print("nao voltou ao campo")
