from comum import *
import struct, collections
def imports(d, offs):
    a4 = offs[4]
    hs, n = struct.unpack_from("<II", d, a4)
    base = a4 + hs + n * 4
    r = []
    for i in range(n):
        no, _ = struct.unpack_from("<HH", d, a4 + hs + i * 4)
        r.append(d[base + no:d.index(b"\x00", base + no)].decode())
    return r
def tokens(code, a, z):
    out = []; p = a
    while p < z:
        op = code[p]
        if op == 0x14: out.append(code[p + 1]); p += 2
        elif op == 0x15: out.append((code[p + 1] << 8) | code[p + 2]); p += 3
        elif op == 0x13: out.append(struct.unpack_from(">I", code, p + 1)[0]); p += 5
        elif 0x16 <= op <= 0x1f: out.append(op - 0x16); p += 1
        elif op == 0x24: out.append(None); p += 1
        else: out.append("?"); p += 1
    return out
def chamadas(d_rom, func="SetEnemyParty", lang="EN"):
    cam = nds_rom.caminhos(d_rom)
    res = []
    for c in sorted(cam):
        if not (c.startswith(f"script/{lang}/") and c.endswith(".sb")): continue
        d = nds_rom.ler(d_rom, c)
        if d[:4] != b"SB  ": continue
        offs = list(struct.unpack_from("<6I", d, 8)) + [len(d)]
        imp = imports(d, offs)
        if func not in imp: continue
        k = imp.index(func)
        code = d[offs[0]:offs[1]]
        p = 0
        while True:
            p = code.find(bytes([0x4a, k]), p)
            if p == -1: break
            if code[p - 2] == 0x14:
                argc = code[p - 1]; cand=None
                for janela in range(argc, argc * 5 + 1):
                    toks = tokens(code, p - 2 - janela, p - 2)
                    if len(toks) >= argc and "?" not in toks[-argc:]:
                        cand = toks[-argc:]; break
                res.append({'arquivo': c, 'mapa': c.split('/')[-1][:-3], 'pos': p + offs[0], 'argc': argc, 'args': cand})
            else:
                res.append({'arquivo': c, 'mapa': c.split('/')[-1][:-3], 'pos': p + offs[0], 'argc': None, 'args': None})
            p += 2
    return res
