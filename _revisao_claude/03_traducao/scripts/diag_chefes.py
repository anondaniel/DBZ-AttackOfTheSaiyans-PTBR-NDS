"""DIAGNOSTICO (nao e entrega): um sprite de CHEFE aceita ser usado na
tabela de inimigos comuns?

Palco: a batalha real de 1 lobo no Monte Paozu (pz5/p0027_pre.bin, refeita
passo a passo como no ab_batalha.py). Na ROM original, a linha 104 (Wolf)
recebe do chefe: file, palno, size, shadow, name_id e os pesos de ataque
atk1-4 (os 4 primeiros do chefe, renormalizados para somar 100).
HP vai para 3000 SO nesta ROM, para o inimigo sobreviver e atacar.

Captura: inicio, etiqueta do alvo e ~40 s de luta (quadros a cada 90).
Acusa travamento se a tela ficar identica por muito tempo.

uso: diag_chefes.py [linhas_boss_param separadas por virgula]
"""
import os
import random
import sys

import numpy as np

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import gravar_num, gravar_str_mesmo_tamanho, ler_num, tabelas_com_offset
from ds import DS

src = open("/ds/scripts/piloto.py").read()
exec(src[src.index("def no_campo"):src.index("n_bat = 0")])

ORIG = "/ds/rom/aots.nds"
PRE, PASSO, SEM = "/ds/saida/pz5/p0027_pre.bin", 27, 3
OUT = "/ds/saida/diag_chefes"
CHEFES = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [13, 37, 39, 5, 42]
os.makedirs(OUT, exist_ok=True)


def monta(boss, saida):
    rom = bytearray(open(ORIG, "rb").read())
    for lang in ["EN", "US", "FR", "SP", "GR", "IT"]:
        c = f"btl/bdat/{lang}/bdat.bin"
        b = bytearray(nds_rom.ler(rom, c))
        tabs = tabelas_com_offset(b)
        ep, bp = tabs["enemy_param"], tabs["boss_param"]
        arq = bp["linhas"][boss]["file"]
        gravar_str_mesmo_tamanho(b, ep, 104, "file", arq)
        for col in ("palno", "size", "shadow", "name_id"):
            gravar_num(b, ep, 104, col, ler_num(b, bp, boss, col))
        pesos = [ler_num(b, bp, boss, f"atk{k}") for k in range(1, 5)]
        tot = sum(pesos) or 1
        pesos = [round(p * 100 / tot) for p in pesos]
        pesos[0] += 100 - sum(pesos)
        for k, p in enumerate(pesos, 1):
            gravar_num(b, ep, 104, f"atk{k}", p)
        gravar_num(b, ep, 104, "hp", 3000)
        nds_rom.substituir(rom, c, bytes(b))
        if lang == "EN":
            nomes = [l["en"] for l in tabs["character_name"]["linhas"]]
            nome = nomes[ler_num(b, bp, boss, "name_id") - 1]
    open(saida, "wb").write(rom)
    return nome, arq, pesos


DIRS = ["up", "up+right", "right", "down+right", "down", "down+left", "left", "up+left"]
random.seed(SEM)
d = random.choice(DIRS)
for p in range(1, PASSO + 1):
    if random.random() < 0.35:
        d = random.choice(DIRS)
    q = random.choice([20, 40, 60])

est = open(PRE, "rb").read()
for boss in CHEFES:
    rom = f"/ds/rom/diag_chefe_{boss}.nds"
    nome, arq, pesos = monta(boss, rom)
    tag = f"{boss:02d}_{arq}"
    with DS(rom) as ds:
        ds.espera(5)
        ds.carregar(est)
        ds.aperta(*d.split("+"), segura=q, depois=2)
        for _ in range(600):
            if em_batalha(ds.tela()):
                break
            ds.espera(1)
        else:
            print(f"{boss} {nome} ({arq}): NAO ENTROU EM BATALHA")
            ds.tela().save(f"{OUT}/{tag}_falhou.png")
            continue
        ds.espera(40)
        ds.tela().save(f"{OUT}/{tag}_inicio.png")
        ds.aperta("a", segura=6, depois=30)
        ds.tela().save(f"{OUT}/{tag}_alvo.png")
        anterior, parado, n = None, 0, 0
        fim = "luta seguiu 40 s"
        for k in range(27):
            for _ in range(3):
                ds.aperta("a", segura=6, depois=24)
            t = ds.tela()
            n += 1
            t.save(f"{OUT}/{tag}_q{n:02d}.png")
            a = np.asarray(t)
            if anterior is not None and np.array_equal(a, anterior):
                parado += 1
                if parado >= 4:
                    fim = "TRAVOU (tela identica por 4 capturas)"
                    break
            else:
                parado = 0
            anterior = a
            if no_campo(t) or no_level_up(t):
                fim = f"batalha terminou (captura {n})"
                break
    os.remove(rom)
    print(f"{boss} {nome} ({arq}) pesos={pesos}: {fim}")
