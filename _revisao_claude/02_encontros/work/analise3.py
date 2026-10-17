from analise import *
APRES = {'name_id','file','palno','size','shadow','atk1','atk2','atk3','atk4'}
cols = [c[0] for c in T['coe']['enemy_param']['colunas'] if c[0] in EP['coe'][0]]
print('colunas', cols)
for a,b in (('orig','coe'),('rc1','coe'),('orig','rc1')):
    bad = collections.defaultdict(list)
    for i in range(173):
        for c in cols:
            if c in APRES: continue
            if EP[a][i].get(c) != EP[b][i].get(c): bad[i].append((c,EP[a][i].get(c),EP[b][i].get(c)))
    print(a,'->',b,'campos de combate/recompensa alterados:', dict(bad) if bad else 'nenhum')
# atk weights / pow
for i in sorted(set(range(173))):
    e=EP['coe'][i]; o=EP['orig'][i]
    if e!=EP['rc1'][i]:
        w=[e[f'atk{k}'] for k in (1,2,3,4)]; p=[e[f'atk{k}_pow'] for k in (1,2,3,4)]; wo=[o[f'atk{k}'] for k in (1,2,3,4)]
        print(i, 'pesos coe',w,'rc1',[EP['rc1'][i][f'atk{k}'] for k in (1,2,3,4)],'orig',wo,'pow',p, 'size o/r/c', o['size'],EP['rc1'][i]['size'],e['size'],'shadow',o['shadow'],EP['rc1'][i]['shadow'],e['shadow'])
# nomes rc1 == coe nos revisados
for i in range(173):
    if EP['coe'][i]!=EP['rc1'][i]:
        a=nome('rc1',i+1); b=nome('coe',i+1)
        if a==b: print('nome inalterado', i, a)
# todos idiomas: nomes iguais?
for lang in ('US','FR','SP','GR','IT'):
    t=tabelas(R['coe'],lang); nm=t['character_name']['linhas']; ep=t['enemy_param']['linhas']
    d=[i for i in range(173) if ep[i]!=EP['coe'][i]]
    dn=[i for i in range(173) if EP['coe'][i]['name_id'] and nm[EP['coe'][i]['name_id']-1]!=NM['coe'][EP['coe'][i]['name_id']-1]]
    print(lang,'enemy_param difere do EN em',len(d),'linhas; nomes diferem em',len(dn))
