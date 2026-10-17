"""Aplica correcoes_texto.json numa ROM (referencia para o build; gera a ROM de teste).

uso: python -B aplicar_correcoes.py <rom_entrada.nds> <rom_saida.nds> [correcoes_texto.json]

- scripts: sb.textos / sb.com_textos (mesmo numero de textos) + nds_rom.substituir
- tabelas: bdat_strings.gravar_str + conferir (nenhuma outra celula muda) + nds_rom.substituir
- confere que cada "antes" bate com o texto atual (se ja estiver no "depois", pula)
"""
import collections
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "lib"))
import nds_rom  # noqa: E402
from bdat_strings import conferir, gravar_str  # noqa: E402
from sb import com_textos, textos  # noqa: E402


def aplicar(rom, entradas):
    """rom: bytearray (alterada no lugar). Devolve contagem."""
    n = collections.Counter()
    por_sb = collections.defaultdict(list)
    por_bd = collections.defaultdict(list)
    for e in entradas:
        (por_sb[e["arquivo"]] if e["tipo"] == "sb" else por_bd[e["lang"]]).append(e)
    for c, es in sorted(por_sb.items()):
        d = nds_rom.ler(rom, c)
        ts = textos(d)
        mudou = False
        for e in es:
            atual = ts[e["indice"]].decode("latin-1")
            if atual == e["depois"]:
                n["sb_ja_aplicada"] += 1
                continue
            assert atual == e["antes"], f"{c}:{e['indice']}: texto atual nao bate com 'antes': {atual!r}"
            ts[e["indice"]] = e["depois"].encode("latin-1")
            mudou = True
            n["sb"] += 1
        if mudou:
            nds_rom.substituir(rom, c, com_textos(d, ts))
    for lang, es in sorted(por_bd.items()):
        c = f"btl/bdat/{lang}/bdat.bin"
        velho = bytearray(nds_rom.ler(rom, c))
        from bdat import ler_container
        tabs = ler_container(bytes(velho))
        b = bytearray(velho)
        muda = {}
        for e in es:
            atual = tabs[e["tabela"]]["linhas"][e["linha"]][e["coluna"]]
            if atual == e["depois"]:
                n["bdat_ja_aplicada"] += 1
                continue
            assert atual == e["antes"], f"{lang}:{e['tabela']}:{e['linha']}: texto atual nao bate: {atual!r}"
            b, _ = gravar_str(b, e["tabela"], e["linha"], e["coluna"], e["depois"])
            muda[(e["tabela"], e["linha"], e["coluna"])] = e["depois"]
            n["bdat"] += 1
        if muda:
            conferir(velho, b, muda)
            nds_rom.substituir(rom, c, bytes(b))
    return n


def main():
    ent, sai = sys.argv[1], sys.argv[2]
    cj = sys.argv[3] if len(sys.argv) > 3 else os.path.join(AQUI, "correcoes_texto.json")
    rom = bytearray(open(ent, "rb").read())
    n = aplicar(rom, json.load(open(cj, encoding="utf-8")))
    open(sai, "wb").write(rom)
    print(dict(n), "->", sai, "SHA-256", hashlib.sha256(rom).hexdigest())


if __name__ == "__main__":
    main()
