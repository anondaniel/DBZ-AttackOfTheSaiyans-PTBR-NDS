"""Limites tecnicos: paginas de fala com linhas demais, linhas manuais largas,
textos de tabela mais largos que o maior original do grupo, rotulos de falante."""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from rev_wrap import linhas_pagina, paginas, wpal

S = os.path.join(os.path.dirname(__file__), "..", "saida")
O = json.load(open(os.path.join(S, "textos_orig.json"), encoding="utf-8"))
N = json.load(open(os.path.join(S, "textos_novo.json"), encoding="utf-8"))
L1 = bytes.fromhex(N["fnt"]["latin1.fnt"])[:256]
L0 = bytes.fromhex(N["fnt"]["latin0.fnt"])[:256]
L1o = bytes.fromhex(O["fnt"]["latin1.fnt"])[:256]
L0o = bytes.fromhex(O["fnt"]["latin0.fnt"])[:256]
LIM = 196
out = open(os.path.join(S, "larguras.txt"), "w", encoding="utf-8")


def p(*a):
    print(*a, file=out)


# ---- 1. falas
p("== 1. PAGINAS DE FALA (modelo: quebra automatica em", LIM, "px na fonte pequena; <n> forca quebra) ==")
vistos = set()
pag_mais = []
lin_larga = []
for c in sorted(O["sb"]):
    if not c.startswith("script/US/") or "/dbg/" in c:
        continue
    to, tn = O["sb"][c]["textos"], N["sb"][c]["textos"]
    for i, en in enumerate(to):
        pt = tn[i]
        if pt == en or "<p>" not in pt or pt in vistos:
            continue
        vistos.add(pt)
        pe, pp = paginas(en), paginas(pt)
        if len(pe) != len(pp):
            p("paginas diferentes:", c, i)
            continue
        for k, (a, b) in enumerate(zip(pe, pp)):
            la = linhas_pagina(a, L1o, LIM, 0)
            lb = linhas_pagina(b, L1, LIM, 0)
            if len(lb) > 3 and len(lb) > len(la):
                pag_mais.append((c[10:], i, k, len(la), len(lb), b))
            # linha manual (com <n>) mais larga que a caixa
            if "<n>" in b:
                for ln in re.split(r"<[nN]>", re.sub(r"<k>|<w=\d+>", "", b)):
                    w = wpal(ln, L1, 0)
                    if w > LIM:
                        lin_larga.append((c[10:], i, w, ln))
p(f"-- paginas com mais de 3 linhas e mais linhas que o original: {len(pag_mais)}")
for x in pag_mais:
    p(f"  {x[0]}:{x[1]} pag{x[2]}: EN {x[3]} linhas -> PT {x[4]} linhas | {x[5][:160]!r}")
p(f"-- linhas com <n> mais largas que {LIM}px (o jogo requebra ou corta): {len(lin_larga)}")
for x in sorted(lin_larga, key=lambda x: -x[2]):
    p(f"  {x[0]}:{x[1]} {x[2]}px | {x[3]!r}")

# ---- 2. falantes (rotulo)
p("\n== 2. ROTULOS DE FALANTE (1o argumento de Msg) ==")
sys.path.insert(0, os.path.dirname(__file__))
fal_o, fal_n = set(), collections.Counter()
for c in O["sb"]:
    if not c.startswith("script/US/") or "/dbg/" in c:
        continue
    for tag, src, dst in (("o", O, None), ("n", N, None)):
        d = src["sb"][c]
        imps, code, ts = d["imps"], bytes.fromhex(d["code"]), d["textos"]
        if "Msg" not in imps:
            continue
        msg = imps.index("Msg")
        q = 0
        while (q := code.find(b"\x26", q)) != -1:
            if q + 4 < len(code) and code[q + 2] == 0x26:
                a, b = code[q + 1], code[q + 3]
                k = q + 4
                while k < len(code) and 0x16 <= code[k] <= 0x1F:
                    k += 1
                if (k + 1 < len(code) and code[k] == 0x4A and code[k + 1] == msg and a < len(ts)
                        and b < len(ts) and "<p>" in ts[b] and "<p>" not in ts[a]):
                    if tag == "o":
                        fal_o.add(ts[a])
                    else:
                        fal_n[ts[a]] += 1
            q += 1
mo = max(wpal(x, L1o, 0) for x in fal_o)
p("maior rotulo original:", mo, "px", max(fal_o, key=lambda x: wpal(x, L1o, 0)))
for x, k in sorted(fal_n.items(), key=lambda t: -wpal(t[0], L1, 0))[:25]:
    p(f"  {wpal(x, L1, 0):4d}px x{k} {x!r}{'  <-- passa do maior original' if wpal(x, L1, 0) > mo else ''}")

# ---- 3. tabelas
p("\n== 3. TABELAS: texto PT mais largo que o maior original do mesmo grupo (tabela, coluna, com/sem <n>) ==")
grp = collections.defaultdict(lambda: [0, 0, ""])
for k, v in O["bdat"].items():
    lang, tab, i, col = k.split(":")
    if lang != "US" or not v.strip():
        continue
    g = (tab, col, "<n>" in v or "<p>" in v)
    for f, L in ((0, L0o), (1, L1o)):
        w = max(wpal(x, L, 0) for x in re.split(r"<[nNpP]>", v))
        if w > grp[g][f]:
            grp[g][f] = w
            if f == 1:
                grp[g][2] = v
ruins = []
for k, v in N["bdat"].items():
    lang, tab, i, col = k.split(":")
    if lang != "US" or not v.strip() or v == O["bdat"][k]:
        continue
    if tab.startswith("enemy_param"):
        continue
    g = (tab, col, "<n>" in O["bdat"][k] or "<p>" in O["bdat"][k])
    w1 = max(wpal(x, L1, 0) for x in re.split(r"<[nNpP]>", v))
    w0 = max(wpal(x, L0, 0) for x in re.split(r"<[nNpP]>", v))
    if w1 > grp[g][1] or w0 > grp[g][0]:
        ruins.append((tab, i, col, w1, grp[g][1], w0, grp[g][0], v, O["bdat"][k]))
p(f"total {len(ruins)}")
for r in ruins:
    p(f"  {r[0]}:{r[1]}:{r[2]} peq {r[3]}/{r[4]} gr {r[5]}/{r[6]} | {r[7]!r} (EN {r[8]!r})")

# ---- 4. nomes de inimigo
p("\n== 4. character_name (US): os 20 nomes mais largos (fonte pequena) ==")
nomes = [(wpal(v, L1, 0), k, v) for k, v in N["bdat"].items() if k.startswith("US:character_name:") and k.endswith(":us")]
mxo = max(wpal(v, L1o, 0) for k, v in O["bdat"].items() if k.startswith("US:character_name:") and k.endswith(":us"))
p("maior nome original:", mxo, "px")
for w, k, v in sorted(nomes, reverse=True)[:20]:
    p(f"  {w}px {k} {v!r}")
out.close()
print("ok", len(pag_mais), len(lin_larga), len(ruins))
