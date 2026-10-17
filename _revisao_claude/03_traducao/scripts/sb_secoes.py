"""Estrutura de um .sb: cabecalho, secoes e onde ficam os nomes.
uso: sb_secoes.py <caminho> [nome_procurado]"""
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = open("/ds/rom/aots.nds", "rb").read()
d = nds_rom.ler(rom, sys.argv[1])
alvo = sys.argv[2].encode() if len(sys.argv) > 2 else b"SetEnemyParty"
offs = struct.unpack_from("<6I", d, 8)
print("cabecalho:", d[:8], [hex(o) for o in offs], "tam", hex(len(d)))
fim = list(offs[1:]) + [len(d)]
for i, (a, z) in enumerate(zip(offs, fim)):
    ch = d[a:a + 48]
    print(f"secao {i}: 0x{a:05x}-0x{z:05x} ({z - a} b)  {ch.hex(' ')}")
p = d.find(alvo)
print(f"'{alvo.decode()}' em 0x{p:x}")
# procura quem aponta para esse nome (u16/u32 com offset relativo a cada secao)
for i, base in enumerate(offs):
    rel = p - base
    if 0 <= rel < 0x10000:
        for fmt, tam in (("<H", 2), ("<I", 4)):
            pat = struct.pack(fmt, rel)
            q = d.find(pat)
            achados = []
            while q != -1 and len(achados) < 8:
                achados.append(hex(q))
                q = d.find(pat, q + 1)
            print(f"  rel. secao {i} = 0x{rel:x} {fmt}: {achados}")
