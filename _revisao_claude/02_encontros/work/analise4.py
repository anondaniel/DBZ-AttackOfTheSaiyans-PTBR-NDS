from analise import *
def info_chr(n, f):
    d = nds_rom.ler(R[n], f'btl/ene/{f}.chr')
    c = ler_chr(d); err=[]; an = ler_anims(d, c['fim_tiles'], err)
    return len(c['pals']), [len(a) for a in an], err
cache={}
def ic(n,f):
    k=(n,f)
    if k not in cache:
        try: cache[k]=info_chr(n,f)
        except Exception as e: cache[k]=(None,None,[repr(e)])
    return cache[k]
used = set()
for x in CH['coe']:
    for v in x['args'][2:12]:
        if isinstance(v,int) and 2<=v<=173: used.add(v-1)
print('linhas de enemy_param usadas (slots+tipos):', len(used))
# regra no original: n anims vs max atk index
rel=collections.Counter()
for i,e in enumerate(EP['orig']):
    if not e['name_id']: continue
    npal, an, err = ic('orig', e['file'])
    mx = max([k for k in (1,2,3,4) if e[f'atk{k}']>0] or [0])
    rel[(len(an) if an else None, mx)] += 1
print('orig (n_anims, maior atk usado):', sorted(rel.items(), key=lambda x: str(x)))
probs=[]
for n in ('rc1','coe'):
    for i in sorted(used):
        e=EP[n][i]
        npal, an, err = ic(n, e['file'])
        mx = max([k for k in (1,2,3,4) if e[f'atk{k}']>0] or [0])
        p=[]
        if npal is None or err: p.append(f'erro chr {err[:2]}')
        else:
            if e['palno']>=npal: p.append(f'palno {e["palno"]}>= {npal}')
            if len(an) < 3+mx: p.append(f'anims {len(an)} < 3+{mx}')
            if any(x==0 for x in an): p.append('anim vazia')
        if p: probs.append((n,i,nome(n,i+1),e['file'],e['palno'],p))
print('problemas graficos:', probs if probs else 'nenhum')
# paletas: cada (file,palno) usada por mais de uma linha?
for n in ('rc1','coe'):
    ap=collections.defaultdict(list)
    for i in sorted(used): ap[(EP[n][i]['file'],EP[n][i]['palno'])].append(i)
    print(n,'aparencias compartilhadas por >1 linha:', {k:[(i,nome(n,i+1)) for i in v] for k,v in ap.items() if len(v)>1})
# arquivos chr alterados rc1->coe: paletas antigas preservadas?
cam=nds_rom.caminhos(R['coe'])
for f in sorted(c for c in cam if c.startswith('btl/ene/')):
    a=nds_rom.ler(R['rc1'],f); b=nds_rom.ler(R['coe'],f)
    if a!=b:
        pa=paletas(a); pb=paletas(b)
        print(f, 'paletas', len(pa),'->',len(pb), 'antigas intactas', pb[:len(pa)]==pa, 'resto igual', a[8+len(pa)*32:]==b[8+len(pb)*32:])
