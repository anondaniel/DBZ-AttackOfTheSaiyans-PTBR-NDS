"""[etapa 18 / 13.1] Copia do verificar.py da etapa 13, com saida em 18_Pele_e_Texto_Boot/verificacao
e uma secao a mais: diferenca 13 -> 13.1 (diff_13.txt).

Re-executa as verificacoes estaticas das revisoes 01 (integridade) e 02
(encontros) sobre a ROM nova, comparando com o original, a rc.1 e a etapa 12.
As de texto (revisao 03) ficam em texto/verificar_textos.py.
Saidas: verificacao/integridade.txt, verificacao/encontros.txt, verificacao/resumo.json
uso: python -B verificar.py [rom]
"""
import sys, os, json, struct, collections, itertools
sys.dont_write_bytecode = True
from comum import *
import nds_rom
from bdat import ler_container
from dados_inimigos import (ene_eff, info_chr, encontros, mapas_por_linha, dist_pal, pesos, pows,
                            enemy_rows, invoca)
from plano13 import PLANO13, REVERTIDAS

VER = os.path.join(PASTA18, 'verificacao')
IDIOMAS = ('EN', 'US', 'FR', 'SP', 'GR', 'IT')
TEXTO_TABS = ('btl_mes_', 'cf_mes_', 'use_item_mes', 'btl_acc_mes', 'pt_eqp_mes', 'key_item_mes', 'character_name')


class Log:
    def __init__(self, path):
        self.f = open(path, 'w', encoding='utf-8'); self.falhas = []
    def __call__(self, *a):
        s = ' '.join(str(x) for x in a); print(s); self.f.write(s + '\n')
    def check(self, cond, msg):
        self(('OK   ' if cond else 'FALHA') + ' ' + msg)
        if not cond: self.falhas.append(msg)
        return cond


def arquivos(d):
    cam = nds_rom.caminhos(d)
    return {c: nds_rom.fat_entrada(d, fid) for c, fid in cam.items()}


def integridade(nova, L):
    rc1, orig, coe = rom('rc1'), rom('orig'), rom('coe')
    L('# Integridade (refaz a revisao 01 sobre a ROM nova)')
    L('SHA-256', sha256(nova), '| CRC32 %08x' % crc32(nova), '| bytes', len(nova))
    u32, u16 = nds_rom.u32, nds_rom.u16
    L.check(len(nova) == 134217728 and nova[0x14] == 0x0A, 'tamanho 128 MiB = capacidade do cabeçalho')
    L.check(nova[0:0x10] == rc1[0:0x10], 'título/código/fabricante iguais (DB KAI RPG / BRPE / AF)')
    for nome, o, s in (('ARM9', 0x20, 0x2C), ('ARM7', 0x30, 0x3C)):
        L.check(nova[u32(nova, o):u32(nova, o) + u32(nova, s)] == orig[u32(orig, o):u32(orig, o) + u32(orig, s)],
                f'{nome} idêntico ao original')
    L.check(nova[u32(nova, 0x40):u32(nova, 0x40) + u32(nova, 0x44)] == orig[u32(orig, 0x40):u32(orig, 0x40) + u32(orig, 0x44)], 'FNT idêntica ao original')
    L.check(u32(nova, 0x50) == 0 and u32(nova, 0x54) == 0 and u32(nova, 0x58) == 0 and u32(nova, 0x5C) == 0, 'sem overlays (como o original)')
    b = u32(nova, 0x68)
    L.check(nova[b:b + 0x840] == orig[b:b + 0x840], 'banner idêntico')
    L.check(u16(nova, 0x15E) == nds_rom.crc16(nova[:0x15E]), 'CRC16 do cabeçalho (0x15E) válido')
    L.check(u16(nova, 0x15C) == u16(orig, 0x15C), 'CRC do logotipo igual ao original')
    hdr = [hex(i) for i in range(0x1000) if nova[i] != rc1[i]]
    L.check(set(hdr) <= {'0x80', '0x81', '0x82', '0x83', '0x15e', '0x15f'}, f'cabeçalho: só tamanho usado/CRC16 mudaram vs rc.1 {hdr}')
    fa = arquivos(nova)
    ints = sorted((a, z, c) for c, (a, z) in fa.items() if z > a)
    L.check(all(0 <= a <= z <= len(nova) for a, z, _ in ints), 'FAT: todas as entradas dentro da ROM')
    sobre = [(x[2], y[2]) for x, y in zip(ints, ints[1:]) if y[0] < x[1]]
    L.check(not sobre, f'FAT: nenhuma sobreposição {sobre[:3]}')
    usado = u32(nova, 0x80)
    L.check(usado == max(z for _, z, _ in ints), 'tamanho usado (0x80) = maior fim na FAT')
    L.check(all(x == 0xFF for x in nova[usado:]), 'cauda até 128 MiB toda em 0xFF')
    # diferenca por arquivo
    fr = arquivos(rc1)
    mud = sorted(c for c in fa if nds_rom.ler(nova, c) != nds_rom.ler(rc1, c))
    L(f'arquivos diferentes da rc.1: {len(mud)}')
    for c in mud:
        L('   ', c, fr[c][1] - fr[c][0], '->', fa[c][1] - fa[c][0])
    tipos = collections.Counter(c.rsplit('.', 1)[-1] for c in mud)
    L('   por tipo:', dict(tipos))
    L.check(all(c.startswith(('btl/ene/ene', 'btl/bdat/', 'script/US/', 'script/EN/')) for c in mud),
            'só mudaram .chr de inimigo, bdat.bin e scripts US/EN')
    # bytes fora dos arquivos alterados
    mask = bytearray(len(nova))
    for c in mud:
        for (a, z) in (fa[c], fr[c]):
            mask[a:z] = b'\x01' * (z - a)
    for i in (0x80, 0x81, 0x82, 0x83, 0x15E, 0x15F):
        mask[i] = 1
    fat = u32(nova, 0x48); cam = nds_rom.caminhos(nova)
    for c in mud:  # entradas da FAT dos arquivos alterados
        mask[fat + cam[c] * 8: fat + cam[c] * 8 + 8] = b'' * 8
    import numpy as np
    m = np.frombuffer(bytes(mask), dtype=np.uint8).astype(bool)
    dif = np.frombuffer(nova, dtype=np.uint8) != np.frombuffer(rc1, dtype=np.uint8)
    fora = int((dif & ~m).sum())
    L.check(fora == 0, f'nenhum byte diferente da rc.1 fora dos arquivos alterados (posições antigas e novas) e do cabeçalho: {fora}')
    # tabelas
    for lang in IDIOMAS:
        tn = ler_container(nds_rom.ler(nova, f'btl/bdat/{lang}/bdat.bin'))
        tr = ler_container(nds_rom.ler(rc1, f'btl/bdat/{lang}/bdat.bin'))
        dif_t = [n for n in tr if tr[n]['linhas'] != tn[n]['linhas']]
        perm = {'enemy_param', 'character_name'} | ({n for n in tr if n.startswith(TEXTO_TABS)} if lang in ('US', 'EN') else set())
        L.check(set(dif_t) <= perm and tn.keys() == tr.keys(), f'bdat {lang}: tabelas alteradas {sorted(dif_t)}')
        L.check(tn['boss_param']['linhas'] == tr['boss_param']['linhas'] and tn['player_param']['linhas'] == tr['player_param']['linhas'],
                f'bdat {lang}: boss_param e player_param idênticos')
    eo = ler_container(nds_rom.ler(orig, 'btl/bdat/US/bdat.bin'))['enemy_param']['linhas']
    en = ler_container(nds_rom.ler(nova, 'btl/bdat/US/bdat.bin'))['enemy_param']['linhas']
    APRES = {'file', 'palno', 'size', 'shadow', 'atk1', 'atk2', 'atk3', 'atk4'}
    comb = [(i, c) for i in range(173) for c in en[i] if c not in APRES and en[i][c] != eo[i][c]]
    L.check(not comb, f'enemy_param: nível/HP/MP/atributos/EXP/zeni/AP/itens/atk_pow/resistências/name_id = original nas 173 linhas {comb[:5]}')
    L.check(all(sum(pesos(e)) == 100 for e in en), 'atk1-atk4 somam 100 nas 173 linhas')
    difp = [i for i in range(173) if pesos(en[i]) != pesos(eo[i])]
    L(f'linhas com atk1-atk4 diferentes do ORIGINAL: {len(difp)} {difp}')
    return mud


def encontros_rev(nova, L):
    rc1, orig, coe = rom('rc1'), rom('orig'), rom('coe')
    L('# Encontros e coerência dos inimigos (refaz a revisão 02 + checagens novas)')
    G = {n: encontros(d) for n, d in (('orig', orig), ('rc1', rc1), ('coe', coe), ('nova', nova))}
    L.check(len(G['nova']) == 2143 and all(g['argc'] == 15 for g in G['nova']), f"{len(G['nova'])} chamadas SetEnemyParty, todas com 15 argumentos")
    L.check([(g['mapa'], g['args']) for g in G['nova']] == [(g['mapa'], g['args']) for g in G['orig']], 'grupos idênticos ao original (byte a byte nos argumentos)')
    L(f"scripts com grupos: {len({g['mapa'] for g in G['nova']})}; grupos distintos: {len({tuple(g['args']) for g in G['nova']})}")
    T = {n: ler_container(nds_rom.ler(d, 'btl/bdat/EN/bdat.bin')) for n, d in (('orig', orig), ('rc1', rc1), ('coe', coe), ('nova', nova))}
    EP = {n: T[n]['enemy_param']['linhas'] for n in T}
    BP = {n: T[n]['boss_param']['linhas'] for n in T}
    NM = {n: T[n]['character_name']['linhas'] for n in T}
    D = {'orig': orig, 'rc1': rc1, 'coe': coe, 'nova': nova}
    def nome(n, i):
        if 1 <= i <= 173:
            e = EP[n][i - 1]; return NM[n][e['name_id'] - 1]['en'] if e['name_id'] else f'(vazio {i})'
        b = BP[n][i - 174]; return '[CHEFE] ' + (NM[n][b['name_id'] - 1]['en'] if b['name_id'] else '')
    def arq(n, i):
        return EP[n][i - 1]['file'] if i <= 173 else BP[n][i - 174]['file']
    # IDs validos
    inval = []
    for g in G['nova']:
        for v in [x for x in g['args'][2:12] if isinstance(x, int) and x > 1]:
            if not (2 <= v <= 228) or (v <= 173 and not EP['nova'][v - 1]['name_id']):
                inval.append((g['mapa'], v))
    L.check(not inval, f'IDs válidos (2..228, linhas com nome) em slots e lista de tipos {inval[:5]}')
    vaz = [g for g in G['nova'] if not [v for v in g['args'][6:12] if isinstance(v, int) and v > 1]]
    L.check(not vaz, 'nenhum grupo sem inimigo real')
    # pre-carga: sprite de slot que nao esta entre os tipos listados.
    # Metrica A (estrita): so IDs reais (>1) nos slots. Metrica B (a da revisao 02):
    # conta tambem o valor 1 dos slots (marcador de vazio/reserva de invocacao)
    # como se fosse o Saibaman basico (ene001_01).
    def sem_pre(n, com_marcador):
        c = 0; ex = []
        for g in G[n]:
            tipos = {arq(n, v) for v in g['args'][2:6] if isinstance(v, int) and 1 < v <= 228}
            slots = [v for v in g['args'][6:12] if isinstance(v, int) and (1 if com_marcador else 2) <= v <= 228]
            if any(arq(n, v) not in tipos for v in slots):
                c += 1; ex.append(g['mapa'])
        return c, ex
    cont = {n: sem_pre(n, False) for n in G}
    contB = {n: sem_pre(n, True) for n in G}
    L(f"grupos com sprite de slot fora da lista de tipos (pré-carga), métrica estrita (só IDs reais): original {cont['orig'][0]}, rc.1 {cont['rc1'][0]}, etapa 12 {cont['coe'][0]}, nova {cont['nova'][0]}")
    L(f"   mesma contagem pela métrica da revisão 02 (conta o marcador 1 como Saibaman ene001_01): original {contB['orig'][0]}, rc.1 {contB['rc1'][0]}, etapa 12 {contB['coe'][0]}, nova {contB['nova'][0]}")
    L.check(cont['nova'][0] == cont['rc1'][0] == cont['orig'][0], 'pré-carga (métrica estrita): igual à rc.1 e ao original')
    L.check(set(cont['nova'][1]) <= set(cont['orig'][1]), 'os grupos que sobram são os mesmos do jogo original')
    L('   mapas (nova):', sorted(set(cont['nova'][1])))
    L('   métrica B, mapas (nova):', sorted(set(contB['nova'][1])))
    # Saibamen do capitulo 14
    ev = [g for g in G['nova'] if g['args'][12] == 41 and 2 in g['args'][6:12]]
    L(f"grupos de evento (arg12=41) com o ID 2: {len(ev)} em {sorted({g['mapa'] for g in ev})}")
    L.check(nome('nova', 2) == 'J. Sai' and arq('nova', 2) == 'ene001_01' and EP['nova'][1] == EP['orig'][1],
            f"ID 2 (linha 1) = '{nome('nova', 2)}' com sprite {arq('nova', 2)}, linha idêntica ao original")
    for i in REVERTIDAS:
        L.check(EP['nova'][i] == EP['rc1'][i] == EP['orig'][i] and nome('nova', i + 1) == nome('rc1', i + 1),
                f"linha {i} ({nome('nova', i + 1)}) = rc.1 = original")
    for lang in ('US', 'FR', 'SP', 'GR', 'IT'):
        t = ler_container(nds_rom.ler(nova, f'btl/bdat/{lang}/bdat.bin'))
        L.check(t['enemy_param']['linhas'] == EP['nova'], f'enemy_param {lang} = EN')
    # graficos e pesos
    eff = ene_eff(nova)
    L.check(eff == ene_eff(orig), 'eneEff.bin (efeito dos golpes por linha) idêntico ao original')
    usados = set()
    for g in G['nova']:
        for v in g['args'][2:12]:
            if isinstance(v, int) and 2 <= v <= 173: usados.add(v - 1)
    prob = []
    for i in sorted(usados):
        e = EP['nova'][i]; ic = info_chr(nova, e['file'])
        if ic is None: prob.append((i, 'chr inexistente')); continue
        if e['palno'] >= ic['npal']: prob.append((i, 'palno'))
        if ic['anims'] is None:
            if e['file'] != 'ene011_01': prob.append((i, 'anim', ic['erros'][:1]))
            continue
        if any(x == 0 for x in ic['anims']): prob.append((i, 'anim vazia'))
        for k in range(4):
            if e[f'atk{k+1}'] > 0:
                if 3 + k >= len(ic['anims']): prob.append((i, f'slot {k+1} sem animação'))
                if not eff[i, k]: prob.append((i, f'slot {k+1} com peso e sem golpe no eneEff'))
    L(f'linhas usadas em encontros: {len(usados)}')
    L.check(not prob, f'sprites/paletas/animações válidas e todo slot com peso tem animação e golpe definido {prob[:8]}')
    for n in ('orig', 'rc1', 'coe'):
        q = [(i, k + 1) for i in sorted(usados) for k in range(4) if EP[n][i][f'atk{k+1}'] > 0 and not eff[i, k]]
        L(f'   (comparação) {n}: slots com peso e sem golpe no eneEff: {len(q)} {q}')
    inv = [(i, k + 1, EP['nova'][i][f'atk{k+1}_pow']) for i in range(173) for k in range(4) if EP['nova'][i][f'atk{k+1}'] > 0 and invoca(eff, i, k)]
    L('slots de INVOCAÇÃO com peso > 0 (linha, slot, ID invocado):', inv)
    L.check(all(2 <= p <= 173 and EP['nova'][p - 1]['name_id'] for _, _, p in inv), 'todas as invocações apontam para linhas válidas')
    tro = sorted(PLANO13)
    falta = []
    for g in G['nova']:
        tipos = {v for v in g['args'][2:6] if isinstance(v, int)}
        for v in {x for x in g['args'][6:12] if isinstance(x, int) and 1 < x <= 173}:
            for i, k, p in inv:
                if i == v - 1 and p not in tipos and p != v:
                    falta.append((g['mapa'], v, p))
    L.check(not falta, f'em todo grupo com invocador, o invocado está na lista de tipos (pré-carga) ou é o próprio {sorted(set(falta))[:6]}')
    L('invocações nas linhas trocadas:', [(i, k, p, nome('nova', p)) for i, k, p in inv if i in tro])
    # aparencia unica, conflitos, distancias
    ap = collections.defaultdict(list)
    for i in sorted(usados): ap[(EP['nova'][i]['file'], EP['nova'][i]['palno'])].append(i)
    L.check(all(len(v) == 1 for v in ap.values()), f'cada linha usada tem aparência (arquivo, paleta) própria {[v for v in ap.values() if len(v) > 1][:3]}')
    por_mapa = collections.defaultdict(set)
    for g in G['nova']:
        for v in g['args'][2:12]:
            if isinstance(v, int) and 1 < v <= 173: por_mapa[g['mapa']].add(v - 1)
    confl = []; perto = []
    pals = lambda i: info_chr(nova, EP['nova'][i]['file'])['pals'][EP['nova'][i]['palno']]
    for m, ids in por_mapa.items():
        for i, j in itertools.combinations(sorted(ids), 2):
            a = (EP['nova'][i]['file'], EP['nova'][i]['palno']) == (EP['nova'][j]['file'], EP['nova'][j]['palno'])
            b = nome('nova', i + 1) == nome('nova', j + 1)
            if a != b: confl.append((m, i, j))
            if EP['nova'][i]['file'] == EP['nova'][j]['file'] and not a:
                perto.append((dist_pal(pals(i), pals(j)), m, i, j))
    L.check(not confl, f'nenhum mapa com mesma cara e nome diferente (ou vice-versa) {confl[:5]}')
    perto.sort()
    L('menores distâncias de paleta entre variantes do mesmo sprite no mesmo mapa (nova):', perto[:8])
    L.check(not perto or perto[0][0] >= 100, 'todas >= 100 (no jogo original a menor é 103)')
    for par in ((2, 168), (95, 104), (111, 57), (97, 106)):
        i, j = par
        if EP['nova'][i]['file'] == EP['nova'][j]['file']:
            L(f'   par da revisão {par}: distância {dist_pal(pals(i), pals(j))}')
        else:
            L(f'   par da revisão {par}: sprites diferentes agora ({EP["nova"][i]["file"]} × {EP["nova"][j]["file"]})')
    # tamanho 2 em grupos com mais de um inimigo
    big = collections.Counter()
    for g in G['nova']:
        sl = [v for v in g['args'][6:12] if isinstance(v, int) and 1 < v <= 173]
        if len(sl) > 1:
            for v in sl:
                if EP['nova'][v - 1]['size'] == 2: big[(v - 1, nome('nova', v))] += 1
    L(f'linhas de tamanho 2 em grupos com >1 inimigo: {dict(big)}')
    L.check(all(i not in PLANO13 for i, _ in big), 'nenhuma linha trocada de tamanho 2 em grupo com mais de um inimigo')
    # nomes proibidos nas trocadas / nomes repetidos
    nn = [nome('nova', i + 1) for i in tro]
    L.check(not [x for x in nn if any(w in x.lower() for w in ('saiyajin', 'saibaman', 'broto', 'pirat', 'corsári'))], 'nenhuma troca com nome de Saiyajin/Saibaman/broto/pirata')
    todos = [nome('nova', i + 1) for i in range(173) if EP['nova'][i]['name_id'] and nome('nova', i + 1)]
    dup = [x for x, c in collections.Counter(todos).items() if c > 1]
    L.check(not dup, f'nomes de inimigo únicos {dup}')
    pal = collections.Counter(w for x in nn for w in x.split() if len(w) > 3)
    L('palavras mais repetidas nos nomes trocados:', pal.most_common(8))
    return {'pre_carga_estrita': {k: v[0] for k, v in cont.items()}, 'pre_carga_metrica_revisao02': {k: v[0] for k, v in contB.items()}, 'invocacoes': inv}


def diff_13(nova, L):
    """so devem mudar os .chr das paletas corrigidas e os bdat US/EN (texto do boot), mais FAT/cabecalho"""
    from pele131 import PELE, ROUPA
    import json
    r13 = rom('13')
    L('# Diferenca ROM 13 -> ROM 13.1')
    L('ROM 13  ', sha256(r13)); L('ROM 13.1', sha256(nova))
    cam = nds_rom.caminhos(r13)
    L.check(cam == nds_rom.caminhos(nova), 'mesma árvore de arquivos (FNT)')
    mud = sorted(c for c in cam if nds_rom.ler(nova, c) != nds_rom.ler(r13, c))
    esperado = sorted({f'btl/ene/{v[0]}.chr' for v in list(PELE.values()) + list(ROUPA.values())} | {'btl/bdat/US/bdat.bin', 'btl/bdat/EN/bdat.bin'})
    L(f'arquivos diferentes: {len(mud)}')
    f13 = {c: nds_rom.fat_entrada(r13, fid) for c, fid in cam.items()}
    fn = {c: nds_rom.fat_entrada(nova, fid) for c, fid in cam.items()}
    for c in mud:
        L('   ', c, f'{f13[c][1] - f13[c][0]} -> {fn[c][1] - fn[c][0]} bytes', 'no lugar' if f13[c][0] == fn[c][0] else f'realocado 0x{f13[c][0]:X} -> 0x{fn[c][0]:X}')
    L.check(mud == esperado, 'só mudaram os .chr das paletas corrigidas e os bdat.bin US/EN')
    hdr = [hex(i) for i in range(0x1000) if nova[i] != r13[i]]
    L.check(set(hdr) <= {'0x80', '0x81', '0x82', '0x83', '0x15e', '0x15f'}, f'cabeçalho: só tamanho usado/CRC16 {hdr}')
    fat = nds_rom.u32(nova, 0x48)
    fat_mud = sorted(c for c in cam if f13[c] != fn[c])
    L(f'entradas da FAT alteradas: {fat_mud}')
    # paletas: so os indices pedidos
    for f in sorted({v[0] for v in list(PELE.values()) + list(ROUPA.values())}):
        from chr_paletas import paletas
        pa, pb = paletas(nds_rom.ler(r13, f'btl/ene/{f}.chr')), paletas(nds_rom.ler(nova, f'btl/ene/{f}.chr'))
        dif = sorted((k, i) for k in range(len(pa)) for i in range(16) if pa[k][i] != pb[k][i])
        ped = sorted((v[1], i) for v in PELE.values() if v[0] == f for i in v[3]) + sorted((v[1], i) for v in ROUPA.values() if v[0] == f for i in v[2])
        L.check(dif == sorted(ped) and len(pa) == len(pb), f'{f}: só mudaram (paleta, índice) {dif}')
        a, b = nds_rom.ler(r13, f'btl/ene/{f}.chr'), nds_rom.ler(nova, f'btl/ene/{f}.chr')
        L.check(len(a) == len(b) and a[8 + len(pa) * 32:] == b[8 + len(pb) * 32:] and a[:8] == b[:8], f'{f}: cabeçalho, tiles e quadros idênticos')
    # bdat: so a celula do boot
    delta = json.load(open(os.path.join(PASTA18, 'texto', 'correcoes_131.json'), encoding='utf-8'))
    for lang in IDIOMAS:
        ta = ler_container(nds_rom.ler(r13, f'btl/bdat/{lang}/bdat.bin')); tb = ler_container(nds_rom.ler(nova, f'btl/bdat/{lang}/bdat.bin'))
        dif = [(n, i, col) for n in ta for i, (x, y) in enumerate(zip(ta[n]['linhas'], tb[n]['linhas'])) for col in x if x[col] != y[col]]
        ped = [(c['tabela'], c['linha'], c['coluna']) for c in delta if c['lang'] == lang]
        L.check(dif == ped and ta.keys() == tb.keys(), f'bdat {lang}: células alteradas {dif}')
    m = np.frombuffer(nova, dtype=np.uint8) != np.frombuffer(r13, dtype=np.uint8)
    mask = np.zeros(len(nova), dtype=bool)
    for c in mud:
        for a, z in (f13[c], fn[c]):
            mask[a:z] = True
        mask[fat + cam[c] * 8: fat + cam[c] * 8 + 8] = True
    for i in (0x80, 0x81, 0x82, 0x83, 0x15E, 0x15F):
        mask[i] = True
    fora = int((m & ~mask).sum())
    L.check(fora == 0, f'nenhum byte diferente da 13 fora desses arquivos, das suas entradas na FAT e do cabeçalho: {fora}')
    return mud


import numpy as np


def main(path=None):
    os.makedirs(VER, exist_ok=True)
    nova = open(path or ROM_NOVA, 'rb').read()
    L1 = Log(os.path.join(VER, 'integridade.txt'))
    mud = integridade(nova, L1)
    L2 = Log(os.path.join(VER, 'encontros.txt'))
    r2 = encontros_rev(nova, L2)
    L3 = Log(os.path.join(VER, 'diff_13.txt'))
    mud13 = diff_13(nova, L3)
    res = {'rom': os.path.basename(path or ROM_NOVA), 'sha256': sha256(nova), 'crc32': '%08x' % crc32(nova),
           'arquivos_alterados_vs_rc1': mud, 'arquivos_alterados_vs_13': mud13,
           'falhas_integridade': L1.falhas, 'falhas_encontros': L2.falhas, 'falhas_diff_13': L3.falhas, **r2}
    json.dump(res, open(os.path.join(VER, 'resumo.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('\nFALHAS:', L1.falhas + L2.falhas)
    return not (L1.falhas or L2.falhas)


if __name__ == '__main__':
    sys.exit(0 if main(*(sys.argv[1:2])) else 1)
