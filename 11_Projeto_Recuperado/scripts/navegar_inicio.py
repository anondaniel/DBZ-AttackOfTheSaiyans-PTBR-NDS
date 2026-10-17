"""Passa da tela de 'resetting backup memory' e da abertura, capturando a
tela a cada passo para eu ver onde o jogo chega."""
import os
import sys

sys.path.insert(0, "/ds/scripts")
from ds import DS

ROM = sys.argv[1] if len(sys.argv) > 1 else "/ds/rom/aots.nds"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/ds/saida/nav"
PASSOS = int(sys.argv[3]) if len(sys.argv) > 3 else 40
os.makedirs(OUT, exist_ok=True)

with DS(ROM) as ds:
    ds.espera(600)
    ds.tela().save(f"{OUT}/p00.png")
    for i in range(1, PASSOS + 1):
        ds.aperta("a", segura=4, depois=60)
        if i % 4 == 0:
            ds.tela().save(f"{OUT}/p{i:02d}.png")
    ds.tela().save(f"{OUT}/final.png")
    est = ds.salvar()
    with open(f"{OUT}/estado.bin", "wb") as f:
        f.write(est)
    print(f"quadro {ds.quadro}; save state {len(est):,} bytes em {OUT}/estado.bin")
