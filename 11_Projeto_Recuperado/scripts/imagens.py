"""Aplica as imagens em PT-BR numa ROM: rotulos do menu (rotulos.py,
rotulos2.py, rotulos3.py), faixas de fim de batalha (faixas_batalha.py),
faixas de nome de local (faixas_locais.py), "Tenshinhan" com letras
estreitas para caber no painel de batalha (tenshinhan_estreito.py) e
cartoes de titulo de capitulo (titulos.py -> /ds/saida/titulos/*.map).
uso: imagens.py <rom_entrada> <rom_saida>"""
import os
import subprocess
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

ent, sai = sys.argv[1], sys.argv[2]
for k, script in enumerate(("rotulos.py", "rotulos2.py", "rotulos3.py", "faixas_batalha.py", "faixas_locais.py",
                            "tenshinhan_estreito.py")):
    subprocess.run([sys.executable, f"/ds/scripts/{script}", ent if k == 0 else sai, sai], check=True,
                   stdout=subprocess.DEVNULL)
rom = bytearray(open(sai, "rb").read())
n = 0
for k in range(17):
    f = f"/ds/saida/titulos/C{k:02d}_9999us.map"
    if not os.path.exists(f):
        continue
    c = f"fld/map/C{k:02d}/C{k:02d}_9999us.map"
    print(c, nds_rom.substituir(rom, c, open(f, "rb").read()))
    n += 1
open(sai, "wb").write(rom)
print(f"rotulos + {n} titulos -> {sai}")
