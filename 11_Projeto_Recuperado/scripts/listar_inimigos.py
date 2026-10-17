"""Lista todos os inimigos (enemy_param) e chefes (boss_param) com nome,
sprite, paleta e atributos, e classifica quais sao do universo Dragon Ball
e quais sao bicho/generico.
"""
import csv
import json
import re
import struct
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/ds/scripts")
src = open("/ds/scripts/analisar_bdat.py").read()
exec(src[src.index("ROM = "):src.index(
    "# ---------------------------------------------------------------------------\n# 1) bdat.bin")])
from bdat import ler_container

LANG = sys.argv[1] if len(sys.argv) > 1 else "EN"
tabs = ler_container(lz10(arquivo(f"btl/bdat/{LANG}/bdat.bin")))

print(f"{len(tabs)} tabelas lidas")
for nome, t in tabs.items():
    print(f"  {nome:20} {t['n_linhas']:4} linhas x {t['tam_linha']:3} b, "
          f"{len(t['colunas'])} colunas")

# ---- nomes ----
cn = tabs["character_name"]
print(f"\ncharacter_name: colunas {[c[0] for c in cn['colunas']]}")
col_nome = cn["colunas"][0][0]      # nesta tabela a coluna se chama 'n'
nomes = [l.get(col_nome, "") for l in cn["linhas"]]
print(f"  {len(nomes)} nomes; primeiros: {nomes[:10]}")

# ---- validacao do leitor ----
ep = tabs["enemy_param"]
primeiro = ep["linhas"][0]
print(f"\nvalidacao: primeira linha de enemy_param -> file={primeiro.get('file')!r} "
      f"name_id={primeiro.get('name_id')}")
assert primeiro.get("file", "").startswith("ene"), "leitor de string errado"


def nome_de(nid):
    # testa as duas convencoes (base 0 e base 1) e escolhe a que da nome
    for idx in (nid, nid - 1):
        if 0 <= idx < len(nomes) and nomes[idx]:
            return nomes[idx]
    return f"?{nid}"


# Base do name_id. A primeira versao aceitava a base que achasse QUALQUER
# nome de saiyajin — e a base 0 passava, com todos os nomes deslocados uma
# linha. O teste decisivo: o sprite do Saibaman (ene001_01) tem 5 paletas,
# e as 5 linhas que usam ele tem que ser TODAS variantes de Saibaman.
def variantes_saibaman(b):
    n = 0
    for l in ep["linhas"]:
        if l.get("file") == "ene001_01":
            i = l["name_id"] - b
            if 0 <= i < len(nomes) and "Sai" in nomes[i]:
                n += 1
    return n


placar = {b: variantes_saibaman(b) for b in (0, 1)}
base = max(placar, key=placar.get)
print(f"linhas de ene001_01 que sao Saibaman, por base: {placar} -> base {base}")
assert placar[base] == 5, "nenhuma base poe os 5 Saibamen no sprite do Saibaman"

BICHO = ("Wolf", "Bear", "Tiger", "Dinosaur", "Pterodactyl", "Snake", "Bat",
         "Bird", "Boar", "Crab", "Fish", "Frog", "Lizard", "Monkey", "Rat",
         "Spider", "Worm", "Bug", "Beetle", "Plant", "Tree", "Mushroom",
         "Scorpion", "Hawk", "Eagle", "Crocodile", "Turtle", "Shark", "Squid",
         "Octopus", "Gorilla", "Ape", "Rhino", "Raptor", "Cat", "Dog", "Pig",
         "Cow", "Sheep", "Moth", "Bee", "Wasp", "Ant", "Fly", "Slime",
         "Mole", "Rabbit", "Deer", "Elk", "Yeti", "Mammoth", "Horn")


def eh_bicho(n):
    return any(k.lower() in n.lower() for k in BICHO)


def dump(tab, rotulo):
    linhas = []
    for i, l in enumerate(tab["linhas"]):
        nid = l.get("name_id", 0)
        nm = nomes[nid - base] if 0 <= nid - base < len(nomes) else f"?{nid}"
        linhas.append({"tabela": rotulo, "idx": i, "nome": nm, "name_id": nid,
                       "file": l.get("file", ""), "palno": l.get("palno"),
                       "lv": l.get("lv"), "hp": l.get("hp"), "exp": l.get("exp"),
                       "zeni": l.get("zeni"), "bicho": eh_bicho(nm)})
    return linhas


inim = dump(ep, "inimigo")
chef = dump(tabs["boss_param"], "chefe")
todos = inim + chef

with open("/ds/saida/inimigos.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(todos[0].keys()))
    w.writeheader()
    w.writerows(todos)

print(f"\n{'#':>3} {'nome':26} {'sprite':11} {'pal':>3} {'lv':>3} {'hp':>6}")
for r in inim:
    marca = "  <- bicho" if r["bicho"] else ""
    print(f"{r['idx']:>3} {r['nome'][:26]:26} {r['file']:11} {r['palno']!s:>3} "
          f"{r['lv']!s:>3} {r['hp']!s:>6}{marca}")

print(f"\n=== chefes (boss_param: {len(chef)}) ===")
for r in chef:
    print(f"{r['idx']:>3} {r['nome'][:26]:26} {r['file']:11} {r['palno']!s:>3} "
          f"{r['lv']!s:>3} {r['hp']!s:>6}")

# ---- resumo ----
sprites = Counter(r["file"] for r in inim)
print("\n" + "=" * 70)
print(f"inimigos comuns: {len(inim)} linhas, {len({r['nome'] for r in inim})} nomes distintos")
print(f"sprites distintos usados: {len(sprites)}  "
      f"(o resto e o mesmo desenho com outra paleta)")
nb = sum(1 for r in inim if r["bicho"])
print(f"marcados como bicho/natureza pelo nome: {nb} de {len(inim)}")
print(f"chefes: {len(chef)}")
print("\nCSV completo: /ds/saida/inimigos.csv")
