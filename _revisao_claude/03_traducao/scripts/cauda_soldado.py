"""Cauda do Soldado Saiyajin (ene200_01, derivado do Raditz) mais visivel.
A cauda enrolada na cintura foi desenhada com os tons de pele (indices
9, A, B) e se confunde com a barriga. Aqui ela fica marrom-escura:
9 -> B, A -> B, B -> 1.
Deteccao por quadro: faixa horizontal fina (1-2 px de altura) de 9/A/B,
com contorno escuro (1 ou F) em cima e embaixo e >= 5 px de largura,
na altura da cintura. Os pixels achados sao trocados nos TILES (valem
para todos os quadros que usam o tile).
uso: cauda_soldado.py <rom_entrada> <rom_saida> [--previa]"""
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/ds/scripts")
import nds_rom
from dump_tiles import ler_chr, rgb
from render_quadros import ler_anims
from quadro_indices import montar

PELE = (9, 10, 11)
ESCURO = (1, 15)
TROCA = {9: 11, 10: 11, 11: 1}
ARQ = "btl/ene/ene200_01.chr"


def cauda_do_quadro(idx):
    achados = set()
    ys = [y for y in range(160) if any(v > 0 for v in idx[y])]
    if not ys:
        return achados
    topo, pe = min(ys), max(ys)
    faixa = range(topo + (pe - topo) * 30 // 100, topo + (pe - topo) * 62 // 100)
    for y in faixa:
        x = 0
        while x < 160:
            if idx[y][x] in PELE:
                x2 = x
                while x2 < 160 and idx[y][x2] in PELE + ESCURO and idx[y][x2] > 0:
                    x2 += 1
                run = [xx for xx in range(x, x2) if idx[y][xx] in PELE]
                if len(run) >= 5:
                    ok = []
                    for xx in run:
                        # altura da faixa de pele nessa coluna (<= 2) e contorno escuro acima/abaixo
                        a = y
                        while a - 1 >= 0 and idx[a - 1][xx] in PELE:
                            a -= 1
                        b = y
                        while b + 1 < 160 and idx[b + 1][xx] in PELE:
                            b += 1
                        if b - a <= 1 and idx[a - 1][xx] in ESCURO and idx[b + 1][xx] in ESCURO:
                            ok.append(xx)
                    if len(ok) >= 5:
                        achados.update((xx, y) for xx in ok)
                x = x2
            else:
                x += 1
    return achados


def aplicar(d):
    c = ler_chr(d)
    anims = ler_anims(d, c["fim_tiles"])
    npal = d[5]
    base = 8 + npal * 32
    novo = bytearray(d)
    mudar = {}
    previas = []
    for ai, a in enumerate(anims):
        for qi in range(len(a)):
            idx, org = montar(c, anims, ai, qi)
            pts = cauda_do_quadro(idx)
            for p in pts:
                t, tx, ty = org[p]
                mudar[(t, tx, ty)] = TROCA[idx[p[1]][p[0]]]
            previas.append((ai, qi, idx, pts))
    for (t, tx, ty), v in mudar.items():
        i = base + t * 32 + ty * 4 + tx // 2
        b = novo[i]
        novo[i] = (b & 0x0F) | (v << 4) if tx & 1 else (b & 0xF0) | v
    return bytes(novo), mudar, previas, c


def folha_previa(previas, c, saida, pal=0):
    cel = 70
    cols = 14
    rows = (len(previas) + cols - 1) // cols
    im = Image.new("RGB", (cols * cel * 2, rows * cel * 2), (40, 40, 44))
    for k, (ai, qi, idx, pts) in enumerate(previas):
        q = Image.new("RGB", (160, 160), (60, 60, 60))
        px = q.load()
        for y in range(160):
            for x in range(160):
                v = idx[y][x]
                if v > 0:
                    px[x, y] = (0, 255, 0) if (x, y) in pts else rgb(c["pals"][pal][v])
        bb = q.getbbox()
        q = q.crop((45, 50, 115, 120)).resize((cel * 2, cel * 2), 0)
        im.paste(q, ((k % cols) * cel * 2, (k // cols) * cel * 2))
    im.save(saida)


if __name__ == "__main__":
    ent, sai = sys.argv[1], sys.argv[2]
    rom = bytearray(open(ent, "rb").read())
    d = nds_rom.ler(rom, ARQ)
    novo, mudar, previas, c = aplicar(d)
    n_q = sum(1 for p in previas if p[3])
    print(f"{len(mudar)} pixels de tile trocados; cauda achada em {n_q} de {len(previas)} quadros")
    if "--previa" in sys.argv:
        folha_previa(previas, c, "/ds/saida/cauda_previa.png")
        print("previa -> /ds/saida/cauda_previa.png")
    else:
        print(nds_rom.substituir(rom, ARQ, novo))
        open(sai, "wb").write(rom)
        print("->", sai)
