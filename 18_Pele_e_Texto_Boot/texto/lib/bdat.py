"""Leitor do formato BDAT da Monolith Soft (o mesmo de Xenoblade),
derivado dos dados desta ROM — nao de documentacao externa.

Estrutura de uma tabela, conferida em enemy_param:

  0x00  "BDAT"
  0x04  u16 flags
  0x06  u16 nomes_off     -> nome da tabela, seguido dos registros de coluna
  0x08  u16 tam_linha     (enemy_param: 80)
  0x0A  u16 linhas_off    (enemy_param: 0x350)
  0x0C  u16 n_linhas      (enemy_param: 173)
  0x0E  u16 hash_off      -> fim da lista de colunas
  0x10  u16 hash_slots
  0x20  definicoes de coluna, 4 bytes cada: u8 tipo_celula, u8 tipo_valor,
        u16 posicao_na_linha

Registro de nome de coluna: u16 def_off, u16 link, nome\\0. O primeiro vem
colado no nome da tabela (sem alinhar); os seguintes comecam no proximo
endereco PAR.

Tipos de valor: 1=u8 2=u16 3=u32 4=s8 5=s16 6=s32 7=string(u16, relativo
ao inicio da tabela) 8=float. Tipo 0 = coluna sem valor na linha.

Validacao: o primeiro 'file' tem que dar 'ene001_01' e as strings dos
graficos comecam exatamente onde as linhas terminam (0x350 + 173*80).
"""
import struct

TAMANHO = {1: 1, 2: 2, 3: 4, 4: 1, 5: 2, 6: 4, 7: 2, 8: 4}
FMT = {1: "<B", 2: "<H", 3: "<I", 4: "<b", 5: "<h", 6: "<i", 7: "<H", 8: "<f"}


def cstr(b, o):
    f = b.index(b"\x00", o)
    return b[o:f].decode("latin-1")


def ler_tabela(t):
    assert t[:4] == b"BDAT", "nao e BDAT"
    u16 = lambda o: struct.unpack_from("<H", t, o)[0]
    nomes_off, tam_linha = u16(0x06), u16(0x08)
    linhas_off, n_linhas = u16(0x0A), u16(0x0C)
    hash_off = u16(0x0E)

    nome_tabela = cstr(t, nomes_off)
    # Regra conferida nas 35 tabelas:
    #  - o PRIMEIRO registro de coluna vem colado no nulo do nome da tabela,
    #    sem alinhamento (em boss_param e character_name ele comeca em
    #    endereco impar)
    #  - entre registros, o ENDERECO e alinhado a par
    p = nomes_off + len(nome_tabela) + 1
    colunas = []
    while p + 4 < hash_off:
        def_off = u16(p)
        nome = cstr(t, p + 4)
        tipo_cel, tipo_val, pos = t[def_off], t[def_off + 1], u16(def_off + 2)
        colunas.append((nome, tipo_cel, tipo_val, pos))
        p += 4 + len(nome) + 1
        p += p & 1

    linhas = []
    for i in range(n_linhas):
        base = linhas_off + i * tam_linha
        lin = {}
        for nome, tc, tv, pos in colunas:
            if tv == 0 or tv not in FMT:
                continue
            v = struct.unpack_from(FMT[tv], t, base + pos)[0]
            if tv == 7:
                v = cstr(t, v) if 0 < v < len(t) else ""
            lin[nome] = v
        linhas.append(lin)
    return {"nome": nome_tabela, "tam_linha": tam_linha, "n_linhas": n_linhas,
            "colunas": colunas, "linhas": linhas}


def ler_container(b):
    n = struct.unpack_from("<I", b, 0)[0]
    offs = [struct.unpack_from("<I", b, 4 + i * 4)[0] for i in range(n + 1)]
    inicios = sorted(o for o in offs if 0 < o < len(b))
    tabs = {}
    for i, a in enumerate(inicios):
        z = inicios[i + 1] if i + 1 < len(inicios) else len(b)
        if b[a:a + 4] == b"BDAT":
            tb = ler_tabela(b[a:z])
            tabs[tb["nome"]] = tb
    return tabs
