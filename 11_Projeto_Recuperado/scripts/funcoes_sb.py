"""Lista identificadores (nomes de funcao) que aparecem nos .sb de uma
pasta de scripts, e em quais arquivos. Filtra por substring opcional.
uso: funcoes_sb.py <filtro_nome_arquivo> [filtro_funcao]"""
import collections
import re
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = open("/ds/rom/aots.nds", "rb").read()
cam = nds_rom.caminhos(rom)
fa = sys.argv[1]
ff = sys.argv[2].lower() if len(sys.argv) > 2 else ""
uso = collections.defaultdict(set)
for c in cam:
    if not (c.startswith("script/EN/") and c.endswith(".sb") and fa in c):
        continue
    d = nds_rom.ler(rom, c)
    for s in re.findall(rb"[A-Za-z_][A-Za-z0-9_]{3,}", d):
        s = s.decode()
        if s[0].isupper() or "_" in s:
            uso[s].add(c.rsplit("/", 1)[-1])
for s in sorted(uso):
    if ff and ff not in s.lower():
        continue
    fs = sorted(uso[s])
    print(f"{s:36s} {len(fs):4d}  {fs[:5]}")
