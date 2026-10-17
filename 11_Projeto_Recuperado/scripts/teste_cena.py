"""ROM de TESTE (nao e entrega): o icone da Ilha de Treinamento no
mapa-mundi passa a abrir outra cena/mapa (string de 8 letras, mesmo
tamanho de 'tut01_00'). Serve para ver uma cena traduzida sem jogar ate
ela. A cena pode sair com o grupo errado (quem esta no grupo vem do save).

uso: teste_cena.py <rom_base> <cena> <saida>
"""
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from sb import com_textos, textos

base, cena, saida = sys.argv[1], sys.argv[2].encode(), sys.argv[3]
assert len(cena) == 8
rom = bytearray(open(base, "rb").read())
for c in nds_rom.caminhos(rom):
    if c.endswith("/cf/worldmap.sb"):
        d = nds_rom.ler(rom, c)
        ts = textos(d)
        ts = [cena if t == b"tut01_00" else t for t in ts]
        nds_rom.substituir(rom, c, com_textos(d, ts))
open(saida, "wb").write(rom)
print("ok", saida)
