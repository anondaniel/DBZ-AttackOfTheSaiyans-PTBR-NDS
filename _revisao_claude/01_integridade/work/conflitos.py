import sys, struct, collections
sys.path.insert(0, sys.argv[1])
exec(open(sys.argv[1] + '/grupos.py', encoding='utf-8').read().split("print('chamadas")[0])
sys.path.insert(1, r'C:\Projetos\09_Dragon_Ball_Z_Attack_of_the_Saiyans\11_Projeto_Recuperado\scripts')
from bdat import ler_container
t = ler_container(FS['btl/bdat/EN/bdat.bin'])
ep = t['enemy_param']['linhas']; nm = t['character_name']['linhas']; col = t['character_name']['colunas'][0][0]
app = lambda i: (ep[i]['file'], ep[i]['palno'])
nome = lambda i: nm[ep[i]['name_id'] - 1][col] if ep[i]['name_id'] else ''
ok = lambda x: isinstance(x, int) and 1 < x <= 173
so_tipos = collections.Counter(); grupos_extra = 0; conf = set()
for m, o, argc, a in grupos:
    s = {x - 1 for x in a[6:12] if ok(x)}
    tp = {x - 1 for x in a[2:6] if ok(x)}
    extra = tp - s
    if extra:
        grupos_extra += 1
        for e in extra: so_tipos[e] += 1
    ids = s | tp
    for i in ids:
        for j in ids:
            if i < j and ((app(i) == app(j)) != (nome(i) == nome(j))):
                conf.add((m, i, nome(i), app(i), j, nome(j), app(j)))
print('grupos com IDs so na lista de tipos (args[2:6]) e fora dos slots:', grupos_extra)
print('linhas afetadas (linha: n grupos, nome atual):', {k: (v, nome(k)) for k, v in sorted(so_tipos.items())})
print('conflitos aparencia/nome considerando tipos+slots:', len(conf))
for c in sorted(conf)[:30]: print('  ', c)
