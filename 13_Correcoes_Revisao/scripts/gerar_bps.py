"""Gera e confere os dois BPS da etapa 13 e registra hashes.

  rc.1 (41412a47...)          -> ROM nova : DBZ_PTBR_etapa13_sobre_rc1.bps
  original EN (CRC a9f0b8f9)  -> ROM nova : DBZ_PTBR_etapa13_completo.bps

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

DATA = '2026-10-12'
SAIDAS = {
    'rc1': ('DBZ_PTBR_etapa13_sobre_rc1.bps', f'DBZ NDS - PT-BR rc.1 + correcoes da revisao (etapa 13) - {DATA}'),
    'orig': ('DBZ_PTBR_etapa13_completo.bps', f'DBZ NDS - PT-BR completo com correcoes da revisao (etapa 13) - {DATA}'),
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
        caminho = os.path.join(PASTA13, nome)
        open(caminho, 'wb').write(p)
        out1 = bps_proj.aplicar(src, p)
        out2, est = meubps.apply(src, p)
        assert out1 == nova and out2 == nova, nome
        assert all(est[k] for k in ('src_crc_ok', 'src_size_ok', 'tgt_crc_ok', 'patch_crc_ok')), est
        assert zlib.crc32(p) & 0xffffffff == 0x2144DF1C  # CRC do arquivo inteiro com o CRC final correto
        # recusa as outras ROMs como origem
        recusa = {}
        for outra in ('orig', 'rc1', 'coe'):
            if outra == base:
                continue
            try:
                bps_proj.aplicar(rom(outra), p); recusa[outra] = 'ACEITOU (erro)'
            except AssertionError as e:
                recusa[outra] = 'recusada: ' + str(e)
        res['patches'][nome] = {**hashes(p), 'origem': base, 'origem_crc32': est['info']['src_crc'],
                                'origem_sha256': sha256(src), 'destino_crc32': est['info']['tgt_crc'],
                                'crc_patch': est['info']['patch_crc'], 'metadado': meta,
                                'reproduz_rom_nova_bps_py': out1 == nova, 'reproduz_rom_nova_meubps': out2 == nova,
                                'comandos': est['cmds'], 'recusa_outras_origens': recusa}
        print(nome, len(p), 'bytes, SHA-256', hashlib.sha256(p).hexdigest(), '-> reproduz a ROM nova com os 2 aplicadores')
    # hashes de todos os BPS do projeto (BAIXO-4 / item 10)
    todos = {}
    for raiz in ('11_Projeto_Recuperado', '12_Coerencia_Historia', '13_Correcoes_Revisao'):
        for dirpath, _, files in os.walk(os.path.join(BASE, raiz)):
            for f in files:
                if f.lower().endswith('.bps'):
                    d = open(os.path.join(dirpath, f), 'rb').read()
                    todos[os.path.relpath(os.path.join(dirpath, f), BASE)] = hashes(d)
    res['todos_bps'] = todos
    json.dump(res, open(os.path.join(PASTA13, 'verificacao', 'hashes_e_bps.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(json.dumps(res['rom_nova'], indent=1))


if __name__ == '__main__':
    main()
