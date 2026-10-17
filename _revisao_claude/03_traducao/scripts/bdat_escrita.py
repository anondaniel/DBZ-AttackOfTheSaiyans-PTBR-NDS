"""Gravacao em tabelas BDAT, campo a campo, sem mudar o layout.

Por enquanto so o que o hack de sprite precisa:
  - numero em coluna de tamanho fixo
  - string trocada por outra do MESMO tamanho (nao mexe em ponteiro)
"""
import struct

from bdat import FMT, ler_tabela


def tabelas_com_offset(b):
    n = struct.unpack_from("<I", b, 0)[0]
    offs = [struct.unpack_from("<I", b, 4 + i * 4)[0] for i in range(n + 1)]
    ini = sorted(o for o in offs if 0 < o < len(b))
    res = {}
    for i, a in enumerate(ini):
        z = ini[i + 1] if i + 1 < len(ini) else len(b)
        if b[a:a + 4] == b"BDAT":
            t = ler_tabela(bytes(b[a:z]))
            u16 = lambda o: struct.unpack_from("<H", b, a + o)[0]
            t["off"] = a
            t["linhas_off"] = u16(0x0A)
            t["col"] = {c[0]: c for c in t["colunas"]}
            res[t["nome"]] = t
    return res


def _pos(t, linha, coluna):
    _, _, tv, pos = t["col"][coluna]
    return tv, t["off"] + t["linhas_off"] + linha * t["tam_linha"] + pos


def ler_num(b, t, linha, coluna):
    tv, p = _pos(t, linha, coluna)
    return struct.unpack_from(FMT[tv], b, p)[0]


def gravar_num(b, t, linha, coluna, valor):
    tv, p = _pos(t, linha, coluna)
    assert tv != 7, "coluna de string"
    struct.pack_into(FMT[tv], b, p, valor)


def gravar_str_mesmo_tamanho(b, t, linha, coluna, novo):
    tv, p = _pos(t, linha, coluna)
    assert tv == 7
    str_off = struct.unpack_from("<H", b, p)[0]
    a = t["off"] + str_off
    fim = b.index(b"\x00", a)
    velho = bytes(b[a:fim])
    novo = novo.encode("latin-1")
    assert len(novo) == len(velho), f"tamanho diferente: {velho!r} -> {novo!r}"
    b[a:fim] = novo
    return velho.decode("latin-1")
