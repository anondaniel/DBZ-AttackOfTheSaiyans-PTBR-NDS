"""Reextrai as chamadas SetEnemyParty (mesma logica de grupos_inimigos.py, sem exec)
e mede o efeito do filtro `1 < x <= 173` usado em 12_Coerencia_Historia/auditar.py."""
import sys, struct, collections, json
sys.path.insert(0, sys.argv[1])
import nitro
P = r'C:\Projetos\09_Dragon_Ball_Z_Attack_of_the_Saiyans'
rom = open(P + r'\12_Coerencia_Historia\DBZ Attack of the Saiyans PT-BR Coerencia.nds', 'rb').read()
h, f = nitro.files(rom)
FS = {n: rom[a:z] for n, a, z in f.values()}


def imports(d, offs):
    a4 = offs[4]
    hs, n = struct.unpack_from('<II', d, a4)
    base = a4 + hs + n * 4
    r = []
    for i in range(n):
        no, _ = struct.unpack_from('<HH', d, a4 + hs + i * 4)
        r.append(d[base + no:d.index(b'\x00', base + no)].decode())
    return r


def tokens(code, a, z):
    out = []; p = a
    while p < z:
        op = code[p]
        if op == 0x14: out.append(code[p + 1]); p += 2
        elif op == 0x15: out.append((code[p + 1] << 8) | code[p + 2]); p += 3
        elif op == 0x13: out.append(struct.unpack_from('>I', code, p + 1)[0]); p += 5
        elif 0x16 <= op <= 0x1f: out.append(op - 0x16); p += 1
        elif op == 0x24: out.append(None); p += 1
        else: out.append('?'); p += 1
    return out


grupos = []
for c in sorted(FS):
    if not (c.startswith('script/EN/') and c.endswith('.sb')): continue
    d = FS[c]
    if d[:4] != b'SB  ': continue
    offs = list(struct.unpack_from('<6I', d, 8)) + [len(d)]
    imp = imports(d, offs)
    if 'SetEnemyParty' not in imp: continue
    k = imp.index('SetEnemyParty')
    code = d[offs[0]:offs[1]]
    p = 0
    while True:
        p = code.find(bytes([0x4a, k]), p)
        if p == -1: break
        if code[p - 2] == 0x14:
            argc = code[p - 1]; cand = None
            for janela in range(argc, argc * 5 + 1):
                toks = tokens(code, p - 2 - janela, p - 2)
                if len(toks) >= argc and '?' not in toks[-argc:]:
                    cand = toks[-argc:]; break
            grupos.append((c.split('/')[-1][:-3], p + offs[0], argc, cand))
        p += 2
print('chamadas SetEnemyParty:', len(grupos), '| mapas:', len({g[0] for g in grupos}), '| argc:', collections.Counter(g[2] for g in grupos))
slots = collections.Counter()
for m, o, argc, a in grupos:
    if argc == 15:
        for v in a[6:12]: slots[v] += 1
print('valores nos slots 6..11 (mais comuns):', slots.most_common(8))
com_id1 = [(m, hex(o), a[6:12]) for m, o, argc, a in grupos if argc == 15 and 1 in a[6:12]]
mapas_id1 = sorted({x[0] for x in com_id1})
print('grupos com ID 1 (= linha 0, Saibaman basico) ignorados pelo filtro 1<x:', len(com_id1), 'em', len(mapas_id1), 'mapas:', mapas_id1)
print('exemplos:', com_id1[:10])
vazios = [g for g in grupos if g[2] == 15 and not [x for x in g[3][6:12] if isinstance(x, int) and 1 < x <= 173]]
print('grupos "vazios" pelo filtro da etapa 12:', len(vazios), '| destes, so tem ID 1:', sum(1 for g in vazios if 1 in g[3][6:12]))
json.dump({'com_id1': com_id1}, open(sys.argv[2], 'w'), indent=1)

if len(sys.argv) > 3:
    for m, o, argc, a in grupos:
        if m in ('bam01_00', 'snd01_00', 'mut01_00', 'c1007_01', 'tut01_00', 'c0602_00'):
            print(m, hex(o), a)
