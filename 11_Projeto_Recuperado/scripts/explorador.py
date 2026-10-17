"""Exploracao automatica: passeio aleatorio com passos longos, resolvendo
batalhas/dialogos/level-up (mesmas regras do piloto.py). Registra toda
troca de mapa (tela de cima fica preta) e para no mapa-mundi, num quadro
de batalha contra alvo (env ALVO_BATALHA=1) ou no limite de passos.

uso: explorador.py <rom> <estado> <saida> [passos=300] [semente=1]
"""
import os
import random
import sys

import numpy as np

sys.path.insert(0, "/ds/scripts")
from ds import DS

src = open("/ds/scripts/piloto.py").read()
exec(src[src.index("def no_campo"):src.index("n_bat = 0")])

ROM, INI, OUT = sys.argv[1:4]
PASSOS = int(sys.argv[4]) if len(sys.argv) > 4 else 300
random.seed(int(sys.argv[5]) if len(sys.argv) > 5 else 1)
os.makedirs(OUT, exist_ok=True)
DIRS = ["up", "up+right", "right", "down+right", "down", "down+left", "left", "up+left"]


def preta(img):
    return np.asarray(img)[0:192].mean() < 8


def resolve(ds, tag):
    """sai de batalha/dialogo/level-up; devolve 'mapa' se cair no mapa-mundi"""
    guard = 0
    bat = False
    while not no_campo(ds.tela()) and guard < 600:
        t = ds.tela()
        if no_mapa_mundi(t):
            return "mapa"
        if em_batalha(t) and not bat:
            ds.espera(40)
            t2 = ds.tela()
            # confirma: ainda batalha e tela de cima acesa (transicao de mapa
            # tambem pode piscar azul)
            if not (em_batalha(t2) and np.asarray(t2)[0:192].mean() > 30):
                guard += 1
                continue
            bat = True
            t2.save(f"{OUT}/{tag}_bat.png")
            if os.environ.get("PARAR_NA_BATALHA") == "1":
                return "bat"
        if no_level_up(t):
            for _ in range(4):
                ds.aperta("right", segura=4, depois=8)
            ds.aperta("a", segura=6, depois=20)
            ds.aperta("up", segura=6, depois=10)
            ds.aperta("a", segura=6, depois=30)
        elif preta(t):
            ds.espera(20)
        else:
            ds.aperta("a", "r", segura=8, depois=16)
        guard += 1
    return "travou" if guard >= 600 else ("bat" if bat else "ok")


with DS(ROM) as ds:
    ds.espera(5)
    ds.carregar(open(INI, "rb").read())
    ds.espera(10)
    d = random.choice(DIRS)
    trocas = 0
    n_bat = 0
    MAX_BAT = int(os.environ.get("MAX_BAT", "0"))
    for p in range(1, PASSOS + 1):
        if random.random() < 0.35:
            d = random.choice(DIRS)
        pre = ds.salvar()  # estado de antes do passo (para A/B entre ROMs)
        ds.aperta(*d.split("+"), segura=random.choice([20, 40, 60]), depois=2)
        t = ds.tela()
        if not no_campo(t) and not no_mapa_mundi(t):
            # pode ser entrada de batalha: guarda o estado de antes
            open(f"{OUT}/p{p:04d}_pre.bin", "wb").write(pre)
        if preta(t):
            ds.espera(60)
            trocas += 1
            ds.tela().save(f"{OUT}/troca{trocas:02d}_p{p:04d}.png")
            open(f"{OUT}/troca{trocas:02d}.bin", "wb").write(ds.salvar())
            print(f"troca de mapa {trocas} no passo {p} (dir {d})")
        r = resolve(ds, f"p{p:04d}")
        if r == "bat":
            n_bat += 1
            print(f"batalha {n_bat} no passo {p}")
            if (MAX_BAT and n_bat >= MAX_BAT) or os.environ.get("PARAR_NA_BATALHA") == "1":
                open(f"{OUT}/estado.bin", "wb").write(ds.salvar())
                print("parou apos", n_bat, "batalhas")
                sys.exit(0)
        if r == "mapa":
            ds.tela().save(f"{OUT}/mapa_mundi.png")
            open(f"{OUT}/estado.bin", "wb").write(ds.salvar())
            print(f"MAPA-MUNDI no passo {p}")
            sys.exit(0)
        if r == "travou":
            ds.tela().save(f"{OUT}/travou.png")
            open(f"{OUT}/estado.bin", "wb").write(ds.salvar())
            print(f"travou no passo {p}")
            sys.exit(1)
        if p % 25 == 0:
            ds.tela().save(f"{OUT}/p{p:04d}.png")
    open(f"{OUT}/estado.bin", "wb").write(ds.salvar())
    ds.tela().save(f"{OUT}/final.png")
    print(f"fim: {PASSOS} passos, {trocas} trocas de mapa")
