"""Extracao dos textos (US/EN) de uma ROM em memoria.

carregar_rom(caminho) -> bytes   (.nds ou .zip com um .nds dentro, lido em memoria)
extrair(rom) -> {"sb": {caminho: {"textos": [...], "imps": [...], "code": bytes}},
                 "bdat": {"LANG:tabela:linha:coluna": texto},
                 "fnt": {"latin0.fnt": bytes, "latin1.fnt": bytes}}
Mesmo formato de _revisao_claude/03_traducao/scripts/rev_extrair.py (code em bytes).
"""
import os
import struct
import sys
import zipfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nds_rom  # noqa: E402
from bdat import ler_container  # noqa: E402
from sb import textos  # noqa: E402

LANGS = ("US", "EN")
ORIG_ZIP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
                                         "00_Original", "Dragon Ball Z_ Attack of the Saiyans.zip"))


def carregar_rom(caminho):
    if caminho.lower().endswith(".zip"):
        with zipfile.ZipFile(caminho) as z:
            nome = [n for n in z.namelist() if n.lower().endswith(".nds")][0]
            return z.read(nome)
    with open(caminho, "rb") as f:
        return f.read()


def imports(d):
    offs = list(struct.unpack_from("<6I", d, 8))
    a4 = offs[4]
    hs, n = struct.unpack_from("<II", d, a4)
    base = a4 + hs + n * 4
    r = []
    for i in range(n):
        no, _ = struct.unpack_from("<HH", d, a4 + hs + i * 4)
        r.append(d[base + no:d.index(b"\x00", base + no)].decode("latin-1"))
    return r


def extrair(rom, langs=LANGS):
    cam = nds_rom.caminhos(rom)
    out = {"sb": {}, "bdat": {}, "fnt": {}}
    pref = tuple(f"script/{lg}/" for lg in langs)
    for c in sorted(cam):
        if c.startswith(pref) and c.endswith(".sb"):
            d = nds_rom.ler(rom, c)
            if d[:4] != b"SB  ":
                continue
            offs = list(struct.unpack_from("<6I", d, 8))
            out["sb"][c] = {"textos": [t.decode("latin-1") for t in textos(d)],
                            "imps": imports(d), "code": bytes(d[offs[0]:offs[1]])}
    for lang in langs:
        p = f"btl/bdat/{lang}/bdat.bin"
        if p not in cam:
            continue
        for nome, tb in ler_container(nds_rom.ler(rom, p)).items():
            cols = [cc[0] for cc in tb["colunas"] if cc[2] == 7]
            for i, lin in enumerate(tb["linhas"]):
                for col in cols:
                    out["bdat"][f"{lang}:{nome}:{i}:{col}"] = lin.get(col, "")
    for f in ("latin0.fnt", "latin1.fnt"):
        out["fnt"][f] = nds_rom.ler(rom, f)
    return out


def falantes(sbinfo):
    """indices dos textos usados como NOME de quem fala: 26 n 26 f consts 4a Msg (f com <p>)"""
    imps, code, ts = sbinfo["imps"], sbinfo["code"], sbinfo["textos"]
    if "Msg" not in imps:
        return set()
    msg = imps.index("Msg")
    r = set()
    q = 0
    while (q := code.find(b"\x26", q)) != -1:
        if q + 4 < len(code) and code[q + 2] == 0x26:
            a, b = code[q + 1], code[q + 3]
            k = q + 4
            while k < len(code) and 0x16 <= code[k] <= 0x1F:
                k += 1
            if (k + 1 < len(code) and code[k] == 0x4A and code[k + 1] == msg and a < len(ts)
                    and b < len(ts) and "<p>" in ts[b] and "<p>" not in ts[a]):
                r.add(a)
        q += 1
    return r
