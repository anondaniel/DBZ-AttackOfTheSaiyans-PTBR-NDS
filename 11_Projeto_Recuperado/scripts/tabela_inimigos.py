"""Destrincha o bdat.bin: diretorio de secoes e a tabela de inimigos.

Cabecalho observado:  23 00 00 00 | 74 95 01 00 | 94 00 00 00 | c4 40 ...
  -> 0x23 = 35 secoes, seguido dos offsets de cada uma.

A secao que contem as strings 'eneNNN_MM' e a tabela de inimigos: cada
registro aponta para o arquivo de grafico pelo nome.
"""
import re
import struct
import sys
from collections import Counter

sys.path.insert(0, "/ds/scripts")
src = open("/ds/scripts/analisar_bdat.py").read()
ini = src.index("ROM = ")
fim = src.index("# ---------------------------------------------------------------------------\n# 1) bdat.bin")
exec(src[ini:fim])   # reaproveita leitura de FNT/FAT e lz10

LANG = sys.argv[1] if len(sys.argv) > 1 else "EN"
bdat = lz10(arquivo(f"btl/bdat/{LANG}/bdat.bin"))

n_sec = u32(bdat, 0)
offs = [u32(bdat, 4 + i * 4) for i in range(n_sec + 1)]
print(f"{n_sec} secoes (+1 valor extra no diretorio)")

# o primeiro valor do diretorio parece o tamanho total; os demais, inicios
secoes = []
inicios = sorted(o for o in offs if 0 < o < len(bdat))
for i, a in enumerate(inicios):
    b = inicios[i + 1] if i + 1 < len(inicios) else len(bdat)
    secoes.append((a, b))

print(f"\n{'#':>3} {'inicio':>8} {'fim':>8} {'tamanho':>8}  conteudo")
for i, (a, b) in enumerate(secoes):
    trecho = bdat[a:b]
    ss = [m.group().decode() for m in re.finditer(rb"[\x20-\x7E]{4,}", trecho)]
    ex = ", ".join(ss[:3])
    print(f"{i:>3} 0x{a:06X} 0x{b:06X} {b - a:>8}  {len(ss):>3} strings  {ex[:60]}")

# ---------------------------------------------------------------------------
# tabela de inimigos: a secao com mais 'eneNNN_MM'
# ---------------------------------------------------------------------------
melhor = max(range(len(secoes)),
             key=lambda i: len(re.findall(rb"ene\d{3}_\d{2}", bdat[secoes[i][0]:secoes[i][1]])))
a, b = secoes[melhor]
sec = bdat[a:b]
posicoes = [m.start() for m in re.finditer(rb"ene\d{3}_\d{2}", sec)]
passos = Counter(posicoes[i + 1] - posicoes[i] for i in range(len(posicoes) - 1))
passo = passos.most_common(1)[0][0]
print(f"\ntabela de inimigos: secao {melhor} (0x{a:06X}..0x{b:06X})")
print(f"{len(posicoes)} referencias a grafico; passo mais comum {passo} bytes "
      f"(distribuicao {passos.most_common(4)})")

# o primeiro registro comeca antes da primeira string: acha o deslocamento
# da string dentro do registro assumindo que a secao comeca num registro
off_str = posicoes[0] % passo
n_reg = (b - a) // passo
print(f"registro de {passo} bytes, string do grafico no byte {off_str}; "
      f"{n_reg} registros ({(b - a) % passo} bytes de sobra)")

print("\nprimeiros 3 registros:")
for r in range(3):
    reg = sec[r * passo:(r + 1) * passo]
    print(f"  [{r}] {reg.hex(' ')}")

# ---------------------------------------------------------------------------
# tabela de nomes (Goku, Gohan... Saibaman... Bear)
# ---------------------------------------------------------------------------
p_nomes = bdat.find(b"Goku\x00")
print(f"\ntabela de nomes: 'Goku' em 0x{p_nomes:06X}")
# procura o inicio da secao onde os nomes estao
sec_nomes = next(i for i, (x, y) in enumerate(secoes) if x <= p_nomes < y)
xa, xb = secoes[sec_nomes]
print(f"  na secao {sec_nomes} (0x{xa:06X}..0x{xb:06X})")
print(f"  inicio da secao: {bdat[xa:xa + 64].hex(' ')}")
