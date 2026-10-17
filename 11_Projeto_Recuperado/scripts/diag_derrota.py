"""Mostra a faixa "Derrota" no emulador: ROM de teste com o inimigo da
batalha gravada (linha 104, Wolf) imortal em todos os idiomas, e refaz a
batalha (pz5/p0027_pre.bin); ja dentro dela, poe HP 1 no grupo
(derrota_estado.py) e segue apertando A ate a faixa e a volta.
A ROM de teste fica em /ds/rom/dd_teste.nds e e apagada no fim.
uso: diag_derrota.py [saida_dir]"""
import os
import shutil
import struct
import subprocess
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat import FMT
from bdat_escrita import gravar_num, tabelas_com_offset

BASE = "/ds/rom/aots_ptbr_img.nds"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/ds/saida/derrota"
ROM = "/ds/rom/dd_teste.nds"
FORTE = {"hp": 60000, "def": 999}

rom = bytearray(open(BASE, "rb").read())
for lang in ["EN", "US", "FR", "SP", "GR", "IT"]:
    c = f"btl/bdat/{lang}/bdat.bin"
    b = bytearray(nds_rom.ler(rom, c))
    ep = tabelas_com_offset(b)["enemy_param"]
    # so imortal: copiar ataques de chefe (linha 7) fez o inimigo nunca acertar
    for col, v in FORTE.items():
        tv = ep["col"][col][2]
        maximo = (1 << (8 * struct.calcsize(FMT[tv]) - (1 if FMT[tv][1].islower() else 0))) - 1
        gravar_num(b, ep, 104, col, min(v, maximo))
    nds_rom.substituir(rom, c, bytes(b))
open(ROM, "wb").write(rom)
shutil.rmtree(OUT, ignore_errors=True)
try:
    # 1) entra na batalha na ROM de teste e salva o estado; 2) HP 1 no grupo e segue
    subprocess.run(["python3", "/ds/scripts/batalha_fim.py", "/ds/saida/pz5/p0027_pre.bin",
                    "27", "3", OUT + "_pre", ROM], capture_output=True, text=True,
                   env=dict(os.environ, SALVA_EM="12", PARA="1"))
    r = subprocess.run(["python3", "/ds/scripts/derrota_estado.py", OUT + "_pre/estado_12.bin", OUT, ROM],
                       capture_output=True, text=True)
    print(r.stdout.strip()[-300:], r.stderr.strip()[-300:])
finally:
    os.remove(ROM)
print("ROM de teste apagada:", not os.path.exists(ROM))
