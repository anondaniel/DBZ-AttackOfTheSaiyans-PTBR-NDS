"""Imagem lado a lado da mesma batalha (mesmo save state) em 3 ROMs."""
from PIL import Image, ImageDraw

S = "/ds/saida"
itens = [
    (f"{S}/ctl2/q0015.png", "ROM dos lobos: cobra segue cobra"),
    (f"{S}/exp32/q0015.png", "sonda: todo inimigo vira Saibaman"),
    (f"{S}/diag1/q0015.png", "linha do Wolf hackeada"),
]
w, h = 256, 192
out = Image.new("RGB", (w * len(itens), h + 14), (20, 20, 20))
d = ImageDraw.Draw(out)
for i, (arq, rot) in enumerate(itens):
    out.paste(Image.open(arq).convert("RGB").crop((0, 0, w, h)), (i * w, 14))
    d.text((i * w + 4, 2), rot, fill=(255, 255, 0))
out = out.resize((out.width * 2, out.height * 2), Image.NEAREST)
out.save(f"{S}/comparativo_lobos.png")
print("ok")
