from analise import *
r = CH['coe']
cat = collections.Counter('cutscene(cf1)' if '/cf1/' in x['arquivo'] else ('debug' if x['mapa'].startswith('dbg') else 'mapa(cf0)') for x in r)
print(cat)
print('scripts por tipo', collections.Counter('cf1' if '/cf1/' in a else ('dbg' if 'dbg' in a else 'cf0') for a in {x['arquivo'] for x in r}))
uniq = {tuple(x['args']) for x in r}
print('grupos unicos (args identicos)', len(uniq))
g = json.load(open(BASE+'/12_Coerencia_Historia/grupos.json',encoding='utf-8'))
print('grupos.json', len(g), len({x['mapa'] for x in g}))
mine = [{'mapa':x['mapa'],'offset':x['pos'],'ids':[v-1 for v in x['args'][6:12] if isinstance(v,int) and 1<v<=173]} for x in CH['rc1']]
print('grupos.json == meu decode rc1:', mine == g)
# revisao json
rv = json.load(open(BASE+'/12_Coerencia_Historia/revisao_inimigos.json',encoding='utf-8'))
print('revisao entries', len(rv), 'animais', sum(1 for x in rv if x['animal_original']!='Variante de Saibaman original'))
# diff rows rc1 vs coe
dif = [i for i in range(173) if EP['rc1'][i]!=EP['coe'][i]]
print('linhas enemy_param alteradas rc1->coe', len(dif), dif)
dif2 = [i for i in range(173) if EP['orig'][i]!=EP['coe'][i]]
print('linhas alteradas orig->coe', len(dif2))
bd = [i for i in range(len(BP['coe'])) if BP['rc1'][i]!=BP['coe'][i]]
print('boss_param alterado rc1->coe', bd)
nd = [i for i in range(len(NM['coe'])) if NM['rc1'][i]!=NM['coe'][i]]
print('nomes alterados rc1->coe', len(nd))
