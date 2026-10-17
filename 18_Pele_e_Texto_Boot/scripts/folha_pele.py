"""Folha antes/depois (ROM 13 x ROM 13.1) so dos inimigos humanos com a pele corrigida, 4x.
Para cada linha: quadro 0 da animacao 0 (parado) e um quadro de golpe (animacao 3), antes e depois,
mais as amostras das cores trocadas. Desenho igual ao de midia/antes_depois/scripts/sprites.py
(Y de OAM > 32 da a volta).
uso: python -B folha_pele.py   -> verificacao/pele_antes_depois.png
"""
import sys, os
sys.dont_write_bytecode = True
from comum import *
import nds_rom
from dump_tiles import ler_chr, tile_img
from render_quadros import ler_anims, DIM, mascara
from dados_inimigos import enemy_rows
from pele131 import PELE, ROUPA
from PIL import Image, ImageDraw, ImageFont

S = 4
BG = (24, 28, 36); PANEL = (92, 96, 110); TXT = (240, 240, 240); SUB = (170, 180, 200); ACC = (255, 200, 90)


def fonte(n, b=False):
    return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if b else 'C:/Windows/Fonts/arial.ttf', n)


def render(raw, palno, anim, q):
    c = ler_chr(raw); errs = []
    an = ler_anims(raw, c['fim_tiles'], errs)
    assert not errs and an
    anim = min(anim, len(an) - 1)
    quadro = an[anim][min(q, len(an[anim]) - 1)]
    pal = c['pals'][palno]; tiles = c['tiles']
    cv = Image.new('RGBA', (480, 480), (0, 0, 0, 0))
    for x, y, tl, at, hf, vf in reversed(quadro['pecas']):
        if y > 32:
            y -= 256
        w, h = DIM[(at >> 6, (at >> 2) & 3)]
        bloco = Image.new('RGB', (w, h)); masc = Image.new('L', (w, h))
        for ty in range(h // 8):
            for tx in range(w // 8):
                i = tl + ty * (w // 8) + tx
                if i < len(tiles):
                    bloco.paste(tile_img(tiles[i], pal, fundo=(0, 0, 0)), (tx * 8, ty * 8))
                    masc.paste(mascara(tiles[i]), (tx * 8, ty * 8))
        if hf: bloco, masc = bloco.transpose(Image.FLIP_LEFT_RIGHT), masc.transpose(Image.FLIP_LEFT_RIGHT)
        if vf: bloco, masc = bloco.transpose(Image.FLIP_TOP_BOTTOM), masc.transpose(Image.FLIP_TOP_BOTTOM)
        cv.paste(bloco, (240 + x, 300 + y), masc)
    return cv, len(an[anim])


def rgb(c):
    r, g, b = c
    return (r * 255 // 31, g * 255 // 31, b * 255 // 31)


def main():
    a13, a131 = rom('13'), rom('nova')
    en = enemy_rows(a131, 'US')
    linhas = []
    for row in sorted(PELE):
        f, pn, mp, mud = PELE[row]
        assert en[row]['file'] == f and en[row]['palno'] == pn
        ra, rb = nds_rom.ler(a13, f'btl/ene/{f}.chr'), nds_rom.ler(a131, f'btl/ene/{f}.chr')
        _, nq = render(ra, pn, 3, 0)
        ims = [render(ra, pn, 0, 0)[0], render(rb, pn, 0, 0)[0], render(ra, pn, 3, nq // 2)[0], render(rb, pn, 3, nq // 2)[0]]
        bb = None
        for im in ims:
            b = im.getbbox(); bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
        bb = (bb[0] - 2, bb[1] - 2, bb[2] + 2, bb[3] + 2)
        mud_all = dict(mud); mud_all.update(ROUPA.get(row, (None, None, {}))[2])
        linhas.append((row, en[row]['_nome'], f, pn, mp, ims, bb, mud, ROUPA.get(row, (None, None, {}))[2]))
    PW = max((l[6][2] - l[6][0]) for l in linhas) * S
    TW = 420
    W = 20 + 2 * (PW + 16) + 30 + 2 * (PW + 16) + TW
    alturas = [max((l[6][3] - l[6][1]) * S, 150) + 40 for l in linhas]
    H = 90 + sum(alturas)
    img = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(img)
    d.text((20, 14), 'Pele dos inimigos humanos: ROM 13 (antes) x ROM 13.1 (depois), escala 4x', font=fonte(26, True), fill=TXT)
    d.text((20, 50), 'Parado (animação 0, quadro 0) e golpe (animação 3, quadro do meio). Roupa da etapa 13 mantida; só os índices de pele (e o contorno) voltaram aos tons do original.', font=fonte(16), fill=SUB)
    y = 90
    xs = [20, 20 + PW + 16, 20 + 2 * (PW + 16) + 30, 20 + 3 * (PW + 16) + 30]
    rot = ['13 parado', '13.1 parado', '13 golpe', '13.1 golpe']
    for (row, nome, f, pn, mp, ims, bb, mud, roupa), h in zip(linhas, alturas):
        for k, im in enumerate(ims):
            base = Image.new('RGBA', im.size, PANEL + (255,)); base.alpha_composite(im)
            c = base.crop(bb).convert('RGB')
            img.paste(c.resize((c.width * S, c.height * S), Image.NEAREST), (xs[k], y + 26))
            d.text((xs[k], y + 4), rot[k], font=fonte(15, True), fill=ACC)
        tx = xs[3] + PW + 24
        d.text((tx, y + 4), f'Linha {row}: {nome}', font=fonte(20, True), fill=TXT)
        d.text((tx, y + 32), f'{f}  paleta {pn}  (pele do original: paleta {mp})', font=fonte(15), fill=SUB)
        yy = y + 60
        for i, (a, b) in sorted(mud.items()):
            d.rectangle([tx, yy, tx + 22, yy + 18], fill=rgb(a), outline=(0, 0, 0))
            d.text((tx + 28, yy), '→', font=fonte(15, True), fill=TXT)
            d.rectangle([tx + 48, yy, tx + 70, yy + 18], fill=rgb(b), outline=(0, 0, 0))
            d.text((tx + 78, yy), f'índice {i}: {a} → {b}' + ('  (contorno)' if i == 1 else ''), font=fonte(14), fill=TXT)
            yy += 22
        for i, (a, b) in sorted(roupa.items()):
            d.rectangle([tx, yy, tx + 22, yy + 18], fill=rgb(a), outline=(0, 0, 0))
            d.text((tx + 28, yy), '→', font=fonte(15, True), fill=TXT)
            d.rectangle([tx + 48, yy, tx + 70, yy + 18], fill=rgb(b), outline=(0, 0, 0))
            d.text((tx + 78, yy), f'índice {i}: {a} → {b}  (roupa, distância)', font=fonte(14), fill=ACC)
            yy += 22
        d.line([(0, y + h - 1), (W, y + h - 1)], fill=(60, 68, 84), width=1)
        y += h
    os.makedirs(os.path.join(PASTA18, 'verificacao'), exist_ok=True)
    saida = os.path.join(PASTA18, 'verificacao', 'pele_antes_depois.png')
    img.save(saida)
    print(saida, img.size)


if __name__ == '__main__':
    main()
