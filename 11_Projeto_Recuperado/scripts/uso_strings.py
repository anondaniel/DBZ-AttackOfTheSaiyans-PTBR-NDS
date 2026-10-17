"""Para cada texto traduzido SEM marcacao <p> (nomes, rotulos), em todos os
scripts US onde aparece: qual funcao recebe esse texto? (procura o push
'26 <indice>' no codigo e a proxima chamada '4a <import>'). Se algum desses
textos vai para funcao que nao e de exibicao, e identificador: nao pode
ser traduzido la."""
import collections
import json
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from sb import textos

acum = json.load(open("/ds/traducao/ptbr.json", encoding="utf-8"))
curtos = {k for k in acum if "<p>" not in k and "<k>" not in k}
rom = open("/ds/rom/aots.nds", "rb").read()
uso = collections.defaultdict(collections.Counter)
for c in nds_rom.caminhos(rom):
    if not (c.startswith("script/US/") and c.endswith(".sb")):
        continue
    d = nds_rom.ler(rom, c)
    if d[:4] != b"SB  ":
        continue
    offs = list(struct.unpack_from("<6I", d, 8))
    a4 = offs[4]
    hs, n = struct.unpack_from("<II", d, a4)
    base = a4 + hs + n * 4
    imps = []
    for i in range(n):
        no, _ = struct.unpack_from("<HH", d, a4 + hs + i * 4)
        imps.append(d[base + no:d.index(b"\x00", base + no)].decode())
    code = d[offs[0]:offs[1]]
    ts = textos(d)
    for i, t in enumerate(ts):
        s = t.decode("latin-1")
        if s not in curtos:
            continue
        p = 0
        while True:
            p = code.find(bytes([0x26, i]), p)
            if p == -1:
                break
            q = code.find(b"\x4a", p + 2)
            while q != -1 and q + 1 < len(code) and code[q + 1] >= len(imps):
                q = code.find(b"\x4a", q + 1)
            fn = imps[code[q + 1]] if q != -1 else "?"
            uso[s][fn] += 1
            p += 2
for s in sorted(uso, key=lambda k: -sum(uso[k].values())):
    print(f"{s!r:40s} -> {dict(uso[s].most_common(6))}")
