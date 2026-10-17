"""Monta um quadro em INDICES de paleta (nao em cores) e devolve tambem,
para cada pixel do quadro, de qual (tile, px, py) ele veio. Base para
editar o desenho (cortar cabelo, pintar ombreira) direto nos tiles.

montar(d, anim, quadro) -> (idx[H][W] com -1 = vazio, origem{(x,y): (tile, tx, ty)})
Quadro em coordenadas (0..159, 0..159), com o pe em (80, 140).

uso direto: quadro_indices.py <chr> <anim> <quadro> -> grade de 16 imagens,
uma por indice destacado, ampliada.
"""
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/ds/scripts")
import nds_rom
from dump_tiles import ler_chr, rgb
from render_quadros import DIM, ler_anims

W = H = 160


def pix(tile, x, y):
    b = tile[y * 4 + x // 2]
    return (b >> 4) if x & 1 else (b & 15)


def montar(c, anims, ai, qi):
    idx = [[-1] * W for _ in range(H)]
    origem = {}
    for x0, y0, tl, at, hf, vf in reversed(anims[ai][qi]["pecas"]):
        w, h = DIM[(at >> 6, (at >> 2) & 3)]
        for py in range(h):
            for px in range(w):
                sx = w - 1 - px if hf else px
                sy = h - 1 - py if vf else py
                i = tl + (sy // 8) * (w // 8) + sx // 8
                if i >= len(c["tiles"]):
                    continue
                v = pix(c["tiles"][i], sx % 8, sy % 8)
                X, Y = 80 + x0 + px, 140 + y0 + py
                if v and 0 <= X < W and 0 <= Y < H:
                    idx[Y][X] = v
                    origem[(X, Y)] = (i, sx % 8, sy % 8)
    return idx, origem


def imagem(idx, pal, destaque=None, escala=4):
    im = Image.new("RGB", (W, H), (60, 60, 60))
    px = im.load()
    for y in range(H):
        for x in range(W):
            v = idx[y][x]
            if v > 0:
                px[x, y] = (255, 0, 255) if v == destaque else rgb(pal[v])
    return im.resize((W * escala, H * escala), Image.NEAREST)


if __name__ == "__main__":
    nome, ai, qi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    d = nds_rom.ler(open("/ds/rom/aots.nds", "rb").read(), f"btl/ene/{nome}.chr")
    c = ler_chr(d)
    anims = ler_anims(d, c["fim_tiles"])
    idx, _ = montar(c, anims, ai, qi)
    ys = [y for y in range(H) for x in range(W) if idx[y][x] > 0]
    xs = [x for y in range(H) for x in range(W) if idx[y][x] > 0]
    caixa = (min(xs) - 2, min(ys) - 2, max(xs) + 3, max(ys) + 3)
    cw, ch = (caixa[2] - caixa[0]) * 3, (caixa[3] - caixa[1]) * 3
    g = Image.new("RGB", (cw * 8, (ch + 14) * 2), (20, 20, 20))
    dr = ImageDraw.Draw(g)
    for k in range(16):
        im = imagem(idx, c["pals"][0], destaque=k if k else None, escala=1).crop(caixa)
        im = im.resize((cw, ch), Image.NEAREST)
        x, y = (k % 8) * cw, (k // 8) * (ch + 14)
        g.paste(im, (x, y + 14))
        dr.text((x + 2, y), "original" if k == 0 else f"cor {k}", fill=(255, 255, 0))
    g.save(f"/ds/saida/indices_{nome}_a{ai}q{qi}.png")
    print("ok", caixa)
