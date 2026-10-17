"""Abre o banco de batalha (btl/bdat/EN/bdat.bin) e o diretorio de
graficos de inimigo (btl/ene/) para levantar:

  - a lista completa de nomes, em ordem, com o offset de cada um
  - quantos arquivos de grafico de inimigo existem e com quais IDs
"""
import json
import re
import struct
import sys
from collections import defaultdict

ROM = "/ds/rom/aots.nds"
with open(ROM, "rb") as f:
    rom = f.read()


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


fnt_off, fat_off, fat_tam = u32(rom, 0x40), u32(rom, 0x48), u32(rom, 0x4C)
fat = [(u32(rom, fat_off + i * 8), u32(rom, fat_off + i * 8 + 4)) for i in range(fat_tam // 8)]
caminhos = {}


def walk(dir_id, prefixo):
    base = fnt_off + (dir_id & 0x0FFF) * 8
    p = fnt_off + u32(rom, base)
    fid = u16(rom, base + 4)
    while True:
        t = rom[p]
        p += 1
        if t == 0:
            break
        n = t & 0x7F
        nome = rom[p:p + n].decode("ascii", "replace")
        p += n
        if t & 0x80:
            walk(u16(rom, p), prefixo + nome + "/")
            p += 2
        else:
            caminhos[prefixo + nome] = fid
            fid += 1


walk(0xF000, "")


def arquivo(c):
    a, b = fat[caminhos[c]]
    return rom[a:b]


def lz10(d):
    if not d or d[0] != 0x10:
        return d
    tam = d[1] | (d[2] << 8) | (d[3] << 16)
    out = bytearray()
    p = 4
    while len(out) < tam:
        fl = d[p]
        p += 1
        for bit in range(8):
            if len(out) >= tam:
                break
            if fl & (0x80 >> bit):
                b0, b1 = d[p], d[p + 1]
                p += 2
                n = (b0 >> 4) + 3
                disp = (((b0 & 0xF) << 8) | b1) + 1
                for _ in range(n):
                    out.append(out[-disp])
            else:
                out.append(d[p])
                p += 1
    return bytes(out)


# ---------------------------------------------------------------------------
# 1) bdat.bin
# ---------------------------------------------------------------------------
bdat = lz10(arquivo("btl/bdat/EN/bdat.bin"))
print(f"btl/bdat/EN/bdat.bin: {len(bdat):,} bytes (descomprimido)")
print(f"primeiros 64 bytes: {bdat[:64].hex(' ')}\n")

# todas as strings ASCII imprimiveis com >=3 caracteres
strings = [(m.start(), m.group().decode()) for m in
           re.finditer(rb"[\x20-\x7E]{3,}", bdat)]
print(f"{len(strings)} strings ASCII encontradas")

# mostra a vizinhanca de nomes-chave para achar onde fica a tabela de nomes
for chave in (b"Saibaman", b"Wolf", b"Bear", b"Raditz", b"Broly"):
    p = bdat.find(chave)
    if p >= 0:
        print(f"  {chave.decode():10} em 0x{p:06X}")

# regiao contigua de strings: onde estao os nomes
# agrupa strings que estejam a menos de 64 bytes uma da outra
grupos = []
for off, s in strings:
    if grupos and off - grupos[-1][-1][0] < 64:
        grupos[-1].append((off, s))
    else:
        grupos.append([(off, s)])
grupos.sort(key=lambda g: -len(g))
print(f"\n{len(grupos)} aglomerados de texto; os maiores:")
for g in grupos[:6]:
    print(f"  0x{g[0][0]:06X}..0x{g[-1][0]:06X}: {len(g)} strings  "
          f"ex.: {[s for _, s in g[:6]]}")

with open("/ds/saida/bdat_strings.json", "w") as fo:
    json.dump([{"off": o, "txt": s} for o, s in strings], fo, indent=0)

# ---------------------------------------------------------------------------
# 2) graficos de inimigo
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
ene = sorted(c for c in caminhos if c.startswith("btl/ene/"))
print(f"btl/ene/: {len(ene)} arquivos")
ids = defaultdict(list)
for c in ene:
    m = re.match(r"btl/ene/ene(\d+)_(\d+)\.(\w+)$", c)
    if m:
        ids[int(m.group(1))].append((int(m.group(2)), m.group(3)))
    else:
        print(f"  fora do padrao: {c}")
print(f"{len(ids)} IDs de inimigo distintos: {min(ids)}..{max(ids)}")
exts = defaultdict(int)
for v in ids.values():
    for _, e in v:
        exts[e] += 1
print(f"extensoes: {dict(exts)}")
var = defaultdict(int)
for i, v in ids.items():
    var[len(v)] += 1
print(f"arquivos por ID: {dict(sorted(var.items()))}")
faltam = [i for i in range(min(ids), max(ids) + 1) if i not in ids]
print(f"IDs faltando na sequencia: {faltam[:40]}{'...' if len(faltam) > 40 else ''}")

print("\noutras pastas de btl/:")
subs = defaultdict(int)
for c in caminhos:
    if c.startswith("btl/"):
        subs[c.split("/")[1]] += 1
for s, n in sorted(subs.items()):
    print(f"  btl/{s}/: {n}")
