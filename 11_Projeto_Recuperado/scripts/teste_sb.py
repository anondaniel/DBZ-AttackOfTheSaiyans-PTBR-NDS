"""Testes do reescritor de textos .sb em TODOS os scripts de TODOS os idiomas:
 1) ida e volta com os mesmos textos -> bytes identicos
 2) todos os textos 30% mais longos -> textos lidos de volta = os novos,
    e secoes 0,1,3,4,5 byte a byte iguais as originais
"""
import collections
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from sb import _secoes, com_textos, textos

rom = open("/ds/rom/aots.nds", "rb").read()
res = collections.Counter()
falhas = []
for c in nds_rom.caminhos(rom):
    if not (c.startswith("script/") and c.endswith(".sb")):
        continue
    d = nds_rom.ler(rom, c)
    if d[:4] != b"SB  ":
        res["nao-SB"] += 1
        continue
    ts = textos(d)
    if com_textos(d, ts) != d:
        falhas.append(("ida-e-volta", c))
        continue
    longos = [t + b"#" * (len(t) * 3 // 10 + 1) for t in ts]
    d2 = com_textos(d, longos)
    if textos(d2) != longos:
        falhas.append(("leitura", c))
        continue
    o1, o2 = _secoes(d) + [len(d)], _secoes(d2) + [len(d2)]
    for s in (0, 1, 3, 4, 5):
        if d[o1[s]:o1[s + 1]] != d2[o2[s]:o2[s + 1]]:
            falhas.append((f"secao {s}", c))
            break
    else:
        res["ok"] += 1
print(dict(res), "| falhas:", len(falhas), falhas[:5])
