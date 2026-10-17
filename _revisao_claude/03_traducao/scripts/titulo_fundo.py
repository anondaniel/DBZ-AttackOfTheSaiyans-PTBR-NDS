"""Fundo limpo (sem texto) de um cartao de titulo de capitulo.
O letreiro e branco com contorno preto. Em cada versao de idioma (base=
japones, en, fr, gr, it, sp, us), marca como texto os pixels quase brancos
ou quase pretos dentro das faixas de texto (+1 px de margem). Por pixel, usa
a cor mais comum entre as versoes que NAO tem texto ali; se todas tem,
preenche com a media dos vizinhos ja limpos.
uso: titulo_fundo.py <NN>  -> /ds/saida/titulos/fundo_CNN.png"""
import collections
import os
import struct
import sys

from PIL import Image

sys.path.insert(0, "/ds/scripts")
import imp
import nds_rom
from dump_tiles import rgb

LANGS = ["", "en", "fr", "gr", "it", "sp", "us"]


def ler_map(d):
    w, h = d[6] * 8, d[7] * 8
    pal = list(struct.unpack_from("<256H", d, 0x10))
    px, _ = imp.descomprimir(d, w, h, 0x210)
    return w, h, pal, px


def versoes(rom, n):
    r = {}
    for lg in LANGS:
        try:
            r[lg] = ler_map(nds_rom.ler(rom, f"fld/map/C{n:02d}/C{n:02d}_9999{lg}.map"))
        except Exception:
            pass
    return r


def e_letreiro(c):
    return min(c) >= 225 or max(c) <= 45


def mascara(cores, w, h, faixa, comum):
    """texto = branco/preto que NAO e compartilhado pela maioria das versoes
    (fundo branco igual em todas e arte, nao letreiro)"""
    m = [False] * (w * h)
    for y in range(faixa[0], faixa[1]):
        for x in range(w):
            i = y * w + x
            if e_letreiro(cores[i]) and comum[i].get(cores[i], 0) <= 5:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < h and 0 <= xx < w:
                            m[yy * w + xx] = True
    return m


def linhas_texto(cores_us, comum, w, h):
    """linhas (y) com letreiro proprio da versao US"""
    return [y for y in range(20, 172)
            if sum(1 for x in range(w) if e_letreiro(cores_us[y * w + x])
                   and comum[y * w + x].get(cores_us[y * w + x], 0) <= 3) > 8]


def faixa_texto(cores_us, comum, w, h):
    ys = linhas_texto(cores_us, comum, w, h)
    return (max(0, min(ys) - 2), min(h, max(ys) + 3)) if ys else (0, 0)


def fundo(rom, n):
    vs = versoes(rom, n)
    w, h = vs["us"][0], vs["us"][1]
    cores = {lg: [rgb(v[2][p]) for p in v[3]] for lg, v in vs.items()}
    comum = [collections.Counter(cores[lg][i] for lg in cores) for i in range(w * h)]
    f = (20, 172)
    masc = {lg: mascara(c, w, h, f, comum) for lg, c in cores.items()}
    out = list(cores["us"])
    buraco = []
    for i in range(f[0] * w, f[1] * w):
        livres = [cores[lg][i] for lg in cores if not masc[lg][i]]
        if livres:
            out[i] = collections.Counter(livres).most_common(1)[0][0]
        else:
            buraco.append(i)
    # preenche buracos com a media dos vizinhos ja definidos (varias passadas)
    pend = set(buraco)
    while pend:
        novo = {}
        for i in pend:
            y, x = divmod(i, w)
            viz = [out[j] for j in (i - 1, i + 1, i - w, i + w)
                   if 0 <= j < w * h and j not in pend and abs((j % w) - x) <= 1]
            if viz:
                novo[i] = tuple(sum(c[k] for c in viz) // len(viz) for k in range(3))
        if not novo:
            break
        for i, c in novo.items():
            out[i] = c
        pend -= set(novo)
    return w, h, out, linhas_texto(cores["us"], comum, w, h), len(buraco)


if __name__ == "__main__":
    n = int(sys.argv[1])
    rom = open("/ds/rom/aots.nds", "rb").read()
    w, h, out, f, nb = fundo(rom, n)
    os.makedirs("/ds/saida/titulos", exist_ok=True)
    im = Image.new("RGB", (w, h))
    im.putdata(out)
    im.save(f"/ds/saida/titulos/fundo_C{n:02d}.png")
    print(f"C{n:02d}: faixa de texto y={f}, {nb} pixels preenchidos por vizinhos")
