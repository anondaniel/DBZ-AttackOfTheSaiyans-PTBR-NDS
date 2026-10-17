"""Descobre o opcode que empilha string: procura op X tal que 'X 08' ...
'X 09' ... 'X 0a' aparecam em sequencia curta (Kame House, kam01_00,
Wobj001) no codigo do worldmap.sb, e mostra o trecho de cada local."""
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = open("/ds/rom/aots.nds", "rb").read()
d = nds_rom.ler(rom, "script/EN/cf/worldmap.sb")
offs = list(struct.unpack_from("<6I", d, 8)) + [len(d)]
code = d[offs[0]:offs[1]]
for op in range(256):
    for p in range(len(code) - 2):
        if code[p] == op and code[p + 1] == 8:
            j = code.find(bytes([op, 9]), p + 2, p + 30)
            if j != -1 and code.find(bytes([op, 10]), j + 2, j + 30) != -1:
                print(f"op 0x{op:02x} em 0x{p + offs[0]:05x}: {code[p:p + 80].hex(' ')}")
