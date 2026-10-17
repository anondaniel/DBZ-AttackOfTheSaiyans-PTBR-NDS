"""Imagem final: a mesma batalha aleatoria no Monte Paozu (mesmo save
state, mesmo passo) na ROM original e na ROM dos lobos."""
from PIL import Image, ImageDraw

S = "/ds/saida/ab122"
col = [("ROM original", "aots"), ("ROM com o hack", "aots_lobos_saibaman")]
w, h, top = 256, 192, 14
out = Image.new("RGB", (w * 2, top + h * 2), (20, 20, 20))
d = ImageDraw.Draw(out)
for i, (rot, nome) in enumerate(col):
    d.text((i * w + 4, 2), rot, fill=(255, 255, 0))
    for j, fase in enumerate(["inicio", "alvo"]):
        im = Image.open(f"{S}/{nome}_{fase}.png").convert("RGB").crop((0, 0, w, h))
        out.paste(im, (i * w, top + j * h))
out = out.resize((out.width * 2, out.height * 2), Image.NEAREST)
out.save("/ds/saida/lobos_ao_vivo_paozu.png")
print("ok")
