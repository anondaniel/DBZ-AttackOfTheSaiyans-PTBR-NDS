"""Gera correcoes_texto.json e ptbr_mudancas.json a partir de correcoes_def.py e en_only_def.py.

uso: python -B gerar_correcoes.py [rom_base_rc1.nds]

- confere que cada "antes" e o texto atual da ROM base (rc.1)
- espelha cada correcao em todas as ocorrencias com o mesmo texto ingles original e o
  mesmo texto PT atual, nas pastas US e EN
- traduz as falas/celulas que so existem em ingles na pasta EN
- valida cada texto novo (marcacoes, glifos, paginas/linhas, larguras de tabela, rotulos)
  e para com erro se algo nao passar
"""
import collections
import difflib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "lib"))
sys.path.insert(0, AQUI)
import correcoes_def as CD  # noqa: E402
import en_only_def as ED  # noqa: E402
import regras as R  # noqa: E402
import textos_rom as T  # noqa: E402

BASE = os.path.normpath(os.path.join(AQUI, "..", ".."))
ROM_RC1 = os.path.join(BASE, "01_ROM", "DBZ Attack of the Saiyans PT-BR.nds")
EN_ONLY_MOTIVO = "fala/célula em inglês que só existe na pasta EN (variante do texto da US); traduzida"


def norm(s):
    return re.sub(r"[\s\-]", "", s.lower())


def main():
    rom_base = sys.argv[1] if len(sys.argv) > 1 else ROM_RC1
    rc = T.extrair(T.carregar_rom(rom_base))
    og = T.extrair(T.carregar_rom(T.ORIG_ZIP))
    F, Fo = R.Fontes(rc["fnt"]), R.Fontes(og["fnt"])
    grp = R.grupos_tabela({k: v for k, v in og["bdat"].items() if R.TAB.match(k.split(":")[1])}, Fo)
    fal = {c: T.falantes(v) for c, v in og["sb"].items()}
    max_rot = max(R.wpal(og["sb"][c]["textos"][i], Fo.L1) for c in fal if "/US/" in c and "/dbg/" not in c
                  for i in fal[c])

    entradas, erros, avisos = [], [], []
    feito = {}  # loc -> novo

    def ogtxt(c, i):
        t = og["sb"][c]["textos"]
        return t[i] if i < len(t) else None

    def checa_sb(c, i, antes, depois, orig):
        e = R.checar_comum(orig, depois, F)
        e0 = set(R.checar_comum(orig, antes, F)) if antes != orig else set()
        ef, af = R.checar_fala(orig, depois, Fo.L1, F.L1)
        ef0 = set(R.checar_fala(orig, antes, Fo.L1, F.L1)[0]) if antes != orig else set()
        e = [x for x in e if x not in e0] + [x for x in ef if x not in ef0]
        if i in fal.get(c, ()):
            w = R.wpal(depois, F.L1)
            if w > max_rot:
                e.append(f"rótulo de quem fala com {w}px (> {max_rot}px)")
        for x in e:
            erros.append(f"{c}:{i}: {x} | {depois!r}")
        for x in af:
            avisos.append(f"{c}:{i}: {x}")

    def checa_bd(k, antes, depois, orig):
        e = R.checar_comum(orig, depois, F) + R.checar_tabela(k, orig, depois, grp, F)
        if antes != orig:
            e0 = set(R.checar_comum(orig, antes, F) + R.checar_tabela(k, orig, antes, grp, F))
            e = [x for x in e if x not in e0]
        for x in e:
            erros.append(f"{k}: {x} | {depois!r}")

    def registra(loc, antes, depois, grav, motivo, origem, chave):
        if loc in feito:
            erros.append(f"{loc}: mudado duas vezes")
            return
        feito[loc] = depois
        if loc[0] == "sb":
            _, c, i = loc
            assert rc["sb"][c]["textos"][i] == antes
            entradas.append({"tipo": "sb", "arquivo": c, "indice": i, "antes": antes, "depois": depois,
                             "gravidade": grav, "motivo": motivo, "origem": origem, "chave_en": chave})
        else:
            _, k = loc
            lang, tab, i, col = k.split(":")
            assert rc["bdat"][k] == antes
            entradas.append({"tipo": "bdat", "lang": lang, "tabela": tab, "linha": int(i), "coluna": col,
                             "antes": antes, "depois": depois, "gravidade": grav, "motivo": motivo,
                             "origem": origem, "chave_en": chave})

    def aplica_subs(txt, subs, onde):
        novo = txt
        for a, b in subs:
            n = novo.count(a)
            if n != 1:
                erros.append(f"{onde}: trecho {a!r} aparece {n} vezes em {novo!r}")
                return None
            novo = novo.replace(a, b)
        return novo

    # ---------- 1. correcoes em scripts
    for base, idx, subs, grav, motivo, origem in CD.SB:
        cs = [c for c in rc["sb"] if c.startswith("script/US/") and c.endswith("/" + base + ".sb")]
        assert len(cs) == 1, (base, cs)
        c0 = cs[0]
        antes, chave = rc["sb"][c0]["textos"][idx], ogtxt(c0, idx)
        depois = aplica_subs(antes, subs, f"{c0}:{idx}")
        if depois is None:
            continue
        locs = []
        for c, v in rc["sb"].items():
            for i, t in enumerate(v["textos"]):
                if t == antes:
                    if ogtxt(c, i) == chave:
                        locs.append((c, i))
                    else:
                        avisos.append(f"{c}:{i}: mesmo texto PT de {base}:{idx}, mas outro original "
                                      f"({ogtxt(c, i)!r}); não mudado")
        for c, i in sorted(locs):
            checa_sb(c, i, antes, depois, chave)
            registra(("sb", c, i), antes, depois, grav, motivo, origem, chave)

    # ---------- 2. correcoes em tabelas
    for tab, row, subs, grav, motivo, origem in CD.BD:
        k0 = f"US:{tab}:{row}:us"
        antes, chave = rc["bdat"][k0], og["bdat"][k0]
        depois = aplica_subs(antes, subs, k0)
        if depois is None:
            continue
        for k, t in rc["bdat"].items():
            if not k.startswith(("US:", "EN:")) or not R.TAB.match(k.split(":")[1]) or t != antes:
                continue
            if og["bdat"][k] == chave:
                checa_bd(k, antes, depois, chave)
                registra(("bdat", k), antes, depois, grav, motivo, origem, chave)
            else:
                avisos.append(f"{k}: mesmo texto PT de {k0}, mas outro original ({og['bdat'][k]!r}); não mudado")

    # ---------- 3. falas que so existem em ingles na pasta EN
    reuso = []
    usados_sb_en = set()
    for c in sorted(rc["sb"]):
        if not c.startswith("script/EN/") or "/dbg/" in c:
            continue
        cu = c.replace("/EN/", "/US/")
        for i, s in enumerate(og["sb"][c]["textos"]):
            if rc["sb"][c]["textos"][i] != s or R.classifica(s) == "interno":
                continue
            us_o = ogtxt(cu, i)
            us_f = feito.get(("sb", cu, i), rc["sb"][cu]["textos"][i]) if i < len(rc["sb"][cu]["textos"]) else None
            if us_o is None or us_f == us_o or us_f == s:
                continue  # a US tambem esta em ingles (nome/interjeicao) ou e igual
            if s in ED.SB_EN:
                depois = ED.SB_EN[s]
                usados_sb_en.add(s)
                como = "tradução própria"
            else:
                razao = difflib.SequenceMatcher(None, norm(us_o), norm(s)).ratio()
                if razao < 0.75 or R.marcas(us_f) != R.marcas(s):
                    erros.append(f"{c}:{i}: fala EN-only sem tradução definida (US {us_o!r}) | {s!r}")
                    continue
                depois = us_f
                como = "mesma tradução da US"
                if norm(us_o) != norm(s):
                    reuso.append((c, i, round(razao, 2), s, us_o))
            checa_sb(c, i, s, depois, s)
            registra(("sb", c, i), s, depois, "BAIXO", f"{EN_ONLY_MOTIVO} ({como})", "relatorio03 sec2 (pasta EN)", s)
    for s in set(ED.SB_EN) - usados_sb_en:
        erros.append(f"en_only_def.SB_EN nao usado: {s!r}")

    usados_bd_en = set()
    for k in sorted(rc["bdat"]):
        lang, tab, i, col = k.split(":")
        if lang != "EN" or not R.TAB.match(tab):
            continue
        s = og["bdat"][k]
        if not s.strip() or rc["bdat"][k] != s:
            continue
        ku = f"US:{tab}:{i}:us"
        us_o = og["bdat"][ku]
        us_f = feito.get(("bdat", ku), rc["bdat"][ku])
        if us_f == us_o or us_f == s:
            continue
        if s in ED.BD_EN:
            depois = ED.BD_EN[s]
            usados_bd_en.add(s)
            como = "tradução própria"
        else:
            razao = difflib.SequenceMatcher(None, norm(us_o), norm(s)).ratio()
            if razao < 0.75 or R.marcas(us_f) != R.marcas(s):
                erros.append(f"{k}: célula EN-only sem tradução definida (US {us_o!r}) | {s!r}")
                continue
            depois = us_f
            como = "mesma tradução da US"
            if norm(us_o) != norm(s):
                reuso.append((k, "", round(razao, 2), s, us_o))
        checa_bd(k, s, depois, s)
        registra(("bdat", k), s, depois, "BAIXO", f"{EN_ONLY_MOTIVO} ({como})", "relatorio03 sec2 (pasta EN)", s)
    for s in set(ED.BD_EN) - usados_bd_en:
        erros.append(f"en_only_def.BD_EN nao usado: {s!r}")

    # ---------- 4. ptbr_mudancas + usos da mesma chave que nao mudaram
    mud = {}
    for e in entradas:
        k = e["chave_en"]
        if k in mud and mud[k] != e["depois"]:
            erros.append(f"chave {k!r} com duas traduções novas: {mud[k]!r} x {e['depois']!r}")
        mud[k] = e["depois"]
    mudados = set(feito)
    outros_usos = []
    for k in mud:
        for c, v in og["sb"].items():
            if not c.startswith(("script/US/", "script/EN/")):
                continue
            for i, t in enumerate(v["textos"]):
                if t == k and ("sb", c, i) not in mudados:
                    outros_usos.append((k, f"{c}:{i}", rc["sb"][c]["textos"][i]))
        for kk, t in og["bdat"].items():
            if t == k and kk.startswith(("US:", "EN:")) and ("bdat", kk) not in mudados and R.TAB.match(kk.split(":")[1]):
                outros_usos.append((k, kk, rc["bdat"][kk]))

    # ---------- saida
    entradas.sort(key=lambda e: (e["tipo"], e.get("arquivo", e.get("tabela", "")), e.get("lang", ""),
                                 e.get("indice", e.get("linha", 0))))
    json.dump(entradas, open(os.path.join(AQUI, "correcoes_texto.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(mud, open(os.path.join(AQUI, "ptbr_mudancas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.makedirs(os.path.join(AQUI, "saida"), exist_ok=True)
    with open(os.path.join(AQUI, "saida", "gerar_log.txt"), "w", encoding="utf-8") as f:
        f.write(f"ERROS ({len(erros)})\n" + "\n".join(erros) + "\n")
        f.write(f"\nAVISOS ({len(avisos)})\n" + "\n".join(avisos) + "\n")
        f.write(f"\nREUSO DA TRADUÇÃO US EM TEXTO EN COM PEQUENA DIFERENÇA ({len(reuso)})\n")
        for x in reuso:
            f.write(f"  {x[0]}:{x[1]} r={x[2]}\n     EN {x[3]!r}\n     US {x[4]!r}\n")
        f.write(f"\nCHAVES COM OUTROS USOS NÃO MUDADOS ({len(outros_usos)})\n")
        for x in outros_usos:
            f.write(f"  {x[1]} | chave {x[0]!r} | atual {x[2]!r}\n")
    cont = collections.Counter((e["gravidade"], e.get("lang") or e["arquivo"].split("/")[1],
                                "en-only" if e["origem"].startswith("relatorio03 sec2") else "corr") for e in entradas)
    print(json.dumps({f"{a}/{b}/{c}": n for (a, b, c), n in sorted(cont.items())}, ensure_ascii=False, indent=0))
    print(f"entradas {len(entradas)} | chaves ptbr {len(mud)} | erros {len(erros)} | avisos {len(avisos)} | "
          f"reuso {len(reuso)} | outros usos {len(outros_usos)}")
    if erros:
        print("\n".join(erros[:80]))
        sys.exit(1)


if __name__ == "__main__":
    main()
