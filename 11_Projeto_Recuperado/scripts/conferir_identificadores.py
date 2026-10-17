"""Confere a ROM traduzida contra a original, script a script:
 - todo texto passado a funcao que NAO exibe (identificador) e igual ao original
 - a secao de codigo so difere nos bytes de indice repontados (26 <i>),
   e so em chamadas de exibicao
uso: conferir_identificadores.py <rom_traduzida>"""
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from aplicar_traducao import EXIBE, _chamadas, _falas
from sb import textos

orig = open("/ds/rom/aots.nds", "rb").read()
nova = open(sys.argv[1], "rb").read()
ruins, conferidos, rep = [], 0, 0


def partes(d):
    offs = list(struct.unpack_from("<6I", d, 8))
    a4 = offs[4]
    hs, n = struct.unpack_from("<II", d, a4)
    base = a4 + hs + n * 4
    imps = []
    for k in range(n):
        no, _ = struct.unpack_from("<HH", d, a4 + hs + k * 4)
        imps.append(d[base + no:d.index(b"\x00", base + no)].decode())
    return d[offs[0]:offs[1]], imps, textos(d)


for c in nds_rom.caminhos(orig):
    if not (c.startswith(("script/US/", "script/EN/")) and c.endswith(".sb")):
        continue
    a, b = nds_rom.ler(orig, c), nds_rom.ler(nova, c)
    if a[:4] != b"SB  " or a == b:
        continue
    conferidos += 1
    ca, imps, ta = partes(a)
    cb, _, tb = partes(b)
    if len(ca) != len(cb):
        ruins.append((c, "codigo mudou de tamanho"))
        continue
    falas = {p for p, _ in _falas(ca, imps, ta)}
    for k in range(len(ca)):
        if ca[k] != cb[k]:
            if k - 1 in falas:
                rep += 1
                # o novo indice aponta para a traducao do mesmo nome
                if tb[cb[k]] == ta[ca[k]]:
                    ruins.append((c, f"repontado mas sem traducao em 0x{k:x}"))
            else:
                ruins.append((c, f"byte de codigo 0x{k:x} mudou fora de fala"))
    # texto curto (nao-dialogo) usado fora de exibicao tem que estar intacto
    for p, i, f in _chamadas(ca, imps):
        if f is not None and f not in EXIBE and i < len(ta) and b"<p>" not in ta[i]:
            if tb[i] != ta[i]:
                ruins.append((c, f"{f}({ta[i]!r}) virou {tb[i]!r}"))
print(f"{conferidos} scripts conferidos, {rep} repontamentos em exibicao")
for r in ruins[:40]:
    print("  PROBLEMA", r)
print("OK" if not ruins else f"{len(ruins)} problema(s)")
