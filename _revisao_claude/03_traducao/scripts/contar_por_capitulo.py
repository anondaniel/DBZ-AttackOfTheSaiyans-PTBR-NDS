"""Palavras de dialogo por capitulo (scripts cCCss) e por mapa."""
import collections
import json
import re

it = json.load(open("/ds/saida/textos_us.json", encoding="utf-8"))


def pal(s):
    return len(re.findall(r"[A-Za-z']+", re.sub(r"<[^>]*>", " ", s)))


c = collections.defaultdict(lambda: [0, 0])
for x in it:
    if x["fonte"] != "script":
        continue
    arq = x["id"].split(":")[1].split("/")[-1][:-3]
    m = re.match(r"c(\d\d)\d\d", arq)
    k = "cap " + m.group(1) if m else "mapa " + re.sub(r"\d.*", "", arq)
    c[k][0] += 1
    c[k][1] += pal(x["original"])
for k, v in sorted(c.items()):
    print(f"{k:12s} {v[0]:5d} textos {v[1]:6d} palavras")
