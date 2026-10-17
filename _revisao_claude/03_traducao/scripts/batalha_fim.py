"""Refaz a batalha de ab_batalha.py e joga ATE O FIM (ataca com A), tirando
fotos da tela de resultados e da de subida de nivel.
uso: batalha_fim.py <estado_pre> <passo> <semente> <saida_dir> <rom>
env: SALVA_EM=i salva o estado no toque i; PARA=1 encerra logo depois"""
import os
import random
import sys

import numpy as np

sys.path.insert(0, "/ds/scripts")
from ds import DS

src = open("/ds/scripts/piloto.py").read()
exec(src[src.index("def no_campo"):src.index("n_bat = 0")])

PRE, PASSO, SEM, OUT, ROM = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
os.makedirs(OUT, exist_ok=True)
DIRS = ["up", "up+right", "right", "down+right", "down", "down+left", "left", "up+left"]
random.seed(SEM)
d = random.choice(DIRS)
for p in range(1, PASSO + 1):
    if random.random() < 0.35:
        d = random.choice(DIRS)
    q = random.choice([20, 40, 60])

with DS(ROM) as ds:
    ds.espera(5)
    ds.carregar(open(PRE, "rb").read())
    ds.aperta(*d.split("+"), segura=q, depois=2)
    for _ in range(600):
        if em_batalha(ds.tela()):
            break
        ds.espera(1)
    else:
        sys.exit("nao entrou em batalha")
    n = 0
    lv = 0
    for i in range(700):
        t = ds.tela()
        if i == int(os.environ.get("SALVA_EM", "-1")):
            open(f"{OUT}/estado_{i}.bin", "wb").write(ds.salvar())
            if os.environ.get("PARA"):
                break
        if i % 6 == 0 or i > 55:
            t.save(f"{OUT}/f{n:03d}.png")
            n += 1
        if no_level_up(t):
            t.save(f"{OUT}/levelup{lv}.png")
            lv += 1
            for _ in range(4):
                ds.aperta("right", segura=4, depois=8)
            ds.aperta("a", segura=6, depois=20)
            ds.aperta("up", segura=6, depois=10)
            ds.aperta("a", segura=6, depois=30)
            continue
        if i > 40 and no_campo(t):
            t.save(f"{OUT}/campo.png")
            print("voltou ao campo apos", i, "toques")
            break
        ds.aperta("a", segura=6, depois=18)
    print(n, "fotos,", lv, "telas de nivel")
