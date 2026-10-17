"""Escritor de strings BDAT de tamanho LIVRE.

Layout (conferido nas 35 tabelas deste bdat.bin, ver bdat_layout.py):
  contêiner: u32 n_tabelas, u32 tamanho_do_arquivo, u32 offset[n]
  tabela:    cabecalho, colunas, linhas, strings (C, latin-1), zeros ate
             multiplo de 16. Ponteiro de string = u16 relativo ao inicio
             da tabela. Nao ha campo de tamanho nem checksum de strings.

gravar_str(b, tabela, linha, coluna, texto) -> novo bytearray
  - se a string antiga nao e compartilhada e o texto cabe no espaco dela,
    grava no lugar (completa com zeros)
  - senao, poe o texto no fim da area de strings da tabela e aponta a
    celula para ele; a tabela cresce (alinhada a 16), as tabelas seguintes
    sao empurradas e os offsets do contêiner + o tamanho do arquivo sao
    corrigidos. Offsets DENTRO das tabelas sao relativos, nao mudam.

conferir(antes, depois, mudancas) confere que TODAS as celulas de TODAS
as tabelas ficaram iguais, exceto as mudancas pedidas.
"""
import struct

from bdat import ler_container
from bdat_escrita import tabelas_com_offset


def _ordem(b):
    n = struct.unpack_from("<I", b, 0)[0]
    offs = [struct.unpack_from("<I", b, 8 + i * 4)[0] for i in range(n)]
    assert struct.unpack_from("<I", b, 4)[0] == len(b), "campo de tamanho nao bate"
    return n, offs


def _refs(b, t):
    """todas as celulas de string da tabela: [(endereco_da_celula, valor)]"""
    r = []
    for nome, tc, tv, pos in t["colunas"]:
        if tv != 7:
            continue
        for i in range(t["n_linhas"]):
            p = t["off"] + t["linhas_off"] + i * t["tam_linha"] + pos
            r.append((p, struct.unpack_from("<H", b, p)[0]))
    return r


def gravar_str(b, tabela, linha, coluna, texto):
    b = bytearray(b)
    n, offs = _ordem(b)
    tabs = tabelas_com_offset(b)
    t = tabs[tabela]
    _, _, tv, pos = t["col"][coluna]
    assert tv == 7, f"{coluna} nao e string"
    novo = texto.encode("latin-1")
    assert b"\x00" not in novo
    cel = t["off"] + t["linhas_off"] + linha * t["tam_linha"] + pos
    velho_off = struct.unpack_from("<H", b, cel)[0]
    a = t["off"] + velho_off
    velho_len = b.index(b"\x00", a) - a
    refs = _refs(b, t)
    compartilhada = sum(1 for _, v in refs if v == velho_off) > 1

    if not compartilhada and len(novo) <= velho_len:
        b[a:a + velho_len] = novo + b"\x00" * (velho_len - len(novo))
        return b, "no lugar"

    # fim da tabela = inicio da proxima (ou fim do arquivo)
    ini_t = t["off"]
    seguintes = sorted(o for o in offs if o > ini_t)
    fim_t = seguintes[0] if seguintes else len(b)
    fim_str = max(b.index(b"\x00", ini_t + v) for _, v in refs if v) + 1
    livre = fim_t - fim_str
    precisa = len(novo) + 1
    if precisa <= livre:
        delta = 0
    else:
        delta = (precisa - livre + 15) & ~15
        b[fim_t:fim_t] = b"\x00" * delta
        for i in range(n):
            if offs[i] > ini_t:
                struct.pack_into("<I", b, 8 + i * 4, offs[i] + delta)
        struct.pack_into("<I", b, 4, len(b))
    novo_off = fim_str - ini_t
    assert novo_off + precisa <= 0xFFFF, "tabela passaria de 64 KB"
    b[fim_str:fim_str + precisa] = novo + b"\x00"
    struct.pack_into("<H", b, cel, novo_off)
    return b, f"anexado em +0x{novo_off:x} (tabela cresceu {delta} b)"


def conferir(antes, depois, mudancas):
    """mudancas: {(tabela, linha, coluna): valor_novo}"""
    ta, td = ler_container(bytes(antes)), ler_container(bytes(depois))
    assert ta.keys() == td.keys()
    for nome in ta:
        la, ld = ta[nome]["linhas"], td[nome]["linhas"]
        assert len(la) == len(ld), nome
        for i, (x, y) in enumerate(zip(la, ld)):
            for col in x:
                esperado = mudancas.get((nome, i, col), x[col])
                assert y[col] == esperado, f"{nome}[{i}].{col}: {x[col]!r} -> {y[col]!r}"
    _ordem(depois)
    return True
