# Dragon Ball Z: Attack of the Saiyans (DS) — tradução e hack

## Estado

Aguardando a ROM. O extrator está pronto e validado.

**Coloque o arquivo `.nds` em:** `DBZ DS\rom\`

## O que o levantamento faz

`scripts/levantamento_nds.py` só **lê** bytes — não executa nada da ROM.

1. Lê o cabeçalho (título, código, ARM9/ARM7, overlays)
2. Percorre o sistema de arquivos (NitroFS): FNT para nomes, FAT para posições
3. Abre os pacotes NARC, inclusive aninhados
4. Descomprime LZ10 e LZ11 (compressão da BIOS do DS)
5. Classifica cada arquivo pelo formato: tiles (NCGR), paleta (NCLR),
   sprite (NCER), animação (NANR), fonte (NFTR), texto (BMG), som...
6. Procura o que interessa para o hack de inimigos:
   - **nomes de inimigo** (Saibaman, Raditz, Wolf, Bear...) em ASCII e UTF-16
   - **tabela do bestiário**: arquivo de dados que divide em ~150 registros
     de tamanho fixo (os guias do jogo falam em 150 monstros)
   - **gráficos de batalha** agrupados por pasta

Saída: relatório no terminal + `saida/inventario.json` com todos os arquivos.

## Validação

`scripts/teste_rom_sintetica.py` monta uma ROM mínima com estrutura real
e confere o extrator nela:

| Caminho | Resultado |
|---|---|
| FNT com subpasta aninhada | ✅ |
| LZ10, ida e volta byte a byte | ✅ |
| LZ11 nas três formas de comprimento, byte a byte | ✅ |
| NARC com arquivos dentro | ✅ |
| Tabela de 150 × 24 detectada | ✅ |
| Nomes em UTF-16 | ✅ |

O primeiro rascunho do teste tinha um bug no **gerador** de LZ11 (emitia
um byte de flags novo no meio de um grupo de 8 blocos). O teste pegou,
foi corrigido, e agora confere os bytes em vez de só "reconhecer".

## Limitação conhecida

Se o jogo usar **codificação de texto própria** (tabela de caracteres, como
o SNES), a busca por nome em ASCII/UTF-16 não acha nada. Isso aparece no
relatório como tal — não como "não existe". O próximo passo nesse caso é
descobrir a tabela, do mesmo jeito que foi feito no Super Saiya Densetsu.

## Fontes consultadas

- Sprite Database: https://spritedatabase.net/game/1660
- Chefões conhecidos: Piccolo, Raditz, Saibaman, Nappa, Vegeta, Oozaru
  Vegeta; opcionais Annin, Princesa Serpente, Eighter (Androide 8),
  Desertor da Red Ribbon, Sobrevivente Coelho; superchefe Broly
