"""Lista as tabelas do bdat (EN) e procura as que referenciam linhas de
enemy_param: colunas numericas onde aparece 80 (Giant Snake, a 1a luta).
"""
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import ler_num, tabelas_com_offset

rom = open("/ds/rom/aots.nds", "rb").read()
b = bytearray(nds_rom.ler(rom, "btl/bdat/EN/bdat.bin"))
tabs = tabelas_com_offset(b)
for nome, t in tabs.items():
    cols = [c[0] for c in t["colunas"]]
    print(f"{nome:24s} {t['n_linhas']:4d} linhas | {', '.join(cols)[:150]}")

print("\n--- linhas com valor 80 ou 81 (Giant Snake = linha 80, name_id 90) ---")
for nome, t in tabs.items():
    if nome in ("enemy_param", "boss_param", "character_name"):
        continue
    for i, l in enumerate(t["linhas"]):
        hits = [c for c, v in l.items() if isinstance(v, int) and v in (80, 81, 90)]
        if hits:
            print(f"{nome}[{i}] {hits} -> {l}")
