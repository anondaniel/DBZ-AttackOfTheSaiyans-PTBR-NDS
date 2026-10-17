"""Largura das falas com quebra manual (<n>): cada linha traduzida tem que
caber no limite = linha original mais larga das falas com <n> do MESMO lote
(o limite global do jogo e frouxo demais). Paginas sem <n> numa fala que
tem <n> em outra pagina tambem contam: o jogo nao requebra essa fala.
uso: largura_falas.py <loteN.json> <loteN_pt.json>"""
import json
import sys

sys.argv, args = sys.argv[:1], sys.argv[1:]
sys.path.insert(0, "/ds/scripts")
from largura import larg

lote = json.load(open(args[0], encoding="utf-8"))
pt = json.load(open(args[1], encoding="utf-8"))
com_n = [k for k, v in lote.items() if "<n>" in v["original"]]
if not com_n:
    print("nenhuma fala com <n>")
    sys.exit()
lim = max(max(larg(lote[k]["original"], 1)) for k in com_n)
ruins = []
for k in com_n:
    w = max(larg(pt[k], 1))
    if w > lim:
        ruins.append(k)
        print(f"{k:>5} {w}px > {lim}px  {pt[k][:90]!r}")
print(f"limite {lim}px; {len(ruins)} fala(s) passam")
