"""ROM de TESTE (nao e entrega): parte de uma ROM do hack e libera icones
do mapa-mundi antes da hora, para ir aos mapas dos bichos sem jogar a
historia inteira.

No worldmap.sb cada local comeca com
    GetMaxFlag(...) >= N ; jz +X      (<push N> 0e 42 00 XX)
que pula o bloco enquanto a historia nao chegou la. Trocar o salto por
jz +0 faz o script sempre seguir para o SetClickPoint, com as coordenadas
de entrada DO PROPRIO local. Os encontros la sao os do proprio jogo.

O salto corrigido e o ULTIMO "<push N> 0e 42 00 XX" antes do push da
string do mapa (26 <indice>), para nao pegar outro local com o mesmo teste.

uso: teste_atalho_paozu.py [rom_base] [saida] [mapas separados por virgula]
"""
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

BASE = sys.argv[1] if len(sys.argv) > 1 else "/ds/rom/aots_lobos_saibaman.nds"
SAIDA = sys.argv[2] if len(sys.argv) > 2 else "/ds/rom/teste_atalho_paozu.nds"
PORTOES = {  # mapa: push do limite N (i8 14 xx / i16 15 hh ll)
    "pao01_00": "146e",    # Mt. Paozu, >= 110
    "pao08_00": "1501f0",  # East Mt. Paozu, >= 496
    "spi01_00": "150196",  # Spinach Wastes, >= 406
    "fur01_00": "150127",  # Mt. Frappe, >= 295
}
if len(sys.argv) > 3:
    PORTOES = {k: v for k, v in PORTOES.items() if k in sys.argv[3].split(",")}


def strings(d):
    offs = struct.unpack_from("<6I", d, 8)
    a2 = offs[2]
    hs, n = struct.unpack_from("<II", d, a2)
    base = a2 + hs + n * 4
    r = {}
    for i in range(n):
        so = struct.unpack_from("<I", d, a2 + hs + i * 4)[0]
        r[d[base + so:d.index(b"\x00", base + so)].decode("latin-1")] = i
    return r


rom = bytearray(open(BASE, "rb").read())
cam = nds_rom.caminhos(rom)
for c in [c for c in cam if c.endswith("/cf/worldmap.sb")]:
    d = bytearray(nds_rom.ler(rom, c))
    idx = strings(d)
    for mapa, limite in PORTOES.items():
        alvo = bytes([0x26, idx[mapa]])
        p_str = d.find(alvo)
        assert p_str != -1 and d.find(alvo, p_str + 1) == -1, (c, mapa)
        teste = bytes.fromhex(limite) + b"\x0e\x42\x00"
        p = d.rfind(teste, p_str - 0x60, p_str)
        assert p != -1, f"{c} {mapa}: portao nao achado"
        j = p + len(teste)  # byte do deslocamento do salto
        assert d[j] != 0, f"{c} {mapa}: ja neutralizado"
        d[j] = 0
    nds_rom.substituir(rom, c, bytes(d))
    print(f"{c}: {len(PORTOES)} portoes neutralizados")
open(SAIDA, "wb").write(rom)
print("ROM:", SAIDA)
