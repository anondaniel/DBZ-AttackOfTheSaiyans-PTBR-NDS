"""Procura, no codigo (secao 0) de um .sb, os bytes de import de uma funcao
(indice na tabela da secao 4) e mostra o contexto em hex.
uso: sb_contexto.py <caminho> <nome_funcao> [antes] [depois]"""
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = open("/ds/rom/aots.nds", "rb").read()
d = nds_rom.ler(rom, sys.argv[1])
alvo = sys.argv[2]
antes = int(sys.argv[3]) if len(sys.argv) > 3 else 24
depois = int(sys.argv[4]) if len(sys.argv) > 4 else 6
offs = list(struct.unpack_from("<6I", d, 8)) + [len(d)]
a4 = offs[4]
hs, n = struct.unpack_from("<II", d, a4)
base = a4 + hs + n * 4
nomes = []
for i in range(n):
    no, _ = struct.unpack_from("<HH", d, a4 + hs + i * 4)
    nomes.append(d[base + no:d.index(b"\x00", base + no)].decode())
idx = nomes.index(alvo)
print(f"{alvo} = import {idx} (0x{idx:02x})")
code = d[offs[0]:offs[1]]
# tenta: qualquer ocorrencia do byte idx precedida de um byte "opcode"
cont = {}
for p in range(1, len(code)):
    if code[p] == idx:
        cont.setdefault(code[p - 1], []).append(p)
print("bytes que precedem o indice:", {hex(k): len(v) for k, v in sorted(cont.items())})
for op, ps in sorted(cont.items(), key=lambda kv: -len(kv[1]))[:3]:
    print(f"--- precedido por 0x{op:02x}:")
    for p in ps[:6]:
        s = max(0, p - antes)
        print(f"  @0x{p + offs[0]:05x}: {code[s:p - 1].hex(' ')} [{code[p - 1]:02x} {code[p]:02x}] {code[p + 1:p + 1 + depois].hex(' ')}")
