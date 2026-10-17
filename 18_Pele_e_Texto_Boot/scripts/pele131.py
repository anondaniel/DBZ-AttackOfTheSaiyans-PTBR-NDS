"""Etapa 18 (versao 13.1): tons de pele devolvidos aos inimigos humanos.

As paletas novas da etapa 13 (build.py, giro de matiz) pegaram tambem indices de
pele (sombra e meio-tom do rosto/maos) e o contorno geral, deixando rostos azuis,
verdes ou roxos. Aqui, para cada linha HUMANA corrigida, os indices de pele voltam
aos valores da paleta do jogo original que serviu de modelo (a mesma variante de
onde a paleta nova foi derivada). As cores da roupa ficam como na etapa 13.

Indices de pele por sprite: os que tem tom de pele nas 3 variantes originais e
que, no desenho (mapa de indices do quadro 0, conferido ampliado), caem no rosto,
nas maos/bracos e no contorno. O indice 1 e o contorno de todo o sprite; nas 3
variantes originais ele e sempre o mesmo marrom-escuro (9,7,4), ou seja, nao e
cor de roupa no desenho original.

PELE[linha] = (arquivo, paleta, {indice: (antes_rgb555, depois_rgb555)}, modelo_pal_original)
cores em (r, g, b) de 0..31.
"""

# indices de pele de cada sprite (conferidos no mapa de indices ampliado)
IDX_PELE = {
    'ene021_01': (1, 3, 4, 5),        # lutador de quimono: 3 luz, 4 meio-tom, 5 sombra (rosto, maos, cabelo escuro)
    'ene012_01': (1, 11, 12),         # mercenario de oculos: 11 sombra, 12 luz (rosto e bracos)
    'ene026_01': (1, 8, 9),           # guardiao/xama de cajado: 8 sombra, 9 luz (rosto e maos)
    'ene008_01': (1, 6, 7, 8),        # bandida de mangual: 6 sombra, 7 meio-tom, 8 luz (corpo todo)
    'ene020_01': (1, 3, 4, 5, 6),     # monge careca: 3 luz, 4 meio-tom, 5 sombra, 6 sombra escura (rosto/maos e vincos)
    'ene016_01': (1, 3, 4, 5),        # capanga de capuz de coelho: 3 luz, 4 meio-tom, 5 sombra
    'ene015_01': (1, 5, 6, 7, 8),     # lutador de faca: 5 sombra escura, 6 sombra, 7 meio-tom, 8 luz
    'ene014_01': (1, 5, 6, 7),        # pirata de cimitarra: 5 luz, 6 meio-tom, 7 sombra
}

# linha: (arquivo, paleta na ROM 13, paleta original usada como modelo, {indice: (antes, depois)})
PELE = {
    80:  ('ene021_01', 3, 0, {1: ((4, 4, 9), (9, 7, 4)), 4: ((6, 8, 23), (23, 15, 6)), 5: ((2, 3, 17), (17, 11, 2))}),
    101: ('ene021_01', 4, 0, {1: ((4, 9, 5), (9, 7, 4)), 4: ((6, 23, 9), (23, 15, 6)), 5: ((2, 17, 6), (17, 11, 2))}),
    111: ('ene021_01', 5, 1, {1: ((9, 4, 9), (9, 7, 4)), 4: ((21, 6, 23), (23, 15, 6)), 5: ((16, 2, 17), (17, 11, 2))}),
    115: ('ene021_01', 6, 2, {1: ((4, 4, 9), (9, 7, 4)), 4: ((8, 12, 27), (27, 17, 8)), 5: ((3, 5, 19), (19, 12, 3))}),
    95:  ('ene012_01', 3, 0, {1: ((4, 6, 9), (9, 7, 4)), 11: ((7, 15, 21), (21, 13, 7))}),
    104: ('ene012_01', 5, 0, {1: ((4, 9, 4), (9, 7, 4)), 11: ((10, 21, 7), (21, 13, 7))}),
    106: ('ene012_01', 6, 2, {1: ((4, 3, 6), (9, 7, 4)), 11: ((7, 6, 18), (25, 15, 9))}),
    157: ('ene012_01', 7, 1, {1: ((9, 4, 6), (9, 7, 4)), 11: ((25, 9, 19), (25, 15, 9))}),
    103: ('ene026_01', 3, 1, {1: ((5, 4, 9), (9, 7, 4)), 8: ((12, 15, 24), (24, 13, 12)), 9: ((20, 23, 31), (31, 21, 20))}),
    117: ('ene026_01', 4, 2, {1: ((4, 6, 9), (9, 7, 4)), 8: ((7, 14, 17), (17, 10, 7))}),
    114: ('ene008_01', 4, 2, {1: ((4, 8, 9), (9, 7, 4)), 6: ((4, 15, 15), (15, 8, 4)), 7: ((6, 17, 19), (19, 12, 6))}),
    161: ('ene008_01', 5, 0, {1: ((7, 4, 9), (9, 7, 4)), 6: ((11, 4, 23), (23, 11, 4)), 7: ((20, 10, 28), (28, 20, 10)),
                              8: ((27, 19, 30), (30, 27, 19))}),
    116: ('ene020_01', 3, 0, {1: ((5, 4, 9), (9, 7, 4)), 5: ((9, 6, 26), (26, 16, 6)), 6: ((4, 3, 21), (21, 10, 3))}),
    156: ('ene020_01', 4, 1, {1: ((4, 3, 6), (9, 7, 4)), 5: ((7, 4, 19), (26, 16, 6)), 6: ((3, 1, 11), (15, 9, 1))}),
    136: ('ene016_01', 5, 2, {1: ((3, 6, 4), (9, 7, 4)), 4: ((7, 20, 9), (28, 18, 10)), 5: ((4, 17, 4), (23, 10, 5))}),
    149: ('ene015_01', 4, 1, {1: ((5, 4, 9), (9, 7, 4)), 5: ((4, 3, 15), (15, 8, 3)), 6: ((7, 7, 19), (19, 11, 7)),
                              7: ((12, 9, 24), (24, 17, 9))}),
    163: ('ene014_01', 4, 2, {1: ((9, 4, 9), (9, 7, 4)), 7: ((14, 8, 16), (16, 11, 8))}),
}

# ajuste de ROUPA (nao de pele) para manter a distancia de paleta da etapa 13.
# 157 Batedor Venenoso (modelo 33, mesma imagem de 33 Batedor do Ermo): com a pele de volta, a
# distancia para a paleta da linha 33 caiu de 82 para 61 (limite do jogo inteiro: 80). O colete/calca
# (indices 9 e 10) passa de verde-azulado para verde-veneno (matiz -40 graus, saturacao x1,3,
# brilho x1,1); a menor distancia volta a 85. Mesmo mapa: 157 nao divide mapa com outra variante.
ROUPA = {
    157: ('ene012_01', 7, {9: ((8, 16, 15), (6, 18, 9)), 10: ((10, 21, 20), (7, 23, 11))}),
}

# linhas apontadas pela checagem automatica e deixadas como estao (motivo no RELATORIO)
MANTIDAS = {
    82: 'robô (Robô Sentinela, ene062_01): não tem pele',
    99: 'piloto do aerodeslizador (ene003_01) é um cão antropomórfico (focinho branco, pelo); as variantes originais já mudam a cor do pelo (verde-oliva, malva)',
    100: 'idem 99 (mesmo sprite ene003_01)',
    107: 'soldado-cão da Red Ribbon (ene005_01: focinho, orelhas caídas, cauda); as variantes originais já mudam a cor do pelo (marrom, lilás, bege)',
    121: 'robô-caveira (ene002_01): metal, não tem pele',
    134: 'humano, mas a pele (índices 3, 4, 5) é igual à do original; o índice 13 apontado é o couro do capuz/correia (roupa)',
    135: 'idem 134 (índices 3, 4, 5 iguais ao original; 13 é couro do capuz/correia)',
}


def rgb555(c):
    r, g, b = c
    return r | (g << 5) | (b << 10)
