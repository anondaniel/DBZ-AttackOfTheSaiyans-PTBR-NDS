"""Verificacao dos textos de uma ROM PT-BR de DBZ Attack of the Saiyans (pastas US e EN).

uso: python -B verificar_textos.py <rom.nds|rom.zip> <pasta_saida> [--orig <rom_original.nds|.zip>]
     [--correcoes <correcoes_texto.json>]

1. cada entrada de correcoes_texto.json esta com o texto "depois"
2. checagens do relatorio 03, comparando com a ROM original inglesa (lida do zip em memoria):
   - marcacoes de controle EN x PT (<..>, %d/%s, \\NN.., @NN) em todo texto mudado (US e EN)
   - glifos: todo caractere usado tem desenho nas duas fontes (latin0/latin1 da ROM verificada)
   - larguras/linhas: paginas de fala (quebra em 196 px), linhas com <n>, tabelas (maior
     largura original do grupo), rotulos de quem fala
   - ingles restante nas pastas US e EN (deve ser so nomes/interjeicoes: lista de aceitos)
Saidas .txt na pasta de saida; resumo no fim; codigo de saida 0 se tudo ok.
"""
import collections
import json
import os
import re
import sys
import time

sys.dont_write_bytecode = True
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "lib"))
import regras as R  # noqa: E402
import textos_rom as T  # noqa: E402

# palavras inglesas comuns (texto que as contenha e nao mudou em relacao ao original = suspeito)
EN_PAL = re.compile(r"\b(the|you|your|you're|and|is|are|it's|i'm|don't|can't|with|this|that|what|where|here|"
                    r"there|have|has|was|will|just|get|got|not|of|to|for|my|me|we|he|she|they|let's|lets|"
                    r"okay|yes|yeah|please|thanks|thank|sorry|guys|must|been|be|do|does|did|can|could|"
                    r"would|should|from|into|about|now|all|some|any|more|than|then|when|who|how|why)\b", re.I)


def args():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        sys.exit(2)
    rom, saida = a[0], a[1]
    orig = T.ORIG_ZIP
    corr = os.path.join(AQUI, "correcoes_texto.json")
    if "--orig" in a:
        orig = a[a.index("--orig") + 1]
    if "--correcoes" in a:
        corr = a[a.index("--correcoes") + 1]
    return rom, saida, orig, corr


def main():
    rom_p, saida, orig_p, corr_p = args()
    os.makedirs(saida, exist_ok=True)
    t0 = time.time()
    N = T.extrair(T.carregar_rom(rom_p))
    O = T.extrair(T.carregar_rom(orig_p))
    F, Fo = R.Fontes(N["fnt"]), R.Fontes(O["fnt"])
    resumo = collections.OrderedDict()
    erros_total = 0

    def grava(nome, linhas):
        with open(os.path.join(saida, nome), "w", encoding="utf-8") as f:
            f.write("\n".join(linhas) + "\n")

    # ---------- 1. correcoes
    lin, ok, ruim = [], 0, 0
    if os.path.exists(corr_p):
        for e in json.load(open(corr_p, encoding="utf-8")):
            if e["tipo"] == "sb":
                loc = f"{e['arquivo']}:{e['indice']}"
                ts = N["sb"].get(e["arquivo"], {}).get("textos", [])
                atual = ts[e["indice"]] if e["indice"] < len(ts) else None
            else:
                loc = f"{e['lang']}:{e['tabela']}:{e['linha']}:{e['coluna']}"
                atual = N["bdat"].get(loc)
            if atual == e["depois"]:
                ok += 1
            else:
                ruim += 1
                est = "NAO APLICADA (ainda no 'antes')" if atual == e["antes"] else "DIFERENTE"
                lin.append(f"{est} {loc}\n   esperado {e['depois']!r}\n   atual    {atual!r}")
        lin.insert(0, f"correcoes conferidas: {ok} ok, {ruim} com problema ({corr_p})")
    else:
        lin.append(f"(sem {corr_p})")
    grava("1_correcoes.txt", lin)
    resumo["correcoes aplicadas"] = f"{ok} ok / {ruim} com problema"
    erros_total += ruim

    # ---------- textos mudados (US e EN) em relacao ao original
    mud_sb, mud_bd = [], []
    for c, v in N["sb"].items():
        if c not in O["sb"]:
            continue
        to = O["sb"][c]["textos"]
        for i, t in enumerate(v["textos"]):
            if i < len(to) and t != to[i]:
                mud_sb.append((c, i, to[i], t))
    for k, v in N["bdat"].items():
        tab = k.split(":")[1]
        if R.TAB.match(tab) and v != O["bdat"].get(k):
            mud_bd.append((k, O["bdat"].get(k, ""), v))
    extras = [(c, i, t) for c, v in N["sb"].items() if c in O["sb"]
              for i, t in enumerate(v["textos"]) if i >= len(O["sb"][c]["textos"])]

    # ---------- 2a. marcacoes
    lin = []
    for c, i, o, t in mud_sb:
        if R.marcas(o) != R.marcas(t):
            lin.append(f"{c}:{i}: EN {dict(R.marcas(o))} PT {dict(R.marcas(t))} | {t[:120]!r}")
        elif re.search(r"<[^>]*$", t.replace("<k?", "")) and not re.search(r"<[^>]*$", o.replace("<k?", "")):
            lin.append(f"{c}:{i}: tag malformada | {t[:120]!r}")
    for k, o, t in mud_bd:
        if R.marcas(o) != R.marcas(t):
            lin.append(f"{k}: EN {dict(R.marcas(o))} PT {dict(R.marcas(t))} | {t[:120]!r}")
    grava("2_marcacoes.txt", [f"textos mudados: {len(mud_sb)} de script, {len(mud_bd)} de tabela; "
                              f"divergencias: {len(lin)}"] + lin)
    resumo["marcacoes EN x PT"] = f"{len(lin)} divergencias em {len(mud_sb) + len(mud_bd)} textos mudados"
    erros_total += len(lin)

    # ---------- 2b. glifos
    usados = collections.Counter()
    for _, _, _, t in mud_sb:
        usados.update(t)
    for _, _, t in extras:
        usados.update(t)
    for _, _, t in mud_bd:
        usados.update(t)
    sem = sorted(ch for ch in usados if ch in F.sem_glifo(ch))
    lin = ["caracteres >= 0x80 usados: " + "".join(sorted(ch if ord(ch) >= 0xA0 else f"[{ord(ch):02X}]"
                                                         for ch in usados if ord(ch) >= 0x80)),
           f"sem glifo em latin0/latin1: {[(hex(ord(c)), c, usados[c]) for c in sem]}"]
    grava("3_glifos.txt", lin)
    resumo["glifos"] = f"{len(sem)} caracteres sem glifo"
    erros_total += len(sem)

    # ---------- 2c. larguras e linhas
    lin, avi = [], []
    n_err = 0
    lin.append(f"== PAGINAS E LINHAS DE FALA (quebra em {R.LIM} px na fonte pequena) ==")
    vistos = set()
    for c, i, o, t in mud_sb:
        if "/dbg/" in c or (o, t) in vistos:
            continue
        vistos.add((o, t))
        e, a = R.checar_fala(o, t, Fo.L1, F.L1)
        for x in e:
            lin.append(f"ERRO {c}:{i}: {x}")
        for x in a:
            avi.append(f"aviso {c}:{i}: {x}")
        n_err += len(e)
    lin += avi
    lin.append("\n== ROTULOS DE QUEM FALA ==")
    fal_o = [O["sb"][c]["textos"][i] for c in O["sb"] if "/dbg/" not in c for i in T.falantes(O["sb"][c])]
    mo = max(R.wpal(x, Fo.L1) for x in fal_o)
    rot = collections.Counter()
    for c, v in N["sb"].items():
        if "/dbg/" in c:
            continue
        for i in T.falantes(v):
            rot[v["textos"][i]] += 1
    lin.append(f"maior rotulo original: {mo} px")
    for x, k in sorted(rot.items(), key=lambda t: -R.wpal(t[0], F.L1))[:15]:
        w = R.wpal(x, F.L1)
        lin.append(f"  {w:4d}px x{k} {x!r}" + ("  <-- ERRO: passa do maior original" if w > mo else ""))
        n_err += w > mo
    lin.append("\n== TABELAS: largura x maior original do grupo (lingua, tabela, coluna, com/sem <n>, nome/descricao) ==")
    grp = R.grupos_tabela({k: v for k, v in O["bdat"].items() if R.TAB.match(k.split(":")[1])}, Fo)
    for k, o, t in mud_bd:
        if not t.strip():
            continue
        for x in R.checar_tabela(k, o, t, grp, F):
            g = R.grupo(k, o)
            folga = max(R.wpal(t, F.L1) - grp[g][1], R.wpal(t, F.L0) - grp[g][0])
            if k.split(":")[1] == "character_name" and folga <= 5:
                # decisao documentada no lote 2 (notes/traducao.md): nomes de inimigo com limite
                # folgado podem passar poucos pixels; o painel centra o nome
                avi.append(f"aviso {k}: {x} (+{folga} px; nome de inimigo, tolerancia de 5 px) | {t!r}")
                lin.append(avi[-1])
                continue
            lin.append(f"ERRO {k}: {x} | {t!r} (EN {o!r})")
            n_err += 1
    lin.insert(0, f"erros: {n_err}; avisos: {len(avi)}")
    grava("4_larguras.txt", lin)
    resumo["larguras/linhas"] = f"{n_err} erros, {len(avi)} avisos (ver 4_larguras.txt)"
    erros_total += n_err

    # ---------- 2d. ingles restante
    aceitos_p = os.path.join(AQUI, "ingles_aceito.json")
    aceitos = set(json.load(open(aceitos_p, encoding="utf-8"))) if os.path.exists(aceitos_p) else set()
    lin = []
    n_sus = collections.Counter()
    n_total = collections.Counter()
    for lang in ("US", "EN"):
        lin.append(f"== pasta {lang}: textos de exibicao iguais ao original ingles ==")
        vistos = set()
        for c in sorted(N["sb"]):
            if not c.startswith(f"script/{lang}/") or "/dbg/" in c or c not in O["sb"]:
                continue
            to = O["sb"][c]["textos"]
            for i, t in enumerate(N["sb"][c]["textos"][:len(to)]):
                if t != to[i] or R.classifica(t) == "interno":
                    continue
                n_total[lang] += 1
                limpo = R.MARCA.sub(" ", t)
                sus = bool(EN_PAL.search(limpo)) and t not in aceitos
                if sus:
                    n_sus[lang] += 1
                if (t, sus) not in vistos:
                    vistos.add((t, sus))
                    lin.append(f"{'SUSPEITO ' if sus else 'ok       '}{c[len(lang) + 8:]}:{i} {t[:150]!r}")
        for k in sorted(N["bdat"]):
            lg, tab, i, col = k.split(":")
            if lg != lang or not R.TAB.match(tab):
                continue
            t = N["bdat"][k]
            if not t.strip() or t != O["bdat"].get(k):
                continue
            n_total[lang] += 1
            sus = bool(EN_PAL.search(R.MARCA.sub(" ", t))) and t not in aceitos
            n_sus[lang] += sus
            lin.append(f"{'SUSPEITO ' if sus else 'ok       '}{k} {t[:150]!r}")
    lin.insert(0, f"textos em ingles (iguais ao original): US {n_total['US']}, EN {n_total['EN']}; "
                  f"suspeitos (frase com palavras inglesas comuns, fora de ingles_aceito.json): "
                  f"US {n_sus['US']}, EN {n_sus['EN']}")
    grava("5_ingles_restante.txt", lin)
    resumo["ingles restante"] = (f"US {n_total['US']} / EN {n_total['EN']} textos iguais ao original; "
                                 f"suspeitos US {n_sus['US']} / EN {n_sus['EN']}")
    erros_total += n_sus["US"] + n_sus["EN"]

    resumo["tempo"] = f"{time.time() - t0:.0f} s"
    resumo["RESULTADO"] = "OK" if erros_total == 0 else f"{erros_total} problema(s)"
    txt = [f"ROM: {rom_p}", f"original: {orig_p}"] + [f"{k}: {v}" for k, v in resumo.items()]
    grava("0_resumo.txt", txt)
    print("\n".join(txt))
    sys.exit(0 if erros_total == 0 else 1)


if __name__ == "__main__":
    main()
