"""Refaz a batalha gravada (como ab_batalha.py) e executa uma sequencia de
botoes, fotografando a cada passo. Para ver fuga/derrota.
uso: batalha_teste.py <estado_pre> <passo> <semente> <saida_dir> <rom> "<seq>"
  seq: tokens BOTAO[xN][:espera] (como explorar.py), ex.: "rightx3:20 a:40"
env: SALVA_TUDO=1 fotografa todo toque (senao a cada 3)"""
import os
import random
import sys

import numpy as np

sys.path.insert(0, "/ds/scripts")
from ds import DS

src = open("/ds/scripts/piloto.py").read()
exec(src[src.index("def no_campo"):src.index("n_bat = 0")])

PRE, PASSO, SEM, OUT, ROM, SEQ = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6]
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
    ds.espera(60)
    n = 0
    ds.tela().save(f"{OUT}/s{n:03d}.png")
    for tok in SEQ.split():
        espera = 30
        if ":" in tok:
            tok, e = tok.split(":")
            espera = int(e)
        vezes = 1
        if "x" in tok[1:]:
            tok, v = tok.rsplit("x", 1)
            vezes = int(v)
        for _ in range(vezes):
            if tok == "nada":
                ds.espera(espera)
            else:
                ds.aperta(*tok.split("+"), segura=6, depois=espera)
            n += 1
            ds.tela().save(f"{OUT}/s{n:03d}.png")
    print(n, "passos")
