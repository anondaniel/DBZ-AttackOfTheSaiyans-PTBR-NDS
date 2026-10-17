"""Desenha os glifos de latin0.fnt / latin1.fnt testando formatos 1bpp.
Estrutura: 256 bytes de largura por caractere + 256 glifos de N bytes.
uso: ver_fonte.py <arquivo> <larg>x<alt> [msb|lsb] [linha|coluna]
"""
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/ds/scripts")
import nds_rom

arq, dim = sys.argv[1], sys.argv[2]
ordem = sys.argv[3] if len(sys.argv) > 3 else "msb"
W, H = map(int, dim.split("x"))
d = nds_rom.ler(open("/ds/rom/aots.nds", "rb").read(), arq)
larg = d[:256]
nb = (len(d) - 256) // 256
print(arq, "bytes por glifo:", nb, "| bits:", nb * 8, "| formato testado", dim, ordem)
E = 3
g = Image.new("RGB", (16 * (W + 3) * E, 16 * (H + 10) * E), (30, 30, 30))
dr = ImageDraw.Draw(g)
for ch in range(256):
    gl = d[256 + ch * nb: 256 + (ch + 1) * nb]
    bits = []
    for b in gl:
        for k in range(8):
            bits.append((b >> (7 - k)) & 1 if ordem == "msb" else (b >> k) & 1)
    ox, oy = (ch % 16) * (W + 3) * E, (ch // 16) * (H + 10) * E
    for y in range(H):
        for x in range(W):
            i = y * W + x
            if i < len(bits) and bits[i]:
                cor = (255, 255, 255) if x < larg[ch] else (255, 80, 80)
                dr.rectangle((ox + x * E, oy + 9 + y * E, ox + x * E + E - 1, oy + 9 + y * E + E - 1), fill=cor)
    dr.text((ox, oy - 1), f"{ch:02x}", fill=(120, 200, 255))
nome = arq.replace(".fnt", "")
g.save(f"/ds/saida/fonte_{nome}_{dim}_{ordem}.png")
print("ok", f"/ds/saida/fonte_{nome}_{dim}_{ordem}.png")
