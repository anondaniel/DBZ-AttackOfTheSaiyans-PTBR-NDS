from analise import *
import re
def sets_of(n):
    out=collections.defaultdict(list)  # arquivo -> list of sets
    cur=None; prev=None
    for x in CH[n]:
        a=x['args']
        if prev is None or x['arquivo']!=prev['arquivo'] or a[0] <= prev['args'][0]:
            cur=[]; out[x['arquivo']].append(cur)
        cur.append(x); prev=x
    return out
S = sets_of('coe')
def lv(i): return EP['coe'][i-1]['lv'] if i<=173 else BP['coe'][i-174]['lv']
rows=[]
for arq, ss in S.items():
    if '/cf1/' in arq or 'dbg' in arq: continue
    for k,s in enumerate(ss):
        ids=collections.Counter()
        flags=set()
        for x in s:
            for v in x['args'][6:12]:
                if isinstance(v,int) and v>1: ids[v]+=1
            flags.add((x['args'][12], x['args'][13]))
        lvs=[lv(i) for i in ids]
        rows.append((arq.split('/')[-1][:-3], k, min(lvs), max(lvs), sorted(ids), flags))
pickle.dump(rows, open('sets_coe.pkl','wb'))
for r in sorted(rows): print(r[0], 'set',r[1], 'lv',r[2],'-',r[3], [ (i, lv(i)) for i in r[4]], r[5] if any(f!=(None,None) for f in r[5]) else '')
