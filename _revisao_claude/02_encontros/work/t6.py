from comum import *
import pickle, collections
t=tabelas(rom('orig')); bp=t['boss_param']['linhas']; nm=t['character_name']['linhas']
print([c[0] for c in t['boss_param']['colunas']][:12])
for i,b in enumerate(bp): print(i, i+174, b.get('name_id'), nm[b['name_id']-1]['en'] if b.get('name_id') else '', b.get('file'), b.get('palno'), b.get('lv'))
r=pickle.load(open('chamadas_orig.pkl','rb'))
print(collections.Counter((x['args'][12],) for x in r))
print(collections.Counter((x['args'][13],) for x in r))
