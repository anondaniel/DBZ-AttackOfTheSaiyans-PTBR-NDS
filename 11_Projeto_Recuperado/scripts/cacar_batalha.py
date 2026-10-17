"""Anda de um lado para o outro ate a tela de baixo deixar de ser a do
campo (barra laranja "Capsule help display"), ou seja, ate entrar numa
batalha. Salva quadros da entrada da batalha e o save state.

uso: cacar_batalha.py <rom> <estado_inicial> <saida> [max_passos]
"""
import os
import sys

import numpy as np

sys.path.insert(0, "/ds/scripts")
from ds import DS

ROM, INI, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
MAX = int(sys.argv[4]) if len(sys.argv) > 4 else 300
os.makedirs(OUT, exist_ok=True)


def no_campo(img):
    # faixa inferior da tela de baixo (y 372-383): laranja no campo
    a = np.asarray(img)[372:384, 60:200].reshape(-1, 3).mean(0)
    r, g, b = a
    return r > 180 and 100 < g < 200 and b < 90


with DS(ROM) as ds:
    ds.espera(5)
    ds.carregar(open(INI, "rb").read())
    ds.espera(10)
    assert no_campo(ds.tela()), "estado inicial nao esta no campo"
    dirs = ["right", "left"]
    for passo in range(MAX):
        d = dirs[(passo // 12) % 2]
        ds.aperta(d, segura=20, depois=2)
        if not no_campo(ds.tela()):
            print(f"saiu do campo no passo {passo} (quadro {ds.quadro})")
            for i in range(12):
                ds.tela().save(f"{OUT}/b{i:02d}.png")
                ds.espera(30)
            open(f"{OUT}/estado.bin", "wb").write(ds.salvar())
            break
        if passo % 24 == 0:
            ds.tela().save(f"{OUT}/campo{passo:03d}.png")
    else:
        print("nenhuma batalha em", MAX, "passos")
