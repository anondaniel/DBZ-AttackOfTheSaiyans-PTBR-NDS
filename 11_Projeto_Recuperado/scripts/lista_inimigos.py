"""Folha de todos os inimigos comuns (enemy_param) da ROM final: os 48
trocados pelo hack (PLANO) e os que ficaram como no original.
Cada celula: 1o quadro da 1a animacao do sprite, com a paleta da linha, e
o nome PT-BR da tabela US. Grava /ds/saida/inimigos/{trocados,mantidos}.png
e inimigos.csv.
uso: lista_inimigos.py [rom]"""
import csv
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import tabelas_com_offset
from dump_tiles import ler_chr
from plano_bichos import PLANO
from render_quadros import desenha, ler_anims

ROM = sys.argv[1] if len(sys.argv) > 1 else "/ds/rom/aots_ptbr_img.nds"
rom = open(ROM, "rb").read()
orig = open("/ds/rom/aots.nds", "rb").read()
t = tabelas_com_offset(nds_rom.ler(rom, "btl/bdat/US/bdat.bin"))
t0 = tabelas_com_offset(nds_rom.ler(orig, "btl/bdat/US/bdat.bin"))
nomes = [l["us"] for l in t["character_name"]["linhas"]]
nomes0 = [l["us"] for l in t0["character_name"]["linhas"]]
cam = nds_rom.caminhos(rom)
cache = {}


def miniatura(arq, pal):
    c = f"btl/ene/{arq}.chr"
    if c not in cam:
        return None
    if arq not in cache:
        d = nds_rom.ler(rom, c)
        ch = ler_chr(d)
        cache[arq] = (ch, ler_anims(d, ch["fim_tiles"]))
    ch, anims = cache[arq]
    if not anims or not anims[0]:
        return None
    im = desenha(anims[0][0], ch["tiles"], ch["pals"][min(pal, len(ch["pals"]) - 1)])
    m = Image.new("L", im.size)
    m.putdata([0 if p == (60, 60, 60) else 255 for p in im.getdata()])
    bb = m.getbbox()
    if bb:
        im = im.crop(bb)
    im.thumbnail((72, 72), Image.NEAREST)
    return im


linhas = []
vistos = set()
for i, l in enumerate(t["enemy_param"]["linhas"]):
    nid = l["name_id"]
    if not nid or not l["file"] or l["file"] in ("", "dummy"):
        continue
    nome = nomes[nid - 1]
    if not nome.strip():
        continue  # linha cortada do jogo (sem nome, nivel 1)
    antes = nomes0[t0["enemy_param"]["linhas"][i]["name_id"] - 1]
    chave = (l["file"], l["palno"], nome, i in PLANO)
    if chave in vistos:
        continue
    vistos.add(chave)
    linhas.append({"linha": i, "trocado": i in PLANO, "antes": antes, "nome": nome,
                   "arquivo": l["file"], "paleta": l["palno"], "nivel": l["lv"], "hp": l["hp"]})

os.makedirs("/ds/saida/inimigos", exist_ok=True)
with open("/ds/saida/inimigos/inimigos.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["linha", "situacao", "nome original (EN)", "nome no jogo (PT-BR)", "sprite", "paleta", "nivel", "HP"])
    for x in linhas:
        w.writerow([x["linha"], "trocado" if x["trocado"] else "mantido", x["antes"], x["nome"],
                    x["arquivo"], x["paleta"], x["nivel"], x["hp"]])


def folha(lista, titulo, saida, cols=8):
    cw, chh = 120, 112
    rows = (len(lista) + cols - 1) // cols
    im = Image.new("RGB", (cols * cw, rows * chh + 28), (30, 30, 34))
    d = ImageDraw.Draw(im)
    from PIL import ImageFont
    fn = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    d.text((8, 6), titulo, fill=(255, 220, 120), font=fb)
    for k, x in enumerate(lista):
        cx, cy = (k % cols) * cw, 28 + (k // cols) * chh
        d.rectangle((cx + 2, cy + 2, cx + cw - 3, cy + chh - 3), fill=(52, 52, 58))
        m = miniatura(x["arquivo"], x["paleta"])
        if m:
            im.paste(m, (cx + (cw - m.width) // 2, cy + 4 + (72 - m.height)))
        d.text((cx + 5, cy + 78), x["nome"][:20], fill=(255, 255, 255), font=fn)
        sub = ("era " + x["antes"]) if x["trocado"] else f"Nv {x['nivel']}"
        d.text((cx + 5, cy + 93), sub[:21], fill=(170, 170, 180), font=fn)
    im.save(saida)


troc = [x for x in linhas if x["trocado"]]
mant = [x for x in linhas if not x["trocado"]]
folha(troc, f"TROCADOS PELO HACK ({len(troc)})", "/ds/saida/inimigos/trocados.png")
folha(mant, f"MANTIDOS COMO NO ORIGINAL ({len(mant)})", "/ds/saida/inimigos/mantidos.png")
print(len(troc), "trocados,", len(mant), "mantidos")
