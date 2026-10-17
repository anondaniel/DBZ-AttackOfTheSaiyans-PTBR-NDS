# Diálogos (.sb): reescrita com tamanho livre

Script: `scripts/sb.py` (`textos`, `com_textos`)
Testes: `scripts/teste_sb.py` (todos os scripts), `scripts/traduzir_tut.py` +
`scripts/ler_dialogos.py` (no jogo). Captura em `saida/tut2/montagem.png`.

## Formato

- `0x00` "SB  " `01 00 01 00`; `0x08` u32 offset[6] das seções (em ordem,
  alinhadas a 4)
- seções: 0 código · 1 tabela · **2 textos** · 3 funções · 4 imports · 5 nome da cena
- seção 2: `u32 8, u32 n, u32 off[n]` (relativos ao fim da lista),
  strings C em ordem, zeros até múltiplo de 4
- O código pede texto **pelo índice** (opcode `26 <índice>`, 1 byte; o
  maior script tem 227 textos). As seções 3–5 usam offsets relativos a
  si mesmas. Crescer os textos só exige corrigir 3 offsets do cabeçalho.
- Em 175 scripts um valor do código "parece" apontar para a seção 2: é o
  mesmo trecho de código (`00 1e 00 00`) em todos, uma constante, não um
  ponteiro.

## Marcações no texto

`<p>` abre caixa nova, `<k>` espera botão. A quebra de linha dentro da
caixa é **automática** (por palavra). Cabem 3 linhas.

## Idioma que o jogo lê

A ROM USA lê a pasta **`script/US/`**. A tela mostra "Ki-Blast", grafia
que só existe na US. As traduções vão para US e EN.

## Testes

1. **3.599 scripts** (todas as pastas de idioma): recriar com os mesmos
   textos dá bytes idênticos; com todos os textos 30% maiores, os textos
   são lidos de volta certos e as outras 5 seções ficam idênticas.
2. **No jogo:** as 12 falas do Kuririn na Training Island em PT-BR (mais
   longas que o inglês). Jogado do mapa-múndi até o fim do tutorial pós-
   batalha: 9 caixas conferidas. Quebra de linha certa, acentos certos,
   caixa de 3 linhas cabe, a batalha no meio do evento roda normal.
   As falas da pedra e do fantasma (17–25) não foram alcançadas nesse
   trajeto.

## Próximo: extração em massa

Tirar todos os textos (tabelas `bdat` + scripts `.sb` da pasta US) para
uma planilha com ID, contexto e original, traduzir e reinserir com os
dois escritores.
