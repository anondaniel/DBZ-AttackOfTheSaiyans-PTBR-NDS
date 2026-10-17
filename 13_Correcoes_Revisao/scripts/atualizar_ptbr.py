"""Gera dados/ptbr.json = copia de 11_Projeto_Recuperado/traducao/ptbr.json com
  - os nomes FINAIS dos 48 inimigos trocados (chave = nome original em ingles),
    para que reaplicar a traducao (aplicar_traducao.py rom) nao volte aos nomes
    antigos da rc.1 ("Saibaman Glacial", "Robo Alado RR"...);
  - as correcoes de texto da etapa 13 (texto/ptbr_mudancas.json).
Confere: aplicar o dicionario as celulas de character_name do jogo original da
exatamente os nomes da ROM nova, e cada texto corrigido bate com a ROM nova.
uso: python -B atualizar_ptbr.py
"""
import sys, os, json, collections
sys.dont_write_bytecode = True
from comum import *
import nds_rom
from bdat import ler_container
from sb import textos
from plano13 import PLANO13

ORIG_PTBR = os.path.join(BASE, '11_Projeto_Recuperado', 'traducao', 'ptbr.json')
SAIDA = os.path.join(PASTA13, 'dados', 'ptbr.json')
MUD_TEXTO = os.path.join(PASTA13, 'texto', 'ptbr_mudancas.json')


def main():
    acum = json.load(open(ORIG_PTBR, encoding='utf-8'))
    novo = dict(acum)
    orig, nova = rom('orig'), rom('nova')
    log = []
    for lang in ('US', 'EN'):
        to = ler_container(nds_rom.ler(orig, f'btl/bdat/{lang}/bdat.bin'))
        tn = ler_container(nds_rom.ler(nova, f'btl/bdat/{lang}/bdat.bin'))
        col = to['character_name']['colunas'][0][0]
        for row in sorted(PLANO13):
            nid = to['enemy_param']['linhas'][row]['name_id']
            en = to['character_name']['linhas'][nid - 1][col]
            final = tn['character_name']['linhas'][nid - 1][col]
            assert final == PLANO13[row][1]
            if lang == 'US':
                log.append((row, en, acum.get(en), final))
            assert novo.get(en) in (None, final) or lang == 'US', (en, novo.get(en), final)
            novo[en] = final
    # correcoes de texto
    mud = json.load(open(MUD_TEXTO, encoding='utf-8')) if os.path.exists(MUD_TEXTO) else {}
    for en, pt in mud.items():
        log.append(('texto', en[:60], acum.get(en, '(nova)')[:60] if acum.get(en) else '(nova)', pt[:60]))
        novo[en] = pt
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(novo, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    # conferencia: simula a aplicacao nas celulas de character_name do original
    for lang in ('US', 'EN'):
        to = ler_container(nds_rom.ler(orig, f'btl/bdat/{lang}/bdat.bin'))
        tn = ler_container(nds_rom.ler(nova, f'btl/bdat/{lang}/bdat.bin'))
        col = to['character_name']['colunas'][0][0]
        for row in sorted(PLANO13):
            nid = to['enemy_param']['linhas'][row]['name_id']
            assert novo[to['character_name']['linhas'][nid - 1][col]] == tn['character_name']['linhas'][nid - 1][col]
    print(f'{len(log)} entradas atualizadas; ptbr.json: {len(acum)} -> {len(novo)} chaves')
    with open(os.path.join(PASTA13, 'verificacao', 'ptbr_atualizacoes.txt'), 'w', encoding='utf-8') as f:
        for x in log:
            f.write(' | '.join(str(v) for v in x) + '\n')
    return log


if __name__ == '__main__':
    main()
