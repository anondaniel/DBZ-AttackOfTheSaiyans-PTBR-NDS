from comum import *
import re, collections
d=rom('orig'); cam=nds_rom.caminhos(d)
scr=[c for c in cam if c.startswith('script/EN/') and c.endswith('.sb')]
print(len(scr)); print(sorted(set(c.split('/')[2] for c in scr)))
# map references in c-scripts
ref=collections.defaultdict(set)
for c in scr:
    b=nds_rom.ler(d,c)
    for m in re.finditer(rb"([a-z]{3}\d\d_\d\d)", b):
        ref[c.split('/')[-1][:-3]].add(m.group(1).decode())
for k in sorted(ref):
    if k.startswith('c') and k[1:3].isdigit():
        print(k, sorted(x for x in ref[k] if x!=k)[:20])
