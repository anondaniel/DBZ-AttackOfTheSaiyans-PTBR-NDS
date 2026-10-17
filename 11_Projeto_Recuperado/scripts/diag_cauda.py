"""Batalha real com o Soldado Saiyajin na ROM final (PT-BR), para ver a
cauda escura: copia a linha escolhida sobre a do Wolf (104) e refaz a
batalha gravada de 1 lobo (pz5/p0027_pre.bin), como o diag_final.py.
uso: diag_cauda.py [linhas...]  (padrao: 95 101 110)"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import tabelas_com_offset

BASE = "/ds/rom/aots_ptbr_img.nds"
OUT = "/ds/saida/diag_cauda"
os.makedirs(OUT, exist_ok=True)
base = open(BASE, "rb").read()
for linha in [int(a) for a in sys.argv[1:]] or [95, 101, 110]:
    rom = bytearray(base)
    for lang in ["EN", "US", "FR", "SP", "GR", "IT"]:
        c = f"btl/bdat/{lang}/bdat.bin"
        b = bytearray(nds_rom.ler(rom, c))
        ep = tabelas_com_offset(b)["enemy_param"]
        ini, t = ep["off"] + ep["linhas_off"], ep["tam_linha"]
        b[ini + 104 * t:ini + 105 * t] = b[ini + linha * t:ini + (linha + 1) * t]
        nds_rom.substituir(rom, c, bytes(b))
    caminho = f"/ds/rom/dc_{linha}.nds"
    open(caminho, "wb").write(rom)
    tmp = f"{OUT}/tmp_{linha}"
    shutil.rmtree(tmp, ignore_errors=True)
    r = subprocess.run(["python3", "/ds/scripts/ab_batalha.py", "/ds/saida/pz5/p0027_pre.bin",
                        "27", "3", tmp, caminho], capture_output=True, text=True)
    os.remove(caminho)
    print(linha, r.stdout.strip()[-200:], flush=True)
    print("   ", sorted(os.listdir(tmp)) if os.path.isdir(tmp) else "sem saida")
