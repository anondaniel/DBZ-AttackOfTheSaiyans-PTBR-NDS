import sys, json, zipfile
import numpy as np
sys.path.insert(0, sys.argv[1])
import nitro

P = r'C:\Projetos\09_Dragon_Ball_Z_Attack_of_the_Saiyans'
roms = {
    'orig': zipfile.ZipFile(P + r'\00_Original\Dragon Ball Z_ Attack of the Saiyans.zip').read('Dragon Ball Z - Attack of the Saiyans (USA) (En,Fr).nds'),
    'rc1': open(P + r'\01_ROM\DBZ Attack of the Saiyans PT-BR.nds', 'rb').read(),
    'coe': open(P + r'\12_Coerencia_Historia\DBZ Attack of the Saiyans PT-BR Coerencia.nds', 'rb').read(),
    'antiga': open(P + r'\00_Original\rom_antiga_do_switch_2026-10-11\Dragon Ball Z - Attack of the Saiyans.nds', 'rb').read(),
}
res = {}
for k, r in roms.items():
    h, f = nitro.files(r)
    L = len(r)
    print('==', k, {x: (hex(v) if isinstance(v, int) else v) for x, v in h.items()})
    probs = []
    if h['hdr_crc'] != h['hdr_crc_calc']: probs.append('CRC16 cabecalho invalido')
    if h['logo_crc'] != h['logo_crc_calc'] or h['logo_crc'] != 0xCF56: probs.append('logo crc')
    for nm in ('arm9', 'arm7', 'fnt', 'fat', 'ovt9', 'ovt7'):
        if h[nm + '_off'] + h[nm + '_size'] > L: probs.append(nm + ' fora da ROM')
    if h['used_rom'] > L: probs.append('used_rom > tamanho')
    if h['chip_bytes'] != L: probs.append(f"capacidade {h['chip_bytes']} != tamanho {L}")
    mx = 0; bad = []
    for fid, (n, a, z) in f.items():
        if a or z:
            if not (a <= z <= L): bad.append((fid, n, a, z))
            mx = max(mx, z)
    iv = sorted((a, z, n) for n, a, z in f.values() if z > a)
    ov = [(iv[i][2], iv[i + 1][2]) for i in range(len(iv) - 1) if iv[i][1] > iv[i + 1][0]]
    b = h['banner_off']
    bok = nitro.u16(r, b + 2) == nitro.crc16(r[b + 0x20:b + 0x840])
    tail = np.frombuffer(r, dtype=np.uint8)[h['used_rom']:]
    print(f" FAT: {len(f)} entradas | maior fim {hex(mx)} | used_rom {hex(h['used_rom'])} | problemas {probs} | entradas invalidas {bad[:5]} | sobreposicoes {len(ov)} {ov[:3]} | banner crc ok {bok} | cauda apos used_rom {len(tail)} bytes valores {np.unique(tail)[:5].tolist()}")
    res[k] = (h, f)


def comp(a, b, label):
    ra, rb = roms[a], roms[b]
    ha, fa = res[a]; hb, fb = res[b]
    print(f'\n######## {label}: {a} -> {b}')
    print('campos de cabecalho diferentes:', {x: (ha[x], hb[x]) for x in ha if ha[x] != hb[x]})
    print('bytes diferentes em 0x0000-0x3FFF:', [hex(i) for i in range(0x4000) if ra[i] != rb[i]][:40])
    ch = []
    for fid in sorted(set(fa) | set(fb)):
        na, a1, z1 = fa.get(fid, ('?', 0, 0)); nb, a2, z2 = fb.get(fid, ('?', 0, 0))
        if na != nb:
            ch.append((fid, na + '|' + nb, 'NOME MUDOU', z1 - a1, z2 - a2, hex(a1), hex(a2))); continue
        if ra[a1:z1] != rb[a2:z2]:
            ch.append((fid, na, 'conteudo', z1 - a1, z2 - a2, hex(a1), hex(a2)))
        elif (a1, z1) != (a2, z2):
            ch.append((fid, na, 'so posicao', z1 - a1, z2 - a2, hex(a1), hex(a2)))
    for c in ch: print(' ', c)
    print(' total arquivos alterados:', len(ch))
    for nm in ('arm9', 'arm7', 'fnt', 'ovt9', 'ovt7'):
        print(f' {nm} igual:', ra[ha[nm + '_off']:ha[nm + '_off'] + ha[nm + '_size']] == rb[hb[nm + '_off']:hb[nm + '_off'] + hb[nm + '_size']])
    print(' banner igual:', ra[ha['banner_off']:ha['banner_off'] + 0x840] == rb[hb['banner_off']:hb['banner_off'] + 0x840])
    A = np.frombuffer(ra, dtype=np.uint8); B = np.frombuffer(rb, dtype=np.uint8)
    diff = np.flatnonzero(A != B)
    cov = np.zeros(len(ra), dtype=bool)
    cov[:0x4000] = True
    chids = {c[0] for c in ch}
    for h_, f_ in ((ha, fa), (hb, fb)):
        for nm in ('arm9', 'arm7', 'fnt', 'fat', 'ovt9', 'ovt7'):
            cov[h_[nm + '_off']:h_[nm + '_off'] + h_[nm + '_size']] = True
        cov[h_['banner_off']:h_['banner_off'] + 0x840] = True
        for fid, (n, x, y) in f_.items():
            if fid in chids:
                # inclui a folga ate o proximo alinhamento (preenchimento 0xFF do arquivo encolhido)
                cov[x:(y + 0x1FF) & ~0x1FF] = True
    fora = diff[~cov[diff]]
    print(' bytes diferentes total:', len(diff), '| fora das regioes alteradas/estruturais:', len(fora))
    if len(fora):
        grp = []; s = p = int(fora[0])
        for x in fora[1:]:
            x = int(x)
            if x != p + 1: grp.append((hex(s), hex(p + 1))); s = x
            p = x
        grp.append((hex(s), hex(p + 1)))
        print('  faixas:', grp[:20], 'n', len(grp))
    return ch


out = {}
out['rc1_coe'] = comp('rc1', 'coe', 'ETAPA 12')
out['orig_rc1'] = comp('orig', 'rc1', 'rc.1')
out['orig_coe'] = comp('orig', 'coe', 'original -> Coerencia')
out['orig_antiga'] = comp('orig', 'antiga', 'ROM antiga do Switch vs original')
out['rc1_antiga'] = comp('rc1', 'antiga', 'ROM antiga do Switch vs rc.1')
json.dump({k: [list(map(str, c)) for c in v] for k, v in out.items()}, open(sys.argv[2], 'w'), indent=1)
