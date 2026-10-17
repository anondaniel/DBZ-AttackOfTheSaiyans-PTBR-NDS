"""Insumos para a lista de nomes em PT-BR:
1) caracteres nao-ASCII usados em TODAS as strings dos 6 bdat.bin
   (evidencia de quais acentos a fonte tem)
2) os bichos: linha, nome, sprite, paleta, nivel, tamanho e mapas onde aparecem
"""
import ast
import collections
import csv
import re
import subprocess
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat import ler_container

rom = open("/ds/rom/aots.nds", "rb").read()
chars = collections.Counter()
for lang in ["EN", "US", "FR", "SP", "GR", "IT"]:
    tabs = ler_container(nds_rom.ler(rom, f"btl/bdat/{lang}/bdat.bin"))
    for t in tabs.values():
        for l in t["linhas"]:
            for v in l.values():
                if isinstance(v, str):
                    chars.update(c for c in v if ord(c) > 126)
# tambem nos scripts .sb (dialogos)
cam = nds_rom.caminhos(rom)
for c in cam:
    if c.startswith("script/") and c.endswith(".sb"):
        for ch in nds_rom.ler(rom, c):
            if ch > 126:
                chars[chr(ch)] += 0  # so marca presenca (bytecode tambem >126)
print("nao-ASCII nas tabelas:", "".join(sorted(k for k, v in chars.items() if v)))
for alvo in "ãõáéíóúâêôàçÃÕÁÉÍÓÚÂÊÔÀÇ":
    print(alvo, "sim" if chars.get(alvo) else "NAO", end="  ")
print()

tabs = ler_container(nds_rom.ler(rom, "btl/bdat/EN/bdat.bin"))
ep = tabs["enemy_param"]["linhas"]
saida = subprocess.run(["python3", "/ds/scripts/grupos_inimigos.py"], capture_output=True, text=True).stdout
mapas = collections.defaultdict(set)
for ln in saida.splitlines():
    m = re.match(r"(\S+)\s+@\S+ argc=15 (\[.*\])", ln)
    if m:
        args = ast.literal_eval(m.group(2))
        for v in args[6:12]:
            if isinstance(v, int) and v > 1:
                mapas[v - 1].add(re.sub(r"\d.*", "", m.group(1)))
cls = {r[3]: r[2] for r in csv.reader(open("/ds/saida/classificacao.csv")) if r[0] == "BICHO"}
nomes = [l["en"] for l in tabs["character_name"]["linhas"]]
for i, l in enumerate(ep):
    n = nomes[l["name_id"] - 1] if l["name_id"] else ""
    if n in cls:
        print(f"{i:3d} {cls[n]:15s} {n:20s} {l['file']} p{l['palno']} lv{l['lv']:<3d} "
              f"size{l['size']} mapas={','.join(sorted(mapas[i]))}")
