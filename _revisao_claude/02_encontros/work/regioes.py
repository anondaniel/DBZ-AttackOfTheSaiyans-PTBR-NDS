from analise import *
import re
NOMES = {'tut':'Ilha de Treinamento','bam':'Floresta de Bambu','est':'Cidade do Leste (est07-09)','pao':'Montanha Paozu','krd':'Travessia Divina','bud':'Templo das Artes Marciais','gyu':'Castelo do Cutelo','gog':'Montanha dos Cinco Elementos','kiu':'Vulcão Kiwi','fur':'Monte Frappe','spi':'Ermo do Espinafre','kou':'Deserto Break','hii':'Planície Holly','sen':'Fonte do Eremita','enm':'Palácio do Senhor Enma','sna':'Mansão da Princesa','for':'Floresta (Outro Mundo)','yun':'Planalto Yunzabit','ben':'Vaso do Diabo','mas':'Torre Muscle','kai':'Caverna dos Piratas','snd':'Deserto','pir':'Castelo do Pilaf','nem':'Ruínas de Nemuria','mut':'Campo do Mutaito','nap':'Ermo Páprica','las':'Ermo Gizard','ges':'Esgoto (Cid. Oeste)','dbg':'debug'}
# capitulo de cada mapa: menor capitulo de c-script que o referencia
d=R['orig']; cam=nds_rom.caminhos(d)
cap=collections.defaultdict(lambda:99)
for c in cam:
    m=re.match(r'script/EN/cf1/c(\d\d)/c\d{4}_\d\d\.sb',c)
    if not m: continue
    b=nds_rom.ler(d,c)
    for mm in re.finditer(rb"([a-z]{3})(\d\d)_\d\d", b):
        k=mm.group(1).decode()+mm.group(2).decode()
        cap[k]=min(cap[k],int(m.group(1)))
def setsplit(n):
    out=collections.defaultdict(list); prev=None
    for x in CH[n]:
        if prev is None or x['arquivo']!=prev['arquivo'] or x['args'][0]<=prev['args'][0]:
            out[x['arquivo']].append([])
        out[x['arquivo']][-1].append(x); prev=x
    return out
S=setsplit('coe')
def lv(i): return EP['coe'][i-1]['lv'] if i<=173 else BP['coe'][i-174]['lv']
TROC=set(i for i in range(173) if EP['coe'][i]!=EP['orig'][i])
reg=collections.defaultdict(lambda: collections.defaultdict(set))
mapcap={}
for arq,ss in S.items():
    if '/cf1/' in arq: continue
    mp=arq.split('/')[-1][:-3]; pre=mp[:3]; key=mp[:5]
    mapcap[mp]=cap[key]
    for s in ss:
        ids=set(v for x in s for v in x['args'][6:12] if isinstance(v,int) and v>1)
        ev = all(x['args'][12] is not None for x in s)
        if all(v>173 for v in ids): tier='chefe'
        else:
            mx=max(lv(v) for v in ids if v<=173)
            tier='tardio(nv>=46)' if min(lv(v) for v in ids if v<=173)>=46 or (mx>=46 and pre not in('mut','nem','las','nap')) else 'historia'
        for v in ids:
            reg[pre][(tier, 'evento' if ev else 'aleat')].add(v)
caps={}
for mp,c in mapcap.items(): caps.setdefault(mp[:3],set()).add(c)
out=[]
for pre in sorted(reg, key=lambda p:min(caps[p])):
    out.append(f"## {pre} {NOMES.get(pre,'?')} cap {sorted(caps[pre])}")
    for k in sorted(reg[pre]):
        ids=sorted(reg[pre][k])
        tro=[f"{v-1}:{nome('orig',v)}|{nome('rc1',v)}|{nome('coe',v)}(nv{lv(v)})" for v in ids if v<=173 and v-1 in TROC]
        outros=[f"{nome('coe',v)}(nv{lv(v)})" for v in ids if not (v<=173 and v-1 in TROC)]
        out.append(f"  {k}: TROCADOS: {'; '.join(tro)}\n      outros: {', '.join(outros)}")
open('regioes.txt','w',encoding='utf-8').write('\n'.join(out))
