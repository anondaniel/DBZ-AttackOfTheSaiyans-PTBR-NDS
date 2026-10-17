"""Distancias de paleta entre variantes do mesmo sprite (mesmas metricas da etapa 13).

  - mesmo mapa (verificar.py da 13): pares de linhas usadas no mesmo script de encontro
    (args 2..11 do SetEnemyParty), mesmo arquivo, paleta diferente. Limite >= 100.
  - mesmo mapa (build.py da 13): idem com mapas_por_linha (slots + lista de tipos). Limite >= 100.
  - jogo inteiro (build.py da 13, T_GLOBAL): qualquer par de linhas com nome que usam o mesmo
    arquivo com paletas diferentes. Limite >= 80.
Para as linhas pedidas, devolve o minimo de cada linha em cada metrica.
uso: python -B distancias.py [rom.nds]   (padrao: a ROM 13.1; compara com a ROM 13) -> verificacao/distancias.txt
"""
import sys, os, collections, itertools
sys.dont_write_bytecode = True
from comum import *
import nds_rom
from bdat import ler_container
from chr_paletas import paletas
from dados_inimigos import encontros, mapas_por_linha, dist_pal

T_MAPA, T_GLOBAL = 100, 80


def medir(d):
    t = ler_container(nds_rom.ler(d, 'btl/bdat/EN/bdat.bin'))
    ep = t['enemy_param']['linhas']
    pals = {}
    def pal(i):
        f = ep[i]['file']
        if f not in pals:
            pals[f] = paletas(nds_rom.ler(d, f'btl/ene/{f}.chr'))
        return pals[f][ep[i]['palno']]
    G = encontros(d)
    por_mapa = collections.defaultdict(set)
    for g in G:
        for v in g['args'][2:12]:
            if isinstance(v, int) and 1 < v <= 173:
                por_mapa[g['mapa']].add(v - 1)
    mpl = mapas_por_linha(G)
    cam = nds_rom.caminhos(d)
    # linhas com nome cujo sprite existe (algumas linhas sem uso apontam para arquivos inexistentes)
    com_nome = [i for i, e in enumerate(ep) if e['name_id'] and f"btl/ene/{e['file']}.chr" in cam]
    pares_mapa_v = {}
    for m, ids in por_mapa.items():
        for i, j in itertools.combinations(sorted(ids), 2):
            if ep[i]['file'] == ep[j]['file'] and ep[i]['palno'] != ep[j]['palno']:
                pares_mapa_v[(i, j)] = dist_pal(pal(i), pal(j))
    pares_mapa_b, pares_glob = {}, {}
    for i, j in itertools.combinations(com_nome, 2):
        if ep[i]['file'] != ep[j]['file'] or ep[i]['palno'] == ep[j]['palno']:
            continue
        dd = dist_pal(pal(i), pal(j))
        pares_glob[(i, j)] = dd
        if mpl[i] & mpl[j]:
            pares_mapa_b[(i, j)] = dd
    return {'mapa_verificar': pares_mapa_v, 'mapa_build': pares_mapa_b, 'global': pares_glob}


def minimo_linha(pares, r):
    v = [(dd, i if j == r else j) for (i, j), dd in pares.items() if r in (i, j)]
    return min(v) if v else (None, None)


if __name__ == '__main__':
    from pele131 import PELE, ROUPA
    nova = rom(sys.argv[1]) if len(sys.argv) > 1 else rom('nova')
    base = rom('13')
    A, B = medir(base), medir(nova)
    linhas = ['# Distancias de paleta: ROM 13 -> ROM 13.1', '']
    for k, lim in (('mapa_verificar', T_MAPA), ('mapa_build', T_MAPA), ('global', T_GLOBAL)):
        ma, mb = min(A[k].values()), min(B[k].values())
        linhas.append(f'{k}: menor na 13 = {ma}, menor na 13.1 = {mb} (limite {lim}) -> {"OK" if mb >= lim else "FALHA"}')
        linhas.append('   5 menores (13.1): ' + str(sorted((v, a) for a, v in B[k].items())[:5]))
    linhas += ['', 'por linha corrigida (menor distancia, linha vizinha): 13 -> 13.1']
    for r in sorted(set(PELE) | set(ROUPA)):
        linhas.append(f'  {r:3d}  ' + '  |  '.join(f'{k}: {minimo_linha(A[k], r)} -> {minimo_linha(B[k], r)}' for k in A))
    falhas = [k for k, lim in (('mapa_verificar', T_MAPA), ('mapa_build', T_MAPA), ('global', T_GLOBAL)) if min(B[k].values()) < lim]
    linhas.append(''); linhas.append('FALHAS: ' + str(falhas))
    open(os.path.join(PASTA18, 'verificacao', 'distancias.txt'), 'w', encoding='utf-8').write(chr(10).join(linhas) + chr(10))
    print(chr(10).join(linhas))
    sys.exit(1 if falhas else 0)
