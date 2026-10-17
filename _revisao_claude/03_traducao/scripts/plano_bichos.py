"""PLANO do hack "bichos -> universo DB": fonte unica de verdade.

Cada linha de enemy_param (um bicho) recebe:
  sprite:  arquivo .chr + paleta (existente ou NOVA, gerada aqui)
  modelo:  de onde vem tamanho/sombra/pesos de ataque do sprite
           ("e<linha>" = enemy_param, "b<linha>" = boss_param)
  nome:    nome novo em PT-BR (com acento: latin0/latin1.fnt tem o Latin-1 completo, testado em batalha)
Balanceamento (nivel, HP, forca, EXP, drops, resistencias) fica o do bicho.

Paletas novas:
  ene001_01 (Saibaman, 5 paletas originais) ganha variantes por giro do tom
  do corpo (cores 7-10 e 13-15); olhos/contorno/dentes ficam.
  ene200_01 (Soldado Saiyajin, montado de ene220_01) tem so paletas novas.
"""
import colorsys

from chr_paletas import rgb555

SAIBA, SOLDADO = "ene001_01", "ene200_01"

# ---------------- paletas novas ----------------
def _hsv(c):
    return colorsys.rgb_to_hsv((c & 31) / 31, (c >> 5 & 31) / 31, (c >> 10 & 31) / 31)


def _rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return rgb555(round(r * 31), round(g * 31), round(b * 31))


def saiba_var(p0, tom, sat=1.0, luz=1.0):
    """tom em graus; sat/luz multiplicam saturacao/brilho do corpo."""
    p = list(p0)
    for i in (7, 8, 9, 10, 13, 14, 15):
        h, s, v = _hsv(p0[i])
        p[i] = _rgb((tom % 360) / 360, min(1, s * sat), min(1, v * luz))
    return p


SAIBA_NOVAS = {  # nome da paleta: (tom, sat, luz)
    "areia": (38, 0.8, 1.0),        # Saibaman Escavador
    "noite": (230, 0.8, 0.8),       # Saibaman Noturno
    "veneno": (285, 0.9, 0.95),     # Saibaman Venenoso
    "areia_clara": (45, 0.45, 1.1),   # Broto Escavador
    "noite_clara": (215, 0.45, 1.1),  # Broto Noturno
    "veneno_claro": (300, 0.45, 1.1), # Broto Venenoso
    "rubro": (0, 1.0, 0.95),        # Saibaman Rubro (Red Wolf)
    "neve": (195, 0.5, 1.15),        # Saibaman das Neves / da Nevasca
}

# soldado: (realce, meio, sombra, sombra funda) da armadura + lente
def _tons(r, g, b):
    base = (r, g, b)
    f = lambda k: tuple(max(0, min(31, round(x * k))) for x in base)
    return [f(1.15), f(1.0), f(0.62), f(0.35)]


SOLDADO_VAR = {  # cor da armadura (ombreiras/abas/botas) e da lente
    "rosa": ((28, 10, 20), (31, 10, 22)),
    "amarelo": ((29, 25, 4), (31, 29, 4)),
    "preto": ((7, 7, 9), (20, 20, 24)),
    "laranja": ((30, 15, 2), (31, 20, 4)),
    "branco": ((26, 26, 28), (12, 24, 31)),
    "roxo": ((18, 7, 26), (26, 12, 31)),
    "marrom": ((18, 11, 5), (31, 22, 8)),
    "vermelho": ((28, 4, 4), (31, 8, 8)),
    "gelo": ((12, 22, 31), (20, 28, 31)),
}


def soldado_var(p_raditz, nome):
    p = list(p_raditz)
    p[2] = rgb555(5, 5, 6)      # cabelo preto
    p[15] = rgb555(4, 6, 14)    # macacao azul
    armadura, lente = SOLDADO_VAR[nome]
    realce, meio, sombra, funda = _tons(*armadura)
    p[13], p[6], p[7], p[12] = rgb555(*realce), rgb555(*meio), rgb555(*sombra), rgb555(*funda)
    p[14] = rgb555(*lente)
    return p


# ---------------- a tabela ----------------
# linha: (bicho original, sprite, paleta (int = existente, str = nova), modelo, nome novo)
PLANO = {
    # lobos -> Saibamen (cores originais)
    104: ("Wolf", SAIBA, 0, "e0", "Saibaman"),
    105: ("White Wolf", SAIBA, 1, "e1", "Saibaman Glacial"),
    106: ("Red Wolf", SAIBA, "rubro", "e2", "Saibaman Rubro"),
    # ursos -> Saibamen
    113: ("Hungry Bear", SAIBA, 0, "e0", "Saibaman Faminto"),
    114: ("Snow Bear", SAIBA, "neve", "e4", "Saibaman das Neves"),
    115: ("Strong Bear", SAIBA, 3, "e3", "Saibaman Feroz"),
    # pandas -> Saibamen
    116: ("Dangerous Panda", SAIBA, 0, "e0", "Saibaman do Bambu"),
    117: ("Snow Panda", SAIBA, "neve", "e4", "Saibaman da Nevasca"),
    118: ("Ultimate Pandaman", SAIBA, 3, "e3", "Saibaman Supremo"),
    # insetos e larvas -> Saibamen de cores novas
    155: ("Roundworm", SAIBA, "areia", "e0", "Saibaman Escavador"),
    156: ("Dark Firefly", SAIBA, "noite", "e0", "Saibaman Noturno"),
    157: ("Poison Sandbug", SAIBA, "veneno", "e0", "Saibaman Venenoso"),
    161: ("Roundworm Larva", SAIBA, "areia_clara", "e0", "Broto Escavador"),
    162: ("Firefly Larva", SAIBA, "noite_clara", "e0", "Broto Noturno"),
    163: ("Sandbug Larva", SAIBA, "veneno_claro", "e0", "Broto Venenoso"),
    # avestruz/dodo -> Soldado Saiyajin nas cores das aves
    95: ("Ostrich Chicken", SOLDADO, "rosa", "b13", "Batedor Saiyajin"),
    96: ("Sand Dodo", SOLDADO, "amarelo", "b13", "Batedor do Deserto"),
    97: ("Dododo", SOLDADO, "preto", "b13", "Elite Saiyajin"),
    # tigres -> Soldado Saiyajin
    101: ("Tiger", SOLDADO, "laranja", "b13", "Soldado Saiyajin"),
    102: ("Snow Tiger", SOLDADO, "branco", "b13", "Soldado Glacial"),
    103: ("Dimensional Tiger", SOLDADO, "roxo", "b13", "Soldado Dimensional"),
    # javalis -> Soldado Saiyajin
    110: ("Wild Boar", SOLDADO, "marrom", "b13", "Brutamontes Saiyajin"),
    111: ("Champion Boar", SOLDADO, "vermelho", "b13", "Brutamontes Campeão"),
    112: ("Snow Boar", SOLDADO, "gelo", "b13", "Brutamontes Glacial"),
    # caes -> soldado Red Ribbon (ene005)
    107: ("Stray Dog", "ene005_01", 0, "e14", "Desertor Red Ribbon"),
    108: ("Red Ribbon Spy Dog", "ene005_01", 0, "e15", "Espião Red Ribbon"),
    109: ("Super Watchdog", "ene005_01", 2, "e16", "Sentinela Red Ribbon"),
    # lagartas -> soldado Red Ribbon (ene006)
    149: ("Tumble Bug", "ene006_01", 0, "e17", "Recruta Red Ribbon"),
    150: ("Fire Caterpillar", "ene006_01", 1, "e18", "Recruta Incendiário"),
    151: ("Caterpillar", "ene006_01", 2, "e19", "Recruta Veterano"),
    # morcegos -> Vampiro (lutador da Vovo Uranai)
    131: ("Giant Bat", "ene045_01", 0, "e125", "Vampiro"),
    132: ("Vampire Bat", "ene045_01", 1, "e126", "Vampiro Sanguinário"),
    133: ("King Bat", "ene045_01", 2, "e127", "Rei Vampiro"),
    # caranguejos -> Grupo do Coelho
    134: ("Big Crab", "ene016_01", 0, "e44", "Capanga"),
    135: ("Giant Crab", "ene016_01", 1, "e45", "Capanga Gigante"),
    136: ("Dark Crab", "ene016_01", 2, "e46", "Capanga Sombrio"),
    # cobras -> servos da Princesa Serpente
    80: ("Giant Snake", "ene022_01", 0, "e59", "Serva da Princesa"),
    81: ("Mansion Snake", "ene022_01", 2, "e60", "Guarda da Mansão"),
    82: ("Poisonous Snake", "ene022_01", 2, "e61", "Serva Venenosa"),
    # aves de rapina -> piloto Red Ribbon (ene003, tamanho 2: aves vem sozinhas)
    98: ("Firebird", "ene003_01", 0, "e8", "Aviador Red Ribbon"),
    99: ("Blue Hawk", "ene003_01", 1, "e9", "Aviador Azul RR"),
    100: ("Dark Condor", "ene003_01", 2, "e10", "Aviador Sombrio RR"),
    # peixes -> robo da Caverna dos Piratas (tamanho 2)
    119: ("Giant Fish", "ene002_01", 0, "e5", "Robô Pirata"),
    120: ("Wild Fish", "ene002_01", 0, "e6", "Robô Pirata Selvagem"),
    121: ("Sand Fish", "ene002_01", 2, "e7", "Robô Pirata das Areias"),
    # dragoes -> robo Red Ribbon (ene004, tamanho 2)
    74: ("Winged Dragon", "ene004_01", 0, "e11", "Robô Alado RR"),
    75: ("Violent Dragon", "ene004_01", 1, "e12", "Robô de Assalto RR"),
    76: ("Snow Dragon", "ene004_01", 2, "e13", "Robô Ártico RR"),
}
