"""Despeja todos os nomes de inimigo comum e de chefe, na ordem da
tabela, para classificacao."""
import re
import struct
import sys

sys.path.insert(0, "/ds/scripts")
src = open("/ds/scripts/analisar_bdat.py").read()
exec(src[src.index("ROM = "):src.index(
    "# ---------------------------------------------------------------------------\n# 1) bdat.bin")])
from bdat import ler_container

tabs = ler_container(lz10(arquivo("btl/bdat/EN/bdat.bin")))
nomes = [l["en"] for l in tabs["character_name"]["linhas"]]

for rot in ("enemy_param", "boss_param"):
    lin = tabs[rot]["linhas"]
    vazios = 0
    print(f"=== {rot}: {len(lin)} linhas ===")
    for i, l in enumerate(lin):
        # name_id e contado a partir de 1 (conferido: com base 1 as 5 linhas
        # do sprite do Saibaman sao as 5 variantes de Saibaman)
        k = l["name_id"] - 1
        n = nomes[k] if 0 <= k < len(nomes) else "?"
        if not n:
            vazios += 1
            continue
        print(f"{i:3}|{n}|{l.get('file','')}|{l.get('lv')}|{l.get('hp')}")
    print(f"--- {len(lin) - vazios} com nome, {vazios} vazios\n")
