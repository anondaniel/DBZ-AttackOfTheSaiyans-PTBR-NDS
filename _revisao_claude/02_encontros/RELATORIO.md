# Revisão independente: encontros e coerência dos inimigos

Escopo: ROM `12_Coerencia_Historia\DBZ Attack of the Saiyans PT-BR Coerencia.nds` (SHA-256 `130b4ad8…`), comparada com a rc.1 (`01_ROM`, `41412a47…`) e com o original (`00_Original\*.zip`, CRC32 `a9f0b8f9`, lido em memória).
Método: só leitura. Usei os módulos do projeto (`nds_rom`, `bdat`, `dump_tiles`, `render_quadros`, `chr_paletas`) com bytecode desligado, e scripts próprios em `work\`. Os dados brutos estão em `work\sets.txt` (conjuntos de encontros por mapa, com níveis) e em `work\regioes.txt` (região × capítulo × antes/depois).

## Veredito

Ficou bom tirar os Saiyajins e os Saibamen inventados pela rc.1 das áreas iniciais. Mas a revisão também trocou, para todo o jogo, as 4 variantes originais de Saibaman (linhas 1–4). Essas variantes são justamente os Saibamen da batalha canônica do capítulo 14. Hoje o diálogo diz "Uma luta de um contra um com os Saibamen!", e o jogador enfrenta "Robô de Patrulha". **Não recomendo liberar a ROM sem reverter as linhas 1–4**, ou pelo menos a linha 1.

## 1. Contagens declaradas × refeitas

| Item | Declarado | Refeito | Observação |
|---|---|---|---|
| Animais substituídos | 48 | 48 | Linhas do `PLANO`. Original→Coerência e rc.1→Coerência: exatamente 52 linhas de `enemy_param` diferentes (48 + 4). |
| Variantes de Saibaman | 4 | 4 | Linhas 1–4 (J./C./K./T. Sai). 46 nomes mudaram em relação à rc.1. As linhas 81, 107, 108, 112, 132 e 136 mantiveram o nome da rc.1 e trocaram só o sprite. |
| Grupos | 2.143 | 2.143 | Todas as chamadas `SetEnemyParty` têm argc=15. O `grupos.json` é idêntico ao meu decodificador. **Só 270 grupos são distintos**: as cenas repetem as tabelas dos mapas. |
| "Mapas" | 183 | 183 | São **arquivos de script**: 125 mapas (`cf0`), 57 cenas (`cf1`) e 1 de debug. |
| Grupos alterados | — | 0 | Os 2.143 grupos são byte a byte iguais no original, na rc.1 e na Coerência. |
| Arquivos alterados | 27 | 27 | São 21 `.chr` e 6 `bdat.bin`. ARM9, ARM7 e todos os roteiros estão idênticos à rc.1. `boss_param` não foi tocado. |

## 2. Linha do tempo usada

O capítulo de cada mapa vem dos scripts de cena `cCCss` que o referenciam. Os chefes confirmam a ordem.

- 0: Ilha de Treinamento (Jackie Chun).
- 1: Cidade do Leste e Floresta de Bambu.
- 2: Montanha Paozu.
- 3: Travessia Divina.
- 4: Torneio (Piccolo).
- 5: Castelo do Cutelo, Cinco Elementos, Vulcão Kiwi e Frappe.
- **6: Ermo do Espinafre, onde chega o Raditz (chefes `???`/Raditz em `spi01`).**
- 7: Deserto Break.
- 8: Holly, Fonte do Eremita e Leste de Paozu.
- 9: Outro Mundo.
- 10: Yunzabit, Vaso do Diabo, Torre Muscle, Esgoto, Caverna dos Piratas, Deserto e Castelo do Pilaf.
- 11: Nemuria.
- 12: Mutaito.
- 13: Senhor Kaioh.
- **14: Ermo Páprica, com os Saibamen e o Nappa.**
- **15: Ermo Gizard, com o Vegeta.**
- 16: epílogo.

Muitos mapas também têm um conjunto "tardio", de nível 46–52 (às vezes com o raro Dododo nv80 e o Broly nv95). As variantes originais de Saibaman só aparecem nesses conjuntos tardios, sempre com nível 48–52, e nos eventos do capítulo 14. Não decodifiquei o gatilho desses conjuntos tardios.

## 3. Tabela por região e capítulo

Os campos de combate não mudaram em nenhuma linha, então o nível de cada região é o mesmo de antes. Aqui só a aparência e o nome mudaram.

| Região (prefixo) | Cap. | rc.1 (trocados) | Coerência | Avaliação |
|---|---|---|---|---|
| Ilha de Treinamento (tut) | 0 | Serva da Princesa nv3 | Lutador Errante | OK, corrige um anacronismo |
| Floresta de Bambu (bam) | 1 | Soldado Saiyajin, Saibaman do Bambu | Arruaceiro do Bambu, Discípulo Expulso | OK, corrige |
| Montanha Paozu (pao), conj. história | 2/8 | Saibaman (lobo), Vampiro Sanguinário | Atirador da Montanha, Vampiro Sanguinário | OK, corrige |
| Montanha Paozu, conj. tardio nv46–52 | tardio | **J. Sai (original)**, Elite Saiyajin, Aviador RR, Saibaman Rubro/Feroz | Robô de Patrulha, Mercenário de Elite, Piloto Renegado, Atirador Veterano, Mestre Errante | J. Sai nv52 é do jogo original; não está no conjunto do cap. 2 (nv8) |
| Travessia Divina (krd) e Cinco Elementos (gog) | 3/5 | Vampiro | Vampiro Errante | OK |
| Monte Frappe (fur) | 5 | Soldado Glacial, Saibaman Glacial/das Neves | Mercenário da Neve, Guerreira Errante, Bandida Glacial | OK, corrige |
| Cutelo / Holly / Enma (gyu/hii/enm) | 5/8/9 | Robô Ártico RR, Saibaman Glacial/da Nevasca | Guardião Errante, Guerreira Errante, Guardião Peregrino | OK. Bandidos vivos no Palácio do Enma já vêm do original. |
| Vulcão Kiwi (kiu) | 5 | Recruta Incendiário | Soldado Incendiário | OK. Visual = Soldado de Elite RR. |
| Ermo do Espinafre (spi) | 6 | Batedor/Brutamontes/Elite Saiyajin, Saibaman Faminto/Escavador | Batedor do Ermo, Brutamontes do Ermo, Saqueador do Ermo, Batedor Escavador, Mercenário de Elite | OK, corrige. Ver ALTO-3 (Brutamontes do Ermo). |
| Deserto Break (kou) | 7/11 | Serva da Princesa, Saibaman, Recruta RR, Robôs RR, Batedor/Brutamontes/Elite Saiyajin | Lutador Errante, Atirador da Montanha, Recruta Renegado, Mecha Patrulheiro/de Combate, Batedor(a)…, Mercenário de Elite | OK, corrige. Ver MÉDIO-7 (cores quase iguais). |
| Fonte do Eremita (sen) | 8 | Aviador Azul RR, Robô Pirata, Capanga Gigante | Piloto Mercenário, Robô Patrulheiro, Capanga da Fonte | OK |
| Mansão da Princesa (sna) | 9 | Guarda da Mansão | Guarda da Mansão | OK |
| Floresta do Outro Mundo (for) | 9/13 | Recruta Veterano, Soldado Dimensional | Aprendiz da Floresta, Guardião da Floresta | OK |
| Yunzabit (yun) | 10 | Espião RR, Brutamontes Glacial | mesmos nomes, sprites novos | Narrativa OK. Ver ALTO-3. |
| Torre Muscle (mas) | 10 | Espião RR | Espião RR | OK. A Red Ribbon remanescente é lore do próprio jogo. |
| Vaso do Diabo (ben) | 10 + tardio | Rei Vampiro; tardio J./K./T. Sai nv52 | Vampiro Ancião; Robô de Patrulha, Mutante Errante/Sombrio | Conjunto tardio: troca discutível |
| Caverna dos Piratas (kai) | 10 | Robô Pirata Selvagem, Capanga | Robô da Caverna, Capanga da Caverna | OK |
| **Castelo do Pilaf (pir)** | 10 | Serva Venenosa, Sentinela RR, Saibaman Supremo, Rei Vampiro | **Corsária Venenosa, Sentinela Pirata, Corsária Veterana**, Vampiro Ancião | MÉDIO-6: o castelo foi confundido com a caverna |
| Deserto (snd) | 10 + tardio | Robô Alado RR, Robô Pirata das Areias, Saibaman Venenoso; tardio J./C./K. Sai | Mecha Patrulheiro, Robô das Areias, Batedor Venenoso; Robôs/Mutante | Conjunto da história OK; tardio discutível |
| Esgoto (ges), est07–09 | tardio | J./C./K./T. Sai (est07: grupo com **6× J. Sai**) | Robô de Patrulha/do Deserto, Mutante Errante/Sombrio | Discutível. Ver MÉDIO-7. |
| Campo do Mutaito (mut) | 12 | Brutamontes Campeão, Saibaman Feroz/Noturno | Lutador Veterano, Mestre Errante, Lutador Noturno | OK. Ver MÉDIO-7. |
| **Ermo Páprica (nap) + cenas c14** | **14** | K. Sai, Elite Saiyajin…; **evento: J. Sai** | Mutante Errante…; **evento: Robô de Patrulha** | **CRÍTICO-1** |
| **Ermo Gizard (las)** | **15** | J./K. Sai, Aviador Sombrio RR | Robô de Patrulha, Mutante Errante, Piloto Veterano | **ALTO-2** |

Sobre os "inimigos iniciais terrestres": nos capítulos 0 a 13 não sobrou nenhum Saiyajin nem Saibaman. Todas as entradas da rc.1 que antecipavam a história foram corrigidas, e a Red Ribbon que ficou é a remanescente que o próprio jogo já usa (Desertor, Sobrevivente). O erro está no sentido oposto: os Saibamen saíram também de onde eles são canônicos.

## 4. Problemas por gravidade

### CRÍTICO

**1. A batalha canônica contra os Saibamen virou luta contra robôs.**

- Estas cenas chamam `SetEnemyParty` com evento (arg12 = 41, flag `0x01000011`):
  - `c1402_02/98/99`, `c1403_00/01/98/99`, `c1404_00/03`, `c1406_01`, `c1407_00`, `c1408_03` e `c1409_00`;
  - os mapas `nap01–03`.
- Os grupos são:
  - `[1,1,ID2]`: Tenshinhan × Saibaman;
  - `[2,1,ID2]`: Yamcha × Saibaman;
  - `[3,7,ID2×4]`: os 4 que sobram.
- O ID 2 é a linha 1 (J. Sai), que agora se chama "Robô de Patrulha" e usa o sprite `ene062_01` (Robô Ajudante).
- O diálogo da própria cena, já em PT-BR, fala de Saibamen: "Uma luta de um contra um com os Saibamen!" (c1402_02), "O nível de poder dos Saibamen devia ser 1200!" (c1403_00) e "monstro verde" (c1403_00).
- O relatório da outra IA diz que o Saibaman básico foi preservado. Isso não vale na prática: a linha 0 (ID 1) **nunca** aparece como inimigo, porque o ID 1 é só o marcador de vazio e o espaço reservado para invocação da formação 2. Resultado: **não existe mais nenhum Saibaman em batalha no jogo.**
- Correção: reverter as linhas 1–4 para os valores da rc.1/original.

### ALTO

**2. Os Saibamen saíram também dos encontros aleatórios dos capítulos 14 e 15.**

- No Ermo Páprica (`nap`, onde eles brotam), K. Sai virou Mutante Errante.
- No Ermo Gizard (`las`, capítulo do Vegeta), J. Sai virou Robô de Patrulha e K. Sai virou Mutante Errante.
- Os conjuntos nv52 de ben, snd, ges, est07–09 e pao têm o mesmo nível dos capítulos 14 e 15, o que sugere que são tardios. A justificativa "aparece em Paozu antes da invasão" não tem apoio nos dados: o J. Sai está no conjunto nv48–52, não no nv8 do capítulo 2.

**3. Risco de invocação inválida nas linhas 110 e 112.**

- No original, o sprite `ene013_01` (Fugitivo, linhas 35–37) usa o atk3 para **invocar** robôs (`atk3_pow` = 168/169/170). Os grupos dele pré-carregam o invocado na lista de tipos, por exemplo `[168,36]` com a formação 2.
- A Coerência pôs esse sprite e os pesos dele nas linhas 110 "Brutamontes do Ermo" (atk3 = 40%, `atk3_pow` = 30) e 112 "Brutamontes Glacial" (atk3 = 35%, `atk3_pow` = **0**). Elas aparecem sozinhas, sem pré-carga.
- Se o tipo de golpe vier do sprite, como o padrão do original indica, elas tentariam invocar o ID 30 (Raposa Ladra) ou o ID 0 (inválido). Isso pode travar o jogo ou, no mínimo, mudar o comportamento.
- Onde testar: Brutamontes do Ermo em spi/kou e Brutamontes Glacial em yun. Na rc.1 esse risco não existia.

**4. Lista de pré-carga incompatível.**

- Os tipos (args 2–5) funcionam como pré-carga: incluem até os invocados, como as larvas dos insetos.
- Antes, as 4 variantes de Saibaman usavam um único arquivo. Agora usam dois (`ene062` para os IDs 2–3 e `ene053` para os IDs 4–5).
- Por isso, os grupos em que o sprite de um slot não está em nenhum tipo listado passaram de 14 (rc.1) para **82** (Coerência). Os novos estão em ben02–10, est07–09, ges01–02, las02–03, snd01–05, c0903_99, c1003_* e c1007_01. Exemplo: tipos `[2]` e slots `[2,4]`.
- O original já tinha algumas exceções desse tipo (est07, slot 6), então o motor talvez tolere. Mesmo assim é preciso testar. Reverter as linhas 1–4 resolve.

### MÉDIO

**5. Golpes com parâmetros especiais passaram a ser usados.**

- Nas linhas 155–157 (ex-insetos), `atk3_pow` vale 162/163/164 (invocação das larvas no original). O peso do atk3 era 0 na rc.1 e agora é 20–30%.
- Nas linhas 104–106 (ex-lobos), `atk1_pow` vale 105–107 (invocação no original), com peso de 40/50/30%. Essa parte já vinha da rc.1.
- Se o golpe do sprite novo for um ataque normal, o `pow` alto pode virar um bônus de dano grande. Testar o dano.

**6. Piratas no Castelo do Pilaf.**

- As justificativas das linhas 82, 109 e 118 citam a "caverna dos piratas". Mas os mapas delas são `pir02–08` e as cenas `c1009`/`c1010`, ou seja, o **Castelo do Pilaf**. A Caverna dos Piratas é `kai`.
- Corsária Venenosa, Sentinela Pirata e Corsária Veterana ficaram deslocadas.

**7. Cores quase iguais no mesmo mapa.**

- O verificador da outra IA comparou só os índices de paleta. Medindo a distância de cor (RGB555, soma das diferenças), acho estes pares no mesmo mapa:
  - Robô do Deserto (2) × Robô de Alguém (168): **1 unidade**, em est07–09;
  - Batedor do Ermo (95) × Atirador da Montanha (104): 6, em kou;
  - Lutador Veterano (111) × Lutador Arruaceiro (57): 10, em mut;
  - Mercenário de Elite (97) × Atirador Veterano (106): 20, em pao/nap.
- São inimigos com nomes e atributos diferentes e praticamente a mesma cara, o que quebra a regra do projeto.
- Os clones visuais de inimigos de outros mapas (linhas 76, 136 e 150, com distância 1) não chocam no mesmo mapa.

### BAIXO

**8. Nomes.**

- Vários se repetem: "Errante" aparece 6 vezes; há Robô de Patrulha, Robô Patrulheiro e Mecha Patrulheiro; Desertor Red Ribbon e Desertor da RR; Discípulo Expulso e Aluno Expulso.
- Dois nomes estão no masculino com sprite feminino: "Recruta Escavador" (sprite da Bandida) e "Aprendiz Noturno" (sprite da Aluna). Melhor "Escavadora" e "Noturna".
- Acentos estão OK e não há termo do glossário usado errado.

**9. Imprecisões no `RELATORIO_COERENCIA.md`.**

- A Ilha de Treinamento (cap. 0) só tem o Lutador Errante. Arruaceiro do Bambu e Discípulo Expulso ficam na Floresta de Bambu (cap. 1).
- A frase "183 mapas" na verdade conta scripts.

**10. Conteúdo morto.** O sprite do Soldado Saiyajin (`ene200_01`) e as 8 paletas novas do Saibaman não são mais usados. É inofensivo.

**11. Fora do escopo** (repasso para a frente de tradução): há falas em inglês nos roteiros, que são idênticos aos da rc.1. Exemplos: c1404_00 "U...Ugh! The ground is shaking!" e c1406_01 "W-what?! This ki!…".

## 5. O que confere

- Nenhum ID inválido: 0 referências fora de 1–228 e 0 linhas vazias usadas. Nenhum grupo ficou sem inimigo.
- Grupos e níveis por região não mudaram: os grupos são idênticos, e as 173 linhas têm todos os campos de combate e recompensa iguais nas três ROMs (nível, HP, MP, atributos, EXP, zeni, AP, itens 1–4, resistências e elementos). Mudaram só `name_id`/`file`/`palno`/`size`/`shadow`/`atk1–4`.
- As 151 linhas usadas têm `.chr` existente, `palno` válido e animações decodificáveis. O número de animações sempre cobre os pesos de ataque. Os 21 arquivos conferem com o `animacoes_conferidas.json`. As paletas antigas estão intactas, e os tiles e animações são idênticos aos da rc.1.
- A única exceção de decodificação é `ene011_01` (raposas), que é um limite do parser e vem do arquivo original sem alteração.
- Sprite grande (tamanho 2) em grupo com mais de um inimigo: só o Robô Corsário original, que já era assim. Nenhuma linha trocada.
- Cada linha tem aparência única por (arquivo, paleta). Na rc.1 havia 24 aparências compartilhadas.
- As 6 línguas têm `enemy_param` idêntico. Os 4 patches/SHA declarados conferem com as ROMs.

## 6. Recomendações e testes

1. Reverter as linhas 1–4 para a rc.1. Isso resolve CRÍTICO-1, ALTO-2 e ALTO-4.
2. Nas linhas 110 e 112, escolher um modelo que não seja o `ene013_01`, ou zerar o peso do atk3. Na falta disso, testar a batalha.
3. Corrigir os nomes e cores do Castelo do Pilaf e dos pares quase idênticos (MÉDIO-6 e MÉDIO-7).
4. Testes jogando:
   - cap. 14: Tenshinhan e Yamcha × Saibaman e os 4 restantes;
   - Brutamontes do Ermo (spi) e Brutamontes Glacial (yun);
   - insetos e larvas em spi, mut e snd, olhando dano e invocação;
   - um encontro nv52 em ben ou snd, olhando sprites;
   - abertura na Ilha de Treinamento.
