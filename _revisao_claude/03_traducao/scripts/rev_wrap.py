"""Simulacao de quebra de linha das falas (fonte pequena latin1).
Modelo: <n> forca quebra; linha que passa de LIM e quebrada por palavra.
Conta linhas por pagina (<p>). Mede em unidades da tabela de avancos
(+extra px por caractere, parametro)."""
import json
import os
import re

S = os.path.join(os.path.dirname(__file__), "..", "saida")
CODE = re.compile(r"<[^>]*>|\\\d+(?:[PpA][0-9A-Za-z])?")


def carrega(tag):
    d = json.load(open(os.path.join(S, f"textos_{tag}.json"), encoding="utf-8"))
    L = bytes.fromhex(d["fnt"]["latin1.fnt"])[:256]
    return d, L


def wpal(p, L, extra):
    p = CODE.sub("", p)
    w = 0
    for parte in re.split(r"(@\d\d)", p):
        if re.fullmatch(r"@\d\d", parte):
            w += 10
        else:
            w += sum(L[ord(c)] + extra if ord(c) < 256 else 8 for c in parte)
    return w


def paginas(s):
    """divide em paginas: cada <p> abre pagina; devolve lista de strings"""
    partes = s.split("<p>")
    return [x for x in partes[1:]] if s.startswith("<p>") else partes


def linhas_pagina(pg, L, lim, extra):
    """quebra uma pagina; devolve lista (texto, largura) das linhas"""
    pg = re.sub(r"<k>|<w=\d+>|<d>|<t>", "", pg)
    out = []
    for ln in re.split(r"<[nN]>", pg):
        pal = ln.split(" ")
        cur = ""
        for w in pal:
            cand = (cur + " " + w) if cur else w
            if cur and wpal(cand, L, extra) > lim:
                out.append(cur)
                cur = w
            else:
                cur = cand
        out.append(cur)
    return [(x, wpal(x, L, extra)) for x in out]
