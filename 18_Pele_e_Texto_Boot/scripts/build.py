"""Etapa 18 - versao 13.1: monta a ROM a partir da ROM da etapa 13 (reproduzivel).

Base: 13_Correcoes_Revisao/DBZ Attack of the Saiyans PT-BR.nds (SHA-256 0616e6c6..., assert).
Mudancas:
  1. pele dos inimigos humanos: indices de pele das paletas novas voltam aos tons da
     paleta original usada como modelo (tabela PELE em pele131.py) + 1 ajuste de roupa para
     manter a distancia de paleta (ROUPA, linha 157); so os .chr dessas paletas mudam,
     do mesmo tamanho (gravados no lugar);
  2. textos do boot (texto/correcoes_131.json, uma entrada por celula):
     13.1  - primeira tela, cf_mes_MENU linha 120, colunas us/en nos bdat US/EN;
     13.1b - indicador "Resetting..." da tela seguinte, cf_mes_MENU linha 121, coluna us
             (so no bdat US; no EN essa linha e "Saving...").
Tudo e conferido com asserts: so os arquivos esperados mudam, cada celula/paleta muda
so onde foi pedido, ARM9/ARM7/FNT/banner iguais, CRC16 do cabecalho valido.

uso: python -B build.py            (grava 18_Pele_e_Texto_Boot/DBZ Attack of the Saiyans PT-BR.nds)
     python -B build.py --seco     (so confere, nao grava)
"""
import sys, os, json
sys.dont_write_bytecode = True
from comum import *
import nds_rom
from bdat import ler_container
from bdat_strings import gravar_str, conferir
from chr_paletas import paletas, com_paletas
from pele131 import PELE, ROUPA, rgb555

TEXTO = os.path.join(PASTA18, 'texto', 'correcoes_131.json')


def gravar_arquivo(rom_, paths, caminho, dados):
    """Grava o arquivo no MESMO endereco da ROM 13 se couber ate o inicio do proximo arquivo
    (os bdat.bin US/EN crescem 64 bytes e cabem na folga de alinhamento); senao, realoca no fim
    (nds_rom.substituir). Sobra do espaco antigo vira 0xFF. Corrige a FAT e o CRC16 do cabecalho."""
    import struct
    fid = paths[caminho]
    fat = nds_rom.u32(rom_, 0x48)
    a, z = nds_rom.fat_entrada(rom_, fid)
    seguintes = [nds_rom.fat_entrada(rom_, f)[0] for f in paths.values() if nds_rom.fat_entrada(rom_, f)[0] > a]
    prox = min(seguintes) if seguintes else None   # ultimo arquivo: deixa para substituir()
    if prox is not None and a + len(dados) <= prox:
        assert all(x == 0xFF for x in rom_[z:max(z, a + len(dados))]), 'folga nao esta livre'
        rom_[a:a + len(dados)] = dados
        if a + len(dados) < z:
            rom_[a + len(dados):z] = bytes([0xFF]) * (z - a - len(dados))
        struct.pack_into("<I", rom_, fat + fid * 8 + 4, a + len(dados))
        struct.pack_into("<H", rom_, 0x15E, nds_rom.crc16(rom_[0:0x15E]))
        return f"no lugar (0x{a:08X}, {len(dados)} bytes; antes {z - a}; folga ate o proximo {prox - a})"
    return nds_rom.substituir(rom_, caminho, dados)


def build(gravar=True):
    base = rom('13')
    out = bytearray(base)
    paths = nds_rom.caminhos(base)
    alterados = []

    # ---- 1. paletas (pele)
    por_arquivo = {}
    for row, (f, pn, mp, mud) in sorted(PELE.items()):
        por_arquivo.setdefault(f, []).append((row, pn, mud))
    for row, (f, pn, mud) in sorted(ROUPA.items()):
        por_arquivo.setdefault(f, []).append((row, pn, mud))
    ep13 = ler_container(nds_rom.ler(base, 'btl/bdat/EN/bdat.bin'))['enemy_param']['linhas']
    for f, lst in sorted(por_arquivo.items()):
        path = f'btl/ene/{f}.chr'
        old = nds_rom.ler(base, path)
        pals = [list(p) for p in paletas(old)]
        for row, pn, mud in lst:
            assert ep13[row]['file'] == f and ep13[row]['palno'] == pn, (row, f, pn)
            for i, (antes, depois) in mud.items():
                assert pals[pn][i] == rgb555(antes), (row, i, 'cor da ROM 13 nao confere')
                pals[pn][i] = rgb555(depois)
        new = com_paletas(old, pals)
        assert len(new) == len(old) and new[8 + len(pals) * 32:] == old[8 + len(pals) * 32:]
        # so os indices pedidos mudaram
        pa, pb = paletas(old), paletas(new)
        dif = {(k, i) for k in range(len(pa)) for i in range(16) if pa[k][i] != pb[k][i]}
        pedido = {(pn, i) for _, pn, mud in lst for i in mud}
        assert len(pedido) == sum(len(mud) for _, _, mud in lst), 'indice repetido entre pele e roupa'
        assert dif == pedido, (f, dif ^ pedido)
        como = gravar_arquivo(out, paths, path, new)
        alterados.append(path)
        print(path, como)

    # ---- 2. textos do boot (varias celulas; agrupadas por bdat, cada arquivo gravado uma vez)
    corr = json.load(open(TEXTO, encoding='utf-8'))
    celulas = [(c['lang'], c['tabela'], c['linha'], c['coluna']) for c in corr]
    assert len(set(celulas)) == len(celulas), 'celula repetida em correcoes_131.json'
    por_lang = {}
    for c in corr:
        por_lang.setdefault(c['lang'], []).append(c)
    for lang, lst in sorted(por_lang.items()):
        path = f"btl/bdat/{lang}/bdat.bin"
        old = nds_rom.ler(out, path)
        b = bytearray(old)
        for c in lst:
            t = ler_container(old)[c['tabela']]['linhas'][c['linha']]
            assert t[c['coluna']] == c['antes'], (lang, c['linha'], t[c['coluna']])
            b, como = gravar_str(b, c['tabela'], c['linha'], c['coluna'], c['depois'])
            print(path, f"{c['tabela']}:{c['linha']}:{c['coluna']}", como)
        # todas as celulas de todas as tabelas iguais, exceto as pedidas para este arquivo
        conferir(old, b, {(c['tabela'], c['linha'], c['coluna']): c['depois'] for c in lst})
        como2 = gravar_arquivo(out, paths, path, bytes(b))
        alterados.append(path)
        print(path, '|', como2)

    after = bytes(out)
    # ---------------------------------------------------------- conferencias
    assert nds_rom.caminhos(after) == paths
    mud = []
    for p, fid in paths.items():
        a, z = nds_rom.fat_entrada(base, fid); aa, zz = nds_rom.fat_entrada(after, fid)
        if base[a:z] != after[aa:zz]:
            mud.append(p)
    assert sorted(mud) == sorted(alterados), (sorted(mud), sorted(alterados))
    u32 = nds_rom.u32
    for o_off, s_off in ((0x20, 0x2C), (0x30, 0x3C)):  # ARM9, ARM7
        assert base[u32(base, o_off):u32(base, o_off) + u32(base, s_off)] == after[u32(after, o_off):u32(after, o_off) + u32(after, s_off)]
    assert base[0x40:0x50] == after[0x40:0x50]
    assert nds_rom.u16(after, 0x15E) == nds_rom.crc16(after[:0x15E])
    assert len(after) == len(base) == 134217728
    diffs_hdr = [i for i in range(0x1000) if base[i] != after[i]]
    assert set(diffs_hdr) <= {0x80, 0x81, 0x82, 0x83, 0x15E, 0x15F}, diffs_hdr
    # bdat: so a celula pedida mudou (em todas as tabelas), nos 6 idiomas os demais bdat iguais
    for lang in ('FR', 'SP', 'GR', 'IT'):
        assert nds_rom.ler(after, f'btl/bdat/{lang}/bdat.bin') == nds_rom.ler(base, f'btl/bdat/{lang}/bdat.bin')
    if gravar:
        open(ROM_NOVA, 'wb').write(after)
    print('arquivos alterados:', len(mud))
    for p in sorted(mud):
        print('  ', p)
    print('SHA-256', sha256(after), 'CRC32 %08x' % crc32(after))
    return after, sorted(mud)


if __name__ == '__main__':
    build(gravar='--seco' not in sys.argv)
