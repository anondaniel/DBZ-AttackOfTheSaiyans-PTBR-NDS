"""Classifica os 151 inimigos comuns por familia de sprite.

A classificacao e por SPRITE (cada trio divide o mesmo desenho, so muda a
paleta) — e a unidade que se troca no hack.

Categorias:
  DB      personagem ou faccao do universo Dragon Ball
  REF     monstro generico no nome, mas que e referencia a DB
          (ver nota em cada um)
  HUMANO  humano generico (bandido, pirata, lutador de dojo)
  BICHO   animal ou inseto
  MONSTRO sobrenatural/criatura sem ligacao com DB
"""
import csv
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/ds/scripts")
import re
import struct
src = open("/ds/scripts/analisar_bdat.py").read()
exec(src[src.index("ROM = "):src.index(
    "# ---------------------------------------------------------------------------\n# 1) bdat.bin")])
from bdat import ler_container

tabs = ler_container(lz10(arquivo("btl/bdat/EN/bdat.bin")))
nomes = [l["en"] for l in tabs["character_name"]["linhas"]]

CLASSE = {
    "ene001_01": ("DB", "Saibamen"),
    "ene002_01": ("DB", "robos da Caverna dos Piratas (DB classico)"),
    "ene003_01": ("DB", "Red Ribbon"), "ene004_01": ("DB", "Red Ribbon"),
    "ene005_01": ("DB", "Red Ribbon"), "ene006_01": ("DB", "Red Ribbon"),
    "ene007_01": ("DB", "Red Ribbon"),
    "ene016_01": ("DB", "Grupo Coelho"), "ene016_02": ("DB", "Grupo Coelho"),
    "ene022_01": ("DB", "servos da Princesa Serpente"),
    "ene045_01": ("REF", "vampiro — lutador da Vovo Uranai (Dracula Man)"),
    "ene046_01": ("REF", "mumia — lutador da Vovo Uranai (Mummy Man)"),
    "ene030_01": ("REF", "dinossauro — sobrevivencia do Gohan com o Piccolo"),
    "ene008_01": ("HUMANO", "bandidas"), "ene010_01": ("HUMANO", "bandidos"),
    "ene011_01": ("HUMANO", "raposas ladras"), "ene012_01": ("HUMANO", "assassinos/fugitivos"),
    "ene013_01": ("HUMANO", "fugitivo"), "ene014_01": ("HUMANO", "piratas/bandidas"),
    "ene015_01": ("HUMANO", "piratas/bandidos"), "ene017_01": ("HUMANO", "dojo"),
    "ene020_01": ("HUMANO", "dojo"), "ene021_01": ("HUMANO", "dojo"),
    "ene023_01": ("HUMANO", "saqueadores"), "ene026_01": ("HUMANO", "xamas/guardas"),
    "ene027_01": ("HUMANO", "tribo"),
    "ene029_01": ("BICHO", "dragoes"), "ene031_01": ("BICHO", "cobras"),
    "ene036_01": ("BICHO", "avestruz/dodo"), "ene037_01": ("BICHO", "aves de rapina"),
    "ene038_01": ("BICHO", "tigres"), "ene039_01": ("BICHO", "lobos"),
    "ene040_01": ("BICHO", "caes"), "ene041_01": ("BICHO", "javalis"),
    "ene042_01": ("BICHO", "ursos"), "ene042_02": ("BICHO", "pandas"),
    "ene043_01": ("BICHO", "peixes"), "ene047_01": ("BICHO", "morcegos"),
    "ene051_01": ("BICHO", "caranguejos"), "ene058_01": ("BICHO", "lagartas"),
    "ene060_01": ("BICHO", "insetos"), "ene061_01": ("BICHO", "larvas"),
    "ene032_01": ("MONSTRO", "fantasmas"), "ene033_01": ("MONSTRO", "carnicais"),
    "ene034_02": ("MONSTRO", "demonios"), "ene035_01": ("MONSTRO", "majins"),
    "ene044_01": ("MONSTRO", "lobisomens"), "ene052_01": ("MONSTRO", "homens-peixe"),
    "ene053_01": ("MONSTRO", "experimentos"), "ene055_01": ("MONSTRO", "homem-areia"),
    "ene057_01": ("MONSTRO", "cientista/guardas"), "ene059_02": ("MONSTRO", "giras"),
    "ene062_01": ("MONSTRO", "robos genericos"),
}

por_cat = defaultdict(list)
sem_classe = []
vazios = 0
for l in tabs["enemy_param"]["linhas"]:
    k = l["name_id"] - 1
    nm = nomes[k] if 0 <= k < len(nomes) else ""
    if not nm:
        vazios += 1
        continue
    f = l["file"]
    if f not in CLASSE:
        sem_classe.append((nm, f))
        continue
    cat, fam = CLASSE[f]
    por_cat[cat].append((nm, f, fam))

total = sum(len(v) for v in por_cat.values())
print(f"inimigos com nome: {total}  (vazios: {vazios})")
assert not sem_classe, f"sprites sem classe: {sem_classe}"

ORDEM = ["DB", "REF", "HUMANO", "BICHO", "MONSTRO"]
print(f"\n{'categoria':9} {'inimigos':>8} {'sprites':>8}")
for c in ORDEM:
    lst = por_cat[c]
    print(f"{c:9} {len(lst):>8} {len({f for _, f, _ in lst}):>8}")

print()
for c in ORDEM:
    fams = defaultdict(list)
    for nm, f, fam in por_cat[c]:
        fams[(f, fam)].append(nm)
    print(f"--- {c} ---")
    for (f, fam), ns in sorted(fams.items()):
        print(f"  {f} {fam:48} {', '.join(ns)}")

with open("/ds/saida/classificacao.csv", "w", newline="", encoding="utf-8") as fo:
    w = csv.writer(fo)
    w.writerow(["categoria", "sprite", "familia", "inimigo"])
    for c in ORDEM:
        for nm, f, fam in por_cat[c]:
            w.writerow([c, f, fam, nm])
print("\nCSV: /ds/saida/classificacao.csv")
