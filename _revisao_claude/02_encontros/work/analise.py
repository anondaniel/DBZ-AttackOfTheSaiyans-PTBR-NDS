from comum import *
import pickle, collections, json, re
from dump_tiles import ler_chr
from render_quadros import ler_anims
from chr_paletas import paletas

R = {n: rom(n) for n in ('orig','rc1','coe')}
T = {n: tabelas(R[n]) for n in R}
EP = {n: T[n]['enemy_param']['linhas'] for n in R}
NM = {n: T[n]['character_name']['linhas'] for n in R}
BP = {n: T[n]['boss_param']['linhas'] for n in R}
CH = {n: pickle.load(open(f'chamadas_{n}.pkl','rb')) for n in R}
def nome(n, i):  # i = id 1-based
    if 1 <= i <= 173:
        e = EP[n][i-1]; return NM[n][e['name_id']-1]['en'] if e['name_id'] else f'(vazio {i})'
    if 174 <= i <= 228:
        b = BP[n][i-174]; return '[CHEFE] ' + (NM[n][b['name_id']-1]['en'] if b['name_id'] else f'(vazio {i})')
    return f'?{i}'

# 1. contagens
res = {}
for n in R:
    r = CH[n]
    res[n] = {'chamadas': len(r), 'scripts': len({x['mapa'] for x in r}),
              'argc15': sum(x['argc']==15 for x in r)}
print('CONTAGENS', res)
# grupos identicos entre ROMs?
for n in ('rc1','coe'):
    same = all(a['mapa']==b['mapa'] and a['args']==b['args'] for a,b in zip(CH['orig'],CH[n])) and len(CH['orig'])==len(CH[n])
    print('grupos identicos orig vs', n, same)

# usados
def slots(a): return [v for v in a[6:12] if isinstance(v,int) and v>0]
def tipos(a): return [v for v in a[2:6] if isinstance(v,int)]
usados = collections.Counter()
for x in CH['coe']:
    for v in slots(x['args']): usados[v]+=1
    for v in tipos(x['args']): usados[v]+=0
print('ids distintos em slots', len([k for k in usados if usados[k]]))
# 2. validade de IDs
inval = []
for x in CH['coe']:
    for v in slots(x['args']) + tipos(x['args']):
        if v == 1: continue
        if not (2 <= v <= 228): inval.append((x['mapa'], v)); continue
        if v <= 173 and not EP['coe'][v-1]['name_id']: inval.append((x['mapa'], v, 'linha vazia'))
print('IDs invalidos', inval[:20], len(inval))
# vazio
vaz = [x for x in CH['coe'] if not [v for v in slots(x['args']) if v != 1]]
print('grupos sem inimigo real', len(vaz), [ (x['mapa'],x['args']) for x in vaz][:5])
