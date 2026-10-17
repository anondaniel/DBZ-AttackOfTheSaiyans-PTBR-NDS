"""Diagnostico: para cada tabela, mostra o fim do nome da tabela e os
primeiros registros de coluna em hex, para descobrir a regra de
alinhamento sem chutar."""
import re
import struct
import sys

src = open("/ds/scripts/analisar_bdat.py").read()
exec(src[src.index("ROM = "):src.index(
    "# ---------------------------------------------------------------------------\n# 1) bdat.bin")])

b = lz10(arquivo("btl/bdat/EN/bdat.bin"))
n = struct.unpack_from("<I", b, 0)[0]
offs = sorted(o for o in (struct.unpack_from("<I", b, 4 + i * 4)[0] for i in range(n + 1))
              if 0 < o < len(b))
for i, a in enumerate(offs):
    z = offs[i + 1] if i + 1 < len(offs) else len(b)
    t = b[a:z]
    u16 = lambda o: struct.unpack_from("<H", t, o)[0]
    no = u16(6)
    fim = t.index(b"\x00", no)
    nome = t[no:fim].decode()
    # proximos 12 bytes depois do nulo do nome
    depois = t[fim + 1:fim + 13]
    print(f"{nome:16} nome_off=0x{no:03X} len={len(nome):2} "
          f"({'par' if (len(nome) + 1) % 2 == 0 else 'IMPAR'}) "
          f"-> depois do nulo: {depois.hex(' ')}")
