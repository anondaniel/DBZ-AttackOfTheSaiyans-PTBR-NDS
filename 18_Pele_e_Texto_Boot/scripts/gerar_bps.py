"""Gera e confere os tres BPS da versao 13.1b (etapa 18) e registra hashes.
(13.1b = 13.1 + "Resetting..." -> "Preparando..."; os nomes dos arquivos continuam v13.1.)

  rc.1 (41412a47...)          -> ROM 13.1b: DBZ_PTBR_v13.1_sobre_rc1.bps
  original EN (CRC a9f0b8f9)  -> ROM 13.1b: DBZ_PTBR_v13.1_completo.bps
  ROM 13 (0616e6c6...)        -> ROM 13.1b: DBZ_PTBR_v13.1_sobre_13.bps

Cada patch e aplicado com DOIS aplicadores independentes (scripts/bps.py do
projeto e o aplicador escrito do zero pela revisao 01, work/meubps.py) e a
saida tem que ser identica byte a byte a ROM nova.
uso: python -B gerar_bps.py
"""
import sys, os, json, hashlib, zlib, importlib.util
sys.dont_write_bytecode = True
from comum import *
import nds_rom
import bps as bps_proj

spec = importlib.util.spec_from_file_location(
    'meubps', os.path.join(BASE, '_revisao_claude', '01_integridade', 'work', 'meubps.py'))
meubps = importlib.util.module_from_spec(spec); spec.loader.exec_module(meubps)

DATA = '2026-10-17'
# ROM 13.1 anterior (guardada antes da 13.1b): os patches novos tambem tem que recusa-la
ROM_131A = os.path.join(PASTA18, 'versoes', 'DBZ Attack of the Saiyans PT-BR 13.1a.nds')
SHA_131A = '408815b99220a72c9947f3ff902748f10a916b6ff06989198a809cc161637595'
assert sha256(open(ROM_131A, 'rb').read()) == SHA_131A
SAIDAS = {
    'rc1': ('DBZ_PTBR_v13.1_sobre_rc1.bps', f'DBZ NDS - PT-BR rc.1 -> v13.1b (pele dos inimigos + textos do boot) - {DATA}'),
    'orig': ('DBZ_PTBR_v13.1_completo.bps', f'DBZ NDS - PT-BR completo v13.1b (pele dos inimigos + textos do boot) - {DATA}'),
    '13': ('DBZ_PTBR_v13.1_sobre_13.bps', f'DBZ NDS - PT-BR v13 -> v13.1b (pele dos inimigos + textos do boot) - {DATA}'),
}


def regioes(origem, destino):
    cam = nds_rom.caminhos(origem)
    reg = []
    for c, fid in cam.items():
        a1, z1 = nds_rom.fat_entrada(origem, fid)
        a2, z2 = nds_rom.fat_entrada(destino, fid)
        if (a1, z1) != (a2, z2) or origem[a1:z1] != destino[a2:z2]:
            reg.append((a1, z1))
    return reg


def hashes(d):
    return {'bytes': len(d), 'crc32': '%08x' % (zlib.crc32(d) & 0xffffffff),
            'sha1': hashlib.sha1(d).hexdigest(), 'sha256': hashlib.sha256(d).hexdigest()}


def main():
    nova = open(ROM_NOVA, 'rb').read()
    res = {'rom_nova': {'arquivo': os.path.basename(ROM_NOVA), **hashes(nova)}, 'patches': {}}
    for base, (nome, meta) in SAIDAS.items():
        src = rom(base)
        p = bps_proj.criar(src, nova, regioes(src, nova), meta.encode('ascii'))
        caminho = os.path.join(PASTA18, nome)
        open(caminho, 'wb').write(p)
        out1 = bps_proj.aplicar(src, p)
        out2, est = meubps.apply(src, p)
        assert out1 == nova and out2 == nova, nome
        assert all(est[k] for k in ('src_crc_ok', 'src_size_ok', 'tgt_crc_ok', 'patch_crc_ok')), est
        assert zlib.crc32(p) & 0xffffffff == 0x2144DF1C  # CRC do arquivo inteiro com o CRC final correto
        # recusa as outras ROMs como origem
        recusa = {}
        for outra in ('orig', 'rc1', 'coe', '13', ROM_131A):
            if outra == base:
                continue
            rot = '13.1a' if outra == ROM_131A else outra
            try:
                bps_proj.aplicar(rom(outra), p); recusa[rot] = 'ACEITOU (erro)'
            except AssertionError as e:
                recusa[rot] = 'recusada: ' + str(e)
            assert recusa[rot].startswith('recusada'), (nome, rot)
            # segundo aplicador: nao levanta erro, devolve as conferencias de CRC
            o2, e2 = meubps.apply(rom(outra), p)
            assert not e2['src_crc_ok'] and not e2['tgt_crc_ok'], (nome, rot)
            recusa[rot] += ' | meubps: CRC da origem e do destino nao batem'
        res['patches'][nome] = {**hashes(p), 'origem': base, 'origem_crc32': est['info']['src_crc'],
                                'origem_sha256': sha256(src), 'destino_crc32': est['info']['tgt_crc'],
                                'crc_patch': est['info']['patch_crc'], 'metadado': meta,
                                'reproduz_rom_nova_bps_py': out1 == nova, 'reproduz_rom_nova_meubps': out2 == nova,
                                'comandos': est['cmds'], 'recusa_outras_origens': recusa}
        print(nome, len(p), 'bytes, SHA-256', hashlib.sha256(p).hexdigest(), '-> reproduz a ROM nova com os 2 aplicadores')
    # hashes de todos os BPS do projeto (BAIXO-4 / item 10)
    todos = {}
    for raiz in ('11_Projeto_Recuperado', '12_Coerencia_Historia', '13_Correcoes_Revisao', '18_Pele_e_Texto_Boot'):
        for dirpath, _, files in os.walk(os.path.join(BASE, raiz)):
            for f in files:
                if f.lower().endswith('.bps'):
                    d = open(os.path.join(dirpath, f), 'rb').read()
                    todos[os.path.relpath(os.path.join(dirpath, f), BASE)] = hashes(d)
    res['todos_bps'] = todos
    json.dump(res, open(os.path.join(PASTA18, 'verificacao', 'hashes_e_bps.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(json.dumps(res['rom_nova'], indent=1))


if __name__ == '__main__':
    main()
