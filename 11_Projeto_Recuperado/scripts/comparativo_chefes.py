"""Grade dos chefes como inimigo comum (diag_chefes.py): uma linha por
chefe, colunas = etiqueta do alvo + 3 momentos da luta."""
import os

from PIL import Image, ImageDraw

S = "/ds/saida/diag_chefes"
CHEFES = [(13, "ene220_01", "Raditz"), (37, "ene221_01", "Nappa"),
          (39, "ene222_01", "Vegeta"), (40, "ene222_02", "Oozaru Vegeta"),
          (5, "ene214_01", "Piccolo"), (42, "ene223_01", "Broly")]
COLS = os.environ.get("COLS", "alvo,q03,q10,q20").split(",")
w, h, faixa = 256, 192, 12
out = Image.new("RGB", (w * len(COLS), len(CHEFES) * (h + faixa)), (20, 20, 20))
d = ImageDraw.Draw(out)
for i, (b, arq, nome) in enumerate(CHEFES):
    y = i * (h + faixa)
    d.text((4, y), f"{nome} ({arq}) no lugar do Wolf", fill=(255, 255, 0))
    for j, c in enumerate(COLS):
        f = f"{S}/{b:02d}_{arq}_{c}.png"
        if os.path.exists(f):
            out.paste(Image.open(f).convert("RGB").crop((0, 0, w, h)), (j * w, y + faixa))
out.save("/ds/saida/chefes_como_inimigo.png")
print("ok", out.size)
