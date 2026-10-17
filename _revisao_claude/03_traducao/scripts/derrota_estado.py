"""Mostra a faixa "Derrota": pega um estado JA DENTRO da batalha
(batalha_fim.py com SALVA_EM), zera o HP dos 3 do grupo e segue apertando A.
No save state (melonDS) os registros de batalha do grupo ficam a cada 0x24C
bytes a partir de 0xcde08 (u32: HP atual, HP mostrado, HP maximo, 0, KI...).
uso: derrota_estado.py <estado_batalha> <saida_dir> <rom>"""
import os
import struct
import sys

import numpy as np

sys.path.insert(0, "/ds/scripts")
from ds import DS

src = open("/ds/scripts/piloto.py").read()
exec(src[src.index("def no_campo"):src.index("n_bat = 0")])

EST, OUT, ROM = sys.argv[1], sys.argv[2], sys.argv[3]
HP = int(os.environ.get("HP", "0"))  # 0 = nocaute direto (com 1 o grupo regenera e o inimigo quase nao acerta)
os.makedirs(OUT, exist_ok=True)
s = bytearray(open(EST, "rb").read())
for k in range(3):
    a = 0xcde08 + k * 0x24C
    cur, mostra, maximo = struct.unpack_from("<3I", s, a)
    assert 0 < cur <= maximo < 1000, (hex(a), cur, maximo)
    struct.pack_into("<2I", s, a, HP, HP)

with DS(ROM) as ds:
    ds.espera(5)
    ds.carregar(bytes(s))
    n = 0
    for i in range(400):
        t = ds.tela()
        t.save(f"{OUT}/f{n:03d}.png")
        n += 1
        if i > 20 and no_campo(t):
            print("voltou ao campo apos", i, "toques")
            break
        ds.aperta("a", segura=6, depois=12)
    print(n, "fotos")
    # estado final: jogo recarregado pela tela de titulo (tabelas de texto da ROM atual)
    open(f"{OUT}/estado_fim.bin", "wb").write(ds.salvar())
