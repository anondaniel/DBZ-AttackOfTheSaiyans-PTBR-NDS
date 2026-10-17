import sys, struct
sys.path.insert(0, sys.argv[1])
exec(open(sys.argv[1] + '/grupos.py', encoding='utf-8').read().split("print('chamadas")[0])
for m, o, argc, a in grupos:
    if argc == 15 and 1 in a[6:12]:
        k_ = [c for c in FS if c.startswith('script/EN/') and c.endswith('/' + m + '.sb')][0]; d = FS[k_]; off0 = struct.unpack_from('<I', d, 8)[0]
        print(m, hex(o), a[:12], d[o - 40:o + 2].hex(' '))
