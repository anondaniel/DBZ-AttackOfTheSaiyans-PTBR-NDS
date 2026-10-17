"""Joga a partir de um estado e FOTOGRAFA cada caixa de dialogo:
  - caixa de dialogo na tela de cima: espera o texto parar de ser escrito,
    salva, aperta A
  - batalha: A+R ate acabar (sem fotografar)
  - level-up: distribui pontos e confirma (como o piloto.py)
  - campo: anda direita/esquerda para disparar eventos
Para depois de N caixas ou de M passos.
uso: ler_dialogos.py <rom> <estado> <saida> [n_caixas=20] [passos=600]
"""
import os
import sys

import numpy as np

sys.path.insert(0, "/ds/scripts")
from ds import DS

src = open("/ds/scripts/piloto.py").read()
exec(src[src.index("def no_campo"):src.index("n_bat = 0")])

ROM, INI, OUT = sys.argv[1:4]
N = int(sys.argv[4]) if len(sys.argv) > 4 else 20
M = int(sys.argv[5]) if len(sys.argv) > 5 else 600
os.makedirs(OUT, exist_ok=True)


def caixa(img):
    a = np.asarray(img)[175:185, 200:250].reshape(-1, 3).astype(int)
    r, g, b = a.mean(0)
    return abs(r - 58) < 12 and abs(g - 50) < 12 and abs(b - 55) < 12 and a.std(0).max() < 14


with DS(ROM) as ds:
    ds.espera(5)
    ds.carregar(open(INI, "rb").read())
    ds.espera(10)
    n, lado = 0, 0
    for passo in range(M):
        t = ds.tela()
        if caixa(t):
            # espera o texto terminar de ser escrito (tela estavel)
            ant = None
            for _ in range(40):
                ds.espera(8)
                a = np.asarray(ds.tela())[100:192]
                if ant is not None and np.array_equal(a, ant):
                    break
                ant = a
            n += 1
            ds.tela().save(f"{OUT}/c{n:02d}.png")
            if n >= N:
                break
            ds.aperta("a", segura=6, depois=20)
        elif em_batalha(t):
            ds.aperta("a", "r", segura=8, depois=16)
        elif no_level_up(t):
            for _ in range(4):
                ds.aperta("right", segura=4, depois=8)
            ds.aperta("a", segura=6, depois=20)
            ds.aperta("up", segura=6, depois=10)
            ds.aperta("a", segura=6, depois=30)
        elif no_campo(t):
            lado += 1
            ds.aperta("right" if (lado // 12) % 2 == 0 else "left", segura=20, depois=2)
        else:
            ds.aperta("a", segura=6, depois=20)
    open(f"{OUT}/estado.bin", "wb").write(ds.salvar())
    print(f"{n} caixas fotografadas em {passo + 1} passos")
