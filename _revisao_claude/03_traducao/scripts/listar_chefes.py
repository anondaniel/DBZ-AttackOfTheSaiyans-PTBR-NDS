"""Lista boss_param (EN) com os campos de desenho, e os .chr de btl/ene."""
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import tabelas_com_offset

rom = open("/ds/rom/aots.nds", "rb").read()
b = bytearray(nds_rom.ler(rom, "btl/bdat/EN/bdat.bin"))
tabs = tabelas_com_offset(b)
nomes = [l["en"] for l in tabs["character_name"]["linhas"]]
bp = tabs["boss_param"]
print("colunas boss_param:", [c[0] for c in bp["colunas"]])
print("colunas enemy_param:", [c[0] for c in tabs["enemy_param"]["colunas"]])
for i, l in enumerate(bp["linhas"]):
    if not l["name_id"]:
        continue
    atk = [l.get(f"atk{k}") for k in range(1, 7)]
    print(f"{i:2d} {nomes[l['name_id'] - 1]:22s} {l['file']:10s} pal={l['palno']} "
          f"size={l['size']} shadow={l['shadow']} lv={l['lv']} hp={l['hp']} atk={atk}")
cam = nds_rom.caminhos(rom)
chr_ = sorted(c.split("/")[-1] for c in cam if c.startswith("btl/ene/"))
print("btl/ene:", len(chr_), [c for c in chr_ if c >= "ene1"])
