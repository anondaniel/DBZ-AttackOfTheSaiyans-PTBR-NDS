"""Grade antes x depois dos ursos e pandas (diag_bichos.py): uma linha por
bicho, quadro com a etiqueta de nome do alvo."""
import os

from PIL import Image, ImageDraw

S = os.environ.get("S", "/ds/saida/diag_bichos1")
BICHOS = [
    (113, "Hungry Bear -> Saibaman"),
    (114, "Snow Bear -> T. Sai"),
    (115, "Strong Bear -> K. Sai"),
    (116, "Dangerous Panda -> Saibaman"),
    (117, "Snow Panda -> T. Sai"),
    (118, "Ultimate Pandaman -> K. Sai"),
]
w, h, faixa, topo = 256, 192, 12, 12
out = Image.new("RGB", (w * 2, topo + len(BICHOS) * (h + faixa)), (20, 20, 20))
d = ImageDraw.Draw(out)
d.text((4, 0), "ROM original", fill=(255, 255, 0))
d.text((w + 4, 0), "ROM com o hack", fill=(255, 255, 0))
for i, (linha, rot) in enumerate(BICHOS):
    y = topo + i * (h + faixa)
    d.text((4, y), rot, fill=(255, 255, 255))
    for j, fase in enumerate(("antes", "depois")):
        im = Image.open(f"{S}/{linha}_{fase}_alvo.png").convert("RGB").crop((0, 0, w, h))
        out.paste(im, (j * w, y + faixa))
out = out.resize((out.width * 2, out.height * 2), Image.NEAREST)
out.save("/ds/saida/ursos_pandas_antes_depois.png")
print("ok", out.size)
