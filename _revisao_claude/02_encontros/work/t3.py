from encontros import *
import collections, pickle
out={}
for n in ('orig','rc1','coe'):
    d=rom(n); r=chamadas(d); t=tabelas(d); ep=t['enemy_param']['linhas']
    pickle.dump(r, open(f'chamadas_{n}.pkl','wb'))
    def f(i): return ep[i-1]['file'] if 1<=i<=len(ep) else f'BOSS{i}'
    bad=[]; notin=0
    for x in r:
        a=x['args']; ty=[v for v in a[2:6] if isinstance(v,int)]; sl=[v for v in a[6:12] if isinstance(v,int) and v>0]
        if set(sl)-set(ty): notin+=1
        fs=set(f(v) for v in sl); ft=set(f(v) for v in ty if v!=1 or a[2]==1)
        if fs-ft: bad.append((x['mapa'],a, sorted(fs-ft)))
    print(n, 'grupos',len(r),'slot fora de types',notin,'arquivo de slot nao coberto por types',len(bad))
    for b in bad[:60]: print('   ',b)
