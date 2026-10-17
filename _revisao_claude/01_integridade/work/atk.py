"""atk1-atk4: sao pesos (%) de escolha de ataque? Efeito no dano esperado."""
import sys, zipfile, json
sys.path.insert(0, sys.argv[1])
import nitro
sys.path.insert(1, r'C:\Projetos\09_Dragon_Ball_Z_Attack_of_the_Saiyans\11_Projeto_Recuperado\scripts')
from bdat import ler_container
P = r'C:\Projetos\09_Dragon_Ball_Z_Attack_of_the_Saiyans'
roms = {'orig': zipfile.ZipFile(P + r'\00_Original\Dragon Ball Z_ Attack of the Saiyans.zip').read('Dragon Ball Z - Attack of the Saiyans (USA) (En,Fr).nds'),
        'rc1': open(P + r'\01_ROM\DBZ Attack of the Saiyans PT-BR.nds', 'rb').read(),
        'coe': open(P + r'\12_Coerencia_Historia\DBZ Attack of the Saiyans PT-BR Coerencia.nds', 'rb').read()}


def ep(r):
    h, f = nitro.files(r)
    d = {n: r[a:z] for n, a, z in f.values()}
    t = ler_container(d['btl/bdat/EN/bdat.bin'])
    names = t['character_name']['linhas']
    col = t['character_name']['colunas'][0][0]
    rows = t['enemy_param']['linhas']
    for x in rows:
        x['_nome'] = names[x['name_id'] - 1][col] if x['name_id'] else ''
    return rows


E = {k: ep(v) for k, v in roms.items()}
o, a, b = E['orig'], E['rc1'], E['coe']
somas = {}
for i, x in enumerate(o):
    s = x['atk1'] + x['atk2'] + x['atk3'] + x['atk4']
    somas[s] = somas.get(s, 0) + 1
print('soma atk1..4 no ORIGINAL (todas as 173 linhas):', somas)
for k in ('rc1', 'coe'):
    s2 = {}
    for x in E[k]:
        s = x['atk1'] + x['atk2'] + x['atk3'] + x['atk4']; s2[s] = s2.get(s, 0) + 1
    print('soma em', k, s2)
# o pow com peso 0 no original: o ataque existe?
REV = sorted(i for i in range(173) if a[i]['file'] != b[i]['file'] or a[i]['palno'] != b[i]['palno'] or a[i]['atk1'] != b[i]['atk1'] or a[i]['atk2'] != b[i]['atk2'] or a[i]['atk3'] != b[i]['atk3'] or a[i]['atk4'] != b[i]['atk4'])
print('linhas alteradas rc1->coe (enemy_param):', len(REV), REV)


def esp(x):
    return sum(x[f'atk{k}'] * x[f'atk{k}_pow'] for k in range(1, 5)) / 100.0


out = []
print('\nlinha | nome orig | nome coe | lv | atk% orig | atk% rc1 | atk% coe | pow | E[pow] orig/rc1/coe | slots com pow>0 e peso 0 (coe) | slots peso>0 e pow==0 (coe)')
for i in REV:
    x, y, z = o[i], a[i], b[i]
    w = lambda r: tuple(r[f'atk{k}'] for k in range(1, 5))
    pw = tuple(x[f'atk{k}_pow'] for k in range(1, 5))
    morto = [k for k in range(1, 5) if z[f'atk{k}_pow'] and not z[f'atk{k}']]
    novo = [k for k in range(1, 5) if z[f'atk{k}'] and not z[f'atk{k}_pow']]
    linha = dict(linha=i, nome_orig=x['_nome'], nome_rc1=y['_nome'], nome_coe=z['_nome'], lv=z['lv'], file=(x['file'], y['file'], z['file']),
                 atk_orig=w(x), atk_rc1=w(y), atk_coe=w(z), pow=pw, E_orig=esp(x), E_rc1=esp(y), E_coe=esp(z), morto=morto, peso_sem_pow=novo)
    out.append(linha)
    print(f"{i:3} | {x['_nome'][:18]:18} | {z['_nome'][:20]:20} | {z['lv']:2} | {w(x)} | {w(y)} | {w(z)} | {pw} | {esp(x):.1f}/{esp(y):.1f}/{esp(z):.1f} | {morto} | {novo}")
# conferir todas as outras colunas de combate identicas ao original em TODAS as linhas
COMB = ['power', 'zeni', 'exp', 'ap', 'item1', 'item2', 'item3', 'item4', 'atk1_pow', 'atk2_pow', 'atk3_pow', 'atk4_pow', 'lv', 'hp', 'mp', 'str', 'def', 'rec', 'tec', 'agi', 'luc',
        'sleep', 'bind', 'poison', 'dark', 'stan', 'panic', 'freez', 'dead', 'carrot', 'physics', 'slash', 'blast', 'atr_fire', 'atr_thunder', 'atr_ice', 'list', 'name_id']
dif = [(i, c) for i in range(173) for c in COMB if o[i][c] != b[i][c]]
print('\ncolunas de combate/recompensa/resistencia diferentes orig->coe:', dif[:20], len(dif))
dif = [(i, c) for i in range(173) for c in COMB if a[i][c] != b[i][c]]
print('colunas de combate/recompensa/resistencia diferentes rc1->coe:', dif[:20], len(dif))
json.dump(out, open(sys.argv[2], 'w'), indent=1, ensure_ascii=False)
