# Levantamento — Attack of the Saiyans (DS)

ROM: `Dragon Ball Z - Attack of the Saiyans (USA) (En,Fr).nds`
128 MB, código `BRPE`, título interno `DB KAI RPG`, SHA-1 `b5d8ebbc…4736`

## A estrutura

- **7.010 arquivos** no NitroFS; 1.074 comprimidos em LZ10
- Gráficos em **formato próprio** (`.chr`, `.ima`), não no padrão Nitro
- `btl/ene/eneNNN_MM.chr` — um arquivo de gráfico por inimigo
- `btl/bdat/<idioma>/bdat.bin` — **o banco de dados de batalha**
- `script/<idioma>/` — roteiro da história
- **6 idiomas no cartucho**: EN, US, FR, SP, GR, IT (mesmo a versão "USA")

## O banco de dados: formato BDAT da Monolith

O `bdat.bin` é um contêiner de **35 tabelas com colunas nomeadas** — o
mesmo formato que a Monolith Soft usa em Xenoblade. Leitor escrito e
validado: 35 tabelas, 567 colunas, zero inconsistência.

Tabelas relevantes: `enemy_param` (173 linhas × 80 b, 47 colunas),
`boss_param` (55 × 88 b), `player_param`, `skill_<personagem>`,
`passive_<personagem>`, itens, acessórios, `character_name` (237 nomes) e
as tabelas de mensagem.

Colunas de `enemy_param`: `name_id`, `file` (sprite), `palno` (paleta),
`size`, `shadow`, `power`, `zeni`, `exp`, `ap`, `item1-4`, `atk1-4`,
`atk1_pow-atk4_pow`, `lv`, `hp`, `mp`, `str`, `def`, `rec`, `tec`, `agi`,
`luc`, resistências (`sleep`, `poison`, `dark`, `panic`, `freez`, `dead`,
`carrot`…) e elementos (`physics`, `slash`, `blast`…).

## Erros meus que o processo pegou

1. **Alinhamento das colunas.** O primeiro registro de coluna vem colado
   no nome da tabela; os seguintes são alinhados a endereço par. Errei a
   regra duas vezes antes de olhar as 35 tabelas lado a lado.
2. **`name_id` é contado a partir de 1.** Com base 0 a lista inteira sai
   deslocada uma linha — e parecia plausível, porque cai nome de saiyajin
   em algum lugar. O teste decisivo: o sprite do Saibaman tem 5 paletas;
   com base 1 as 5 linhas são os 5 Saibamen, com base 0 só 4. Depois da
   correção, toda família (lobos, ursos, coelhos…) cai inteira num sprite.
3. **`bdat.bin` não é LZ10.** Afirmei isso sem conferir; o script de
   escrita pegou (o arquivo começa com `23 00 00 00`, não com `10`).

## Os inimigos comuns: 151 com nome + 22 slots vazios

| Categoria | Inimigos | Sprites |
|---|---:|---:|
| Universo DB | 28 | 10 |
| Referência a DB | 9 | 3 |
| Humano genérico | 34 | 13 |
| **Bicho** | **48** | **16** |
| Monstro genérico | 32 | 11 |
| **Total** | **151** | **53** |

**Universo DB (28):** Saibamen (5), robôs da Caverna dos Piratas (3),
Red Ribbon (11), Grupo Coelho (6), servos da Princesa Serpente (3).

**Referência (9):** vampiro e múmia são os lutadores da Vovó Uranai
(Dracula Man, Mummy Man); o dinossauro remete à sobrevivência do Gohan.

**Bicho (48):** dragões, cobras, avestruz/dodô, aves de rapina, tigres,
lobos, cães, javalis, ursos, pandas, peixes, morcegos, caranguejos,
lagartas, insetos e larvas.

**Humano genérico (34):** bandidos, piratas, assassinos, lutadores de
dojo, saqueadores, xamãs, tribo.

**Monstro genérico (32):** fantasmas, carniçais, demônios, majins,
lobisomens, homens-peixe, experimentos de laboratório, "Giras", robôs.

A classificação é pelo **nome** (texto do próprio jogo) mais o meu
conhecimento de Dragon Ball; as linhas "Referência" são julgamento meu.

## Chefes: 44 com nome

Jackie Chun, Paopao, Monster Carrot, Chiaotzu, Piccolo (×2), Annin,
Shu Machine, Mai Machine, Raditz, Raditz's Soul (×2), Princesa Serpente
(×2), Goz, **Eighter (Androide 8)**, General White, RR Power Robot,
Pilaf Fusion Mech, Pilaf Machine, TPP-EX, Nappa (×2), Vegeta (×2),
Oozaru Vegeta, **Broly (nível 95, 85.000 HP)**, e outros.

## O que isso significa para o hack

- **Trocar o sprite é trocar uma string.** O campo `file` guarda o nome do
  arquivo (`ene039_01`) numa área de strings de tamanho fixo. Trocar
  "lobo" por "Saibaman" é escrever `ene001_01` no lugar — mesmo tamanho,
  sem ponteiro para ajustar. O `bdat.bin` **não é comprimido**:
  edita e grava no mesmo lugar da ROM. (A primeira versão desta nota
  dizia LZ10. Estava errado: os 6 idiomas começam direto com o
  cabeçalho do contêiner, `23 00 00 00`.)
- **Paleta multiplica variedade.** O `palno` escolhe a paleta: o Saibaman
  já tem 5. Dá para ter "Saibaman de gelo", "de fogo" etc. sem desenhar.
- **22 linhas vazias** em `enemy_param` e 11 em `boss_param` — espaço para
  inimigo **novo** sem apagar nenhum existente.
- **Balanceamento é edição de planilha**: HP, EXP, drop e resistência são
  colunas nomeadas.

O que **não** está resolvido: o formato `.chr`. Ele só é necessário para
arte nova (nível 3). Trocar sprite e paleta (níveis 1 e 2) não precisa dele.

## Arquivos gerados

- `saida/inimigos.csv` — todos os inimigos e chefes com sprite e atributos
- `saida/classificacao.csv` — inimigos comuns por categoria
- `saida/todos_nomes.txt` — lista crua
- `saida/inventario.json` — os 7.010 arquivos do cartucho

Scripts: `levantamento_nds.py`, `bdat.py`, `listar_inimigos.py`,
`classificar.py`
