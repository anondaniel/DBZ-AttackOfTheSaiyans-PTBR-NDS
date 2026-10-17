"""Lista (1) nomes de quem fala ainda sem traducao e (2) traducoes com
caracteres que a fonte nao tem (glifo de listras)."""
import json
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from aplicar_traducao import ACUM, _falantes

acum = json.load(open(ACUM, encoding="utf-8"))
fal = sorted(_falantes())
print("FALANTES SEM TRADUCAO:")
print(" | ".join(f for f in fal if f not in acum))

rom = open("/ds/rom/aots.nds", "rb").read()
# glifo "de listras": o mesmo desenho do 0x81 (codigo sem caractere)
for fnt in ("latin0.fnt", "latin1.fnt"):
    d = nds_rom.ler(rom, fnt)
    nb = (len(d) - 256) // 256
    lixo = d[256 + 0x81 * nb:256 + 0x82 * nb]
    faltam = {ch for ch in range(0x80, 256) if d[256 + ch * nb:256 + (ch + 1) * nb] == lixo}
    ruins = {k: v for k, v in acum.items() if any(ord(c) in faltam for c in v)}
    print(f"\n{fnt}: sem glifo: {''.join(chr(c) for c in sorted(faltam) if c >= 0xA0)}")
    for k, v in ruins.items():
        print(f"   {v!r}")
