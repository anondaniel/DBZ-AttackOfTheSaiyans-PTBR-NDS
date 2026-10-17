"""Troca/adiciona paletas num .chr (dCHR).

  0x05 u8 n_paletas; paletas de 32 bytes a partir de 0x08; o resto do
  arquivo (tiles + tabela de quadros) vem logo depois e usa offsets
  relativos, entao inserir paletas so empurra esse bloco.

com_paletas(d, paletas) -> novo .chr com exatamente essas paletas
rgb555(r, g, b) com r,g,b em 0..31
"""
import struct


def rgb555(r, g, b):
    return r | (g << 5) | (b << 10)


def paletas(d):
    assert d[:4] == b"dCHR"
    return [list(struct.unpack_from("<16H", d, 8 + p * 32)) for p in range(d[5])]


def com_paletas(d, novas):
    assert d[:4] == b"dCHR" and 1 <= len(novas) <= 16
    velhas = d[5]
    corpo = d[8 + velhas * 32:]
    cab = bytearray(d[:8])
    cab[5] = len(novas)
    pal = b"".join(struct.pack("<16H", *p) for p in novas)
    return bytes(cab) + pal + corpo
