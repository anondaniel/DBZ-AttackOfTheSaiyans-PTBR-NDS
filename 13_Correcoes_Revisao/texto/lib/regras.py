"""Regras de validacao de texto (mesmo modelo do relatorio 03, rev_wrap/rev_larguras).

- marcacoes de controle: <..>, %d/%s, \\NN.. (cor/icone/botao), @NN, na mesma quantidade
- so Latin-1 com glifo nas duas fontes (latin0/latin1 da ROM)
- falas: quebra automatica em 196 px na fonte pequena (latin1); <n> forca quebra;
  pagina nao pode passar de 3 linhas se tiver mais linhas que o original;
  linha manual (<n>) acima de 196 px so e tolerada se o original ja tinha linha tao larga
- tabelas: largura <= maior largura original do grupo (lingua, tabela, coluna, com/sem <n>),
  nas fontes latin0 e latin1
- rotulos de quem fala: <= maior rotulo original (81 px)
"""
import collections
import re

LIM = 196
MARCA = re.compile(r"<[^>]*>|%[ds]|\\\d+(?:[PpA][0-9A-Za-z])?|@\d\d")
CODE = re.compile(r"<[^>]*>|\\\d+(?:[PpA][0-9A-Za-z])?")
SEM_GLIFO = set("¤¥¦§ª¬\xad¯²³µ¶¸¹º¼½¾Þþ")
TAB = re.compile(r"^(btl_mes_|cf_mes_|use_item_mes|btl_acc_mes|pt_eqp_mes|key_item_mes|character_name)")


def marcas(s):
    return collections.Counter(MARCA.findall(s))


def avancos(fnt):
    return bytes(fnt[:256])


def wpal(p, L):
    p = CODE.sub("", p)
    w = 0
    for parte in re.split(r"(@\d\d)", p):
        if re.fullmatch(r"@\d\d", parte):
            w += 10
        else:
            w += sum(L[ord(c)] if ord(c) < 256 else 8 for c in parte)
    return w


def paginas(s):
    partes = s.split("<p>")
    return partes[1:] if s.startswith("<p>") else partes


def linhas_pagina(pg, L, lim=LIM):
    pg = re.sub(r"<k>|<w=\d+>|<d>|<t>", "", pg)
    out = []
    for ln in re.split(r"<[nN]>", pg):
        cur = ""
        for w in ln.split(" "):
            cand = (cur + " " + w) if cur else w
            if cur and wpal(cand, L) > lim:
                out.append(cur)
                cur = w
            else:
                cur = cand
        out.append(cur)
    return [(x, wpal(x, L)) for x in out]


def linhas_manuais(s, L):
    """larguras das linhas separadas por <n> (so faz sentido se houver <n>)"""
    r = []
    for pg in paginas(s) if "<p>" in s else [s]:
        if "<n>" not in pg and "<N>" not in pg:
            continue  # pagina sem quebra manual: so quebra automatica
        for ln in re.split(r"<[nN]>", re.sub(r"<k>|<w=\d+>", "", pg)):
            r.append((ln, wpal(ln, L)))
    return r


class Fontes:
    def __init__(self, fnt):
        self.f0, self.f1 = fnt["latin0.fnt"], fnt["latin1.fnt"]
        self.L0, self.L1 = avancos(self.f0), avancos(self.f1)

    def sem_glifo(self, s):
        """caracteres sem desenho em alguma das fontes"""
        ruins = set()
        for f, bpg in ((self.f0, 15), (self.f1, 10)):
            g = lambda c: f[256 + c * bpg:256 + (c + 1) * bpg]
            listra = g(0x8D)
            for ch in set(s):
                o = ord(ch)
                if o > 255 or ch in SEM_GLIFO:
                    ruins.add(ch)
                elif o >= 0x80 and (g(o) == listra or not any(g(o))):
                    ruins.add(ch)
        return ruins


def checar_comum(orig, novo, fontes):
    """marcacoes, glifos, espaco duplo. Devolve lista de erros."""
    e = []
    if marcas(orig) != marcas(novo):
        e.append(f"marcacoes diferentes: EN {dict(marcas(orig))} PT {dict(marcas(novo))}")
    try:
        novo.encode("latin-1")
    except UnicodeEncodeError:
        e.append("caractere fora do Latin-1")
    sg = fontes.sem_glifo(novo)
    if sg:
        e.append(f"sem glifo na fonte: {''.join(sorted(sg))!r}")
    if "  " in re.sub(r"<[^>]*>", "#", novo) and "  " not in re.sub(r"<[^>]*>", "#", orig):
        e.append("espaco duplo")
    if re.search(r"<[^>]*$", novo.replace("<k?", "")) and not re.search(r"<[^>]*$", orig.replace("<k?", "")):
        e.append("tag malformada")
    return e


def checar_fala(orig, novo, L1o, L1):
    """paginas/linhas de um texto de script. Devolve (erros, avisos)."""
    e, a = [], []
    if "<p>" in novo or "<p>" in orig:
        pe, pp = paginas(orig), paginas(novo)
        if len(pe) != len(pp):
            e.append(f"numero de paginas mudou: {len(pe)} -> {len(pp)}")
        else:
            for k, (x, y) in enumerate(zip(pe, pp)):
                lx, ly = linhas_pagina(x, L1o), linhas_pagina(y, L1)
                if len(ly) > 3 and len(ly) > len(lx):
                    e.append(f"pagina {k}: {len(ly)} linhas (original {len(lx)})")
    mo = max([w for _, w in linhas_manuais(orig, L1o)] or [0])
    for ln, w in linhas_manuais(novo, L1):
        if w > LIM:
            if w > mo:
                e.append(f"linha manual com {w}px (> {LIM}; maior do original {mo}px): {ln!r}")
            else:
                a.append(f"linha manual com {w}px (> {LIM}, mas o original tinha {mo}px): {ln!r}")
    return e, a


# tabelas de item: linha par = nome, linha impar = descricao (conferido nas 4 tabelas)
TAB_ITEM = ("use_item_mes", "btl_acc_mes", "pt_eqp_mes", "key_item_mes")


def grupo(chave, orig):
    lang, tab, i, col = chave.split(":")
    return (lang, tab, col, "<n>" in orig or "<p>" in orig, int(i) % 2 if tab in TAB_ITEM else None)


def grupos_tabela(og_bdat, fontes_orig):
    """maior largura original por (lingua, tabela, coluna, tem<n>, nome/descricao) nas duas fontes"""
    grp = collections.defaultdict(lambda: [0, 0])
    for k, v in og_bdat.items():
        if not v.strip():
            continue
        g = grupo(k, v)
        for f, L in ((0, fontes_orig.L0), (1, fontes_orig.L1)):
            w = max(wpal(x, L) for x in re.split(r"<[nNpP]>", v))
            grp[g][f] = max(grp[g][f], w)
    return grp


def checar_tabela(chave, orig, novo, grp, fontes):
    g = grupo(chave, orig)
    w0 = max(wpal(x, fontes.L0) for x in re.split(r"<[nNpP]>", novo))
    w1 = max(wpal(x, fontes.L1) for x in re.split(r"<[nNpP]>", novo))
    e = []
    if w1 > grp[g][1] or w0 > grp[g][0]:
        e.append(f"largura peq {w1}/{grp[g][1]} gr {w0}/{grp[g][0]} acima do maior original do grupo")
    return e


def classifica(s):
    """mesmo criterio de rev_comparar.py: dialogo / exibido / exibido? / interno"""
    if "<p>" in s or "<P>" in s or "<k>" in s:
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
