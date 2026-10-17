"""Paletas do SOLDADO SAIYAJIN generico, a partir do sprite do Raditz.

Mapa de cores do ene220_01 (diag_paleta.py + quadro_indices.py):
  1 contorno/fios escuros | 2 cabelo | 3,4 cinzas (botas) | 5 branco
  6,7,12,13 dourado = OMBREIRAS e abas do quadril (o peito e escuro)
  8 vermelho | 9,10,11 pele | 14 lente do scouter | 15 cinza escuro

Soldado: cabelo preto, macacao azul; 3 variantes com a cor da ave que
substitui (rosa/amarelo/preto) nas ombreiras (+ abas) e na lente.
"""
from chr_paletas import rgb555

VARIANTES = {  # realce(13), meio(6), sombra(7), sombra funda(12), lente(14)
    "rosa": [(31, 20, 27), (28, 10, 20), (18, 5, 13), (10, 3, 8), (31, 10, 22)],
    "amarelo": [(31, 31, 14), (29, 25, 4), (20, 16, 2), (11, 9, 1), (31, 29, 4)],
    "preto": [(12, 12, 14), (7, 7, 9), (4, 4, 6), (2, 2, 3), (20, 20, 24)],
}


def soldado(orig, variante):
    p = list(orig)
    p[2] = rgb555(5, 5, 6)      # cabelo preto
    p[15] = rgb555(4, 6, 14)    # cinza escuro -> azul escuro
    realce, meio, sombra, funda, lente = VARIANTES[variante]
    p[13], p[6], p[7], p[12], p[14] = (rgb555(*realce), rgb555(*meio), rgb555(*sombra),
                                       rgb555(*funda), rgb555(*lente))
    return p
