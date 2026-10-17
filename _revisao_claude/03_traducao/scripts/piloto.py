"""Piloto automatico: anda numa sequencia de direcoes; se sair do campo
(batalha, dialogo, menu), aperta A+R ate voltar. Registra cada batalha
(primeiro quadro com a barra de comandos) e salva estado no fim.

uso: piloto.py <rom> <estado> <saida> "<dir>@<quadros>[:<vezes>] ..."
  ex.: "right@30:20 up@30:5"
env: PARA_EM_BATALHA=1 -> para no 1o quadro de batalha (para inspecionar)
"""
import os
import sys

import numpy as np

sys.path.insert(0, "/ds/scripts")
from ds import DS

ROM, INI, OUT, SEQ = sys.argv[1:5]
PARA = os.environ.get("PARA_EM_BATALHA") == "1"
os.makedirs(OUT, exist_ok=True)


def no_campo(img):
    # campo = botao vermelho (y~255) e verde (y~320) na tela de baixo;
    # dialogo tambem tem a barra laranja, mas nao tem esses dois botoes
    a = np.asarray(img).astype(int)
    r1, g1, b1 = a[245:265, 110:145].reshape(-1, 3).mean(0)
    r2, g2, b2 = a[310:330, 110:145].reshape(-1, 3).mean(0)
    return r1 > 180 and g1 < 130 and b1 < 130 and g2 > 140 and r2 < 140 and b2 < 140


def em_batalha(img):
    # tela de baixo de batalha: fundo azul forte no meio (roda de comandos
    # ou paineis dos personagens)
    a = np.asarray(img)[200:370, 0:8].reshape(-1, 3).mean(0)
    r, g, b = a
    return b > 150 and r < 100


def no_mapa_mundi(img):
    # moldura laranja lisa na borda esquerda da tela de cima
    m = np.asarray(img)[10:180, 1:3].reshape(-1, 3).astype(int)
    r, g, b = m.mean(0)
    return abs(r - 203) < 12 and abs(g - 130) < 12 and b < 30 and m.std(0).max() < 6


def no_level_up(img):
    # tela de baixo "BONUS POINTS": verde escuro no canto (27, 79, 12)
    r, g, b = np.asarray(img)[215:225, 5:25].reshape(-1, 3).astype(int).mean(0)
    return abs(r - 27) < 10 and abs(g - 79) < 10 and abs(b - 12) < 10


n_bat = 0
with DS(ROM) as ds:
    ds.espera(5)
    ds.carregar(open(INI, "rb").read())
    ds.espera(10)
    passo = 0
    for tok in SEQ.split():
        vezes = 1
        if ":" in tok:
            tok, v = tok.split(":")
            vezes = int(v)
        d, q = tok.split("@")
        for _ in range(vezes):
            passo += 1
            if d == "nada":
                ds.espera(int(q))
            elif no_campo(ds.tela()):
                ds.aperta(*d.split("+"), segura=int(q), depois=2)
            if passo % 10 == 0:
                ds.tela().save(f"{OUT}/p{passo:04d}.png")
            # fora do campo: resolve
            guard = 0
            while not no_campo(ds.tela()) and guard < 400:
                t = ds.tela()
                if no_mapa_mundi(t):
                    t.save(f"{OUT}/mapa_mundi.png")
                    open(f"{OUT}/estado.bin", "wb").write(ds.salvar())
                    print(f"mapa-mundi no passo {passo} (quadro {ds.quadro})")
                    sys.exit(0)
                if em_batalha(t) and guard == 0:
                    n_bat += 1
                    ds.espera(40)
                    ds.tela().save(f"{OUT}/bat{n_bat:02d}.png")
                    open(f"{OUT}/bat{n_bat:02d}.bin", "wb").write(ds.salvar())
                    print(f"batalha {n_bat} no passo {passo} (quadro {ds.quadro})")
                    if PARA:
                        open(f"{OUT}/estado.bin", "wb").write(ds.salvar())
                        sys.exit(0)
                if no_level_up(t):
                    # gasta os pontos de bonus no atributo selecionado e confirma
                    for _ in range(4):
                        ds.aperta("right", segura=4, depois=8)
                    ds.aperta("a", segura=6, depois=20)
                    # "Is this what you want?" abre com o cursor em No
                    ds.aperta("up", segura=6, depois=10)
                    ds.aperta("a", segura=6, depois=30)
                else:
                    ds.aperta("a", "r", segura=8, depois=16)
                guard += 1
            if guard >= 400:
                ds.tela().save(f"{OUT}/travou{passo:04d}.png")
                print("nao voltou ao campo no passo", passo)
                open(f"{OUT}/estado.bin", "wb").write(ds.salvar())
                sys.exit(1)
    ds.tela().save(f"{OUT}/final.png")
    open(f"{OUT}/estado.bin", "wb").write(ds.salvar())
    print(f"{passo} passos, {n_bat} batalhas, quadro {ds.quadro}")
