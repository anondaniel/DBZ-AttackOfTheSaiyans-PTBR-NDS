"""Mapa de bytes de tabelas BDAT: cabecalho inteiro (0x00-0x20 em u16),
onde ficam linhas, strings e hash, e o que ha entre o fim de uma tabela
e o inicio da proxima. Tambem mostra o contêiner (offsets u32).
uso: bdat_layout.py [tabela ...]"""
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import tabelas_com_offset

rom = open("/ds/rom/aots.nds", "rb").read()
b = bytearray(nds_rom.ler(rom, "btl/bdat/EN/bdat.bin"))
n = struct.unpack_from("<I", b, 0)[0]
offs = [struct.unpack_from("<I", b, 4 + i * 4)[0] for i in range(n + 1)]
print(f"contêiner: n={n}, {len(b)} bytes, offs[0..3]={[hex(o) for o in offs[:4]]}, ultimo={hex(offs[-1])}")
print("offs[-1] == len?", offs[-1] == len(b), " cabecalho termina em", hex(4 + (n + 1) * 4))
tabs = tabelas_com_offset(b)
ordem = sorted(tabs.values(), key=lambda t: t["off"])
alvo = sys.argv[1:] or ["character_name", "enemy_param", "cf_mes_MENU"]
for k, t in enumerate(ordem):
    a = t["off"]
    z = ordem[k + 1]["off"] if k + 1 < len(ordem) else len(b)
    if t["nome"] not in alvo:
        continue
    h = struct.unpack_from("<16H", b, a)
    print(f"\n== {t['nome']} @0x{a:x}..0x{z:x} ({z - a} b)")
    print("  cab u16:", " ".join(f"{x:04x}" for x in h))
    print("  cab u32 0x10..0x20:", [hex(x) for x in struct.unpack_from("<4I", b, a + 0x10)])
    lin_ini = t["linhas_off"]
    lin_fim = lin_ini + t["n_linhas"] * t["tam_linha"]
    # strings referenciadas
    refs = []
    for nome, tc, tv, pos in t["colunas"]:
        if tv == 7:
            for i in range(t["n_linhas"]):
                refs.append(struct.unpack_from("<H", b, a + lin_ini + i * t["tam_linha"] + pos)[0])
    refs = [r for r in refs if r]
    print(f"  linhas 0x{lin_ini:x}..0x{lin_fim:x}; strings ref 0x{min(refs):x}..0x{max(refs):x}" if refs else
          f"  linhas 0x{lin_ini:x}..0x{lin_fim:x}; sem strings")
    if refs:
        ult = max(refs)
        fim_str = b.index(b"\x00", a + ult) - a
        print(f"  ultima string termina em 0x{fim_str:x}; tabela tem 0x{z - a:x}")
        print("  cauda:", b[a + fim_str:z].hex(" ")[:120])
    # valores do cabecalho que batem com limites conhecidos
    for i, x in enumerate(h):
        marcas = {lin_ini: "linhas_off", lin_fim: "fim linhas", z - a: "tam tabela"}
        if refs:
            marcas[min(refs)] = "ini strings"
            marcas[fim_str + 1] = "fim strings(+1)"
        if x in marcas:
            print(f"   cab[0x{i * 2:02x}] = 0x{x:x} -> {marcas[x]}")
