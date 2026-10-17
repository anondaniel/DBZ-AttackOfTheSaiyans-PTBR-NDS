"""Mostra linhas de enemy_param (+nome) de ROMs. uso: python linhas.py rom1 [rom2 ...] -- i,j,k"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, __import__('os').path.dirname(__file__))
sys.path.insert(1, r'C:\Projetos\09_Dragon_Ball_Z_Attack_of_the_Saiyans\11_Projeto_Recuperado\scripts')
import nds_rom
from bdat import ler_container
k = sys.argv.index('--'); roms = sys.argv[1:k]; idx = [int(x) for x in sys.argv[k + 1].split(',')]
for r in roms:
    d = open(r, 'rb').read()
    for lang in ('US', 'EN'):
        t = ler_container(nds_rom.ler(d, f'btl/bdat/{lang}/bdat.bin'))
        ep = t['enemy_param']['linhas']; nm = t['character_name']['linhas']; col = t['character_name']['colunas'][0][0]
        for i in idx:
            e = ep[i]
            print(r.split('/')[-1], lang, i, nm[e['name_id'] - 1][col], {k2: e[k2] for k2 in list(e)[:22]})
