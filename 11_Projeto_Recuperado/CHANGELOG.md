# Changelog — Dragon Ball Z: Attack of the Saiyans PT-BR

Tradução para português do Brasil + troca de inimigos ("bichos" → universo DB)
do jogo de Nintendo DS. Formato inspirado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [1.0.0-rc.1] — 2026-09-29 (estado atual)

Candidata a 1.0: tudo traduzido e validado em trechos no emulador; falta a
primeira jogada completa, do começo ao fim.

### Identificação

| Item | Valor |
|---|---|
| ROM de origem | Dragon Ball Z - Attack of the Saiyans (USA) (En,Fr), código `BRPE`, 134.217.728 bytes |
| Origem: CRC32 / SHA-1 | `a9f0b8f9` / `b5d8ebbc8813db68270ea02f0e581f6005f54736` |
| Patch | `patches/aots_ptbr.bps`, 2.112.001 bytes |
| Patch: SHA-256 | `8d3e04696a56de81734b29e3a39558a92f857994b7621a19ec13b63fc949a423` |
| ROM resultante: CRC32 | `670e3cf1` |
| ROM resultante: SHA-1 | `74f536b0780857784eadb6d5e56b717ffbca49a0` |
| ROM resultante: SHA-256 | `41412a4727328d5341ba2f7d17fa567c84db137d8cd082bc32389c6d27643a5f` |

O patch foi validado com dois aplicadores independentes (`scripts/bps.py` e o
`python-bps`): os dois reconstroem exatamente a ROM resultante acima.
Instruções em `patches/COMO-APLICAR.md`.

### Corrigido (29/09)
- Títulos dos capítulos 0 e 7: sobras do letreiro em inglês (manchas cinza e
  traço preto no C07; riscos na areia no C00). `scripts/titulos.py` (`LIMPA_SOBRAS`).

### Adicionado / corrigido (28/09)
- 39 faixas de nome de local ao chegar (ex.: "~West City~" → "~Cidade do Oeste~"),
  com fonte pixelada própria (`scripts/faixas_locais.py`, `scripts/fonte_faixa.py`).
  10 nomes encurtados para caber (ex.: "Templo Marcial", "Planeta do Kaioh").
- Faixas de 32 texels (Esgoto, Deserto, Inferno) centradas como no original
  (antes "Esgoto" saía partido).
- "Tenshinhan" não encosta mais no "LV" no painel de batalha: letras n, h, a, e
  estreitas em códigos livres da fonte, só nesse nome (`scripts/tenshinhan_estreito.py`).
- Conferidas no emulador as falas de NPC na Cidade do Leste.

### Adicionado / corrigido (26/09)
- Segunda leva de textos em imagem: RESERVA, ATACANTE, JOGO, ITENS OBTIDOS,
  RESULTADO, PONTOS EXTRAS!!, NÍVEL +1!, Continuar/Novo Jogo, siglas dos
  atributos (Po De Cu Té Ve So), faixas Vitória!!/Derrota/Fuga!.
- Botão Y da tela de pontos: "Tentar de Novo" (cortado) → "Refazer".
- Cauda do Soldado Saiyajin escurecida (`scripts/cauda_soldado.py`).

### Estado anterior (antes de 26/09)
- Lotes 1 a 11 de texto: prólogo, capítulos 0 a 16, créditos, menus, itens,
  golpes, mensagens de batalha, lojas, objetivos, nomes, falas de NPCs e
  objetos dos mapas (~5.800 textos, ~55 mil palavras). Detalhes em `notes/traducao.md`.
- Títulos dos 17 capítulos, MENU, GRUPO e DICAS em imagem (`notes/imagens.md`).
- Hack de inimigos: bichos trocados por inimigos do universo DB, com nomes em
  PT-BR (`notes/hack_final.md`; patch só do hack em `patches/versoes-antigas/`).

### Mantido em inglês de propósito
NEXT, HP, LV, AP, KI, EXP, ALL, MISS/TOTAL, Sparking!, logo do jogo e tela de
licença da Nintendo (`notes/imagens.md`).

### Pendente
- Jogar do começo ao fim (primeiro teste completo, na outra máquina).
- Ver no jogo: a maior parte das falas de NPC fora da Cidade do Leste, 36 das
  39 faixas de local e os títulos novos dos capítulos 0 e 7.
- Nomes do glossário marcados "?" (Cutelo, Mestre Shen, Número 8, Punho do Lobo…).

## Onde fica cada coisa

- **Neste repositório:** `scripts/`, `traducao/`, `notes/`, `patches/`.
- **Fora do git** (ver `.gitignore`): ROMs (`rom/`, comerciais e grandes), saídas
  de teste do emulador (`saida/`) e ferramentas de terceiros. Ficam no contêiner
  `dbz-sandbox` (`/ds`) e no backup `C:\Users\daniel.figueira\Backups\DBZ-DS_2026-10-01\`.
