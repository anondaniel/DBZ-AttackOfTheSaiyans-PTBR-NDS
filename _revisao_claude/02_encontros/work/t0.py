from comum import *
import zlib
for n in ('orig','rc1','coe'):
    d=rom(n); print(n, len(d), sha(d), hex(zlib.crc32(d)))
t=tabelas(rom('coe'))
print(list(t.keys()))
ep=t['enemy_param']
print([c[0] for c in ep['colunas']])
print(ep['linhas'][0])
cn=t['character_name']; print([c[0] for c in cn['colunas']]); print(cn['linhas'][:3])
