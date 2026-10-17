"""A/B de uma batalha aleatoria: parte do estado de ANTES do passo que
disparou a batalha no explorador.py, refaz exatamente aquele passo (direcao
e duracao recalculadas a partir da semente) e captura a batalha em cada ROM.

uso: ab_batalha.py <estado_pre> <passo> <semente> <saida_dir> <rom1> [rom2 ...]
Saidas: <saida>/<nome_rom>_{inicio,alvo}.png
"""
import os
import random
import sys

import numpy as np

sys.path.insert(0, "/ds/scripts")
from ds import DS

src = open("/ds/scripts/piloto.py").read()
exec(src[src.index("def no_campo"):src.index("n_bat = 0")])

PRE, PASSO, SEM, OUT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
ROMS = sys.argv[5:]
os.makedirs(OUT, exist_ok=True)
DIRS = ["up", "up+right", "right", "down+right", "down", "down+left", "left", "up+left"]

# refaz a sequencia de sorteios do explorador.py ate o passo pedido
random.seed(SEM)
d = random.choice(DIRS)
for p in range(1, PASSO + 1):
    if random.random() < 0.35:
        d = random.choice(DIRS)
    q = random.choice([20, 40, 60])
print(f"passo {PASSO}: direcao {d}, {q} quadros")

est = open(PRE, "rb").read()
for rom in ROMS:
    nome = os.path.basename(rom)[:-4]
    with DS(rom) as ds:
        ds.espera(5)
        ds.carregar(est)
        ds.aperta(*d.split("+"), segura=q, depois=2)
        for _ in range(600):
            if em_batalha(ds.tela()):
                break
            ds.espera(1)
        else:
            print(nome, ": nao entrou em batalha")
            continue
        ds.espera(40)
        ds.tela().save(f"{OUT}/{nome}_inicio.png")
        # espera a roda de comandos e escolhe Ataque -> aparece o nome do alvo
        for _ in range(40):
            ds.aperta("a", segura=6, depois=24)
            t = np.asarray(ds.tela())
            # etiqueta do alvo: caixa laranja no alto da tela de cima
            if t[8:20, 90:170].reshape(-1, 3).mean(0)[0] > 150 and \
               t[8:20, 90:170].reshape(-1, 3).mean(0)[2] < 120:
                break
        ds.tela().save(f"{OUT}/{nome}_alvo.png")
        print(nome, ": ok")
