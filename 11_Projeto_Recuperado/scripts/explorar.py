"""Avanca o jogo apertando uma sequencia de botoes, capturando a tela e
guardando save states pelo caminho.

uso: explorar.py <rom> <saida> <sequencia> [estado_inicial]

sequencia: tokens separados por espaco, cada um BOTAO[xN][:espera]
  ex.: "ax30:60 upx5:10 ax10"   (a 30 vezes esperando 60 quadros...)
"""
import os
import sys

sys.path.insert(0, "/ds/scripts")
from ds import DS

ROM, OUT, SEQ = sys.argv[1], sys.argv[2], sys.argv[3]
INICIAL = sys.argv[4] if len(sys.argv) > 4 else None
CADA = int(os.environ.get("CADA", "5"))  # captura a cada N passos
os.makedirs(OUT, exist_ok=True)

with DS(ROM) as ds:
    if INICIAL:
        ds.espera(5)
        ds.carregar(open(INICIAL, "rb").read())
    else:
        ds.espera(600)
    n = 0
    for tok in SEQ.split():
        espera = 30
        segura = 4
        if "@" in tok:  # BOTAO@N = segura o botao N quadros (andar)
            tok, resto = tok.split("@", 1)
            s = resto.split(":")[0].split("x")[0]
            segura = int(s)
            tok += resto[len(s):]
        if ":" in tok:
            tok, e = tok.split(":")
            espera = int(e)
        vezes = 1
        if "x" in tok[1:]:
            tok, v = tok.rsplit("x", 1)
            vezes = int(v)
        toque = None
        if tok.startswith("t") and "," in tok:  # tX,Y = toque na tela de baixo
            toque = tuple(int(v) for v in tok[1:].split(","))
            tok = "nada"
        botoes = [] if tok == "nada" else tok.split("+")
        for _ in range(vezes):
            if toque:
                ds.toca(*toque, segura=segura if segura != 4 else 6, depois=espera)
            elif botoes:
                ds.aperta(*botoes, segura=segura, depois=espera)
            else:
                ds.espera(espera)
            n += 1
            if n % CADA == 0:
                ds.tela().save(f"{OUT}/q{n:04d}.png")
    ds.tela().save(f"{OUT}/final.png")
    open(f"{OUT}/estado.bin", "wb").write(ds.salvar())
    print(f"{n} passos, quadro {ds.quadro}; estado em {OUT}/estado.bin")
