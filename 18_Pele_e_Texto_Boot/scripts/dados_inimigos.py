"""Leitura dos dados de inimigos para a etapa 13 (somente leitura).

eneEff.bin (btl/ene/eneEff.bin, 103.808 bytes): um registro de 150 bytes por
(linha de enemy_param, slot de ataque 1-4), sem cabecalho (os 8 bytes finais
sao zeros). Cada registro = 5 subentradas de 15 u16. O ARM9 copia o registro
pelo ID do inimigo (funcao 0x020379D8: tabela em 0x02360000, ID<=0xAD ->
4 ataques; chefes -> bossEff.bin, 6 ataques) e o executor do golpe
(0x02040B58) le os campos 6 (alvo/flags), 7 (TIPO do efeito), 8, 9, 11, 12, 13.
Campo 7 == 0x4000 -> INVOCACAO: sorteia 0-99 < campo 11 e chama o invocador
com atk<N>_pow como ID do inimigo invocado (0x02041D48). Tipo 0 -> o executor
nao faz nada (vai direto ao fim).

A escolha do slot (0x02057F38) soma os pesos atk1..atk4 de enemy_param e nao
olha o eneEff: um slot com peso > 0 e registro vazio e escolhido mesmo assim.

Animacao: o slot N usa a animacao 3+N-1 do .chr (0 parado, 1-2 dano/etc.).
"""
import collections, struct, re, ast, io, contextlib, sys, os
from comum import *
import nds_rom
from bdat import ler_container
from dump_tiles import ler_chr
from render_quadros import ler_anims
from chr_paletas import paletas

TIPOS = {1: 'golpe', 2: 'golpe', 4: 'golpe', 0x10: 'efeito10', 0x20: 'efeito20', 0x40: 'efeito40',
         0x80: 'efeito80', 0x100: 'efeito100', 0x200: 'efeito200', 0x400: 'efeito400',
         0x800: 'efeito800', 0x1000: 'efeito1000', 0x2000: 'efeito2000', 0x4000: 'INVOCACAO'}


def ene_eff(d_rom):
    d = nds_rom.ler(d_rom, 'btl/ene/eneEff.bin')
    assert len(d) == 173 * 4 * 150 + 8
    out = {}
    for row in range(173):
        for slot in range(4):
            subs = []
            for s in range(5):
                v = struct.unpack_from('<15H', d, (row * 4 + slot) * 150 + s * 30)
                if any(v):
                    subs.append(v)
            out[row, slot] = subs
    return out


def tipos_slot(eff, row, slot):
    """conjunto de tipos (campo 7 & 0x7fff) das subentradas com tipo != 0"""
    return sorted({v[7] & 0x7fff for v in eff[row, slot] if v[7] & 0x7fff})


def invoca(eff, row, slot):
    return any((v[7] & 0x7fff) == 0x4000 for v in eff[row, slot])


def tabelas(d_rom, lang='US'):
    return ler_container(nds_rom.ler(d_rom, f'btl/bdat/{lang}/bdat.bin'))


def enemy_rows(d_rom, lang='US'):
    t = tabelas(d_rom, lang)
    ep = t['enemy_param']['linhas']
    nm = t['character_name']['linhas']
    col = t['character_name']['colunas'][0][0]
    for e in ep:
        e['_nome'] = nm[e['name_id'] - 1][col] if e['name_id'] else ''
    return ep


_anim_cache = {}
def info_chr(d_rom, file):
    k = (id(d_rom), file)
    if k not in _anim_cache:
        if f'btl/ene/{file}.chr' not in nds_rom.caminhos(d_rom):
            return None
        d = nds_rom.ler(d_rom, f'btl/ene/{file}.chr')
        c = ler_chr(d)
        err = []
        try:
            an = ler_anims(d, c['fim_tiles'], err)
        except Exception as e:  # ene011_01: limite conhecido do parser
            an, err = None, [repr(e)]
        _anim_cache[k] = {'npal': len(c['pals']), 'anims': [len(a) for a in an] if an else None,
                          'erros': err, 'pals': [list(p) for p in c['pals']]}
    return _anim_cache[k]


def pesos(e):
    return [e[f'atk{k}'] for k in (1, 2, 3, 4)]


def pows(e):
    return [e[f'atk{k}_pow'] for k in (1, 2, 3, 4)]


# ---------------- encontros (SetEnemyParty) ----------------
def _imports(d, offs):
    a4 = offs[4]
    hs, n = struct.unpack_from('<II', d, a4)
    base = a4 + hs + n * 4
    r = []
    for i in range(n):
        no, _ = struct.unpack_from('<HH', d, a4 + hs + i * 4)
        r.append(d[base + no:d.index(b'\x00', base + no)].decode())
    return r


def _tokens(code, a, z):
    out = []; p = a
    while p < z:
        op = code[p]
        if op == 0x14: out.append(code[p + 1]); p += 2
        elif op == 0x15: out.append((code[p + 1] << 8) | code[p + 2]); p += 3
        elif op == 0x13: out.append(struct.unpack_from('>I', code, p + 1)[0]); p += 5
        elif 0x16 <= op <= 0x1f: out.append(op - 0x16); p += 1
        elif op == 0x24: out.append(None); p += 1
        else: out.append('?'); p += 1
    return out


def encontros(d_rom, lang='EN'):
    """Mesmo decodificador da revisao 02 (work/encontros.py)."""
    cam = nds_rom.caminhos(d_rom)
    res = []
    for c in sorted(cam):
        if not (c.startswith(f'script/{lang}/') and c.endswith('.sb')):
            continue
        d = nds_rom.ler(d_rom, c)
        if d[:4] != b'SB  ':
            continue
        offs = list(struct.unpack_from('<6I', d, 8)) + [len(d)]
        imp = _imports(d, offs)
        if 'SetEnemyParty' not in imp:
            continue
        k = imp.index('SetEnemyParty')
        code = d[offs[0]:offs[1]]
        p = 0
        while True:
            p = code.find(bytes([0x4a, k]), p)
            if p == -1:
                break
            if code[p - 2] == 0x14:
                argc = code[p - 1]; cand = None
                for janela in range(argc, argc * 5 + 1):
                    toks = _tokens(code, p - 2 - janela, p - 2)
                    if len(toks) >= argc and '?' not in toks[-argc:]:
                        cand = toks[-argc:]; break
                res.append({'arquivo': c, 'mapa': c.split('/')[-1][:-3], 'pos': p + offs[0], 'argc': argc, 'args': cand})
            p += 2
    return res


def ids_slots(g):
    return [v for v in g['args'][6:12] if isinstance(v, int) and 1 < v <= 228]


def ids_tipos(g):
    return [v for v in g['args'][2:6] if isinstance(v, int) and 1 < v <= 228]


def mapas_por_linha(grupos):
    mp = collections.defaultdict(set)
    for g in grupos:
        for v in ids_slots(g) + ids_tipos(g):
            if v <= 173:
                mp[v - 1].add(g['mapa'])
    return mp


def dist_pal(p, q):
    return sum(abs(((a >> s) & 31) - ((b >> s) & 31)) for a, b in zip(p, q) for s in (0, 5, 10))
