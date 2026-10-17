"""Etapa 13 - monta a ROM corrigida a partir da rc.1 (reproduzivel).

Base: 01_ROM/DBZ Attack of the Saiyans PT-BR.nds (rc.1, SHA-256 41412a47...).
Escolha documentada no RELATORIO: em vez de remendar a ROM da etapa 12, a
etapa 12 e reaplicada CORRIGIDA sobre a rc.1 (sem as linhas 1-4, sem paletas
mortas, pesos de ataque do jogo original).

Passos:
  1. inimigos: .chr (paletas novas) + enemy_param/character_name nos 6 idiomas
  2. textos: correcoes de texto (texto/correcoes_texto.json) nas pastas US/EN
  3. confere tudo (asserts) e grava a ROM + dados/resultado_inimigos.json/csv

uso: python -B build.py            (grava 13_Correcoes_Revisao/DBZ Attack of the Saiyans PT-BR.nds)
     python -B build.py --seco     (so confere, nao grava)
"""
import sys, os, json, csv, colorsys, collections, itertools, math
sys.dont_write_bytecode = True
from comum import *
import nds_rom
from bdat import ler_container
from bdat_escrita import tabelas_com_offset, gravar_num, ler_num
from bdat_strings import gravar_str, conferir
from chr_paletas import paletas, com_paletas, rgb555
from sb import textos, com_textos
from dados_inimigos import (ene_eff, info_chr, encontros, mapas_por_linha, dist_pal, pesos, pows,
                            tipos_slot, invoca, enemy_rows)
from plano13 import PLANO13, REVERTIDAS, TEMAS

IDIOMAS = ('EN', 'US', 'FR', 'SP', 'GR', 'IT')
T_MAPA = 100    # distancia minima de paleta entre variantes do mesmo sprite no MESMO mapa
                # (no jogo original a menor distancia entre variantes de um sprite e 103)
T_GLOBAL = 80   # distancia minima entre quaisquer variantes do mesmo sprite (evita clones)
LARG_MAX = (92, 106)  # maior nome de inimigo do jogo original (latin1, latin0)
APRES = {'file', 'palno', 'size', 'shadow', 'atk1', 'atk2', 'atk3', 'atk4'}
DADOS = os.path.join(PASTA13, 'dados')
TEXTO = os.path.join(PASTA13, 'texto', 'correcoes_texto.json')


# ---------------------------------------------------------------- paletas
def _hsv(c):
    return colorsys.rgb_to_hsv((c & 31) / 31, ((c >> 5) & 31) / 31, ((c >> 10) & 31) / 31)


def _rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return rgb555(round(r * 31), round(g * 31), round(b * 31))


def paleta_etapa12(p, row):
    """Copia exata de nova_paleta() de 12_Coerencia_Historia/revisao.py."""
    result = list(p)
    for i, c in enumerate(p):
        r, g, b = (c & 31) / 31, ((c >> 5) & 31) / 31, ((c >> 10) & 31) / 31
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        if i and s > .25 and h > .17 and v > .12:
            rr, gg, bb = colorsys.hsv_to_rgb((h + (row % 11 + 1) * .037) % 1, s, v)
            result[i] = rgb555(round(rr * 31), round(gg * 31), round(bb * 31))
    return result


def _pele(h, s, v):
    return 0.02 <= h <= 0.12 and 0.15 <= s <= 0.62 and v >= 0.55


def candidatos(p):
    """Recoloracoes da roupa/corpo: giro de matiz (+ variacao de saturacao/brilho).
    Cor 0 (transparente), tons de pele, cinzas e quase-pretos ficam.
    Devolve [((graus, sat, val), paleta, matiz_media_graus)]"""
    idx = [i for i in range(1, 16) if (lambda h, s, v: s > 0.18 and v > 0.12 and not _pele(h, s, v))(*_hsv(p[i]))]
    out = []
    for graus in range(20, 360, 20):
        for sat, val in ((1.0, 1.0), (1.0, 0.72), (0.65, 1.08), (1.25, 0.9)):
            q = list(p)
            sx = sy = 0.0
            for i in idx:
                h, s, v = _hsv(p[i])
                nh = (h + graus / 360) % 1
                q[i] = _rgb(nh, min(1.0, s * sat), min(1.0, v * val))
                sx += math.cos(2 * math.pi * nh) * s; sy += math.sin(2 * math.pi * nh) * s
            media = (math.degrees(math.atan2(sy, sx)) % 360) if idx else 0
            out.append(((graus, sat, val), q, media))
    return out


def _dist_ang(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


# ---------------------------------------------------------------- pesos
def pesos_finais(row, eo, n_anims, eff):
    """Pesos do jogo original para a linha. Se o sprite doador nao tem a
    animacao de um slot usado (slot k usa a animacao 3+k-1), o peso desse slot
    vai para o(s) slot(s) usado(s) de potencia mais proxima (empate:
    proporcional ao peso original), o que minimiza a mudanca da media
    ponderada de potencia."""
    w0, p0 = pesos(eo), pows(eo)
    usados = [k for k in range(4) if w0[k] > 0]
    for k in usados:
        assert eff[row, k], (row, k, 'peso>0 sem golpe no eneEff do original?')
    ok = [k for k in usados if 3 + k < n_anims]
    if ok == usados:
        return list(w0), None
    w = list(w0)
    nota = []
    for k in usados:
        if k in ok:
            continue
        assert not invoca(eff, row, k)
        tira = w[k]; w[k] = 0
        dmin = min(abs(p0[j] - p0[k]) for j in ok)
        alvo = [j for j in ok if abs(p0[j] - p0[k]) == dmin]
        assert not any(invoca(eff, row, j) for j in alvo)
        tot = sum(w0[j] for j in alvo)
        parte = {j: tira * w0[j] / tot for j in alvo}
        base = {j: int(parte[j]) for j in alvo}
        resto = tira - sum(base.values())
        for j in sorted(alvo, key=lambda j: -(parte[j] - base[j]))[:resto]:
            base[j] += 1
        for j in alvo:
            w[j] += base[j]
        nota.append(f'slot {k+1} ({tira}%, pow {p0[k]}) sem animação no sprite (só {n_anims - 3} golpes) -> '
                    + ', '.join(f'slot {j+1} +{base[j]}' for j in alvo))
    assert sum(w) == 100
    return w, '; '.join(nota)


def media_pow(w, p, eff, row):
    """indicador: media ponderada de atk_pow so dos slots de dano (invocacao fora)."""
    num = sum(w[k] * p[k] for k in range(4) if not invoca(eff, row, k))
    return num / 100.0


def largura(fonte, s):
    return sum(fonte[c] for c in s.encode('latin-1'))


# ---------------------------------------------------------------- build
def build(gravar=True):
    rc1 = rom('rc1'); orig = rom('orig')
    rom_ = bytearray(rc1)
    paths = nds_rom.caminhos(rc1)
    assert paths == nds_rom.caminhos(orig)
    cam_cache = paths
    nds_rom.caminhos = lambda _r: cam_cache   # FNT nao muda nesta etapa (conferido no fim)
    eff = ene_eff(rc1)
    assert eff == ene_eff(orig), 'eneEff.bin mudou?'
    EO = enemy_rows(orig, 'US')
    ER = enemy_rows(rc1, 'US')
    base_tabs = ler_container(nds_rom.ler(rc1, 'btl/bdat/EN/bdat.bin'))
    ep = base_tabs['enemy_param']['linhas']
    grupos = encontros(rc1)
    mapas = mapas_por_linha(grupos)
    fonte1 = nds_rom.ler(rc1, 'latin1.fnt')[:256]
    fonte0 = nds_rom.ler(rc1, 'latin0.fnt')[:256]

    # sanidade: linhas do plano = as 48 do hack da rc.1; modelos nao sao linhas do plano
    sys.path.insert(0, SCRIPTS_PROJ)
    from plano_bichos import PLANO
    assert set(PLANO13) == set(PLANO), set(PLANO13) ^ set(PLANO)
    assert not set(m for m, _, _ in PLANO13.values()) & set(PLANO13)

    # ---- 1. pesos, tamanho/sombra, arquivo
    final = {}
    for row, (model, nome, motivo) in sorted(PLANO13.items()):
        src = ep[model]
        info = info_chr(rc1, src['file'])
        assert info and not info['erros'] and info['anims'] and all(info['anims']), (row, src['file'])
        assert src['size'] <= EO[row]['size'], (row, 'sprite maior que o do bicho original')
        w, nota = pesos_finais(row, EO[row], len(info['anims']), eff)
        final[row] = dict(model=model, nome=nome, motivo=motivo, file=src['file'], size=src['size'],
                          shadow=src['shadow'], pesos=w, nota_pesos=nota)
        assert largura(fonte1, nome) <= LARG_MAX[0] and largura(fonte0, nome) <= LARG_MAX[1], nome

    # ---- 2. paletas (uma nova por linha, unica)
    pals_by_file = {}
    def pals_of(f):
        if f not in pals_by_file:
            pals_by_file[f] = [list(p) for p in paletas(nds_rom.ler(rc1, f'btl/ene/{f}.chr'))]
        return pals_by_file[f]
    # aparencia atual de toda linha com nome (as do plano vao sendo preenchidas)
    apar = {i: (e['file'], e['palno']) for i, e in enumerate(ep) if e['name_id'] and i not in PLANO13}
    def outras(row, f):
        """[(linha, paleta, mesmo_mapa)] das outras linhas que usam o arquivo f"""
        r = []
        for i, (ff, pn) in apar.items():
            if ff == f and i != row:
                r.append((i, pals_of(f)[pn], bool(mapas[i] & mapas[row])))
        return r
    escolha = {}
    for row in sorted(PLANO13):
        f = final[row]['file']
        pals = pals_of(f)
        base_p = pals[ep[final[row]['model']]['palno']]
        viz = outras(row, f)
        def nota(q):
            dm = min([dist_pal(q, p) for _, p, mm in viz if mm] or [999])
            dg = min([dist_pal(q, p) for _, p, mm in viz] or [999])
            return dm, dg
        p12 = paleta_etapa12(base_p, row)
        dm, dg = nota(p12)
        tema = TEMAS.get(row)
        if dm >= T_MAPA and dg >= T_GLOBAL and p12 not in pals and not tema:
            q, como = p12, 'etapa12'
        else:
            melhor = None
            for par, q, media in candidatos(base_p):
                dm2, dg2 = nota(q)
                natural = {(1.0, 1.0): 2, (1.0, 0.72): 1, (0.65, 1.08): 1}.get(par[1:], 0)
                if tema:
                    ok = dm2 >= T_MAPA and dg2 >= T_GLOBAL
                    t_h, t_v = tema
                    afin = -(_dist_ang(media, t_h) if t_h is not None else 0) - (0 if abs(par[2] - t_v) < 0.1 else 200)
                    chave = (ok, afin, natural, min(dg2, 150))
                else:
                    chave = (min(dm2, T_MAPA), min(dg2, 150), natural, dg2)
                if melhor is None or chave > melhor[0]:
                    melhor = (chave, par, q)
            _, par, q = melhor
            como = ('tema ' if tema else 'nova ') + 'giro=%d sat=%.2f val=%.2f' % par
            dm, dg = nota(q)
            assert dm >= T_MAPA and dg >= T_GLOBAL, (row, dm, dg)
        assert q not in pals
        assert len(pals) < 16, (f, len(pals))
        pals.append(q)
        apar[row] = (f, len(pals) - 1)
        final[row].update(palno=len(pals) - 1, paleta=como, dist_mapa=dm, dist_global=dg)

    # ---- 3. grava .chr
    changed = []
    for f, pals in sorted(pals_by_file.items()):
        path = f'btl/ene/{f}.chr'
        old = nds_rom.ler(rc1, path)
        if len(pals) == old[5]:
            continue
        new = com_paletas(old, pals)
        assert new[8 + len(pals) * 32:] == old[8 + old[5] * 32:]
        assert paletas(new)[:old[5]] == paletas(old)
        nds_rom.substituir(rom_, path, new)
        changed.append(path)

    # ---- 4. textos (lista gerada em texto/)
    corr = json.load(open(TEXTO, encoding='utf-8')) if os.path.exists(TEXTO) else []
    sb_corr = collections.defaultdict(list)
    bdat_corr = collections.defaultdict(list)
    for c in corr:
        if c['tipo'] == 'sb':
            sb_corr[c['arquivo']].append(c)
        else:
            assert c['lang'] in ('US', 'EN')
            bdat_corr[c['lang']].append(c)
    for arq, lst in sorted(sb_corr.items()):
        d = nds_rom.ler(rc1, arq)
        ts = textos(d)
        for c in lst:
            assert ts[c['indice']].decode('latin-1') == c['antes'], (arq, c['indice'])
            ts[c['indice']] = c['depois'].encode('latin-1')
        nds_rom.substituir(rom_, arq, com_textos(d, ts))
        changed.append(arq)

    # ---- 5. tabelas (6 idiomas)
    for lang in IDIOMAS:
        path = f'btl/bdat/{lang}/bdat.bin'
        old = nds_rom.ler(rc1, path)
        b = bytearray(old); changes = {}
        col = tabelas_com_offset(b)['character_name']['colunas'][0][0]
        for row in sorted(PLANO13):
            fr = final[row]
            t = tabelas_com_offset(b)['enemy_param']
            if t['linhas'][row]['file'] != fr['file']:
                b, _ = gravar_str(b, 'enemy_param', row, 'file', fr['file'])
            changes['enemy_param', row, 'file'] = fr['file']
            t = tabelas_com_offset(b)['enemy_param']
            vals = {'palno': fr['palno'], 'size': fr['size'], 'shadow': fr['shadow']}
            vals.update({f'atk{k+1}': fr['pesos'][k] for k in range(4)})
            for cc, v in vals.items():
                gravar_num(b, t, row, cc, v)
                changes['enemy_param', row, cc] = v
            nid = ler_num(b, t, row, 'name_id')
            assert sum(e['name_id'] == nid for e in t['linhas']) == 1
            b, _ = gravar_str(b, 'character_name', nid - 1, col, fr['nome'])
            changes['character_name', nid - 1, col] = fr['nome']
        for c in bdat_corr.get(lang, []):
            t = tabelas_com_offset(b)[c['tabela']]
            assert t['linhas'][c['linha']][c['coluna']] == c['antes'], (lang, c['tabela'], c['linha'])
            b, _ = gravar_str(b, c['tabela'], c['linha'], c['coluna'], c['depois'])
            changes[c['tabela'], c['linha'], c['coluna']] = c['depois']
        conferir(old, b, changes)
        nds_rom.substituir(rom_, path, bytes(b))
        changed.append(path)

    after = bytes(rom_)
    nds_rom.caminhos = _caminhos_original
    # ---------------------------------------------------------- conferencias
    assert nds_rom.caminhos(after) == paths
    for p, fid in paths.items():
        a, z = nds_rom.fat_entrada(rc1, fid); aa, zz = nds_rom.fat_entrada(after, fid)
        if p not in changed:
            assert rc1[a:z] == after[aa:zz], p
    u32 = nds_rom.u32
    for o_off, s_off in ((0x20, 0x2C), (0x30, 0x3C)):  # ARM9, ARM7
        assert rc1[u32(rc1, o_off):u32(rc1, o_off) + u32(rc1, s_off)] == after[u32(after, o_off):u32(after, o_off) + u32(after, s_off)]
    assert rc1[0x40:0x50] == after[0x40:0x50]  # FNT/FAT offsets e tamanhos
    assert nds_rom.u16(after, 0x15E) == nds_rom.crc16(after[:0x15E])
    assert len(after) == len(rc1) == 134217728
    diffs_hdr = [i for i in range(0x200) if rc1[i] != after[i]]
    assert set(diffs_hdr) <= {0x80, 0x81, 0x82, 0x83, 0x15E, 0x15F}, diffs_hdr
    # tabelas
    EN = {lang: ler_container(nds_rom.ler(after, f'btl/bdat/{lang}/bdat.bin')) for lang in IDIOMAS}
    eo_tabs = ler_container(nds_rom.ler(orig, 'btl/bdat/EN/bdat.bin'))
    rc_tabs = base_tabs
    novo_ep = EN['EN']['enemy_param']['linhas']
    for lang in IDIOMAS:
        assert EN[lang]['enemy_param']['linhas'] == novo_ep
    for i in range(173):
        for cc, v in novo_ep[i].items():
            if cc not in APRES:
                assert v == eo_tabs['enemy_param']['linhas'][i][cc], (i, cc)   # combate/recompensa = original
        if i not in PLANO13:
            assert novo_ep[i] == rc_tabs['enemy_param']['linhas'][i], i          # inclui 1-4 = rc.1
    for i in REVERTIDAS:
        assert novo_ep[i] == eo_tabs['enemy_param']['linhas'][i]
    # pesos: todo slot com peso tem golpe definido (eneEff) e animacao no sprite
    for i, e in enumerate(novo_ep):
        if not e['name_id'] or not EO[i]['_nome']:
            continue
        an = info_chr(after, e['file'])['anims']
        for k in range(4):
            if e[f'atk{k+1}'] > 0:
                assert eff[i, k], (i, k, 'peso sem golpe')
                assert 3 + k < len(an), (i, k, 'peso sem animacao')
        assert sum(pesos(e)) == 100
        assert e['palno'] < info_chr(after, e['file'])['npal']
    # nomes: so as 48 linhas mudaram em character_name (alem dos textos pedidos)
    nm_rc = rc_tabs['character_name']['linhas']; nm_new = EN['EN']['character_name']['linhas']
    mud_nomes = {i for i in range(len(nm_rc)) if nm_rc[i] != nm_new[i]}
    assert mud_nomes <= {ep[r]['name_id'] - 1 for r in PLANO13}
    # conflitos por mapa (mesmo nome <-> mesma aparencia), incluindo lista de tipos
    nome_de = lambda i: nm_new[novo_ep[i]['name_id'] - 1]['en'] if novo_ep[i]['name_id'] else ''
    ap = lambda i: (novo_ep[i]['file'], novo_ep[i]['palno'])
    por_mapa = collections.defaultdict(set)
    for g in grupos:
        for v in g['args'][2:12]:
            if isinstance(v, int) and 1 < v <= 173:
                por_mapa[g['mapa']].add(v - 1)
    conflitos = []
    for m, ids in por_mapa.items():
        for i, j in itertools.combinations(sorted(ids), 2):
            if (ap(i) == ap(j)) != (nome_de(i) == nome_de(j)):
                conflitos.append((m, i, j))
    assert not conflitos, conflitos[:10]
    for row in PLANO13:
        assert not any(x in nome_de(row).lower() for x in ('saiyajin', 'saibaman', 'broto', 'pirat', 'corsári'))

    resultado = []
    for row in sorted(PLANO13):
        fr = final[row]
        eo = EO[row]
        resultado.append({
            'linha': row, 'animal_original': eo['_nome'], 'nome_rc1': ER[row]['_nome'],
            'nome_etapa12': None, 'nome_final': fr['nome'], 'modelo': fr['model'], 'sprite': fr['file'],
            'paleta': fr['palno'], 'origem_paleta': fr['paleta'], 'dist_paleta_mesmo_mapa': fr['dist_mapa'],
            'dist_paleta_global': fr['dist_global'], 'tamanho': fr['size'], 'sombra': fr['shadow'],
            'pesos_original': pesos(eo), 'pesos_rc1': pesos(ER[row]), 'pesos_final': fr['pesos'],
            'pow': pows(eo), 'media_pow_original': media_pow(pesos(eo), pows(eo), eff, row),
            'media_pow_final': media_pow(fr['pesos'], pows(eo), eff, row),
            'tipos_golpe': [[hex(t) for t in tipos_slot(eff, row, k)] for k in range(4)],
            'nota_pesos': fr['nota_pesos'], 'mudanca_vs_etapa12': fr['motivo'],
            'largura_px': [largura(fonte1, fr['nome']), largura(fonte0, fr['nome'])],
            'mapas': sorted(mapas[row]),
        })
    if gravar:
        open(ROM_NOVA, 'wb').write(after)
        os.makedirs(DADOS, exist_ok=True)
        json.dump(resultado, open(os.path.join(DADOS, 'resultado_inimigos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        with open(os.path.join(DADOS, 'resultado_inimigos.csv'), 'w', encoding='utf-8-sig', newline='') as fcsv:
            wr = csv.DictWriter(fcsv, fieldnames=list(resultado[0].keys()))
            wr.writeheader()
            for x in resultado:
                wr.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v) for k, v in x.items()})
    print('arquivos alterados:', len(changed), '| correcoes de texto:', len(corr))
    print('SHA-256', sha256(after), 'CRC32 %08x' % crc32(after))
    return after, resultado, changed


_caminhos_original = nds_rom.caminhos

if __name__ == '__main__':
    build(gravar='--seco' not in sys.argv)
