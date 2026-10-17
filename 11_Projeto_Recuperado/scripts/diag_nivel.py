"""Mostra a tela "NIVEL +1!" no emulador: ROM de teste em que o inimigo da
batalha gravada (linha 104, Wolf) da muita EXP, em todos os idiomas, e refaz a
batalha (pz5/p0027_pre.bin) ate o fim com batalha_fim.py (que fotografa as
telas de subida de nivel). A ROM de teste e apagada no fim.
uso: diag_nivel.py [saida_dir] [exp]"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import gravar_num, tabelas_com_offset

BASE = "/ds/rom/aots_ptbr_img.nds"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/ds/saida/nivel"
EXP = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
ROM = "/ds/rom/dn_teste.nds"

rom = bytearray(open(BASE, "rb").read())
for lang in ["EN", "US", "FR", "SP", "GR", "IT"]:
    c = f"btl/bdat/{lang}/bdat.bin"
    b = bytearray(nds_rom.ler(rom, c))
    ep = tabelas_com_offset(b)["enemy_param"]
    gravar_num(b, ep, 104, "exp", EXP)
    nds_rom.substituir(rom, c, bytes(b))
open(ROM, "wb").write(rom)
shutil.rmtree(OUT, ignore_errors=True)
try:
    r = subprocess.run(["python3", "/ds/scripts/batalha_fim.py", "/ds/saida/pz5/p0027_pre.bin",
                        "27", "3", OUT, ROM], capture_output=True, text=True)
    print(r.stdout.strip()[-300:], r.stderr.strip()[-300:])
finally:
    os.remove(ROM)
print("ROM de teste apagada:", not os.path.exists(ROM))
