"""Checa se nome e sprite estao alinhados em enemy_param.

Suspeita: os tipos de criatura (dragao, dinossauro, cobra, fantasma,
coelho) aparecem em trios que atravessam a fronteira entre dois sprites,
como se o nome estivesse deslocado uma linha em relacao ao grafico.

Mostra name_id cru, o nome resultante e o sprite, lado a lado, e mede
quantos grupos de sprite ficam "puros" (um tipo so) com deslocamento
0, +1 e -1.
"""
import re
import struct
import sys
from collections import defaultdict

sys.path.insert(0, "/ds/scripts")
src = open("/ds/scripts/analisar_bdat.py").read()
exec(src[src.index("ROM = "):src.index(
    "# ---------------------------------------------------------------------------\n# 1) bdat.bin")])
from bdat import ler_container

tabs = ler_container(lz10(arquivo("btl/bdat/EN/bdat.bin")))
nomes = [l["en"] for l in tabs["character_name"]["linhas"]]
ep = tabs["enemy_param"]["linhas"]

print(f"{'#':>3} {'name_id':>7}  {'nome':24} {'sprite':10} pal")
for i, l in enumerate(ep[:24]):
    nid = l["name_id"]
    print(f"{i:>3} {nid:>7}  {nomes[nid] if nid < len(nomes) else '?':24} "
          f"{l['file']:10} {l['palno']}")

TIPOS = ["Sai", "Robot", "Red Ribbon", "RR ", "Bandit", "Fox", "Rabbit",
         "Dragon", "Dinosaur", "Snake", "Ghost", "Demon", "Pupil", "Pirate",
         "Wolf", "Bear", "Tiger", "Bat", "Frog", "Plant"]


def tipo(n):
    for t in TIPOS:
        if t.lower() in n.lower():
            return t
    return None


print("\npureza dos grupos de sprite por deslocamento do nome:")
for desl in (-1, 0, 1):
    grupos = defaultdict(set)
    for i, l in enumerate(ep):
        j = i + desl
        if not (0 <= j < len(ep)):
            continue
        nid = ep[j]["name_id"]
        t = tipo(nomes[nid]) if nid < len(nomes) else None
        if t:
            grupos[l["file"]].add(t)
    puros = sum(1 for s in grupos.values() if len(s) == 1)
    print(f"  deslocamento {desl:+d}: {puros} de {len(grupos)} sprites com um tipo so")
