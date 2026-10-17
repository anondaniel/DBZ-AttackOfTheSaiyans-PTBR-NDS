"""Junta loteN_pt_a/b/c.json em loteN_pt.json e confere que cobre o lote.
uso: juntar_lote.py <N>"""
import glob
import json
import sys

N = sys.argv[1]
lote = json.load(open(f"/ds/traducao/lote{N}.json", encoding="utf-8"))
pt = {}
for f in sorted(glob.glob(f"/ds/traducao/lote{N}_pt_[a-z].json")):
    parte = json.load(open(f, encoding="utf-8"))
    dup = set(parte) & set(pt)
    assert not dup, f"{f}: chaves repetidas {sorted(dup)[:5]}"
    pt.update(parte)
falta = sorted(set(lote) - set(pt), key=int)
sobra = sorted(set(pt) - set(lote), key=int)
assert not falta and not sobra, f"falta={falta[:10]} sobra={sobra[:10]}"
json.dump(pt, open(f"/ds/traducao/lote{N}_pt.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"lote {N}: {len(pt)} traducoes juntadas")
