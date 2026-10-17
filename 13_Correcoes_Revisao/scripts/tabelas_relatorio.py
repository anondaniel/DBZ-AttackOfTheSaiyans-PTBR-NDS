"""Gera as tabelas Markdown do RELATORIO (inimigos linha a linha) a partir da
ROM nova, da etapa 12, da rc.1 e do original. Saida: verificacao/tabela_inimigos.md"""
import sys, os, json
sys.dont_write_bytecode = True
from comum import *
from dados_inimigos import enemy_rows, pesos, pows, ene_eff, invoca, tipos_slot
from plano13 import PLANO13, REVERTIDAS


def media(w, p, eff, row):
    return sum(w[k] * p[k] for k in range(4) if not invoca(eff, row, k)) / 100.0


def main():
    O, R, C, N = (enemy_rows(rom(n), 'US') for n in ('orig', 'rc1', 'coe', 'nova'))
    eff = ene_eff(rom('orig'))
    res = {x['linha']: x for x in json.load(open(os.path.join(PASTA13, 'dados', 'resultado_inimigos.json'), encoding='utf-8'))}
    L = []
    L.append('| Linha | Bicho original | rc.1 | Etapa 12 | **Final (etapa 13)** | Sprite etapa 12 → final | O que mudou na etapa 13 |')
    L.append('|---|---|---|---|---|---|---|')
    for i in REVERTIDAS:
        L.append(f"| {i} | {O[i]['_nome']} | {R[i]['_nome']} | {C[i]['_nome']} ({C[i]['file']} p{C[i]['palno']}) | **{N[i]['_nome']}** | {C[i]['file']} → {N[i]['file']} p{N[i]['palno']} | Revertida à rc.1 (= jogo original): Saibaman do cap. 14 |")
    for i in sorted(PLANO13):
        x = res[i]
        mud = []
        if C[i]['_nome'] != N[i]['_nome']:
            mud.append('nome')
        if C[i]['file'] != N[i]['file']:
            mud.append('sprite')
        mud.append('paleta nova' if x['origem_paleta'] != 'etapa12' else 'paleta = fórmula da etapa 12')
        if pesos(C[i]) != pesos(N[i]):
            mud.append('pesos')
        motivo = PLANO13[i][2] or ''
        L.append(f"| {i} | {O[i]['_nome']} | {R[i]['_nome']} | {C[i]['_nome']} | **{N[i]['_nome']}** | {C[i]['file']} → {N[i]['file']} p{N[i]['palno']} | {', '.join(mud)}{'. ' + motivo if motivo else ''} |")
    L.append('')
    L.append('### Pesos de escolha de ataque (atk1–atk4) e potência média')
    L.append('')
    L.append('"Média" = Σ peso × atk_pow / 100, só dos slots de dano (o slot de invocação usa atk_pow como ID do inimigo chamado e fica fora). '
             'Tipos de golpe vêm de btl/ene/eneEff.bin (por linha): "inv" = invocação, "-" = slot sem golpe definido.')
    L.append('')
    L.append('| Linha | Final | pow (1–4) | Tipos 1–4 | Original | rc.1 | Etapa 12 | **Final** | Média orig → etapa 12 → final | Observação |')
    L.append('|---|---|---|---|---|---|---|---|---|---|')
    for i in sorted(PLANO13):
        x = res[i]
        tp = []
        for k in range(4):
            t = tipos_slot(eff, i, k)
            tp.append('inv' if invoca(eff, i, k) else ('-' if not eff[i, k] else ('dano' if set(t) <= {1, 2, 4} else '+'.join(hex(v) for v in t))))
        semgolpe = [k + 1 for k in range(4) if C[i][f'atk{k+1}'] > 0 and not eff[i, k]]
        obs = []
        if semgolpe:
            obs.append(f'etapa 12 punha peso em slot sem golpe: {semgolpe}')
        if x['nota_pesos']:
            obs.append(x['nota_pesos'])
        L.append(f"| {i} | {N[i]['_nome']} | {pows(O[i])} | {' / '.join(tp)} | {pesos(O[i])} | {pesos(R[i])} | {pesos(C[i])} | **{pesos(N[i])}** | "
                 f"{media(pesos(O[i]), pows(O[i]), eff, i):.1f} → {media(pesos(C[i]), pows(O[i]), eff, i):.1f} → {media(pesos(N[i]), pows(O[i]), eff, i):.1f} | {'; '.join(obs)} |")
    open(os.path.join(PASTA13, 'verificacao', 'tabela_inimigos.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(len(L), 'linhas de tabela')


if __name__ == '__main__':
    main()
