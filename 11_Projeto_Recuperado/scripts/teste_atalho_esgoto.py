"""ROM de teste: o icone da Cidade do Oeste no mapa-mundi leva ao esgoto
(troca a string "wst01_00" por "ges01_00" no worldmap.sb; mesmo tamanho)."""
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = bytearray(open("/ds/rom/ta_esg_base.nds", "rb").read())
for c in [c for c in nds_rom.caminhos(rom) if c.endswith("/cf/worldmap.sb")]:
    d = bytearray(nds_rom.ler(rom, c))
    alvo = b"wst01_00\x00"
    assert d.count(alvo) == 1, (c, d.count(alvo))
    i = d.find(alvo)
    d[i:i + 8] = b"ges01_00"
    nds_rom.substituir(rom, c, bytes(d))
open("/ds/rom/ta_esgoto.nds", "wb").write(rom)
print("ok")
