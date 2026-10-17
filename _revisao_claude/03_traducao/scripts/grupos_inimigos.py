"""Decodifica as chamadas SetEnemyParty de todos os .sb (EN) e lista os
grupos de inimigos por mapa. Procura em quais mapas aparecem os lobos.

Formato (deduzido do tut01_00.sb, onde a 1a luta e a Giant Snake):
  4a NN        chama o import NN (tabela da secao 4)
  14 xx        empilha byte
  15 hh ll     empilha u16 (big-endian)
  13 aa bb cc dd empilha u32
  16..1f       empilham 0..9 (16=0, 17=1, ...)
  24           empilha "vazio"
  ... args ..., 14 <argc>, 4a <SetEnemyParty>
IDs de inimigo sao 1-based: id = linha de enemy_param + 1.

uso: grupos_inimigos.py [ids_procurados separados por virgula]
"""
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import tabelas_com_offset

rom = open("/ds/rom/aots.nds", "rb").read()
cam = nds_rom.caminhos(rom)
b = bytearray(nds_rom.ler(rom, "btl/bdat/EN/bdat.bin"))
tabs = tabelas_com_offset(b)
ep = tabs["enemy_param"]["linhas"]
nomes = tabs["character_name"]["linhas"]


def nome_ini(i):  # i 1-based
    if not (1 <= i <= len(ep)):
        return f"?{i}"
    nid = ep[i - 1]["name_id"]
    return nomes[nid - 1]["en"] if nid else f"(vazio {i})"


procura = {int(x, 0) for x in sys.argv[1].split(",")} if len(sys.argv) > 1 else set()


def imports(d, offs):
    a4 = offs[4]
    hs, n = struct.unpack_from("<II", d, a4)
    base = a4 + hs + n * 4
    r = []
    for i in range(n):
        no, _ = struct.unpack_from("<HH", d, a4 + hs + i * 4)
        r.append(d[base + no:d.index(b"\x00", base + no)].decode())
    return r


def tokens(code, a, z):
    """tokeniza [a, z) de tras para frente nao da; faz para frente e
    devolve lista de (valor|None|'?') ."""
    out = []
    p = a
    while p < z:
        op = code[p]
        if op == 0x14:
            out.append(code[p + 1]); p += 2
        elif op == 0x15:
            out.append((code[p + 1] << 8) | code[p + 2]); p += 3
        elif op == 0x13:
            out.append(struct.unpack_from(">I", code, p + 1)[0]); p += 5
        elif 0x16 <= op <= 0x1f:
            out.append(op - 0x16); p += 1
        elif op == 0x24:
            out.append(None); p += 1
        else:
            out.append("?"); p += 1
    return out


achados = []
for c in sorted(cam):
    if not (c.startswith("script/EN/") and c.endswith(".sb")):
        continue
    d = nds_rom.ler(rom, c)
    if d[:4] != b"SB  ":
        continue
    offs = list(struct.unpack_from("<6I", d, 8)) + [len(d)]
    imp = imports(d, offs)
    if "SetEnemyParty" not in imp:
        continue
    k = imp.index("SetEnemyParty")
    code = d[offs[0]:offs[1]]
    p = 0
    grupos = []
    while True:
        p = code.find(bytes([0x4a, k]), p)
        if p == -1:
            break
        # argc = "14 0f" logo antes
        if code[p - 2] == 0x14:
            argc = code[p - 1]
            # recua ate achar exatamente argc tokens: tenta janelas crescentes
            for janela in range(argc, argc * 5 + 1):
                toks = tokens(code, p - 2 - janela, p - 2)
                if len(toks) >= argc and "?" not in toks[-argc:]:
                    cand = toks[-argc:]
                    # confere que a tokenizacao termina alinhada
                    if tokens(code, p - 2 - janela, p - 2)[-argc:] == cand:
                        break
            grupos.append((p, argc, cand))
        p += 2
    if grupos:
        mapa = c.split("/")[-1][:-3]
        for p, argc, args in grupos:
            ids = [v for v in args if isinstance(v, int) and 1 <= v <= len(ep)]
            achados.append((mapa, args))
            marca = " <<<" if procura & set(ids) else ""
            if not procura or marca:
                print(f"{mapa:12s} @{p + offs[0]:05x} argc={argc} {args}{marca}")

if procura:
    print()
for alvo in sorted(procura):
    ms = sorted({m for m, a in achados if alvo in a})
    print(f"id {alvo} ({nome_ini(alvo)}): {ms}")
