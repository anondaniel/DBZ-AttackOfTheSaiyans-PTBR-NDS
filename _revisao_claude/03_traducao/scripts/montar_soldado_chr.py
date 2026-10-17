"""Monta o .chr do SOLDADO SAIYAJIN e grava no lugar de ene200_01.chr
(inimigo cortado do jogo: so a tabela de nomes de arquivo o cita).

  base: ene220_01.chr (Raditz) -> tiles com a juba cortada (cortar_juba.py)
        + 3 paletas (rosa, amarelo, preto) de soldado_paletas.py
  ene220_01.chr do chefe Raditz NAO e tocado.

soldado_chr(rom) -> bytes;  instalar(rom_bytearray) -> descricao
"""
import pickle
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from chr_paletas import com_paletas, paletas
from dump_tiles import ler_chr
from soldado_paletas import soldado

ORIGEM, DESTINO = "btl/ene/ene220_01.chr", "btl/ene/ene200_01.chr"
TILES = "/ds/saida/juba/tiles_novos.pkl"


def soldado_chr(rom):
    d = bytearray(nds_rom.ler(rom, ORIGEM))
    c = ler_chr(bytes(d))
    novos = pickle.load(open(TILES, "rb"))
    assert len(novos) == len(c["tiles"])
    ini = 8 + d[5] * 32
    d[ini:ini + len(novos) * 32] = b"".join(novos)
    p0 = paletas(bytes(d))[0]
    return com_paletas(bytes(d), [soldado(p0, v) for v in ("rosa", "amarelo", "preto")])


def instalar(rom):
    antes = nds_rom.ler(rom, ORIGEM)
    acao = nds_rom.substituir(rom, DESTINO, soldado_chr(rom))
    assert nds_rom.ler(rom, ORIGEM) == antes, "o chr do Raditz mudou!"
    return acao


if __name__ == "__main__":
    rom = bytearray(open("/ds/rom/aots.nds", "rb").read())
    print(instalar(rom))
