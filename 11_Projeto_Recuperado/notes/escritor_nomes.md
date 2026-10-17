# Escritor de strings BDAT (tamanho livre)

Script: `scripts/bdat_strings.py` (`gravar_str`, `conferir`)
Testes: `scripts/teste_bdat_strings.py`
Demo no jogo: `scripts/demo_soldado_saiyajin.py`, captura em `saida/escritor_nomes.png`

## Layout que tornou isso simples

Conferido nas 35 tabelas de cada um dos 6 `bdat.bin` (`bdat_layout.py`):

- **Contêiner:** `u32 n_tabelas`, `u32 tamanho_do_arquivo`,
  `u32 offset[n]`. O segundo campo é o tamanho total. Antes eu tratava
  esse campo como se fosse o offset de uma tabela.
- **Tabela:** cabeçalho, colunas, linhas, **strings no fim** (C, latin-1),
  zeros até múltiplo de 16. A string é apontada por `u16` relativo ao
  início da tabela. **Não há** campo de tamanho de strings nem checksum.
  Os bytes 0x12–0x1F do cabeçalho são zero em todas as tabelas.
- `character_name` é a última tabela do arquivo.

## Como grava

1. Se a string antiga não é compartilhada com outra célula e o texto
   novo cabe nela, grava no lugar e completa com zeros.
2. Senão, anexa o texto no fim das strings da tabela e aponta a célula
   para ele. Se faltar espaço, a tabela cresce (alinhada a 16), as
   seguintes são empurradas e os offsets do contêiner e o tamanho do
   arquivo são corrigidos.
3. `conferir()` relê as 35 tabelas e exige que **toda** célula seja igual
   à original, exceto as pedidas.

O `bdat.bin` maior não cabe no lugar original da ROM. O
`nds_rom.substituir` o move para depois da área usada e atualiza a FAT,
o tamanho usado e o CRC.

## Testes

Fora do jogo, nos 6 idiomas: menor (no lugar), maior na última tabela,
maior numa tabela do meio (empurra 34 tabelas) e várias seguidas. Todos
passam no `conferir`.

No jogo: o Wolf (linha 104) recebeu o sprite do Raditz, e o **nome do
próprio lobo** (`character_name[113]`) foi reescrito:
- "Saiyan Soldier" (14 letras): ok.
- "Saiyan Elite Warrior" (20 letras): ok, a caixa do nome se ajusta ao
  texto. O maior nome original é "Ultimate Pandaman" (17).
- A batalha vai até o fim (ataques, vitória, item, volta ao mapa).

## Consequência para o hack

Cada bicho trocado pode ganhar **nome próprio**, reescrevendo o nome
dele mesmo. Não precisa mais apontar para "Saibaman/J. Sai/…", e o
limite de 5 nomes deixa de existir. As colunas de nome por idioma são
`en`, `us`, `fr`, `sp`, `gr`, `it`.

Para a tradução falta ver a fonte (acentos) e os textos que ficam nos
scripts `.sb`, que têm formato próprio.
