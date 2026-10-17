"""Traducao PT-BR: validacao, acumulo e aplicacao na ROM.

  validar <loteN.json> <loteN_pt.json>
      confere cada traducao: mesmas marcacoes (<...>, %d/%s, \\codigos,
      @NN) na mesma quantidade que o original; so caracteres que a fonte
      tem (Latin-1); sem sobra de texto em ingles obvio. Se passar,
      acrescenta em /ds/traducao/ptbr.json (original -> traducao).
  rom <rom_base> <saida>
      aplica ptbr.json nos scripts das pastas US e EN (casando pelo texto
      original) e grava a ROM.
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, "/ds/scripts")

ACUM = "/ds/traducao/ptbr.json"
# codigos de controle: <tag>, %d/%s, \NN com sufixo opcional P?/p?/A? (cor,
# icone, botao: \1P3 \1Pn \4AA \4Pd \4pi \24P3), \42 (aspas), @NN (icone)
MARCA = re.compile(r"<[^>]*>|%[ds]|\\\d+(?:[PpA][0-9A-Za-z])?|@\d\d")


def marcas(s):
    return collections.Counter(MARCA.findall(s))


def validar(lote_path, pt_path):
    lote = json.load(open(lote_path, encoding="utf-8"))
    pt = json.load(open(pt_path, encoding="utf-8"))
    acum = json.load(open(ACUM, encoding="utf-8")) if os.path.exists(ACUM) else {}
    erros = []
    faltam = [k for k in lote if k not in pt]
    if faltam:
        erros.append(f"sem traducao: {faltam[:20]}")
    for k, t in pt.items():
        o = lote[k]["original"]
        if marcas(o) != marcas(t):
            erros.append(f"{k}: marcacoes diferentes\n   EN {dict(marcas(o))}\n   PT {dict(marcas(t))}")
        try:
            t.encode("latin-1")
        except UnicodeEncodeError as e:
            erros.append(f"{k}: caractere fora da fonte: {t[e.start:e.end]!r}")
        # Latin-1 mas sem desenho na fonte do jogo (aparece como listras)
        sem = [c for c in t if c in "¤¥¦§ª¬\xad¯²³µ¶¸¹º¼½¾Þþ"]
        if sem:
            erros.append(f"{k}: a fonte do jogo nao tem {''.join(sem)!r}")
        # tag vira um marcador (e nao vazio), senao "de <f> subiu" parece "de  subiu"
        if "  " in re.sub(r"<[^>]*>", "#", t) and "  " not in re.sub(r"<[^>]*>", "#", o):
            erros.append(f"{k}: espaco duplo")
    if erros:
        print("\n".join(erros))
        print(f"{len(erros)} problema(s); nada foi acumulado")
        sys.exit(1)
    for k, t in pt.items():
        acum[lote[k]["original"]] = t
    json.dump(acum, open(ACUM, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"ok: {len(pt)} traducoes validadas; acumulado = {len(acum)}")


def _por_fonte(acum):
    """Separa o acumulado por ORIGEM (lotes com ids 'sb:' = scripts,
    'bdat:' = tabelas). Um texto so e trocado no tipo de arquivo de onde
    veio: palavra curta de menu ('Item', 'Save') pode ser identificador
    dentro de script."""
    import glob
    fontes = {"script": set(), "tabela": set()}
    for f in glob.glob("/ds/traducao/lote*.json"):
        if not re.search(r"/lote\d+\.json$", f):
            continue
        for v in json.load(open(f, encoding="utf-8")).values():
            for i in v["ids"]:
                fontes["script" if i.startswith("sb:") else "tabela"].add(v["original"])
    # nomes de quem fala (1o argumento de Msg) tambem sao seguros nos scripts,
    # mesmo quando a traducao veio de uma tabela (ex.: "Monster Carrot")
    fontes["script"] |= _falantes()
    # tabelas so tem texto de exibicao: podem receber qualquer traducao
    return {k: v for k, v in acum.items() if k in fontes["script"]}, dict(acum)


def _falantes():
    """Strings usadas como nome de quem fala: 26 <nome> 26 <fala> ... 4a <Msg>"""
    import struct
    import nds_rom
    from sb import textos
    rom = open("/ds/rom/aots.nds", "rb").read()
    r = set()
    for c in nds_rom.caminhos(rom):
        if not (c.startswith("script/US/") and c.endswith(".sb")):
            continue
        d = nds_rom.ler(rom, c)
        if d[:4] != b"SB  ":
            continue
        offs = list(struct.unpack_from("<6I", d, 8))
        a4 = offs[4]
        hs, n = struct.unpack_from("<II", d, a4)
        base = a4 + hs + n * 4
        imps = []
        for i in range(n):
            no, _ = struct.unpack_from("<HH", d, a4 + hs + i * 4)
            imps.append(d[base + no:d.index(b"\x00", base + no)].decode())
        if "Msg" not in imps:
            continue
        msg = imps.index("Msg")
        code = d[offs[0]:offs[1]]
        ts = [t.decode("latin-1") for t in textos(d)]
        p = 0
        while (p := code.find(b"\x26", p)) != -1:
            if p + 4 < len(code) and code[p + 2] == 0x26:
                a, b = code[p + 1], code[p + 3]
                z = code[p + 4:p + 10]
                k = 0
                while k < len(z) and 0x16 <= z[k] <= 0x1F:
                    k += 1
                if (k + 1 < len(z) and z[k] == 0x4A and z[k + 1] == msg and a < len(ts)
                        and b < len(ts) and "<p>" in ts[b] and "<p>" not in ts[a]):
                    r.add(ts[a])
            p += 1
    return r


EXIBE = {"Msg", "Select", "SetClickPoint", "Box"}


def _chamadas(code, imps):
    """Para cada push de texto (26 <i>), a funcao chamada logo depois
    (pulando so empilhamentos simples). Devolve [(pos, i, funcao|None)]."""
    r = []
    p = 0
    while (p := code.find(b"\x26", p)) != -1:
        if p + 1 >= len(code):
            break
        i = code[p + 1]
        q, f = p + 2, None
        for _ in range(12):
            if q >= len(code):
                break
            op = code[q]
            if op == 0x4A and q + 1 < len(code):
                f = imps[code[q + 1]] if code[q + 1] < len(imps) else None
                break
            tam = {0x26: 2, 0x14: 2, 0x38: 2, 0x15: 3, 0x13: 5, 0x24: 1}.get(op)
            if tam is None and 0x16 <= op <= 0x1F:
                tam = 1
            if tam is None and op == 0x29 and q + 1 < len(code) and code[q + 1] == 3:
                tam = 3
            if tam is None:
                break
            q += tam
        r.append((p, i, f))
        p += 2
    return r


def _falas(code, imps, ts):
    """Posicoes do push do NOME em Msg(nome, fala): 26 n 26 f consts 4a Msg,
    com ts[f] contendo <p>. Devolve [(pos, n)]."""
    if "Msg" not in imps:
        return []
    msg = imps.index("Msg")
    r = []
    p = 0
    while (p := code.find(b"\x26", p)) != -1:
        if p + 4 < len(code) and code[p + 2] == 0x26:
            n, f = code[p + 1], code[p + 3]
            k = p + 4
            while k < len(code) and 0x16 <= code[k] <= 0x1F:
                k += 1
            if (k + 1 < len(code) and code[k] == 0x4A and code[k + 1] == msg
                    and n < len(ts) and f < len(ts) and b"<p>" in ts[f] and b"<p>" not in ts[n]):
                r.append((p, n))
        p += 1
    return r


def _traduz_script(d, acum):
    """Troca os textos de um .sb. Texto curto que tambem serve de
    IDENTIFICADOR (vai para funcao que nao exibe, ex. Control("Chi-Chi"))
    fica como esta; a traducao vira uma entrada nova e so as chamadas de
    exibicao passam a apontar para ela."""
    import struct
    from sb import com_textos, textos
    ts = textos(d)
    offs = list(struct.unpack_from("<6I", d, 8))
    a4 = offs[4]
    hs, n = struct.unpack_from("<II", d, a4)
    base = a4 + hs + n * 4
    imps = []
    for k in range(n):
        no, _ = struct.unpack_from("<HH", d, a4 + hs + k * 4)
        imps.append(d[base + no:d.index(b"\x00", base + no)].decode())
    code = bytearray(d[offs[0]:offs[1]])
    usos = _chamadas(bytes(code), imps)
    # identificador: qualquer uso aparente fora de exibicao (falso positivo
    # aqui so causa uma separacao desnecessaria, que e inofensiva)
    ident = {i for _, i, f in usos if f is not None and f not in EXIBE}
    # repontar SO no padrao forte de fala: 26 <nome> 26 <texto com <p>> consts 4a Msg
    fortes = [(p, i, "Msg") for p, i in _falas(bytes(code), imps, ts)]
    usos = fortes
    novos, mudou, extra, repont = list(ts), 0, [], 0
    for i, t in enumerate(ts):
        s = t.decode("latin-1")
        if s not in acum or acum[s] == s:
            continue  # sem traducao, ou traducao igual (nome proprio: "Mez")
        tr = acum[s].encode("latin-1")
        if i in ident and "<p>" not in s:
            j = len(ts) + len(extra)
            if j > 255:
                continue  # indice de 1 byte: sem espaco, fica em ingles
            extra.append(tr)
            for p, ii, f in usos:
                if ii == i and f in EXIBE:
                    code[p + 1] = j
                    repont += 1
            mudou += 1
        else:
            novos[i] = tr
            mudou += 1
    if not mudou:
        return None, 0, 0
    d2 = bytearray(com_textos(d, novos + extra) if not extra else _com_extra(d, novos, extra))
    d2[offs[0]:offs[1]] = code  # secao 0 nao muda de lugar nem de tamanho
    return bytes(d2), mudou, repont


def _com_extra(d, novos, extra):
    """com_textos aceitando MAIS textos que o original (acrescenta no fim)."""
    import struct
    offs = list(struct.unpack_from("<6I", d, 8))
    a2, a3 = offs[2], offs[3]
    hs, _ = struct.unpack_from("<II", d, a2)
    todos = novos + extra
    corpo, lista = bytearray(), []
    for t in todos:
        lista.append(len(corpo))
        corpo += t + b"\x00"
    sec2 = struct.pack("<II", hs, len(todos)) + struct.pack(f"<{len(todos)}I", *lista) + bytes(corpo)
    sec2 += b"\x00" * (-len(sec2) % 4)
    delta = len(sec2) - (a3 - a2)
    out = bytearray(d[:a2]) + sec2 + d[a3:]
    for k in range(3, 6):
        struct.pack_into("<I", out, 8 + k * 4, offs[k] + delta)
    return bytes(out)


def rom(base, saida):
    import nds_rom
    from sb import com_textos, textos
    acum_sb, acum_tab = _por_fonte(json.load(open(ACUM, encoding="utf-8")))
    acum = acum_sb
    r = bytearray(open(base, "rb").read())
    n_arq = n_txt = n_rep = 0
    for c in sorted(nds_rom.caminhos(r)):
        if not (c.startswith(("script/US/", "script/EN/")) and c.endswith(".sb")):
            continue
        d = nds_rom.ler(r, c)
        if d[:4] != b"SB  ":
            continue
        novo, mudou, rep = _traduz_script(d, acum)
        if novo:
            nds_rom.substituir(r, c, novo)
            n_arq += 1
            n_txt += mudou
            n_rep += rep
    print(f"{n_txt} textos trocados em {n_arq} scripts; {n_rep} exibicoes repontadas "
          f"(identificadores preservados)")
    # tabelas (bdat): colunas de texto das tabelas de mensagem e de nomes
    from bdat_escrita import tabelas_com_offset
    from bdat_strings import conferir, gravar_str
    TAB = re.compile(r"^(btl_mes_|cf_mes_|use_item_mes|btl_acc_mes|pt_eqp_mes|key_item_mes|character_name)")
    acum = acum_tab
    for lang in ("US", "EN"):
        c = f"btl/bdat/{lang}/bdat.bin"
        velho = bytearray(nds_rom.ler(r, c))
        b = bytearray(velho)
        muda = {}
        for nome, t in tabelas_com_offset(velho).items():
            if not TAB.match(nome):
                continue
            cols = [cc[0] for cc in t["colunas"] if cc[2] == 7]
            for i, l in enumerate(t["linhas"]):
                for col in cols:
                    s = l.get(col, "")
                    if s in acum and acum[s] != s:
                        b, _ = gravar_str(b, nome, i, col, acum[s])
                        muda[(nome, i, col)] = acum[s]
        conferir(velho, b, muda)
        print(f"{c}: {len(muda)} celulas traduzidas (conferidas) |", nds_rom.substituir(r, c, bytes(b)))
    open(saida, "wb").write(r)
    print("->", saida)


if __name__ == "__main__":
    if sys.argv[1] == "validar":
        validar(sys.argv[2], sys.argv[3])
    else:
        rom(sys.argv[2], sys.argv[3])
