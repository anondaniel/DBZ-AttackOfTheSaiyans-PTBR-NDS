"""Documenta 00_Original/rom_antiga_do_switch_2026-10-11 (somente leitura).
uso: python -B rom_antiga_switch.py  -> verificacao/rom_antiga_switch.json"""
import sys, os, json, hashlib, zlib
sys.dont_write_bytecode = True
from comum import *
import nds_rom
P = os.path.join(BASE, '00_Original', 'rom_antiga_do_switch_2026-10-11', 'Dragon Ball Z - Attack of the Saiyans.nds')
d = open(P, 'rb').read(); o = rom('orig')
dif = [i for i in range(len(o)) if i < 0x8000 and d[i] != o[i]]
igual_resto = d[0x8000:] == o[0x8000:]
zeros = all(d[i] == 0 for i in dif)
cam = nds_rom.caminhos(o)
arq_dif = [c for c in cam if nds_rom.ler(d, c) != nds_rom.ler(o, c)]
res = {'arquivo': os.path.relpath(P, BASE), 'bytes': len(d), 'crc32': '%08x' % (zlib.crc32(d) & 0xffffffff),
       'sha1': hashlib.sha1(d).hexdigest(), 'sha256': hashlib.sha256(d).hexdigest(),
       'bytes_diferentes_do_original': len(dif), 'faixa': [hex(min(dif)), hex(max(dif))] if dif else None,
       'todos_zerados_nela': zeros, 'resto_da_rom_identico': igual_resto, 'arquivos_nitrofs_diferentes': arq_dif,
       'crc16_cabecalho_valido': nds_rom.u16(d, 0x15E) == nds_rom.crc16(d[:0x15E]),
       'conclusao': 'ROM original em ingles (USA, BRPE) com os campos de assinatura/HMAC do cabecalho zerados; nao e PT-BR; nenhum BPS a aceita como origem (CRC32 diferente de a9f0b8f9).'}
json.dump(res, open(os.path.join(PASTA13, 'verificacao', 'rom_antiga_switch.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
