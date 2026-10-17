"""Desmontador aproximado do bytecode .sb (so para leitura).
Opcodes conhecidos (deduzidos): 13 i32 BE, 14 i8, 15 i16 BE, 16-1f const
0-9, 24 vazio, 26 str#, 38 local, 39 arg?, 4a call import, 29 03 xx
get global 0x3xx, 20 03 xx .. 3d set global.
uso: disasm_sb.py <caminho> <ini_hex> <fim_hex>  (offsets no arquivo)"""
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = open("/ds/rom/aots.nds", "rb").read()
d = nds_rom.ler(rom, sys.argv[1])
a, z = int(sys.argv[2], 16), int(sys.argv[3], 16)
offs = list(struct.unpack_from("<6I", d, 8)) + [len(d)]
a4 = offs[4]
hs, n = struct.unpack_from("<II", d, a4)
base = a4 + hs + n * 4
imps = []
for i in range(n):
    no, _ = struct.unpack_from("<HH", d, a4 + hs + i * 4)
    imps.append(d[base + no:d.index(b"\x00", base + no)].decode())
a2 = offs[2]
hs2, n2 = struct.unpack_from("<II", d, a2)
b2 = a2 + hs2 + n2 * 4
strs = []
for i in range(n2):
    so = struct.unpack_from("<I", d, a2 + hs2 + i * 4)[0]
    strs.append(d[b2 + so:d.index(b"\x00", b2 + so)].decode("latin-1"))

p = a
linha = []
while p < z:
    op = d[p]
    if op == 0x13:
        v = struct.unpack_from(">i", d, p + 1)[0]; t = f"i32 {v}"; n_ = 5
    elif op == 0x14:
        t = f"i8 {d[p + 1]}"; n_ = 2
    elif op == 0x15:
        t = f"i16 {(d[p + 1] << 8) | d[p + 2]}"; n_ = 3
    elif 0x16 <= op <= 0x1f:
        t = f"c{op - 0x16}"; n_ = 1
    elif op == 0x24:
        t = "nil"; n_ = 1
    elif op == 0x26:
        t = f"str#{d[p + 1]} {strs[d[p + 1]]!r}" if d[p + 1] < len(strs) else f"str#{d[p+1]}"; n_ = 2
    elif op == 0x38:
        t = f"loc{d[p + 1]}"; n_ = 2
    elif op == 0x39:
        t = f"arg{d[p + 1]}"; n_ = 2
    elif op == 0x4a:
        t = f"CALL {imps[d[p + 1]] if d[p + 1] < len(imps) else d[p + 1]}"; n_ = 2
    elif op == 0x29 and d[p + 1] == 3:
        t = f"g{d[p + 2]:02x}"; n_ = 3
    elif op == 0x20 and d[p + 1] == 3:
        t = f"&g{d[p + 2]:02x}"; n_ = 3
    elif op == 0x3d:
        t = "SET"; n_ = 1
    else:
        t = f"?{op:02x}"; n_ = 1
    linha.append(f"{p:05x}:{t}")
    p += n_
for i in range(0, len(linha), 6):
    print("   ".join(linha[i:i + 6]))
