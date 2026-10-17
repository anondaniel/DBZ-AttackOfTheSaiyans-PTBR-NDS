"""Gera ROM de TESTE (nao e entrega) liberando locais no mapa-mundi.
Mesma tecnica de 11_Projeto_Recuperado/scripts/teste_atalho_mapas.py, so muda caminhos.
uso: python liberar_mapas.py <rom_base> <saida> mapa1,mapa2,..."""
import re, struct, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import nds_rom

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

BASE, SAIDA, MAPAS = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
PORTAO = re.compile(rb"(?:\x14.|\x15..)\x0e\x42\x00(.)", re.S)
rom = bytearray(open(BASE, "rb").read())
for c in [c for c in nds_rom.caminhos(rom) if c.endswith("/cf/worldmap.sb")]:
    d = bytearray(nds_rom.ler(rom, c))
    idx = strings(d)
    ok = []
    for mapa in MAPAS:
        if mapa not in idx:
            print("sem", mapa, c); continue
        alvo = bytes([0x26, idx[mapa]])
        p_str = d.find(alvo)
        if p_str == -1 or d.find(alvo, p_str + 1) != -1:
            print("ambiguo", mapa, c); continue
        ini = p_str - 0x60
        testes = list(PORTAO.finditer(bytes(d[ini:p_str])))
        if not testes:
            print("portao nao achado", mapa, c); continue
        j = ini + testes[-1].start(1)
        if d[j]:
            d[j] = 0
        ok.append(mapa)
    nds_rom.substituir(rom, c, bytes(d))
    print(c, "liberados:", ",".join(ok))
open(SAIDA, "wb").write(rom)
print("ROM:", SAIDA)
