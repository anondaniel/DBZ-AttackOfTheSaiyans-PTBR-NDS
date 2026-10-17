"""Resumo das pastas do NitroFS (quantos arquivos, extensoes, exemplos)
para achar onde ficam os encontros aleatorios."""
import collections
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = open("/ds/rom/aots.nds", "rb").read()
cam = nds_rom.caminhos(rom)
pastas = collections.defaultdict(list)
for c in cam:
    p = c.rsplit("/", 1)[0] if "/" in c else "."
    pastas[p].append(c.rsplit("/", 1)[-1])
filtro = sys.argv[1] if len(sys.argv) > 1 else ""
for p in sorted(pastas):
    if filtro and filtro not in p:
        continue
    nomes = sorted(pastas[p])
    exts = collections.Counter(n.rsplit(".", 1)[-1] for n in nomes)
    print(f"{p:40s} {len(nomes):5d}  {dict(exts)}  ex: {nomes[:4]}")
