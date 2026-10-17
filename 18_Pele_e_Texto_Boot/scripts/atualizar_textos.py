"""Atualiza as copias de texto da pasta 18 a partir das da etapa 13 (que ficam intactas):
  - texto/correcoes_texto.json (lista acumulada usada por verificar_textos.py): cada celula de
    texto/correcoes_131.json passa a ter o "depois" da 13.1/13.1b;
  - texto/ptbr_mudancas.json e dados/ptbr.json: cada chave inglesa (chave_en) do delta passa a ter
    o texto novo. Hoje sao 2 chaves:
      "Resetting backup memory.<n>Press the A Button to begin." (13.1, US e EN linha 120)
      "Resetting..."                                           (13.1b, US linha 121)
Para cada chave, todas as entradas do delta tem que concordar no "antes" e no "depois", e o
dicionario da 13 tem que ter exatamente o "antes" (mesmos asserts da 13.1, agora por chave).
Confere contra a ROM nova (cada celula tem exatamente o texto novo).
uso: python -B atualizar_textos.py
"""
import sys, os, json
sys.dont_write_bytecode = True
from comum import *
import nds_rom
from bdat import ler_container

DELTA = json.load(open(os.path.join(PASTA18, 'texto', 'correcoes_131.json'), encoding='utf-8'))


def chaves_do_delta():
    """{chave_en: (antes, depois)}; asserts: um so antes e um so depois por chave, celulas unicas"""
    cel = [(c['lang'], c['tabela'], c['linha'], c['coluna']) for c in DELTA]
    assert len(set(cel)) == len(cel), 'celula repetida no delta'
    por = {}
    for c in DELTA:
        por.setdefault(c['chave_en'], []).append(c)
    res = {}
    for chave, lst in por.items():
        novo_txt = {c['depois'] for c in lst}
        antes_txt = {c['antes'] for c in lst}
        assert len(novo_txt) == len(antes_txt) == 1, (chave, novo_txt, antes_txt)
        res[chave] = (antes_txt.pop(), novo_txt.pop())
    # duas chaves nao podem ter o mesmo texto novo (cada uma tem seu texto)
    assert len({v[1] for v in res.values()}) == len(res)
    return res


def main():
    chaves = chaves_do_delta()
    # 1. lista acumulada de correcoes
    lst = json.load(open(os.path.join(PASTA13, 'texto', 'correcoes_texto.json'), encoding='utf-8'))
    n = 0
    for e in lst:
        for c in DELTA:
            if e['tipo'] == 'bdat' and (e['lang'], e['tabela'], e['linha'], e['coluna']) == (c['lang'], c['tabela'], c['linha'], c['coluna']):
                assert e['depois'] == c['antes'], (e, c['antes'])
                assert e.get('chave_en') == c['chave_en'], (e.get('chave_en'), c['chave_en'])
                e['depois'] = c['depois']
                e['motivo'] = e['motivo'] + '; ' + c['motivo']
                n += 1
    assert n == len(DELTA), n
    json.dump(lst, open(os.path.join(PASTA18, 'texto', 'correcoes_texto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # 2. dicionarios
    for orig, dest in ((os.path.join(PASTA13, 'texto', 'ptbr_mudancas.json'), os.path.join(PASTA18, 'texto', 'ptbr_mudancas.json')),
                       (os.path.join(PASTA13, 'dados', 'ptbr.json'), os.path.join(PASTA18, 'dados', 'ptbr.json'))):
        d = json.load(open(orig, encoding='utf-8'))
        for chave, (antes_txt, novo_txt) in chaves.items():
            assert d[chave] == antes_txt, (orig, chave, d[chave])
            d[chave] = novo_txt
        ind = 1 if 'mudancas' in orig else 0
        json.dump(d, open(dest, 'w', encoding='utf-8'), ensure_ascii=False, indent=ind)
        # so essas chaves mudaram
        a = json.load(open(orig, encoding='utf-8')); b = json.load(open(dest, encoding='utf-8'))
        assert a.keys() == b.keys() and sorted(k for k in a if a[k] != b[k]) == sorted(chaves)
    # 3. confere com a ROM nova
    nova = rom('nova')
    for c in DELTA:
        t = ler_container(nds_rom.ler(nova, f"btl/bdat/{c['lang']}/bdat.bin"))
        assert t[c['tabela']]['linhas'][c['linha']][c['coluna']] == chaves[c['chave_en']][1] == c['depois']
    print(f'ok: correcoes_texto.json ({n} entradas), ptbr_mudancas.json e dados/ptbr.json ({len(chaves)} chaves) atualizados')
    for chave, (a_, d_) in chaves.items():
        print(f'   {chave!r}: {a_!r} -> {d_!r}')


if __name__ == '__main__':
    main()
