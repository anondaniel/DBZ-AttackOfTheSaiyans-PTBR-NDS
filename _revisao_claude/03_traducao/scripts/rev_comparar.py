"""Compara ROM nova x ROM original x ptbr.json.
saida: saida/comparacao.json + resumo no terminal."""
import collections
import json
import os
import re
import sys

S = os.path.join(os.path.dirname(__file__), "..", "saida")
TR = r"C:\Projetos\09_Dragon_Ball_Z_Attack_of_the_Saiyans\11_Projeto_Recuperado\traducao\ptbr.json"
o = json.load(open(os.path.join(S, "textos_orig.json"), encoding="utf-8"))
n = json.load(open(os.path.join(S, "textos_novo.json"), encoding="utf-8"))
acum = json.load(open(TR, encoding="utf-8"))
TAB = re.compile(r"^(btl_mes_|cf_mes_|use_item_mes|btl_acc_mes|pt_eqp_mes|key_item_mes|character_name)")


def classifica(s):
    if "<p>" in s or "<k>" in s:
        return "dialogo"
    if s.startswith(("#", "===")) or "_" in s or "(" in s or ")" in s:
        return "interno"
    if any(ord(ch) < 32 or 127 <= ord(ch) < 160 for ch in s):
        return "interno"
    if re.fullmatch(r"[A-Za-z0-9]+", s):
        return "exibido?" if s[0].isupper() and not re.search(r"\d", s) and not s.isupper() else "interno"
    if " " in s or "'" in s or "!" in s or "?" in s or "." in s:
        return "exibido"
    return "interno"


res = {"sb_diferente_do_esperado": [], "sb_ingles_restante": [], "sb_extra": [],
       "bdat_diferente": [], "bdat_ingles_restante": [], "sb_mudou_sem_traducao": []}
stats = collections.Counter()
for c, vo in o["sb"].items():
    if not c.startswith(("script/US/", "script/EN/")):
        continue
    vn = n["sb"][c]
    to, tn = vo["textos"], vn["textos"]
    if len(tn) > len(to):
        res["sb_extra"].append([c, tn[len(to):]])
    for i, s in enumerate(to):
        t = tn[i]
        k = classifica(s)
        if s in acum and acum[s] != s:
            stats["com_traducao"] += 1
            if t == acum[s]:
                stats["ok"] += 1
            elif t == s:
                # pode ser identificador preservado (extra com a traducao)
                if acum[s] in tn[len(to):]:
                    stats["ident_preservado"] += 1
                elif k != "interno":
                    res["sb_diferente_do_esperado"].append([c, i, s, t, acum[s]])
                else:
                    stats["interno_nao_trocado"] += 1
            else:
                res["sb_diferente_do_esperado"].append([c, i, s, t, acum[s]])
        else:
            if t != s:
                res["sb_mudou_sem_traducao"].append([c, i, s, t])
            elif k != "interno" and "/dbg/" not in c:
                res["sb_ingles_restante"].append([c, i, k, s])
for key, vo in o["bdat"].items():
    lang, tab, i, col = key.split(":")
    if lang == "FR":
        continue
    vn = n["bdat"][key]
    if not TAB.match(tab):
        if vo != vn:
            res["bdat_diferente"].append([key, vo, vn, "tabela-nao-texto"])
        continue
    if vo in acum and acum[vo] != vo:
        if vn != acum[vo]:
            res["bdat_diferente"].append([key, vo, vn, acum[vo]])
    elif vo.strip():
        if vn == vo:
            res["bdat_ingles_restante"].append([key, vo])
        else:
            res["bdat_diferente"].append([key, vo, vn, None])
json.dump(res, open(os.path.join(S, "comparacao.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(dict(stats))
for k, v in res.items():
    print(k, len(v))
