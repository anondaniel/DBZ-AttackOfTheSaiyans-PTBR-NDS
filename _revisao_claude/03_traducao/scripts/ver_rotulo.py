"""Imprime a grade de indices (hex) de uma regiao de um atlas dIMG ou folha
dCHR (ROM original), para desenhar rotulos traduzidos.
uso: ver_rotulo.py <arquivo_na_rom> x0 y0 x1 y1 [pos_dCHR_no_pacote]"""
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from fonte_grossa import HEX
from rotulos import Atlas, Folha

rom = open("/ds/rom/aots.nds", "rb").read()
c = sys.argv[1]
x0, y0, x1, y1 = map(int, sys.argv[2:6])
d = nds_rom.ler(rom, c)
img = Atlas(d) if d[:4] == b"dIMG" else Folha(d, int(sys.argv[6]) if len(sys.argv) > 6 else 0)
print("     " + "".join(str((x - x0) // 10 % 10) for x in range(x0, x1 + 1)))
print("     " + "".join(str((x - x0) % 10) for x in range(x0, x1 + 1)))
for y in range(y0, y1 + 1):
    print("%4d " % y + "".join(HEX[img.get(x, y)] if img.get(x, y) > 0 else "." for x in range(x0, x1 + 1)))
