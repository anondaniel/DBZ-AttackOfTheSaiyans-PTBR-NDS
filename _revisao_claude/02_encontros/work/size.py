from analise import *
for n in ('orig','rc1','coe'):
    bad=collections.Counter()
    for x in CH[n]:
        sl=[v for v in x['args'][6:12] if isinstance(v,int) and 1<v<=173]
        if len(sl)>1:
            for v in sl:
                if EP[n][v-1]['size']==2: bad[(v-1,nome(n,v))]+=1
    print(n,'linhas tamanho 2 em grupos com >1 inimigo:', dict(bad))
# summon ids in atk_pow: which rows have pow equal to a valid id >100
for i,e in enumerate(EP['orig']):
    for k in (1,2,3,4):
        p=e[f'atk{k}_pow']
        if p>100: print('pow>100', i, nome('orig',i+1), f'atk{k}_pow={p}', 'pesos orig',[e[f"atk{j}"] for j in (1,2,3,4)],'rc1',[EP['rc1'][i][f"atk{j}"] for j in (1,2,3,4)],'coe',[EP['coe'][i][f"atk{j}"] for j in (1,2,3,4)], '-> alvo', nome('coe',p))
