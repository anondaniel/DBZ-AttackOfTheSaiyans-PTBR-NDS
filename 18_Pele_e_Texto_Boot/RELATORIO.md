# 18_Pele_e_Texto_Boot: versão 13.1 (atual: 13.1b)

> **13.1b (2026-10-17):** a ROM desta pasta agora é a 13.1b = 13.1 + "Resetting..." (`Apagando...` → `Preparando...`) na tela que vem depois de apertar A no primeiro boot. Ver a seção **8. 13.1b** no fim. A 13.1 anterior ficou guardada como `versoes\DBZ Attack of the Saiyans PT-BR 13.1a.nds`. As seções 1 a 7 descrevem a 13.1 e continuam valendo, exceto os hashes da seção 4 (que são da 13.1a).

Duas correções aprovadas sobre a ROM da etapa 13. Nenhuma pasta antiga foi alterada (os scripts leem `00_Original`, `01_ROM`, `11_Projeto_Recuperado`, `12_Coerencia_Historia`, `13_Correcoes_Revisao` e `_revisao_claude` só para leitura). Nada foi publicado, nada foi baixado, o Switch e os saves originais não foram tocados.

| | |
|---|---|
| ROM 13.1b | `DBZ Attack of the Saiyans PT-BR.nds` (SHA-256 `26785b882a49d34cfcd12cde4b6e75dc4a0df413b7730abf53653cca88070e68`) |
| ROM 13.1a | `versoes\DBZ Attack of the Saiyans PT-BR 13.1a.nds` (SHA-256 `408815b99220a72c9947f3ff902748f10a916b6ff06989198a809cc161637595`) |
| Base | ROM 13, SHA-256 `0616e6c6fdada1e54d0694bd2e552be64dea3c3e592cd88ddf07b31d8bda3a82` (assert no build) |
| Mudou | 8 `.chr` de inimigo (só paletas) e os 2 `bdat.bin` US/EN (13.1: uma célula de texto cada; 13.1b: mais uma célula no US) |

## 1. Pele dos inimigos humanos

### Como foi decidido

1. Para cada sprite das 24 linhas apontadas, gerei o mapa de índices do quadro parado: cada índice da paleta pintado de magenta sobre o sprite em cinza, ampliado 3x a 7x. Conferi também as 3 paletas originais e as novas lado a lado.
2. Índices de pele são os que têm tom de pele nas 3 variantes originais e caem no rosto, nas mãos ou nos braços.
3. O índice 1 é o contorno do sprite inteiro. Nas 3 variantes originais de todos esses sprites ele é sempre o mesmo marrom-escuro (9,7,4), ou seja, não é cor de roupa no desenho original. Nas linhas corrigidas ele volta a (9,7,4), porque o contorno azul ou roxo em volta do rosto e das mãos era parte do problema.
4. Cada índice de pele volta exatamente ao valor da paleta original que serviu de modelo à paleta nova (a mesma variante de onde a etapa 13 girou a matiz). Por isso o tom varia entre as linhas:
   - claro/médio: paletas 0 e 1 dos sprites;
   - moreno: paleta 2 de `ene008_01` (Bandida Glacial), de `ene026_01` (Guardião Peregrino) e de `ene021_01` (Instrutor Rival).
5. As outras cores, incluindo roupa, cabelo, armas e acessórios, ficaram como na 13. A única exceção é a linha 157 (ver "Ajuste de roupa").

Tabela completa e asserts em `scripts\pele131.py` (`PELE`, `ROUPA`, `MANTIDAS`). Cores em RGB555 (0 a 31 por canal).

### Linhas corrigidas (17)

| Linha | Nome | Sprite / paleta | Pele do original | Índice: antes (13) → depois (13.1) | Motivo |
|---|---|---|---|---|---|
| 80 | Lutador Errante | ene021_01 p3 | p0 (claro) | 1: (4,4,9)→(9,7,4); 4: (6,8,23)→(23,15,6); 5: (2,3,17)→(17,11,2) | rosto, mãos e cabelo azuis (4 = meio-tom, 5 = sombra da pele) |
| 101 | Arruaceiro do Bambu | ene021_01 p4 | p0 | 1: (4,9,5)→(9,7,4); 4: (6,23,9)→(23,15,6); 5: (2,17,6)→(17,11,2) | rosto e mãos verdes |
| 111 | Lutador Veterano | ene021_01 p5 | p1 | 1: (9,4,9)→(9,7,4); 4: (21,6,23)→(23,15,6); 5: (16,2,17)→(17,11,2) | rosto e mãos roxos |
| 115 | Instrutor Rival | ene021_01 p6 | p2 (moreno) | 1: (4,4,9)→(9,7,4); 4: (8,12,27)→(27,17,8); 5: (3,5,19)→(19,12,3) | rosto e mãos azuis |
| 95 | Batedor do Ermo | ene012_01 p3 | p0 | 1: (4,6,9)→(9,7,4); 11: (7,15,21)→(21,13,7) | sombra da pele (queixo e braços) azul |
| 104 | Atirador da Montanha | ene012_01 p5 | p0 | 1: (4,9,4)→(9,7,4); 11: (10,21,7)→(21,13,7) | sombra da pele verde |
| 106 | Atirador Veterano | ene012_01 p6 | p2 | 1: (4,3,6)→(9,7,4); 11: (7,6,18)→(25,15,9) | sombra da pele roxa |
| 157 | Batedor Venenoso | ene012_01 p7 | p1 | 1: (9,4,6)→(9,7,4); 11: (25,9,19)→(25,15,9) | sombra da pele magenta (+ ajuste de roupa, abaixo) |
| 103 | Guardião da Floresta | ene026_01 p3 | p1 | 1: (5,4,9)→(9,7,4); 8: (12,15,24)→(24,13,12); 9: (20,23,31)→(31,21,20) | rosto e mãos azuis |
| 117 | Guardião Peregrino | ene026_01 p4 | p2 (moreno) | 1: (4,6,9)→(9,7,4); 8: (7,14,17)→(17,10,7) | sombra do rosto azul-petróleo |
| 114 | Bandida Glacial | ene008_01 p4 | p2 (moreno) | 1: (4,8,9)→(9,7,4); 6: (4,15,15)→(15,8,4); 7: (6,17,19)→(19,12,6) | corpo (pele exposta) ciano |
| 161 | Recruta Escavadora | ene008_01 p5 | p0 | 1: (7,4,9)→(9,7,4); 6: (11,4,23)→(23,11,4); 7: (20,10,28)→(28,20,10); 8: (27,19,30)→(30,27,19) | corpo inteiro roxo |
| 116 | Discípulo Rebelde | ene020_01 p3 | p0 | 1: (5,4,9)→(9,7,4); 5: (9,6,26)→(26,16,6); 6: (4,3,21)→(21,10,3) | cabeça e mãos azuis |
| 156 | Lutador Noturno | ene020_01 p4 | p1 | 1: (4,3,6)→(9,7,4); 5: (7,4,19)→(26,16,6); 6: (3,1,11)→(15,9,1) | cabeça e mãos azul-escuras |
| 136 | Capanga Sombrio | ene016_01 p5 | p2 | 1: (3,6,4)→(9,7,4); 4: (7,20,9)→(28,18,10); 5: (4,17,4)→(23,10,5) | rosto verde |
| 149 | Ladrão do Deserto | ene015_01 p4 | p1 | 1: (5,4,9)→(9,7,4); 5: (4,3,15)→(15,8,3); 6: (7,7,19)→(19,11,7); 7: (12,9,24)→(24,17,9) | rosto, braços e torso azul-violeta |
| 163 | Batedora Venenosa | ene014_01 p4 | p2 | 1: (9,4,9)→(9,7,4); 7: (14,8,16)→(16,11,8) | sombra da pele roxa |

Observações sobre os índices:
- **ene020_01, índice 6:** é a sombra mais escura do rosto e das mãos e também marca os vincos do manto. Nas 3 variantes originais ele é sempre marrom-escuro, mesmo com manto laranja, amarelo ou vermelho. Por isso voltou ao marrom; o manto novo (azul/roxo) ganha vincos marrons como no original.
- Nas linhas corrigidas, os demais índices de pele já eram iguais ao modelo original (conferido por script). Ficaram iguais e não constam na tabela, por exemplo o índice 3 de ene021_01 e o 12 de ene012_01.

### Ajuste de roupa (distância de paleta)

- **157 Batedor Venenoso** (mesmo sprite e modelo da linha 33, Batedor do Ermo): com a pele de volta, a menor distância para a paleta da linha 33 caiu de 82 para 61. O limite do jogo inteiro na etapa 13 é 80.
- O colete e a calça (índices 9 e 10) passaram de verde-azulado para verde-veneno:
  - 9: (8,16,15) → (6,18,9);
  - 10: (10,21,20) → (7,23,11).
- Foi a menor mudança encontrada numa busca de matiz/saturação/brilho que volta a ≥ 80 contra todas as variantes: matiz −40°, saturação ×1,3, brilho ×1,1. A distância ficou em 85. A pele não foi mexida.
- A linha 157 não divide mapa com outra variante do sprite.

### Linhas apontadas e deixadas como estão (7)

| Linha | Nome | Sprite | Motivo |
|---|---|---|---|
| 82 | Robô Sentinela | ene062_01 | robô bípede; não tem pele |
| 99 | Piloto Mercenário | ene003_01 | o piloto do aerodeslizador é um cão antropomórfico (focinho branco, pelo marrom). As variantes originais já mudam a cor do pelo (oliva, malva) |
| 100 | Piloto Veterano | ene003_01 | idem 99 |
| 107 | Ex-Soldado RR | ene005_01 | soldado-cão (focinho, orelhas caídas, cauda); as variantes originais já têm pelo marrom, lilás e bege |
| 121 | Robô das Areias | ene002_01 | robô-caveira de metal |
| 134 | Capanga da Caverna | ene016_01 | humano, mas a pele (índices 3, 4, 5) já é igual à do original. O índice 13 que a checagem apontou é o couro do capuz e da correia (roupa) |
| 135 | Capanga da Fonte | ene016_01 | idem 134 |

Em 134 e 135 o contorno geral continua azul-escuro e roxo-escuro, como em outras linhas não apontadas (113, 155, 162 e outras). É um tom muito escuro e não muda o rosto. Se quiser uniformizar, basta acrescentar o índice 1 dessas linhas em `PELE`.

### Fora da lista: conferido e sem mudança

Vi as outras 24 linhas novas lado a lado com o modelo original (`naoflag`, folha de trabalho). Nenhuma mudou:
- **Pele humana preservada:** 81 Guarda da Mansão (a variante original p1 já tem pele azul-esverdeada; a 13 manteve), 96, 97, 105, 109, 113, 150, 151, 155 e 162.
- **Não humanos:** 76 Lanceiro Nômade (homem-gato); 102, 110, 112 e 118 (homens-urso); 108 (soldado-cão); 131 a 133 (vampiros, tratados como monstros: as variantes originais do sprite já têm pele azul, amarela e vermelha); 74, 75, 119 e 120 (mechas e robôs); 98 (piloto-cão).

### Cabelo em cores não naturais (não mexido)

O pedido era só pele. Ficaram com cabelo colorido, como já estavam na 13:
- 95 azul, 104 verde e 157 magenta: mechas que caem perto do rosto;
- 111 roxo-escuro;
- 114 ciano;
- 161 mecha azul;
- 163 rosa.

Nas variantes originais o cabelo também muda (loiro, ruivo, branco).

### Distâncias de paleta (refeitas, `verificacao\distancias.txt`)

| Métrica (igual à da 13) | Menor na 13 | Menor na 13.1 | Limite |
|---|---|---|---|
| Mesmo mapa (verificar.py: args 2 a 11 dos grupos) | 109 | 109 | ≥ 100 |
| Mesmo mapa (build.py: slots + lista de tipos) | 109 | 109 | ≥ 100 |
| Jogo inteiro (qualquer par com nome, mesmo arquivo) | 82 | 85 | ≥ 80 |

A menor distância no mesmo mapa entre as linhas corrigidas é 122 (106 × 97). A tabela por linha (13 → 13.1) está no arquivo.

## 2. Texto da primeira tela

| | |
|---|---|
| Chave | `Resetting backup memory.<n>Press the A Button to begin.` |
| Antes (13) | `Apagando os dados salvos.<n>Aperte o Botão A para começar.` |
| Depois (13.1) | `Preparando a memória de salvamento.<n>Aperte o Botão A para começar.` |
| Posições | `cf_mes_MENU` linha 120: coluna `us` no `btl/bdat/US/bdat.bin` e coluna `en` no `btl/bdat/EN/bdat.bin`. Procurei a frase em todos os 7010 arquivos da ROM 13; só existe nesses dois. |
| Largura | linha 1: 162 px na fonte pequena (latin1) e 190 px na grande (latin0). Os limites do grupo (maior original) são 176 e 198/201 px. Cabe numa linha; a quebra `<n>` existente foi mantida. |
| Na tela | conferido no emulador: as duas linhas aparecem centralizadas e inteiras (`verificacao\tela_boot_texto_novo.png`). |

- O dicionário também foi atualizado:
  - `dados\ptbr.json`: cópia da 13 com só essa chave mudada;
  - `texto\ptbr_mudancas.json`;
  - `texto\correcoes_texto.json`: a lista acumulada do verificador, com as 2 entradas atualizadas.
- O delta da 13.1 fica em `texto\correcoes_131.json`.
- "Resetting..." (`Apagando...`) e "Quicksave data corrupt. Deleting." **não foram mexidos**.
- Ao apertar A, a tela seguinte mostra "Apagando..." com o indicador girando (aparece no GIF 00). Ficou como pedido; se quiser coerência com o texto novo, a troca natural seria "Preparando...". **Feito na 13.1b (seção 8).**

## 3. Build

```
cd 18_Pele_e_Texto_Boot\scripts
python -B build.py              # ROM 13 (assert SHA-256) -> ROM 13.1
python -B atualizar_textos.py   # texto\correcoes_texto.json, texto\ptbr_mudancas.json, dados\ptbr.json
python -B gerar_bps.py          # 3 BPS + 2 aplicadores + recusa + hashes -> verificacao\hashes_e_bps.json
python -B verificar.py          # integridade.txt, encontros.txt, diff_13.txt, resumo.json
python -B distancias.py         # verificacao\distancias.txt
python -B ..\texto\verificar_textos.py "..\DBZ Attack of the Saiyans PT-BR.nds" ..\verificacao\texto
python -B folha_pele.py         # verificacao\pele_antes_depois.png
cd ..\midia\antes_depois\scripts && python -B gerar.py
```

- **Determinístico:** rodei o build duas vezes (gravando e `--seco`) e deu o mesmo SHA-256. O `gerar_bps.py` rodado duas vezes deu os mesmos 3 BPS.
- **Gravação no lugar:** os `bdat.bin` US/EN crescem 64 bytes, mas cabem na folga de alinhamento até o próximo arquivo. Por isso são gravados no mesmo endereço da 13, sem realocar. Os `.chr` têm o mesmo tamanho.
- **Cabeçalho:** os primeiros 0x1000 bytes ficaram idênticos aos da 13, inclusive tamanho usado e CRC16.
- **Scripts copiados da 13:**
  - `comum.py`, com os caminhos da pasta 18 e `rom('13')` com assert;
  - `dados_inimigos.py` e `plano13.py`, sem mudança;
  - `verificar.py`, com saída na pasta 18 e a seção nova `diff_13`;
  - `gerar_bps.py`, com 3 origens e recusa testada nos 2 aplicadores;
  - `texto\verificar_textos.py` e `texto\lib\`, sem mudança.
- **Scripts novos:** `pele131.py`, `build.py`, `atualizar_textos.py`, `distancias.py`, `folha_pele.py`.

## 4. Hashes

> Hashes da **13.1a** (a ROM e os BPS desta seção foram substituídos pela 13.1b; os novos estão na seção 8).

**ROM 13.1** (134.217.728 bytes)

| | |
|---|---|
| SHA-256 | `408815b99220a72c9947f3ff902748f10a916b6ff06989198a809cc161637595` |
| SHA-1 | `6deb13ca523c43270cfa7d2f45b392eb9fbe13cf` |
| CRC32 | `cc5d768c` |

**BPS**

| Patch | Origem | Bytes | SHA-256 | SHA-1 |
|---|---|---|---|---|
| `DBZ_PTBR_v13.1_sobre_rc1.bps` | rc.1 (`01_ROM`, SHA-256 `41412a47…`, CRC32 `670e3cf1`) | 284.962 | `6a95176e5b24ae450d7047a1c5554010f85f1a0880e0edcb5efe57fedc3ebc96` | `e3d56895c425e988b2f75ae640447d3c0a182859` |
| `DBZ_PTBR_v13.1_completo.bps` | ROM original em inglês (USA, BRPE, CRC32 `a9f0b8f9`, mesma origem do patch completo da 13) | 2.541.760 | `863d9fdaec876a7bdeaf50b52fe3b568b2934558a724bd7da4050e2d085b5210` | `a24c7fac6159653a837beb62cfa50aa15ce5f456` |
| `DBZ_PTBR_v13.1_sobre_13.bps` | ROM 13 (SHA-256 `0616e6c6…`, CRC32 `51717d80`) | 41.957 | `cbb5ff1e9827c10dfce3b107c0846935a7338d8f5760c9ede3db5f03575eb8b2` | `9258b57e6e01ba3a9be74f25f319b21f2e7e9bd1` |

- Cada BPS foi aplicado com dois aplicadores independentes:
  - `11_Projeto_Recuperado\scripts\bps.py`;
  - `_revisao_claude\01_integridade\work\meubps.py`.
- Os dois reproduzem a ROM 13.1 byte a byte, com CRC de origem, de destino e do patch corretos.
- Cada BPS recusa as outras origens (original, rc.1, etapa 12, ROM 13): `bps.py` levanta "ROM de origem errada" e `meubps.py` acusa CRC de origem e de destino errados.
- O CRC32 de todo BPS válido é `2144df1c` (propriedade do formato).
- Detalhes, incluindo os hashes de todos os BPS do projeto, em `verificacao\hashes_e_bps.json`.

## 5. Verificações (0 falhas)

- **`verificar.py`** (revisões 01 e 02 refeitas sobre a 13.1): `FALHAS: []`.
  - Integridade: ARM9, ARM7, FNT e banner iguais ao original; CRC16 válido; FAT sem sobreposição; cauda 0xFF.
  - Só mudaram `.chr`, `bdat` e scripts US/EN em relação à rc.1; 0 bytes fora.
  - Encontros idênticos ao original; aparência única por linha; nenhum conflito nome × aparência; nomes únicos.
  - Distância no mesmo mapa ≥ 100 (menor 109).
- **`diff_13.txt`** (13 → 13.1):
  - mudaram 10 arquivos, todos gravados no lugar;
  - entradas da FAT alteradas: só as dos 2 `bdat` (tamanho);
  - cabeçalho idêntico;
  - em cada `.chr` só mudaram os pares (paleta, índice) da tabela, e cabeçalho, tiles e quadros são idênticos;
  - em cada `bdat` só mudou a célula `cf_mes_MENU:120` (US: `us`, EN: `en`); FR, SP, GR e IT ficaram iguais;
  - 0 bytes diferentes fora desses arquivos e das suas entradas na FAT.

  Os 10 arquivos:
  - `btl/bdat/EN/bdat.bin` (122.148 → 122.212 bytes)
  - `btl/bdat/US/bdat.bin` (122.532 → 122.596 bytes)
  - `btl/ene/ene008_01.chr`, `ene012_01.chr`, `ene014_01.chr`, `ene015_01.chr`, `ene016_01.chr`, `ene020_01.chr`, `ene021_01.chr`, `ene026_01.chr` (mesmo tamanho)
- **`verificar_textos.py`** (revisão 03): RESULTADO OK.
  - 716/716 correções; 0 divergências de marcação; 0 glifos faltando;
  - 0 erros de largura (4 avisos, os mesmos da 13);
  - inglês suspeito 0/0;
  - saída idêntica à da 13, exceto o caminho do JSON.
- **`distancias.py`:** `FALHAS: []` (tabela na seção 1).

## 6. Mídia

### Antes e depois (`midia\antes_depois\`)

- Regenerado com a ROM 13.1, com os scripts copiados de `13_Correcoes_Revisao\midia\antes_depois\scripts\`, que agora apontam para a 13.1.
- Os nomes ainda vêm do CSV da 13, porque os nomes não mudaram.
- Arquivos:
  - `antes_depois_inimigos.png` e `antes_depois_01..06.png` (versão técnica);
  - `forum\inimigos_1..4.png` (versão do post).

### GIFs (`midia\gifs\`)

**01 a 03:** copiados da 13 sem mudança.

**04_inimigo_trocado.gif** (1.713.842 bytes, 86 quadros, 11,8 s):
- Gravado com a ROM 13.1, melonDS 1.1 numa área de trabalho oculta (sem janela, sem foco, sem teclas globais) e o harness de `_revisao_claude\05_gifs`. As cópias dos scripts usados estão em `midia\gifs\scripts\`.
- Mesmo método da 13:
  - ROM de teste feita com `04_teste\rom_teste\forcar_grupos.py`, modo `TODOS=81`, nos mapas `tut01_00`, `tut02_00` e `c0002_01`;
  - cópia do save do Switch (`saves_copias\copia_switch_savefiles_melonds.sav`, SHA-256 `346c0070…` conferido);
  - `batalha_gif.py … entrada` anda na caverna até a batalha;
  - `montar2.py "3.0-14.75@8"` monta o GIF.
- Mostra Kuririn andando na caverna, a entrada na batalha contra dois "Lutador Errante" já com rosto e mãos em tom de pele, e o alvo "Lutador Errante A".
- Conferência por hash (`hash_teste.txt`):
  - ROM de teste: SHA-256 `3281164c…4c3f`;
  - 21 arquivos diferentes da 13.1, todos `.sb` dos 3 mapas nas 7 pastas;
  - 0 bytes fora deles e da FAT; cabeçalho igual;
  - `btl/ene/ene021_01.chr` idêntico (`331e4d36…`);
  - os 6 `bdat.bin` com o nome idênticos.

**00_tela_boot_texto_novo.gif** (103.532 bytes, 9 s, só para conferência, não para o post):
- Instância nova sem save.
- Mostra a tela "Preparando a memória de salvamento. / Aperte o Botão A para começar." parada por 3 s; depois do A, "Apagando..." e os logos.

### Limpeza

As cópias de trabalho foram apagadas no fim e nenhum melonDS ficou aberto:
- ROM de teste e cópia da 13.1;
- os 2 `.sav` de trabalho;
- emuladores copiados e quadros brutos.

## 7. O que foi conferido visualmente e o que não foi

### Conferido

- Mapas de índices ampliados dos 13 sprites envolvidos: os 12 das linhas apontadas, mais ene023_01 e ene017_01 da lista de fora.
- Rostos ampliados 7x a 8x, antes e depois, de 163, 136, 161, 114, 157, 149 e dos 8 tons de ene012_01.
- `verificacao\pele_antes_depois.png` (4x, as 17 linhas, parado e golpe, antes e depois): todas com rosto e mãos em tom de pele e roupa da 13 mantida.
- Quadros do GIF 4: Lutador Errante (linha 80) em jogo, com sprite e nome iguais aos da 13.1.
- Tela do boot no emulador.
- `forum\inimigos_1.png` regenerado.

### Não conferido

- **Animações:** só os quadros "parado" e "golpe" de cada sprite. Dano, vitória e outros golpes não foram vistos um a um. A paleta é a mesma em todos os quadros, mas um índice de pele poderia aparecer pintando outra coisa num quadro não visto.
- **Em jogo:** das 17 linhas corrigidas, só a 80 foi vista no emulador. As outras 16 só foram desenhadas pelo script, com o mesmo desenhador do quadro antes/depois.
- **Outras imagens:** `antes_depois_01..06`, `antes_depois_inimigos` e `forum\inimigos_2..4` foram regenerados, mas não revistos imagem a imagem.
- **Console e Switch:** não testado em console real nem no Switch.

## 8. 13.1b: "Resetting..." → "Preparando..."

Pedido aprovado: depois de apertar A na primeira tela ("Preparando a memória de salvamento. / Aperte o Botão A para começar."), a tela seguinte dizia "Apagando...". Agora diz "Preparando...".

### Onde a chave aparece

| | |
|---|---|
| Chave | `Resetting...` |
| Posição trocada | `btl/bdat/US/bdat.bin`, `cf_mes_MENU` linha 121, coluna `us` (única) |
| Antes (13 / 13.1a) | `Apagando...` |
| Depois (13.1b) | `Preparando...` |
| `btl/bdat/EN/bdat.bin` | não tem a chave: no EN a linha 121 é `Saving...` (`Salvando...`). Não foi mexido. |
| Outros arquivos | procurei `Resetting`, `Apagando` e `Preparando` nos bytes de todos os arquivos da ROM original, da 13 e da 13.1a (inclusive os `.sb` de `script/US` e `script/EN`) e nas células de todos os 6 bdat. Só aparecem no `cf_mes_MENU` (linhas 120 e 121 e o "Apagando." da linha 16, do salvamento rápido, que é outra chave e não foi mexido). |

### Em que telas aparece (conferido no código do ARM9)

- O jogo lê as mensagens de `cf_mes_MENU` pela função `0x02018CE4` → `0x0201B928` (coluna `us`). O índice é contado a partir de 1 (`sub r2,r3,#1` em `0x0202A984`), então a **mensagem 122 = linha 121**.
- A constante 122 só é usada como mensagem num lugar: a rotina de boot `0x0204E4A8`, que é a primeira cena do jogo (ponteiro em `0x02000C4C`). Ela confere o save e, quando a memória precisa ser preparada (estado 20):
  1. mostra a mensagem 121 (linha 120, "Preparando a memória de salvamento. / Aperte o Botão A...") e espera o A;
  2. mostra a mensagem 122 (linha 121, agora "Preparando...") e formata a memória de salvamento;
  3. se der certo, segue para os logos; se falhar, mostra a mensagem 123 (linha 122, "Falha ao apagar...") e trava.
- O outro `mov r0,#122` do ARM9 (`0x0207C7A0`) é um efeito sonoro (`0x0200BB30`, volume 127), não texto.
- A tela "dados corrompidos e serão apagados, aperte A" (linha 124, mensagem 125, em `0x0201B1A8`) é outro fluxo e não mostra a mensagem 122 depois.
- Não há outra tela que use a linha 121. Por isso "Preparando..." faz sentido em todos os casos em que ela aparece.

Observação, sem mudança: se a formatação falhar, a mensagem de erro continua "Falha ao apagar. Desligue o console e recoloque o cartão." (chave "Memory reset failed..."). Ela só aparece com erro de gravação no cartão. Se quiser coerência total, a troca seria algo como "Falha ao preparar a memória".

### Largura

`Preparando...` tem 60 px na fonte pequena (latin1) e 70 px na grande (latin0). O original "Resetting..." tinha 52/59 px e "Apagando...", 52/60 px. O limite do grupo (maior original) é 195/226 px.

### Scripts

- `texto\correcoes_131.json`: 3 entradas (US 120, EN 120 da 13.1 e US 121 da 13.1b).
- `scripts\build.py`: agrupa as células por bdat; cada célula confere o "antes" (assert); confere que todas as células de todas as tabelas ficaram iguais, exceto as pedidas para aquele arquivo; grava cada bdat uma vez. Recusa célula repetida.
- `scripts\atualizar_textos.py`: agrupa por chave inglesa (`chave_en`). Para cada chave valem os mesmos asserts da 13.1: um só "antes" e um só "depois", e o dicionário da 13 tem exatamente o "antes". Confere também que só essas chaves mudaram nos 2 dicionários, que a `chave_en` da lista acumulada bate e que a ROM nova tem o texto em cada célula.
- `scripts\gerar_bps.py`: metadado "v13.1b" e data 2026-10-17. Os nomes dos arquivos continuam `v13.1`. Agora também testa a recusa da 13.1a como origem e dá erro se o `bps.py` aceitar uma origem errada (antes só registrava).

### Build

- **Base:** ROM 13, com assert de SHA-256.
- **Determinismo:** rodei o build 3 vezes (`--seco` e 2 gravando) e deu sempre o mesmo SHA-256. O `gerar_bps.py` rodado 2 vezes deu os mesmos 3 BPS.
- **US `bdat.bin`:** 122.532 → 122.612 bytes (13.1a: 122.596). A tabela `cf_mes_MENU` cresceu mais 16 bytes. O arquivo continua gravado no mesmo endereço (`0x07685400`; folga até o próximo arquivo: 122.880).
- **13.1a → 13.1b:** só mudou o `btl/bdat/US/bdat.bin` (a célula `cf_mes_MENU:121:us`) e a entrada dele na FAT. O cabeçalho é idêntico.

### Hashes 13.1b

**ROM 13.1b** (`DBZ Attack of the Saiyans PT-BR.nds`, 134.217.728 bytes)

| | |
|---|---|
| SHA-256 | `26785b882a49d34cfcd12cde4b6e75dc4a0df413b7730abf53653cca88070e68` |
| SHA-1 | `c1b41704549c2168d74c0b57ec48a1f771ffb3b1` |
| CRC32 | `f15dda6c` |

**ROM 13.1a guardada** (`versoes\DBZ Attack of the Saiyans PT-BR 13.1a.nds`): SHA-256 `408815b99220a72c9947f3ff902748f10a916b6ff06989198a809cc161637595`, SHA-1 `6deb13ca523c43270cfa7d2f45b392eb9fbe13cf`, CRC32 `cc5d768c`. É a mesma ROM das seções 1 a 7.

**BPS**

| Patch | Origem | Bytes | SHA-256 | SHA-1 |
|---|---|---|---|---|
| `DBZ_PTBR_v13.1_sobre_rc1.bps` | rc.1 (CRC32 `670e3cf1`) | 284.979 | `4b24640e709332504e2cc380240fd1983f1abc8e00741ad66f3a17fac4029eda` | `a451b015b8af8c0b9cdecf76bd44525c26c0fb99` |
| `DBZ_PTBR_v13.1_completo.bps` | original em inglês (USA, CRC32 `a9f0b8f9`) | 2.541.776 | `0e9d59462dbbab873bdd5763593e38ef0f16c1beae7d4a7097bf02969e63dc55` | `f706a978fddaa17f40ce8705b0922215355b46c8` |
| `DBZ_PTBR_v13.1_sobre_13.bps` | ROM 13 (CRC32 `51717d80`) | 42.657 | `26e8ada1cd10e68bf1f6ee024ba7fb8b20c0ac73844e8f3412fb853bd238773c` | `0c05458687e376f8f3222f4b11fdfde559ceb295` |

- Cada BPS reproduz a 13.1b byte a byte com os 2 aplicadores (`bps.py` e `meubps.py`). CRC de origem, de destino (`f15dda6c`) e do patch estão corretos.
- Cada BPS recusa as outras origens: original, rc.1, etapa 12, ROM 13 e 13.1a.
- Detalhes em `verificacao\hashes_e_bps.json`.

### Verificações (0 falhas)

- **`verificar.py`:** `FALHAS: []` (integridade e encontros).
  - `diff_13.txt` sem falha: os mesmos 10 arquivos da 13.1, todos gravados no lugar, sem arquivo novo (mesma árvore FNT).
  - Células: bdat US `[cf_mes_MENU:120:us, cf_mes_MENU:121:us]`, bdat EN `[cf_mes_MENU:120:en]`; FR, SP, GR e IT iguais.
  - 0 bytes diferentes fora desses arquivos e das suas entradas na FAT.
- **`verificar_textos.py`:** RESULTADO OK.
  - 716/716 correções; 0 divergências de marcação; 0 glifos faltando;
  - 0 erros de largura (4 avisos, os mesmos de antes);
  - inglês suspeito 0/0;
  - os arquivos de saída são idênticos aos da 13.1a, exceto o tempo.
- **`distancias.py`:** `FALHAS: []`; `distancias.txt` idêntico ao da 13.1a (as paletas não mudaram).

### Na tela

- **Captura:** `verificacao\tela_boot_2_texto_novo.png` (384×576, as duas telas).
- **Como:** melonDS 1.1 numa área de trabalho oculta (sem janela visível, sem foco, sem teclas globais), com os scripts do harness de `_revisao_claude\05_gifs` (cópias de `midia\gifs\scripts`). Rodei de uma pasta temporária, com instância nova sem save.
- **Sequência:**
  1. aparece a tela "Preparando a memória de salvamento. / Aperte o Botão A para começar.";
  2. com o A, aparece "Preparando..." centralizado e inteiro, com o indicador girando embaixo, por cerca de 1,4 s;
  3. depois vêm os logos ("Licensed by Nintendo" e créditos).
- **Limpeza:** a cópia do emulador, a cópia da ROM (`boot.nds`), o `.sav` criado e os quadros brutos foram apagados. Nenhum melonDS ficou aberto.

### Dicionário

- `dados\ptbr.json` e `texto\ptbr_mudancas.json`: `"Resetting..."` passou a ser `"Preparando..."`. A chave da primeira tela continua com o texto da 13.1.
- `texto\correcoes_texto.json`: a entrada `US:cf_mes_MENU:121:us` agora tem "depois" = `Preparando...`.

### Não conferido

- Console real e Switch.
- A mensagem de falha (linha 122), que só aparece com erro de gravação no cartão.
