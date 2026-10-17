"""Levanta a estrutura das secoes de TODOS os .sb (EN): cabecalhos, se as
secoes sao contiguas, alinhamento, preenchimento no fim de cada secao, e
se algum u32 fora da secao 2 aponta para dentro dela (o que impediria
crescer a secao 2 livremente)."""
import collections
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = open("/ds/rom/aots.nds", "rb").read()
cam = [c for c in nds_rom.caminhos(rom) if c.startswith("script/EN/") and c.endswith(".sb")]
stats = collections.Counter()
exemplos = {}
maior = (0, "")
for c in cam:
    d = nds_rom.ler(rom, c)
    if d[:4] != b"SB  ":
        stats["nao-SB"] += 1
        continue
    offs = list(struct.unpack_from("<6I", d, 8))
    stats[f"cab {d[4:8].hex()}"] += 1
    stats["secoes em ordem" if offs == sorted(offs) else "secoes FORA de ordem"] += 1
    stats["ali4" if all(o % 4 == 0 for o in offs) else "nao-ali4"] += 1
    # secao 2: strings
    a2, a3 = offs[2], offs[3]
    hs, n = struct.unpack_from("<II", d, a2)
    base = a2 + hs + n * 4
    so = [struct.unpack_from("<I", d, a2 + hs + i * 4)[0] for i in range(n)]
    crescente = so == sorted(so)
    fim = max((base + s + d[base + s:].index(b"\x00") + 1) for s in so) if so else base
    stats["str crescente" if crescente else "str NAO crescente"] += 1
    stats[f"hs2={hs}"] += 1
    stats[f"folga fim sec2={a3 - fim}"] += 1
    maior = max(maior, (n, c))
    # algum u32 fora da secao 2 aponta para dentro dela?
    alvo_fora = 0
    for p in range(0x08, len(d) - 3, 4):
        if a2 <= p < a3:
            continue
        v = struct.unpack_from("<I", d, p)[0]
        if a2 < v < a3 and p >= 0x20:
            alvo_fora += 1
    stats["u32 de fora apontando p/ sec2: " + ("0" if not alvo_fora else ">0")] += 1
    if alvo_fora and c not in exemplos:
        exemplos[c] = alvo_fora
print(len(cam), "scripts")
for k, v in sorted(stats.items()):
    print(f"  {k}: {v}")
print("maior n de strings:", maior)
print("exemplos com u32 apontando p/ sec2:", list(exemplos.items())[:5])
