"""Monta um LOTE de traducao: textos unicos (por original) dos scripts
escolhidos, na ordem em que aparecem, com os ids onde ocorrem. Exclui
japones (Shift-JIS) e scripts de depuracao. Grava:
  /ds/traducao/lote<N>.txt   (para ler e traduzir: '### k' + original)
  /ds/traducao/lote<N>.json  (k -> {original, ids})
uso: lote.py <N> <regex de arquivo de script> [--tabelas regex_tabela]
"""
import json
import os
import re
import sys

N, padrao = sys.argv[1], re.compile(sys.argv[2])
tab = re.compile(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == "--tabelas" else None
it = json.load(open("/ds/saida/textos_us.json", encoding="utf-8"))
os.makedirs("/ds/traducao", exist_ok=True)
feitos = {}
if os.path.exists("/ds/traducao/ptbr.json"):
    feitos = json.load(open("/ds/traducao/ptbr.json", encoding="utf-8"))


def japones(s):
    b = s.encode("latin-1", "replace")
    return any(0x81 <= b[i] <= 0x9F and i + 1 < len(b) for i in range(len(b)))


ordem, dados = [], {}
for x in it:
    arq = x["id"].split(":")[1]
    if x["fonte"] == "script":
        if not padrao.search(arq.split("/")[-1]) or "/dbg/" in arq:
            continue
    elif not (tab and tab.search(x["tipo"])):
        continue
    s = x["original"]
    if japones(s) or s in feitos:
        continue
    if s not in dados:
        dados[s] = []
        ordem.append(s)
    dados[s].append(x["id"])
lote = {str(k): {"original": s, "ids": dados[s]} for k, s in enumerate(ordem)}
json.dump(lote, open(f"/ds/traducao/lote{N}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open(f"/ds/traducao/lote{N}.txt", "w", encoding="utf-8") as f:
    for k, s in enumerate(ordem):
        f.write(f"### {k} [{dados[s][0].split(':')[1]}]\n{s}\n")
pal = sum(len(re.findall(r"[A-Za-z']+", re.sub(r"<[^>]*>", " ", s))) for s in ordem)
print(f"lote {N}: {len(ordem)} textos unicos, {pal} palavras")
