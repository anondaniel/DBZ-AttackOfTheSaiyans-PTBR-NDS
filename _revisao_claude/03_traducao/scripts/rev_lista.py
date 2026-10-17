"""Lista unica dos textos PT na ROM nova (pasta US): original EN, PT, ids.
Grava saida/pt_unicos.json e saida/pt_unicos.txt (para leitura)."""
import json
import os
import re

S = os.path.join(os.path.dirname(__file__), "..", "saida")
o = json.load(open(os.path.join(S, "textos_orig.json"), encoding="utf-8"))
n = json.load(open(os.path.join(S, "textos_novo.json"), encoding="utf-8"))
uni = {}
ordem = []


def add(pt, en, i):
    if pt not in uni:
        uni[pt] = {"pt": pt, "en": en, "ids": []}
        ordem.append(pt)
    uni[pt]["ids"].append(i)


for c in sorted(o["sb"]):
    if not c.startswith("script/US/") or "/dbg/" in c:
        continue
    to, tn = o["sb"][c]["textos"], n["sb"][c]["textos"]
    for i, s in enumerate(tn):
        en = to[i] if i < len(to) else "(extra)"
        if s != en:
            add(s, en, f"{c[10:]}:{i}")
for k, v in o["bdat"].items():
    if not k.startswith("US:"):
        continue
    nv = n["bdat"][k]
    if nv != v and not k.split(":")[1].startswith(("enemy_param",)):
        add(nv, v, k[3:])
json.dump([uni[p] for p in ordem], open(os.path.join(S, "pt_unicos.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)
with open(os.path.join(S, "pt_unicos.txt"), "w", encoding="utf-8") as f:
    for k, p in enumerate(ordem):
        u = uni[p]
        f.write(f"### {k} [{u['ids'][0]}] (x{len(u['ids'])})\nEN: {u['en']}\nPT: {u['pt']}\n")
print(len(ordem), "unicos")
