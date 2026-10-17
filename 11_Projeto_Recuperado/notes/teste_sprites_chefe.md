# Teste: sprite de chefe como inimigo comum

Script: `scripts/diag_chefes.py` (ROM de diagnóstico, não é entrega)
Captura: `saida/chefes_como_inimigo.png`

## Resultado: funciona

A tabela de inimigos comuns (`enemy_param`) aceita o arquivo de sprite de
um chefe no campo `file`. Nos 6 testados o chefe aparece com o nome certo,
anda, ataca com a própria animação e causa dano. A luta seguiu 40 s sem
travar:

| Chefe | Arquivo | Tamanho |
|---|---|---|
| Raditz | `ene220_01` | 1 |
| Nappa | `ene221_01` | 1 |
| Vegeta | `ene222_01` | 0 |
| Oozaru Vegeta | `ene222_02` | 2 |
| Piccolo | `ene214_01` | 1 |
| Broly | `ene223_01` | 2 |

## Como foi montado

Palco: a batalha real de 1 lobo no Monte Paozu (`pz5/p0027_pre.bin`). Na
ROM original, a linha 104 (Wolf) recebe do chefe `file`, `palno`,
`size`, `shadow`, `name_id` e os pesos `atk1-4` (os 4 primeiros dos 6
do chefe, renormalizados para somar 100). O HP foi para 3000 **só no
diagnóstico**, para o inimigo sobreviver e atacar várias vezes.

## Limites para usar de verdade

- **Uma paleta só.** Todo sprite de chefe tem só a paleta 0, então duas
  cópias no mesmo grupo saem idênticas. As variações do Saibaman (5
  cores) não existem aqui.
- **Nome.** Hoje o inimigo aparece como "Raditz", "Nappa"… Para virar
  "Soldado Saiyajin" ou similar é preciso escrever texto novo no
  `character_name`, o mesmo escritor de strings que a tradução vai
  exigir.
- **Tamanho 2** (Oozaru, Broly): na formação de 2 inimigos o jogo põe
  os dois fora da tela (visto com ursos e pandas). Esses só servem
  sozinhos.
- **Ataques 5 e 6** do chefe (em geral os especiais) não entram, porque a
  tabela de inimigo comum só tem 4 pesos. Ainda não foi testado se o
  ataque especial aparece em algum dos 4 primeiros.
- `ene200_01.chr` existe no cartucho sem nenhum chefe apontando para
  ele. Ainda não foi visto.
