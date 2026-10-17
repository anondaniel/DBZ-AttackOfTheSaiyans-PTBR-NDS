from analise import *
from chr_paletas import paletas
import importlib.util
spec=importlib.util.spec_from_file_location('rv', BASE+'/12_Coerencia_Historia/revisao.py')
src=open(BASE+'/12_Coerencia_Historia/revisao.py',encoding='utf-8').read()
REV=eval(src[src.index('REVISAO = {')+len('REVISAO = '):src.index('}\n\ndef sha')+1])
# mapas (cf0) por linha
mp=collections.defaultdict(set)
for x in CH['coe']:
    if '/cf1/' in x['arquivo']: continue
    for v in x['args'][6:12]:
        if isinstance(v,int) and 1<v<=173: mp[v-1].add(x['mapa'])
def dist(c1,c2): return sum(abs(((c1>>s)&31)-((c2>>s)&31)) for s in (0,5,10))
for row,(model,name,why) in sorted(REV.items()):
    e=EP['coe'][row]; m=EP['coe'][model]
    pals=paletas(nds_rom.ler(R['coe'],f"btl/ene/{e['file']}.chr"))
    p=pals[e['palno']]; q=pals[m['palno']]
    nd=sum(1 for a,b in zip(p,q) if a!=b); tot=sum(dist(a,b) for a,b in zip(p,q))
    # menor distancia a qualquer paleta usada no mesmo mapa com mesmo arquivo
    juntos=[o for o in range(173) if o!=row and EP['coe'][o]['file']==e['file'] and mp[o]&mp[row]]
    mind=min([sum(dist(a,b) for a,b in zip(p,pals[EP['coe'][o]['palno']])) for o in juntos] or [None]) if juntos else None
    print(f"{row:3d} {name:22s} modelo {model:3d} {nome('coe',model+1):20s} cores_dif {nd:2d} soma_dist {tot:4d} | mesmo sprite no mesmo mapa: {[(o,nome('coe',o+1)) for o in juntos]} dist_min {mind}")
