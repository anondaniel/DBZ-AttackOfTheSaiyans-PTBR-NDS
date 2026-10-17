"""Revisao: extrai textos US/EN (scripts .sb + tabelas bdat) da ROM original
e da ROM nova (somente leitura) e grava saida/textos_{orig,novo}.json.
uso: python rev_extrair.py <rom_orig> <rom_nova> <saida_dir>"""
import json
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(__file__))
import nds_rom
from bdat import ler_container
from sb import textos

TAB = re.compile(r"^(btl_mes_|cf_mes_|use_item_mes|btl_acc_mes|pt_eqp_mes|key_item_mes|character_name)")


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


def extrai(path):
    rom = open(path, "rb").read()
    cam = nds_rom.caminhos(rom)
    out = {"sb": {}, "bdat": {}, "fnt": {}}
    for c in sorted(cam):
        if c.startswith(("script/US/", "script/EN/", "script/FR/")) and c.endswith(".sb"):
            d = nds_rom.ler(rom, c)
            if d[:4] != b"SB  ":
                continue
            ts = [t.decode("latin-1") for t in textos(d)]
            offs = list(struct.unpack_from("<6I", d, 8))
            out["sb"][c] = {"textos": ts, "imps": imports(d),
                            "code": d[offs[0]:offs[1]].hex()}
    for lang in ("US", "EN", "FR"):
        p = f"btl/bdat/{lang}/bdat.bin"
        if p not in cam:
            continue
        t = ler_container(nds_rom.ler(rom, p))
        for nome, tb in t.items():
            cols = [cc[0] for cc in tb["colunas"] if cc[2] == 7]
            for i, l in enumerate(tb["linhas"]):
                for col in cols:
                    v = l.get(col, "")
                    out["bdat"][f"{lang}:{nome}:{i}:{col}"] = v
    for f in ("latin0.fnt", "latin1.fnt"):
        out["fnt"][f] = nds_rom.ler(rom, f).hex()
    return out


if __name__ == "__main__":
    o, n, sd = sys.argv[1:4]
    for tag, p in (("orig", o), ("novo", n)):
        r = extrai(p)
        json.dump(r, open(os.path.join(sd, f"textos_{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False)
        print(tag, len(r["sb"]), "scripts", len(r["bdat"]), "celulas")
