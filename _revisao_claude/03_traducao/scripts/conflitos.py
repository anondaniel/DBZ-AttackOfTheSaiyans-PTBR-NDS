"""Confere a tabela de trocas contra os encontros de cada mapa: acusa mapa
onde dois inimigos DIFERENTES viram o MESMO nome de Saibaman (inclusive
Saibamen de verdade, ids 1-5).

Le a tabela TROCAS do hack_saibaman.py e os grupos do grupos_inimigos.py.
uso: conflitos.py
"""
import ast
import collections
import re
import subprocess

src = open("/ds/scripts/hack_saibaman.py").read()
bloco = src[src.index("TROCAS = {"):]
bloco = bloco[:bloco.index("}\n") + 1]
TROCAS = ast.literal_eval(bloco.split("=", 1)[1].strip())
VAR = ["Saibaman", "J. Sai", "C. Sai", "K. Sai", "T. Sai"]
# id (1-based) -> variante
destino = {linha + 1: VAR[m] for linha, (_, _, m) in TROCAS.items()}
nome_orig = {linha + 1: n for linha, (n, _, _) in TROCAS.items()}
# Saibamen de verdade: so ids 2-5 (J., C., K., T. Sai). O id 1 (Saibaman
# comum) nunca aparece como tipo de grupo; nos scripts ele e o marcador de
# "vazio" (preenche os tipos nao usados e slots vagos da formacao 2).
for i in range(1, 5):
    destino[i + 1] = VAR[i]
    nome_orig[i + 1] = VAR[i] + " (original)"

saida = subprocess.run(["python3", "/ds/scripts/grupos_inimigos.py"],
                       capture_output=True, text=True).stdout
por_mapa = collections.defaultdict(set)
for ln in saida.splitlines():
    m = re.match(r"(\S+)\s+@\S+ argc=15 (\[.*\])", ln)
    if not m:
        continue
    args = ast.literal_eval(m.group(2))
    for v in args[6:12]:  # slots
        if isinstance(v, int) and v in destino:
            por_mapa[m.group(1)].add(v)

ruins = 0
for mapa in sorted(por_mapa):
    por_var = collections.defaultdict(set)
    for i in por_mapa[mapa]:
        por_var[destino[i]].add(i)
    for var, ids in por_var.items():
        if len(ids) > 1:
            ruins += 1
            print(f"CONFLITO {mapa}: {var} <- {[nome_orig[i] for i in sorted(ids)]}")
print("sem conflitos" if not ruins else f"{ruins} conflito(s)")
