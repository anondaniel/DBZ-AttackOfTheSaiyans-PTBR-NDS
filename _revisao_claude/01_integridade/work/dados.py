"""Comparacao no nivel dos dados: bdat (todas as tabelas, todas as colunas) e .chr (paletas x resto)."""
import sys, json, zipfile, struct
sys.path.insert(0, sys.argv[1])
import nitro
sys.path.insert(1, r'C:\Projetos\09_Dragon_Ball_Z_Attack_of_the_Saiyans\11_Projeto_Recuperado\scripts')
from bdat import ler_container

P = r'C:\Projetos\09_Dragon_Ball_Z_Attack_of_the_Saiyans'
orig = zipfile.ZipFile(P + r'\00_Original\Dragon Ball Z_ Attack of the Saiyans.zip').read('Dragon Ball Z - Attack of the Saiyans (USA) (En,Fr).nds')
rc1 = open(P + r'\01_ROM\DBZ Attack of the Saiyans PT-BR.nds', 'rb').read()
coe = open(P + r'\12_Coerencia_Historia\DBZ Attack of the Saiyans PT-BR Coerencia.nds', 'rb').read()


def fsmap(r):
    h, f = nitro.files(r)
    return {n: r[a:z] for n, a, z in f.values()}


FO, FA, FB = fsmap(orig), fsmap(rc1), fsmap(coe)
rep = {}
# ---------- bdat ----------
for lang in ('EN', 'US', 'FR', 'SP', 'GR', 'IT'):
    p = f'btl/bdat/{lang}/bdat.bin'
    tO, tA, tB = ler_container(FO[p]), ler_container(FA[p]), ler_container(FB[p])
    assert set(tA) == set(tB), 'conjunto de tabelas mudou'
    lr = {}
    for tn in tA:
        a, b = tA[tn], tB[tn]
        if [c[:4] for c in a['colunas']] != [c[:4] for c in b['colunas']] or a['n_linhas'] != b['n_linhas'] or a['tam_linha'] != b['tam_linha']:
            lr[tn] = 'ESTRUTURA MUDOU'; continue
        ch = {}
        for i, (ra, rb) in enumerate(zip(a['linhas'], b['linhas'])):
            for col in ra:
                if ra[col] != rb[col]:
                    ch.setdefault(col, []).append((i, ra[col], rb[col]))
        if ch:
            lr[tn] = ch
    rep[lang] = lr
    print(f'\n=== {lang}: tabelas com diferenca rc1->coe:', {t: (v if isinstance(v, str) else {c: len(x) for c, x in v.items()}) for t, v in lr.items()})

# colunas de enemy_param
ep = ler_container(FA['btl/bdat/EN/bdat.bin'])['enemy_param']
print('\nenemy_param colunas:', [(c[0], c[2], c[3]) for c in ep['colunas']], 'tam_linha', ep['tam_linha'], 'linhas', ep['n_linhas'])
tabs = ler_container(FA['btl/bdat/EN/bdat.bin'])
print('tabelas:', {k: (v['n_linhas'], v['tam_linha']) for k, v in tabs.items()})

# Mesmas colunas alteradas em todos os idiomas? e valores iguais entre idiomas?
en = rep['EN'].get('enemy_param', {})
for lang in rep:
    e = rep[lang].get('enemy_param', {})
    print(lang, 'enemy_param colunas alteradas:', sorted(e), 'igual EN:', e == en)

# Detalhe EN: atk1-4, size, shadow, file, palno
for col in sorted(en):
    rows = en[col]
    print(f'\n[{col}] {len(rows)} linhas alteradas. Ex.:', rows[:8])

# Verifica tambem orig vs coe para colunas de combate (devem ser iguais a orig nas linhas nao-hack)
eo = ler_container(FO['btl/bdat/EN/bdat.bin'])['enemy_param']['linhas']
ea = ler_container(FA['btl/bdat/EN/bdat.bin'])['enemy_param']['linhas']
eb = ler_container(FB['btl/bdat/EN/bdat.bin'])['enemy_param']['linhas']
cols_mud_orig_coe = {}
for i, (x, y) in enumerate(zip(eo, eb)):
    for c in x:
        if x[c] != y[c]:
            cols_mud_orig_coe.setdefault(c, set()).add(i)
print('\norig->coe enemy_param colunas alteradas:', {c: len(s) for c, s in cols_mud_orig_coe.items()})
cols_mud_orig_rc1 = {}
for i, (x, y) in enumerate(zip(eo, ea)):
    for c in x:
        if x[c] != y[c]:
            cols_mud_orig_rc1.setdefault(c, set()).add(i)
print('orig->rc1 enemy_param colunas alteradas:', {c: len(s) for c, s in cols_mud_orig_rc1.items()})

# ---------- bytes brutos do bdat: fora da tabela enemy_param/character_name e do pool de strings ----------
json.dump({k: {t: (v if isinstance(v, str) else {c: [list(map(str, r)) for r in x] for c, x in v.items()}) for t, v in d.items()} for k, d in rep.items()},
          open(sys.argv[2], 'w'), indent=1, ensure_ascii=False)

# ---------- .chr ----------
print('\n=== .chr: cabecalho e trecho apos as paletas')
for n in sorted(FA):
    if n.startswith('btl/ene/') and FA[n] != FB[n]:
        a, b = FA[n], FB[n]
        na, nb = a[5], b[5]
        ra, rb = a[8 + na * 32:], b[8 + nb * 32:]
        hdr_a, hdr_b = a[:8], b[:8]
        pal_prefix = b[8:8 + na * 32] == a[8:8 + na * 32]
        print(f' {n}: paletas {na}->{nb} | antigas preservadas {pal_prefix} | resto igual {ra == rb} | cab {hdr_a.hex()} -> {hdr_b.hex()} | +{len(b)-len(a)} bytes')
