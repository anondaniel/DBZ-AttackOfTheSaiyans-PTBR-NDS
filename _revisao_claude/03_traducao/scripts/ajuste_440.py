import json

p = json.load(open("/ds/traducao/lote2_pt.json", encoding="utf-8"))
p["440"] = "O radar aponta o \\1P3Vaso do<n>Diabo\\1Pn... Duas Esferas?!"
json.dump(p, open("/ds/traducao/lote2_pt.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(repr(p["440"]))
