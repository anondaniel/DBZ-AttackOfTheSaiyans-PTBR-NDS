"""Mostra a API publica do libretro.py para eu montar o boot sem janela."""
import inspect
import os
import pkgutil

import libretro

base = os.path.dirname(libretro.__file__)
print("pacote:", base)
print("modulos:", sorted(m.name for m in pkgutil.iter_modules([base])))
print()
print("nomes publicos:", [n for n in dir(libretro) if not n.startswith("_")])
print()
for nome in ("SessionBuilder", "Session", "defaults"):
    obj = getattr(libretro, nome, None)
    if obj is None:
        print(f"{nome}: nao existe")
        continue
    print(f"== {nome} ==")
    for m, f in inspect.getmembers(obj):
        if m.startswith("_"):
            continue
        try:
            sig = str(inspect.signature(f))
        except (TypeError, ValueError):
            sig = ""
        print(f"  {m}{sig}")
    print()

readme = [p for p in os.listdir(os.path.dirname(base)) if "libretro" in p.lower() and p.endswith(".dist-info")]
for d in readme:
    meta = os.path.join(os.path.dirname(base), d, "METADATA")
    if os.path.exists(meta):
        txt = open(meta, encoding="utf-8").read()
        i = txt.find("```")
        print("== exemplo do README ==")
        print(txt[i:i + 2500] if i >= 0 else txt[-2500:])
