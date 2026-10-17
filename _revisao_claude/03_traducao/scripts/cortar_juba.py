"""Corta a juba do sprite do Raditz (ene220_01) direto nos tiles.

Por quadro (98, via quadro_indices.montar):
  1. rosto = media dos pixels de pele (9,10,11) nos 8 px mais altos de pele
  2. cabelo = cor 2, e cor 1 (fios escuros/contorno) que NAO encosta em
     pixel do corpo (qualquer cor fora de {0,1,2})
  3. cabelo a mais de R px do rosto -> transparente (0)
  4. cabelo que sobrou e encosta num pixel cortado -> cor 1 (contorno novo)
Cada pixel de tile recebe o voto de todos os quadros que o usam; conflito
(quadro quer cortar, outro quer manter) resolve para MANTER, e e contado.

uso: cortar_juba.py [raio=12]  -> /ds/saida/juba/{tiles_novos.bin, antes_depois.png}
"""
import collections
import math
import os
import pickle
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/ds/scripts")
import nds_rom
from dump_tiles import ler_chr
from quadro_indices import H, W, imagem, montar
from render_quadros import ler_anims

R = float(sys.argv[1]) if len(sys.argv) > 1 else 12
OUT = "/ds/saida/juba"
os.makedirs(OUT, exist_ok=True)
d = nds_rom.ler(open("/ds/rom/aots.nds", "rb").read(), "btl/ene/ene220_01.chr")
c = ler_chr(d)
anims = ler_anims(d, c["fim_tiles"])
PELE, CABELO = {9, 10, 11}, {1, 2}
viz4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]

votos = collections.defaultdict(collections.Counter)  # (tile, tx, ty) -> votos
sem_rosto = []
quadros = [(ai, qi) for ai, a in enumerate(anims) for qi in range(len(a))]
for ai, qi in quadros:
    idx, orig = montar(c, anims, ai, qi)
    pele = [(x, y) for y in range(H) for x in range(W) if idx[y][x] in PELE]
    if not pele:
        sem_rosto.append((ai, qi))
        continue
    ytop = min(y for _, y in pele)
    rosto = [(x, y) for x, y in pele if y <= ytop + 8]
    fx = sum(x for x, _ in rosto) / len(rosto)
    fy = sum(y for _, y in rosto) / len(rosto)

    def e_cabelo(x, y):
        v = idx[y][x]
        if v == 2:
            return True
        if v == 1:
            for dx, dy in viz4:
                X, Y = x + dx, y + dy
                if 0 <= X < W and 0 <= Y < H and idx[Y][X] not in (-1, 0, 1, 2):
                    return False  # contorno do corpo
            return True
        return False

    cortar = {(x, y) for (x, y) in orig if e_cabelo(x, y) and math.hypot(x - fx, y - fy) > R}
    # ilhas: cabelo que, depois do corte, nao se liga (8-viz) ao corpo
    vivos = {(x, y) for (x, y) in orig if (x, y) not in cortar}
    sementes = [(x, y) for (x, y) in vivos if not e_cabelo(x, y)]
    visto = set(sementes)
    pilha = list(sementes)
    while pilha:
        x, y = pilha.pop()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                q = (x + dx, y + dy)
                if q in vivos and q not in visto:
                    visto.add(q)
                    pilha.append(q)
    cortar |= vivos - visto
    for (x, y), o in orig.items():
        if (x, y) in cortar:
            votos[o][0] += 1
        elif idx[y][x] == 2 and any((x + dx, y + dy) in cortar for dx, dy in viz4):
            votos[o][1] += 1
        else:
            votos[o][idx[y][x]] += 1

tiles = [bytearray(t) for t in c["tiles"]]
conflitos = 0
mudou = 0
for (ti, tx, ty), vs in votos.items():
    b = tiles[ti][ty * 4 + tx // 2]
    atual = (b >> 4) if tx & 1 else (b & 15)
    (v1, n1), *resto = vs.most_common()
    if resto:
        conflitos += 1
    empate = resto and resto[0][1] == n1
    novo = atual if empate else v1  # maioria dos quadros; empate mantem
    if novo != atual:
        mudou += 1
        if tx & 1:
            tiles[ti][ty * 4 + tx // 2] = (b & 0x0F) | (novo << 4)
        else:
            tiles[ti][ty * 4 + tx // 2] = (b & 0xF0) | novo
print(f"raio {R}: {mudou} pixels de tile mudaram, {conflitos} em conflito (mantidos); "
      f"quadros sem rosto: {sem_rosto}")
pickle.dump([bytes(t) for t in tiles], open(f"{OUT}/tiles_novos.pkl", "wb"))

# antes/depois de uma amostra de quadros
c2 = dict(c)
c2["tiles"] = [bytes(t) for t in tiles]
amostra = [(0, 0), (1, 0), (2, 0), (3, 1), (4, 1), (4, 6), (5, 0), (5, 4), (6, 0), (6, 7), (7, 0), (8, 3)]
w, h = 100, 100
g = Image.new("RGB", (w * len(amostra), h * 2 + 14), (20, 20, 20))
dr = ImageDraw.Draw(g)
for i, (ai, qi) in enumerate(amostra):
    for j, cc in enumerate((c, c2)):
        idx, _ = montar(cc, anims, ai, qi)
        im = imagem(idx, c["pals"][0], escala=1).crop((30, 50, 130, 150))
        g.paste(im, (i * w, 14 + j * h))
    dr.text((i * w + 2, 1), f"a{ai} q{qi}", fill=(255, 255, 0))
g = g.resize((g.width * 2, g.height * 2), Image.NEAREST)
g.save(f"{OUT}/antes_depois_r{int(R)}.png")
print("ok")
