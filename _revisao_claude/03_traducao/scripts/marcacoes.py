"""Todas as marcacoes dentro dos textos (tags <...>, codigos @NN, outros
simbolos), com contagem e um exemplo de cada."""
import collections
import json
import re

it = json.load(open("/ds/saida/textos_us.json", encoding="utf-8"))
tags, arr, outros = collections.Counter(), collections.Counter(), collections.Counter()
ex = {}
for x in it:
    s = x["original"]
    for t in re.findall(r"<[^>]*>", s):
        k = re.sub(r"=.*", "=...", t)
        tags[k] += 1
        ex.setdefault(k, s[:90])
    for t in re.findall(r"@\d+", s):
        arr[t] += 1
        ex.setdefault(t, s[:90])
    for ch in re.sub(r"<[^>]*>", "", s):
        if not (ch.isalnum() or ch in " .,!?'\"-:;()&%/#+~*"):
            outros[ch] += 1
            ex.setdefault(ch, s[:90])
print("TAGS:")
for k, v in tags.most_common():
    print(f"  {k:14s} {v:6d}  ex: {ex[k]!r}")
print("CODIGOS @:")
for k, v in arr.most_common():
    print(f"  {k:6s} {v:5d}  ex: {ex[k]!r}")
print("OUTROS SIMBOLOS:")
for k, v in outros.most_common():
    print(f"  {k!r} U+{ord(k):04X} {v:5d}  ex: {ex[k]!r}")
