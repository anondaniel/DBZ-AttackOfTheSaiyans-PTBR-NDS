"""ROM de TESTE (nao e entrega): libera no mapa-mundi os locais pedidos,
achando sozinho o teste "GetMaxFlag(...) >= N ; jz +X" de cada um (mesma
ideia do teste_atalho_paozu.py, sem precisar anotar o N a mao).
Serve para ver falas de NPC de cidades sem jogar a historia ate la.

uso: teste_atalho_mapas.py <rom_base> <saida> <mapas separados por virgula>
  ex.: teste_atalho_mapas.py /ds/rom/aots_ptbr_img.nds /ds/rom/ta_cidades.nds wst01_00,est01_00"""
import re
import struct  # usado pela strings() copiada do teste_atalho_paozu.py
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

src = open("/ds/scripts/teste_atalho_paozu.py").read()
exec(src[src.index("def strings"):src.index("rom = bytearray")])

BASE, SAIDA, MAPAS = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
PORTAO = re.compile(rb"(?:\x14.|\x15..)\x0e\x42\x00(.)", re.S)

rom = bytearray(open(BASE, "rb").read())
for c in [c for c in nds_rom.caminhos(rom) if c.endswith("/cf/worldmap.sb")]:
    d = bytearray(nds_rom.ler(rom, c))
    idx = strings(d)
    for mapa in MAPAS:
        alvo = bytes([0x26, idx[mapa]])
        p_str = d.find(alvo)
        assert p_str != -1 and d.find(alvo, p_str + 1) == -1, (c, mapa)
        ini = p_str - 0x60
        testes = list(PORTAO.finditer(bytes(d[ini:p_str])))
        assert testes, f"{c} {mapa}: portao nao achado"
        j = ini + testes[-1].start(1)  # byte do deslocamento do ultimo salto antes do nome
        if d[j]:
            d[j] = 0
    nds_rom.substituir(rom, c, bytes(d))
    print(f"{c}: {len(MAPAS)} locais liberados")
open(SAIDA, "wb").write(rom)
print("ROM:", SAIDA)
