# Etapa 13: correções da revisão (DBZ Attack of the Saiyans PT-BR, NDS)

Feita em 12/10/2026. Aplica as correções das revisões `_revisao_claude\01_integridade`, `02_encontros` e `03_traducao`.
- Nada fora de `13_Correcoes_Revisao` foi alterado: `00_Original`, `01_ROM`, `11_Projeto_Recuperado`, `12_Coerencia_Historia` e `_revisao_claude` (incluindo `04_teste`) só foram lidos.
- Não usei emulador nem Switch, não instalei nada e não toquei em saves.
- Tudo é remontável por script (`LEIA-ME.md`).

## Resultado

| Arquivo | Bytes | CRC32 | SHA-256 |
|---|---|---|---|
| `DBZ Attack of the Saiyans PT-BR.nds` | 134.217.728 | `51717d80` | `0616e6c6fdada1e54d0694bd2e552be64dea3c3e592cd88ddf07b31d8bda3a82` |
| `DBZ_PTBR_etapa13_sobre_rc1.bps` (rc.1 → nova) | 284.970 | — | `d0c7f99ae125971cc37398a4a7764a44a6acba31fbc4301c96a2a240f3143902` |
| `DBZ_PTBR_etapa13_completo.bps` (original EN → nova) | 2.541.712 | — | `fc0075f26235775532f592da32a3cdbeb45ad0e7eb31d22e68d3ba18b77af0b1` |

- SHA-1 da ROM: `fd287666294d5e163a81edb47a1af259baf03bc8`.
- **Patch sobre a rc.1:** a origem é a rc.1 (`41412a47…`, CRC32 `670e3cf1`).
- **Patch completo:** a origem é a ROM USA (En,Fr) do zip de `00_Original` (CRC32 `a9f0b8f9`), a mesma do `aots_ptbr.bps`.
- **Conferência dos dois BPS:**
  - Cada um foi aplicado com dois aplicadores independentes, o `bps.py` do projeto e o `meubps.py` escrito pela revisão 01.
  - Os dois reproduzem a ROM nova byte a byte.
  - Os três CRC32 internos de cada patch conferem.
  - Cada patch recusa as outras ROMs como origem.
- O `build.py` é determinístico: rodado duas vezes, dá o mesmo SHA-256.

**SHA-256 de todos os BPS do projeto** (item 10, BAIXO-4 da revisão 01; também em `verificacao\hashes_e_bps.json`):

| BPS | Bytes | SHA-256 |
|---|---|---|
| `11_…\patches\aots_ptbr.bps` (original → rc.1) | 2.112.001 | `8d3e04696a56de81734b29e3a39558a92f857994b7621a19ec13b63fc949a423` |
| `11_…\patches\versoes-antigas\aots_bichos_db.bps` | 68.895 | `37e484a77bfd66dbde344e53abed7566395fa8dc545d80057cc169bdcde4fec0` |
| `12_…\Coerencia_sobre_PTBR_1.0.0-rc.1.bps` | 1.263.965 | `25f43232578959cf18b82ee46e986cb347583b8d351f71e58301e159f06e11b1` |
| `12_…\DBZ_PTBR_Coerencia_completo.bps` | 7.762.105 | `1d35b32302c82b5930faaf73bf4c758cf4160680b066621ce01c90ef8c7440c8` |
| `13_…\DBZ_PTBR_etapa13_sobre_rc1.bps` | 284.970 | `d0c7f99ae125971cc37398a4a7764a44a6acba31fbc4301c96a2a240f3143902` |
| `13_…\DBZ_PTBR_etapa13_completo.bps` | 2.541.712 | `fc0075f26235775532f592da32a3cdbeb45ad0e7eb31d22e68d3ba18b77af0b1` |

## Escolha da base: rc.1, com a etapa 12 reaplicada corrigida

Parti da **rc.1** (`01_ROM`, SHA-256 `41412a47…`, conferido por assert no `build.py`) e não da ROM da etapa 12 (`130b4ad8…`).
- **Por que não a etapa 12:** as correções mexem nos mesmos 27 arquivos que a etapa 12 tinha mudado (21 `.chr` e 6 `bdat.bin`). Reverter as linhas 1–4 em cima dela deixaria paletas mortas em `ene062_01` e `ene053_01` e mais uma camada de cópias órfãs.
- **O que o `build.py` faz:** reaplica a lógica de `12_Coerencia_Historia\revisao.py`, com as mesmas funções do projeto (`nds_rom.substituir`, `bdat_strings.gravar_str` + `conferir`, `chr_paletas`) e com o plano corrigido (`scripts\plano13.py`).
- **Paletas:** a fórmula de paleta da etapa 12 é reproduzida exatamente. Ela é mantida onde passa nos limites de distinção (ver o item 5).
- **Diferença em relação à rc.1:**
  - 317 arquivos: 19 `.chr` de inimigo, os 6 `bdat.bin` e 292 scripts `.sb` das pastas US e EN (textos).
  - Fora desses arquivos (posições antigas e novas), só mudam as entradas deles na FAT e os campos do cabeçalho 0x80–0x82 (tamanho usado) e 0x15E (CRC16).
- **Cópias antigas:** as cópias que ficam nas posições antigas dos arquivos realocados e os 208 KB órfãos que já vinham da rc.1 não foram removidos. São inofensivos (fora da FAT) e removê-los exigiria remontar o NitroFS.

## Achado novo que orientou as correções de golpe: o efeito do golpe é da LINHA, não do sprite

Desmontei estaticamente o ARM9 com um desmontador mínimo, `trabalho\armdis.py`:
- **`btl/ene/eneEff.bin`:** 173 linhas × 4 slots × 150 bytes. É a definição de cada golpe de cada linha de `enemy_param`.
- **Carga:** a função 0x020379D8 copia o registro pelo ID do inimigo.
- **Execução:** a função 0x02040B58 lê o campo 7 de cada subentrada como **tipo do efeito**.
  - Tipo `0x4000` = **invocação** (ramo 0x02041D48): sorteia 0–99 contra o campo 11 e chama o invocador com `atk<N>_pow` como **ID do inimigo chamado**.
  - Tipo 0 (slot vazio) = o executor não faz nada.
- **Escolha do golpe:** a função 0x02057F38 soma `atk1`–`atk4` de `enemy_param` sem olhar o `eneEff`. Um slot com peso > 0 e golpe vazio é escolhido mesmo assim.
- **Animação:** o slot N usa a animação 3+N−1 do `.chr` do sprite. Essa é a regra "nº de animações ≥ 3 + maior slot usado", confirmada nas 173 linhas do original.
- **eneEff idêntico:** o `eneEff.bin` é o mesmo no original, na rc.1, na etapa 12 e na ROM nova.

Consequências:
1. **Nenhum substituto herda invocação ou efeito do sprite doador.** O sprite só dá a animação, e o efeito continua sendo o do bicho original daquela linha.
   - Por isso as linhas 110 e 112 (sprite do Fugitivo) nunca invocariam ninguém. O risco do ALTO-3 da revisão 02 não existia nessa forma.
2. **O defeito real era outro:** pesos em slots sem golpe definido. No original isso acontece **0 vezes**; na rc.1, 12 vezes; na etapa 12, **18 vezes**.
   - Exemplo: Brutamontes Glacial, slot 3 com 35%.
   - Nesses turnos o inimigo faz a animação e não tem efeito nenhum.
3. **Os `atk_pow` 105–107 (ex-lobos) e 162–164 (ex-insetos) são IDs de invocação**, não bônus de dano:
   - linhas 104–106 chamam outro de si mesmas (IDs 105–107);
   - linhas 155–157 chamam as linhas 161–163 (as ex-larvas).
   - Todos os grupos em que esses invocadores aparecem já pré-carregam o invocado, porque os grupos são os do jogo original. Conferido em `verificar.py`.
   - Não há dano inválido; o item 6 se resolve devolvendo os pesos originais.

## O que mudou

### 1. CRÍTICO — Saibamen (linhas 1–4): aplicado

- As linhas 1–4 de `enemy_param` e `character_name` voltaram exatamente aos valores da rc.1, que são os do jogo original: J./C./K./T. Sai, sprite `ene001_01`, paletas 1–4.
- As paletas extras da etapa 12 em `ene062_01`/`ene053_01` não existem mais.
- As 48 chamadas de evento do cap. 14 com o ID 2 (`c1402_02` … `c1409_00`, `nap01–03`) voltam a mostrar Saibaman. O mesmo vale para os ermos Páprica/Gizard e os conjuntos nv48–52 (ben, snd, ges, est07–09, pao).

**Pré-carga:**
- **Métrica estrita (só IDs reais nos slots):** grupos com sprite fora da lista de tipos são 6 no original, 6 na rc.1, 51 na etapa 12 e **6 na nova**. Os 6 que sobram são os mesmos do jogo original (est07–09).
- **Métrica da revisão 02** (conta o marcador `1` dos slots como Saibaman `ene001_01`): original 37, rc.1 14, etapa 12 82, nova **37**.
  - A nova não volta a 14 só porque a rc.1 tinha transformado 15 bichos em Saibaman (`ene001_01`), o que "casava" com o marcador.
  - O número da nova é idêntico ao do jogo original, o que mostra que essa métrica conta o marcador e não um problema real.

### 2. ALTO — linhas 110 e 112: aplicado (e revisto com o achado acima)

- **Sprite:** trocado do Fugitivo (`ene013_01`, cujo golpe 3 é a animação de chamar reforço) pelo do Bandido (`ene010_01`): Brutamontes do Ermo (modelo 26) e Brutamontes Glacial (modelo 27), com paletas novas.
- **Pesos:** voltaram aos do javali original: 110 = [40,30,30,0] e 112 = [40,40,0,20]. Isso também tirou o slot 3 da linha 112, que tinha 35% e nenhum golpe.
- **Outros substitutos com invocação:**
  - Só 104–106 e 155–157 invocam, e são as invocações originais dessas linhas (ver acima).
  - Nenhuma linha trocada ganhou efeito especial que não tinha.
  - Os tipos especiais de cada slot estão na tabela de pesos.

### 3. ALTO — pesos atk1–atk4: aplicado

- **Regra:** em todas as 48 linhas os pesos voltaram aos **do jogo original da própria linha**, quando o sprite doador tem a animação de todos os slots usados.
- **Onde o doador tem só 3 golpes**, o peso do slot que falta foi para o slot usado de potência mais próxima (empate: proporcional ao peso original). Isso minimiza a mudança da média ponderada.
  - **76 Lanceiro Nômade:** [20,20,40,20] → [20,40,40,0]. Média 10,0 → 8,0.
  - **111 Lutador Veterano:** [30,30,20,20] → [50,30,20,0]. Média 28,0 → 30,0.
  - **115 Instrutor Rival:** [30,20,20,30] → [43,29,28,0]. Média 0 → 0.
- **Linhas 149 e 150:** com o sprite de 6 animações da etapa 12 (`ene006_01`), a média cairia 10 e 20 pontos, porque o slot 4 é o golpe mais forte do 150. Por isso troquei o doador por um de 7 animações e os pesos ficaram **exatamente** os originais:
  - 149: Ladrão do Deserto, `ene015_01`;
  - 150: Xamã do Vulcão, `ene026_01`.
- **Resultado:**
  - 45 das 48 linhas têm pesos idênticos ao original.
  - Nenhum slot com peso fica sem golpe ou sem animação. Antes eram 18 casos na etapa 12.
  - Nível, HP, MP, atributos, EXP, zeni, AP, itens, `atk_pow` e resistências são idênticos ao original nas 173 linhas.

### 4. MÉDIO — Castelo do Pilaf (pir): aplicado

- **82 → Robô Sentinela** (`ene062_01`, robô pequeno). Era "Corsária Venenosa".
- **109 → Guarda do Castelo** (`ene015_01`, guarda de turbante e cimitarra, combinando com o castelo de estilo árabe). Era "Sentinela Pirata".
- **118 → Capitão da Guarda** (`ene010_01`, brutamontes de espada). Era "Corsária Veterana".
- Ficou fora o sprite do Grupo do Coelho (`ene016`): ele tem orelhas de coelho.
- Na Caverna dos Piratas (kai), Robô da Caverna e Capanga da Caverna continuam.
- Nenhum nome trocado tem "pirata" ou "corsária".

### 5. MÉDIO — cores quase iguais: aplicado

- **Regra nova do `build.py`:** toda linha trocada recebe uma paleta própria com distância (soma |ΔRGB555|) ≥ **100** das outras variantes do mesmo sprite que aparecem no mesmo mapa (no jogo original a menor é 103) e ≥ **80** de qualquer outra variante do mesmo sprite no jogo (evita clones visuais em outras regiões).
  - Onde a paleta da etapa 12 passa nesses limites, ela é mantida (13 linhas).
  - Nas outras, a paleta é gerada por giro de matiz da roupa (pele, cinzas e contornos ficam).
  - Nos nomes com tom (gelo/neve, vulcão, veneno, noturno, sombrio), o giro escolhe um tom coerente.
- **Pares da revisão:**
  - Robô do Deserto × Robô de Alguém: sumiu, porque a linha 2 voltou a ser C. Sai.
  - Batedor do Ermo × Atirador da Montanha: 6 → **193**.
  - Lutador Veterano × Lutador Arruaceiro: 10 → **244**.
  - Mercenário de Elite × Atirador Veterano: 20 → **169**.
  - Os clones de distância 1 (76, 136, 150) também foram resolvidos.
- **Resultado:** a menor distância entre variantes no mesmo mapa ficou em **109** (antes 1), e cada linha usada tem aparência (arquivo, paleta) própria.
- A prévia de todas as linhas, ao lado das variantes do mesmo sprite, está em `verificacao\previa_inimigos.png`. Em vermelho estão as do mesmo mapa.

### 6. MÉDIO — golpes especiais dos ex-insetos e ex-lobos: conferido, sem defeito de dano

- Os `pow` altos são IDs de invocação usados só pelo ramo de invocação (ver o achado).
- Com os pesos originais devolvidos, essas linhas voltam a fazer o que os bichos faziam:
  - **ex-lobos (104–106):** chamam outro igual, 20% dos turnos;
  - **ex-insetos (155–157):** chamam Recruta Escavadora, Aprendiz Noturna e Batedora Venenosa, com 30%, 30% e 50% (só se o sorteio de sucesso do golpe passar).
- **Isso é mudança de comportamento em relação às ROMs anteriores:**
  - na rc.1 os ex-lobos invocavam 50% dos turnos e os ex-insetos nunca invocavam;
  - na etapa 12 os ex-insetos invocavam 20–30% dos turnos.
- É um ponto para o teste jogando.

### 7. BAIXO — nomes: aplicado

- "Errante" ficou só em **Lutador Errante** (80). As outras viraram:
  - 76 Lanceiro Nômade;
  - 105 Guerreira do Gelo;
  - 115 Instrutor Rival ("Mestre" já existe no Campo do Mutaito);
  - 131 Vampiro Jovem (a escala fica Jovem / Sanguinário / Ancião).
- "Robô de Patrulha" voltou a ser J. Sai, e 119 "Robô Patrulheiro" virou **Robô Mergulhador**. "Mecha Patrulheiro" é o único "Patrulheiro".
- **Gênero:** 161 **Recruta Escavadora** e 162 **Aprendiz Noturna** (os sprites são femininos).
- **Quase-duplicatas que a revisão também apontou:**
  - 107 Desertor Red Ribbon → **Ex-Soldado RR** (era quase igual a "Desertor da RR", da linha 14; agora faz série com Ex-Sargento RR);
  - 116 Discípulo Expulso → **Discípulo Rebelde** (era quase igual a "Aluno Expulso").
- **Largura:** todos os nomes cabem no maior nome de inimigo do jogo original: ≤ 92 px na `latin1` e ≤ 106 px na `latin0`. O maior novo é "Brutamontes do Ermo", com 88/106 px.
- Os nomes são únicos entre os 173 inimigos e estão gravados nos 6 idiomas, como fez a etapa 12.

### 8. Tradução: aplicado

A lista é de `texto\correcoes_texto.json`, feita pela frente de texto (`texto\RELATORIO_TEXTO.md` tem a tabela completa, antes/depois e motivos). Ela foi aplicada **diretamente** pelo `build.py`, sem reaplicar o `ptbr.json`, com assert de cada "antes" contra a rc.1.

- **Mudanças de revisão: 140 textos diferentes**, aplicados em 336 posições (US 198 + EN espelhada 138). Por gravidade: 1 ALTO, 73 MÉDIO e 66 BAIXO.
  - **ALTO:** `c1407_00:34` "Rei Demônio Piccolo" → **"Piccolo Daimaoh"**.
  - **Nomes:** "Senhor Kaioh" nos 8 locais. "do Enma" nas tabelas: "Floresta/Árvore do Enma"; em `cf_mes_LOC:9`, "Dentro da Fl. do Enma" para caber na EN. Também "Kami-Sama", "Palácio da Vovó Uranai", "Kuririn e M. Kame" no rótulo, "Turbante do Sr. Popo" e "Selo do Daimaoh" ("Selo do Piccolo Daimaoh" não cabe).
  - **Falas:** Chichi "**Obrigada**" (`c0508_01:9`), concordâncias (emprestado, nelas/nisso, vocês) e frases truncadas e calques da lista do relatório 03.
  - **Termos de status e interface uniformes:** Escuridão, Confusão e ataque surpresa. Também "Encadeamento"/"encadear" no lugar de "corrente", "LV%d", o comando "Especial" no tutorial, "Item roubado: \<i\>." e "Formatando/Falha ao apagar".
  - **Larguras:** as 2 mensagens da Rajada de Ki foram encurtadas ("Agora você destrói o que pisca em branco!"), porque passavam de 196 px.
  - **Mantidos:** "Refazer" e o glossário recomendado (Cutelo, Mestre Shen, Número 8, General White, Coelho Monstro, Chaos…). "Gangue do Coelho" foi registrada em `texto\glossario_adendo.md`.
  - O que não coube ou ficou de fora, e por quê, está na seção 6 do `RELATORIO_TEXTO.md`.
- **Divergência US × EN, resolvida:**
  - As falas em inglês de `c1404_00:24` e `c1406_01:11` existem **só na pasta EN**; na US elas já estão em português.
  - Pela análise estática do ARM9, o executável USA só tem os códigos de idioma `us` e `fr` (tabela em 0x0209B9F4) e monta os caminhos `script/xx/…` e `btl/bdat/%s/…` com eles. A pasta EN não é lida pelo jogo USA.
  - A revisão de encontros leu a pasta EN.
  - **Mesmo assim a EN foi traduzida:** 250 textos que só existiam em inglês ali, em 380 posições (51 com tradução própria e 199 com a tradução final da US do mesmo índice). Agora a US e a EN têm 0 falas suspeitas de inglês.
- **No total:** 716 entradas (posição × pasta), em 292 scripts e nas tabelas de mensagem US/EN.

### 9. `ptbr.json`: aplicado

- **`dados\ptbr.json`:** é a cópia do dicionário do projeto (5.647 → 5.898 chaves) com:
  - os 48 nomes finais de inimigo, com o nome original em inglês como chave. Conferido: aplicar o dicionário às células de `character_name` do original dá exatamente os nomes da ROM nova;
  - as 140 correções;
  - as 250 chaves só da EN.
- O original em `11_Projeto_Recuperado\traducao` ficou intacto.
- **Atenção:** as 250 chaves só da EN não estão nos `lote*.json`, então o `aplicar_traducao.py rom` do projeto não as aplicaria nos scripts. Para remontar, use o `build.py`, que aplica `correcoes_texto.json` direto.

### 10. BAIXO: aplicado

- SHA-256 de todos os BPS: tabela acima.
- A "ROM antiga do Switch" está documentada no `LEIA-ME.md`. É o original em inglês, com 167 bytes de assinatura zerados no cabeçalho, CRC32 `431f0f32`. Conferência em `verificacao\rom_antiga_switch.json`.
- Cópias antigas dentro da ROM: mantidas (ver "Escolha da base").

### Não aplicado

- **Itens BAIXO de texto sem ganho claro ou que não cabem na largura:** "Pena da Cauda de Fênix", "Joia do Coelho Monstro", "Semente dos Deuses" nas tabelas, "Escola Tsuru", rabo × cauda e outros. Estão listados na seção 6 do `RELATORIO_TEXTO.md`.
- **Ordem dos conjuntos tardios (nv46–52):** a revisão 02 não decodificou o gatilho e eu também não. Os Saibamen originais voltaram a eles, como no jogo original.
- **HMACs/assinatura RSA do cabeçalho:** não refeitos, como na rc.1. Isso só importa em DSi/3DS com cartucho real.

## Tabelas por linha de inimigo

| Linha | Bicho original | rc.1 | Etapa 12 | **Final (etapa 13)** | Sprite etapa 12 → final | O que mudou na etapa 13 |
|---|---|---|---|---|---|---|
| 1 | J. Sai | J. Sai | Robô de Patrulha (ene062_01 p3) | **J. Sai** | ene062_01 → ene001_01 p1 | Revertida à rc.1 (= jogo original): Saibaman do cap. 14 |
| 2 | C. Sai | C. Sai | Robô do Deserto (ene062_01 p4) | **C. Sai** | ene062_01 → ene001_01 p2 | Revertida à rc.1 (= jogo original): Saibaman do cap. 14 |
| 3 | K. Sai | K. Sai | Mutante Errante (ene053_01 p3) | **K. Sai** | ene053_01 → ene001_01 p3 | Revertida à rc.1 (= jogo original): Saibaman do cap. 14 |
| 4 | T. Sai | T. Sai | Mutante Sombrio (ene053_01 p4) | **T. Sai** | ene053_01 → ene001_01 p4 | Revertida à rc.1 (= jogo original): Saibaman do cap. 14 |
| 74 | Winged Dragon | Robô Alado RR | Mecha Patrulheiro | **Mecha Patrulheiro** | ene004_01 → ene004_01 p3 | paleta = fórmula da etapa 12, pesos |
| 75 | Violent Dragon | Robô de Assalto RR | Mecha de Combate | **Mecha de Combate** | ene004_01 → ene004_01 p4 | paleta = fórmula da etapa 12, pesos |
| 76 | Snow Dragon | Robô Ártico RR | Guardião Errante | **Lanceiro Nômade** | ene027_01 → ene027_01 p3 | nome, paleta nova, pesos. nome repetido ("Errante") e paleta clone do Homem Desconfiado (dist. 1) |
| 80 | Giant Snake | Serva da Princesa | Lutador Errante | **Lutador Errante** | ene021_01 → ene021_01 p3 | paleta nova, pesos |
| 81 | Mansion Snake | Guarda da Mansão | Guarda da Mansão | **Guarda da Mansão** | ene022_01 → ene022_01 p3 | paleta = fórmula da etapa 12 |
| 82 | Poisonous Snake | Serva Venenosa | Corsária Venenosa | **Robô Sentinela** | ene014_01 → ene062_01 p3 | nome, sprite, paleta nova, pesos. Castelo do Pilaf: era "Corsária Venenosa" (pirata, confundido com a Caverna) |
| 95 | Ostrich Chicken | Batedor Saiyajin | Batedor do Ermo | **Batedor do Ermo** | ene012_01 → ene012_01 p3 | paleta nova, pesos |
| 96 | Sand Dodo | Batedor do Deserto | Batedora do Deserto | **Batedora do Deserto** | ene014_01 → ene014_01 p3 | paleta = fórmula da etapa 12, pesos |
| 97 | Dododo | Elite Saiyajin | Mercenário de Elite | **Mercenário de Elite** | ene012_01 → ene012_01 p4 | paleta = fórmula da etapa 12, pesos |
| 98 | Firebird | Aviador Red Ribbon | Piloto Renegado | **Piloto Renegado** | ene003_01 → ene003_01 p3 | paleta = fórmula da etapa 12 |
| 99 | Blue Hawk | Aviador Azul RR | Piloto Mercenário | **Piloto Mercenário** | ene003_01 → ene003_01 p4 | paleta nova, pesos |
| 100 | Dark Condor | Aviador Sombrio RR | Piloto Veterano | **Piloto Veterano** | ene003_01 → ene003_01 p5 | paleta nova, pesos |
| 101 | Tiger | Soldado Saiyajin | Arruaceiro do Bambu | **Arruaceiro do Bambu** | ene021_01 → ene021_01 p4 | paleta nova |
| 102 | Snow Tiger | Soldado Glacial | Mercenário da Neve | **Mercenário da Neve** | ene010_01 → ene010_01 p3 | paleta nova, pesos |
| 103 | Dimensional Tiger | Soldado Dimensional | Guardião da Floresta | **Guardião da Floresta** | ene026_01 → ene026_01 p3 | paleta nova, pesos |
| 104 | Wolf | Saibaman | Atirador da Montanha | **Atirador da Montanha** | ene012_01 → ene012_01 p5 | paleta nova, pesos |
| 105 | White Wolf | Saibaman Glacial | Guerreira Errante | **Guerreira do Gelo** | ene008_01 → ene008_01 p3 | nome, paleta nova, pesos. nome repetido ("Errante") |
| 106 | Red Wolf | Saibaman Rubro | Atirador Veterano | **Atirador Veterano** | ene012_01 → ene012_01 p6 | paleta nova, pesos |
| 107 | Stray Dog | Desertor Red Ribbon | Desertor Red Ribbon | **Ex-Soldado RR** | ene005_01 → ene005_01 p3 | nome, paleta nova, pesos. quase igual a "Desertor da RR" (linha 14) |
| 108 | Red Ribbon Spy Dog | Espião Red Ribbon | Espião Red Ribbon | **Espião Red Ribbon** | ene005_01 → ene005_01 p4 | paleta = fórmula da etapa 12, pesos |
| 109 | Super Watchdog | Sentinela Red Ribbon | Sentinela Pirata | **Guarda do Castelo** | ene014_01 → ene015_01 p3 | nome, sprite, paleta = fórmula da etapa 12, pesos. Castelo do Pilaf: era "Sentinela Pirata" (sprite de corsária); guarda de turbante, como o castelo de estilo árabe |
| 110 | Wild Boar | Brutamontes Saiyajin | Brutamontes do Ermo | **Brutamontes do Ermo** | ene013_01 → ene010_01 p4 | sprite, paleta nova, pesos. sprite do Fugitivo (golpe 3 = animação de chamar reforço) trocado pelo do Bandido |
| 111 | Champion Boar | Brutamontes Campeão | Lutador Veterano | **Lutador Veterano** | ene021_01 → ene021_01 p5 | paleta nova |
| 112 | Snow Boar | Brutamontes Glacial | Brutamontes Glacial | **Brutamontes Glacial** | ene013_01 → ene010_01 p5 | sprite, paleta nova, pesos. sprite do Fugitivo trocado pelo do Bandido da Neve; slot 3 tinha 35% sem golpe definido |
| 113 | Hungry Bear | Saibaman Faminto | Saqueador do Ermo | **Saqueador do Ermo** | ene023_01 → ene023_01 p3 | paleta nova |
| 114 | Snow Bear | Saibaman das Neves | Bandida Glacial | **Bandida Glacial** | ene008_01 → ene008_01 p4 | paleta nova, pesos |
| 115 | Strong Bear | Saibaman Feroz | Mestre Errante | **Instrutor Rival** | ene021_01 → ene021_01 p6 | nome, paleta nova, pesos. nome repetido ("Errante"; e "Mestre" já existe no mesmo mapa) |
| 116 | Dangerous Panda | Saibaman do Bambu | Discípulo Expulso | **Discípulo Rebelde** | ene020_01 → ene020_01 p3 | nome, paleta nova, pesos. quase igual a "Aluno Expulso" (linha 54) |
| 117 | Snow Panda | Saibaman da Nevasca | Guardião Peregrino | **Guardião Peregrino** | ene026_01 → ene026_01 p4 | paleta nova, pesos |
| 118 | Ultimate Pandaman | Saibaman Supremo | Corsária Veterana | **Capitão da Guarda** | ene014_01 → ene010_01 p6 | nome, sprite, paleta = fórmula da etapa 12, pesos. Castelo do Pilaf: era "Corsária Veterana" (pirata); brutamontes de espada |
| 119 | Giant Fish | Robô Pirata | Robô Patrulheiro | **Robô Mergulhador** | ene002_01 → ene002_01 p3 | nome, paleta = fórmula da etapa 12, pesos. nome repetido ("Patrulheiro" / "de Patrulha") |
| 120 | Wild Fish | Robô Pirata Selvagem | Robô da Caverna | **Robô da Caverna** | ene002_01 → ene002_01 p4 | paleta = fórmula da etapa 12, pesos |
| 121 | Sand Fish | Robô Pirata das Areias | Robô das Areias | **Robô das Areias** | ene002_01 → ene002_01 p5 | paleta nova, pesos |
| 131 | Giant Bat | Vampiro | Vampiro Errante | **Vampiro Jovem** | ene045_01 → ene045_01 p3 | nome, paleta = fórmula da etapa 12, pesos. nome repetido ("Errante") |
| 132 | Vampire Bat | Vampiro Sanguinário | Vampiro Sanguinário | **Vampiro Sanguinário** | ene045_01 → ene045_01 p4 | paleta nova, pesos |
| 133 | King Bat | Rei Vampiro | Vampiro Ancião | **Vampiro Ancião** | ene045_01 → ene045_01 p5 | paleta nova, pesos |
| 134 | Big Club | Capanga | Capanga da Caverna | **Capanga da Caverna** | ene016_01 → ene016_01 p3 | paleta nova |
| 135 | Giant Crab | Capanga Gigante | Capanga da Fonte | **Capanga da Fonte** | ene016_01 → ene016_01 p4 | paleta nova, pesos |
| 136 | Dark Crab | Capanga Sombrio | Capanga Sombrio | **Capanga Sombrio** | ene016_01 → ene016_01 p5 | paleta nova, pesos |
| 149 | Tumble Bug | Recruta Red Ribbon | Recruta Renegado | **Ladrão do Deserto** | ene006_01 → ene015_01 p4 | nome, sprite, paleta nova, pesos. sprite de 6 animações não tem o golpe 4 (20% no original); doador com 7 animações |
| 150 | Fire Caterpillar | Recruta Incendiário | Soldado Incendiário | **Xamã do Vulcão** | ene006_01 → ene026_01 p5 | nome, sprite, paleta nova, pesos. sprite de 6 animações não tem o golpe 4 (20%, o mais forte); doador com 7 animações |
| 151 | Caterpillar | Recruta Veterano | Aprendiz da Floresta | **Aprendiz da Floresta** | ene017_01 → ene017_01 p3 | paleta = fórmula da etapa 12, pesos |
| 155 | Roundworm | Saibaman Escavador | Batedor Escavador | **Batedor Escavador** | ene023_01 → ene023_01 p4 | paleta nova, pesos |
| 156 | Dark Firefly | Saibaman Noturno | Lutador Noturno | **Lutador Noturno** | ene020_01 → ene020_01 p4 | paleta nova |
| 157 | Poison Sandbug | Saibaman Venenoso | Batedor Venenoso | **Batedor Venenoso** | ene012_01 → ene012_01 p7 | paleta nova, pesos |
| 161 | Roundworm Larva | Broto Escavador | Recruta Escavador | **Recruta Escavadora** | ene008_01 → ene008_01 p5 | nome, paleta nova, pesos. gênero: sprite feminino (Bandida) |
| 162 | Firefly Larva | Broto Noturno | Aprendiz Noturno | **Aprendiz Noturna** | ene017_01 → ene017_01 p4 | nome, paleta nova, pesos. gênero: sprite feminino (Aluna) |
| 163 | Sandbug Larva | Broto Venenoso | Batedora Venenosa | **Batedora Venenosa** | ene014_01 → ene014_01 p4 | paleta nova, pesos |

### Pesos de escolha de ataque (atk1–atk4) e potência média

"Média" = Σ peso × atk_pow / 100, só dos slots de dano (o slot de invocação usa atk_pow como ID do inimigo chamado e fica fora). Tipos de golpe vêm de btl/ene/eneEff.bin (por linha): "inv" = invocação, "-" = slot sem golpe definido.

| Linha | Final | pow (1–4) | Tipos 1–4 | Original | rc.1 | Etapa 12 | **Final** | Média orig → etapa 12 → final | Observação |
|---|---|---|---|---|---|---|---|---|---|
| 74 | Mecha Patrulheiro | [0, 20, 0, 30] | dano / dano / 0x400 / dano | [20, 20, 40, 20] | [50, 30, 20, 0] | [50, 30, 20, 0] | **[20, 20, 40, 20]** | 10.0 → 6.0 → 10.0 |  |
| 75 | Mecha de Combate | [0, 20, 0, 30] | dano / dano / 0x400 / dano | [20, 20, 40, 20] | [30, 30, 20, 20] | [30, 30, 20, 20] | **[20, 20, 40, 20]** | 10.0 → 12.0 → 10.0 |  |
| 76 | Lanceiro Nômade | [0, 20, 0, 30] | dano / dano / 0x400 / dano | [20, 20, 40, 20] | [30, 30, 20, 20] | [40, 40, 20, 0] | **[20, 40, 40, 0]** | 10.0 → 8.0 → 8.0 | slot 4 (20%, pow 30) sem animação no sprite (só 3 golpes) -> slot 2 +20 |
| 80 | Lutador Errante | [20, 0, 0, 0] | dano / dano / - / - | [50, 50, 0, 0] | [40, 30, 30, 0] | [50, 30, 20, 0] | **[50, 50, 0, 0]** | 10.0 → 10.0 → 10.0 | etapa 12 punha peso em slot sem golpe: [3] |
| 81 | Guarda da Mansão | [30, -30, 30, 0] | dano / dano / dano / - | [40, 30, 30, 0] | [40, 30, 30, 0] | [40, 30, 30, 0] | **[40, 30, 30, 0]** | 12.0 → 12.0 → 12.0 |  |
| 82 | Robô Sentinela | [40, -50, 0, 30] | dano / dano / dano / dano | [40, 40, 0, 20] | [40, 30, 0, 30] | [40, 15, 40, 5] | **[40, 40, 0, 20]** | 2.0 → 10.0 → 2.0 |  |
| 95 | Batedor do Ermo | [60, 0, 0, 0] | dano / 0x100 / 0x100 / 0x1+0x2000 | [30, 30, 20, 20] | [19, 18, 18, 45] | [40, 20, 40, 0] | **[30, 30, 20, 20]** | 18.0 → 24.0 → 18.0 |  |
| 96 | Batedora do Deserto | [50, 0, 0, 0] | dano / 0x100 / 0x100 / 0x1+0x2000 | [20, 20, 20, 40] | [19, 18, 18, 45] | [40, 15, 40, 5] | **[20, 20, 20, 40]** | 10.0 → 20.0 → 10.0 |  |
| 97 | Mercenário de Elite | [75, 0, 0, 0] | dano / 0x100 / 0x100 / 0x1+0x2000 | [10, 5, 5, 80] | [19, 18, 18, 45] | [30, 20, 30, 20] | **[10, 5, 5, 80]** | 7.5 → 22.5 → 7.5 |  |
| 98 | Piloto Renegado | [0, 0, 0, 0] | dano / dano / dano / - | [40, 30, 30, 0] | [40, 30, 30, 0] | [40, 30, 30, 0] | **[40, 30, 30, 0]** | 0.0 → 0.0 → 0.0 |  |
| 99 | Piloto Mercenário | [0, 0, 30, 0] | dano / dano / dano / - | [40, 30, 30, 0] | [30, 30, 20, 20] | [30, 30, 20, 20] | **[40, 30, 30, 0]** | 9.0 → 6.0 → 9.0 | etapa 12 punha peso em slot sem golpe: [4] |
| 100 | Piloto Veterano | [30, 0, 40, 0] | dano / dano / dano / - | [40, 30, 30, 0] | [30, 30, 20, 20] | [30, 30, 20, 20] | **[40, 30, 30, 0]** | 24.0 → 17.0 → 24.0 | etapa 12 punha peso em slot sem golpe: [4] |
| 101 | Arruaceiro do Bambu | [0, 0, 0, 0] | dano / dano / dano / - | [50, 30, 20, 0] | [19, 18, 18, 45] | [50, 30, 20, 0] | **[50, 30, 20, 0]** | 0.0 → 0.0 → 0.0 |  |
| 102 | Mercenário da Neve | [0, 0, 0, 0] | dano / dano / dano / 0x10 | [40, 20, 20, 20] | [19, 18, 18, 45] | [30, 30, 20, 20] | **[40, 20, 20, 20]** | 0.0 → 0.0 → 0.0 |  |
| 103 | Guardião da Floresta | [0, 0, 0, 0] | dano / dano / dano / 0x10 | [30, 20, 20, 30] | [19, 18, 18, 45] | [30, 20, 30, 20] | **[30, 20, 20, 30]** | 0.0 → 0.0 → 0.0 |  |
| 104 | Atirador da Montanha | [105, 0, 0, 0] | inv / dano / dano / - | [20, 40, 40, 0] | [50, 50, 0, 0] | [40, 20, 40, 0] | **[20, 40, 40, 0]** | 0.0 → 0.0 → 0.0 |  |
| 105 | Guerreira do Gelo | [106, 0, 0, 0] | inv / dano / dano / - | [20, 40, 40, 0] | [50, 30, 20, 0] | [50, 30, 0, 20] | **[20, 40, 40, 0]** | 0.0 → 0.0 → 0.0 | etapa 12 punha peso em slot sem golpe: [4] |
| 106 | Atirador Veterano | [107, 0, 0, 0] | inv / dano / dano / dano | [20, 30, 20, 30] | [50, 40, 10, 0] | [30, 20, 30, 20] | **[20, 30, 20, 30]** | 0.0 → 0.0 → 0.0 |  |
| 107 | Ex-Soldado RR | [30, 0, 10, 0] | dano / dano / dano / - | [25, 50, 25, 0] | [40, 30, 30, 0] | [40, 30, 30, 0] | **[25, 50, 25, 0]** | 10.0 → 15.0 → 10.0 |  |
| 108 | Espião Red Ribbon | [30, 0, 10, 0] | dano / dano / dano / - | [25, 50, 25, 0] | [40, 30, 30, 0] | [40, 30, 30, 0] | **[25, 50, 25, 0]** | 10.0 → 15.0 → 10.0 |  |
| 109 | Guarda do Castelo | [30, 0, 10, 0] | dano / dano / dano / - | [25, 50, 25, 0] | [30, 30, 40, 0] | [40, 15, 40, 5] | **[25, 50, 25, 0]** | 10.0 → 16.0 → 10.0 | etapa 12 punha peso em slot sem golpe: [4] |
| 110 | Brutamontes do Ermo | [30, 0, 30, 0] | dano / dano / dano / - | [40, 30, 30, 0] | [19, 18, 18, 45] | [25, 15, 40, 20] | **[40, 30, 30, 0]** | 21.0 → 19.5 → 21.0 | etapa 12 punha peso em slot sem golpe: [4] |
| 111 | Lutador Veterano | [40, 0, 50, 30] | dano / dano / dano / dano | [30, 30, 20, 20] | [19, 18, 18, 45] | [50, 30, 20, 0] | **[50, 30, 20, 0]** | 28.0 → 30.0 → 30.0 | slot 4 (20%, pow 30) sem animação no sprite (só 3 golpes) -> slot 1 +20 |
| 112 | Brutamontes Glacial | [50, 0, 0, 50] | dano / dano / - / dano | [40, 40, 0, 20] | [19, 18, 18, 45] | [30, 15, 35, 20] | **[40, 40, 0, 20]** | 30.0 → 25.0 → 30.0 | etapa 12 punha peso em slot sem golpe: [3] |
| 113 | Saqueador do Ermo | [0, 0, 0, 0] | dano / dano / dano / - | [40, 30, 30, 0] | [50, 50, 0, 0] | [40, 30, 30, 0] | **[40, 30, 30, 0]** | 0.0 → 0.0 → 0.0 |  |
| 114 | Bandida Glacial | [0, 0, 0, 0] | dano / dano / dano / - | [40, 30, 30, 0] | [50, 30, 20, 0] | [40, 20, 20, 20] | **[40, 30, 30, 0]** | 0.0 → 0.0 → 0.0 | etapa 12 punha peso em slot sem golpe: [4] |
| 115 | Instrutor Rival | [0, 0, 0, 0] | dano / dano / dano / dano | [30, 20, 20, 30] | [50, 30, 20, 0] | [50, 30, 20, 0] | **[43, 29, 28, 0]** | 0.0 → 0.0 → 0.0 | slot 4 (30%, pow 0) sem animação no sprite (só 3 golpes) -> slot 1 +13, slot 2 +9, slot 3 +8 |
| 116 | Discípulo Rebelde | [0, 0, 0, 0] | dano / dano / - / - | [50, 50, 0, 0] | [50, 50, 0, 0] | [50, 40, 10, 0] | **[50, 50, 0, 0]** | 0.0 → 0.0 → 0.0 | etapa 12 punha peso em slot sem golpe: [3] |
| 117 | Guardião Peregrino | [0, 0, 50, 0] | dano / dano / dano / - | [40, 30, 30, 0] | [50, 30, 20, 0] | [30, 20, 30, 20] | **[40, 30, 30, 0]** | 15.0 → 15.0 → 15.0 | etapa 12 punha peso em slot sem golpe: [4] |
| 118 | Capitão da Guarda | [0, 0, 50, 0] | dano / - / dano / dano | [40, 0, 30, 30] | [50, 30, 20, 0] | [40, 15, 40, 5] | **[40, 0, 30, 30]** | 15.0 → 20.0 → 15.0 | etapa 12 punha peso em slot sem golpe: [2] |
| 119 | Robô Mergulhador | [0, 30, 0, 0] | dano / 0x40 / dano / - | [50, 30, 20, 0] | [30, 20, 20, 30] | [30, 20, 20, 30] | **[50, 30, 20, 0]** | 9.0 → 6.0 → 9.0 | etapa 12 punha peso em slot sem golpe: [4] |
| 120 | Robô da Caverna | [0, 0, 0, 50] | dano / - / dano / dano | [50, 0, 30, 20] | [30, 20, 20, 30] | [30, 20, 20, 30] | **[50, 0, 30, 20]** | 10.0 → 15.0 → 10.0 | etapa 12 punha peso em slot sem golpe: [2] |
| 121 | Robô das Areias | [0, 50, 0, 30] | dano / 0x40 / - / dano | [40, 30, 0, 30] | [30, 20, 20, 30] | [30, 20, 20, 30] | **[40, 30, 0, 30]** | 24.0 → 19.0 → 24.0 | etapa 12 punha peso em slot sem golpe: [3] |
| 131 | Vampiro Jovem | [0, 0, 0, 0] | 0x400 / dano / - / dano | [30, 40, 0, 30] | [40, 30, 30, 0] | [40, 30, 30, 0] | **[30, 40, 0, 30]** | 0.0 → 0.0 → 0.0 | etapa 12 punha peso em slot sem golpe: [3] |
| 132 | Vampiro Sanguinário | [0, 30, 0, 0] | 0x400 / dano / dano / dano | [30, 25, 25, 20] | [20, 30, 30, 20] | [20, 30, 30, 20] | **[30, 25, 25, 20]** | 7.5 → 9.0 → 7.5 |  |
| 133 | Vampiro Ancião | [0, 50, 0, 0] | 0x400 / dano / dano / dano | [30, 25, 20, 25] | [20, 30, 20, 30] | [20, 30, 20, 30] | **[30, 25, 20, 25]** | 12.5 → 15.0 → 12.5 |  |
| 134 | Capanga da Caverna | [0, 0, 0, 0] | dano / 0x40 / dano / - | [40, 30, 30, 0] | [40, 30, 30, 0] | [40, 30, 30, 0] | **[40, 30, 30, 0]** | 0.0 → 0.0 → 0.0 |  |
| 135 | Capanga da Fonte | [0, 0, 0, 0] | dano / 0x40 / dano / 0x40 | [30, 30, 20, 20] | [0, 40, 30, 30] | [0, 40, 30, 30] | **[30, 30, 20, 20]** | 0.0 → 0.0 → 0.0 |  |
| 136 | Capanga Sombrio | [0, 50, 0, 30] | dano / 0x40 / dano / 0x40 | [15, 15, 35, 35] | [30, 30, 20, 20] | [30, 30, 20, 20] | **[15, 15, 35, 35]** | 18.0 → 21.0 → 18.0 |  |
| 149 | Ladrão do Deserto | [-70, 0, 0, 50] | dano / dano / - / dano | [40, 40, 0, 20] | [50, 30, 20, 0] | [50, 30, 20, 0] | **[40, 40, 0, 20]** | -18.0 → -35.0 → -18.0 | etapa 12 punha peso em slot sem golpe: [3] |
| 150 | Xamã do Vulcão | [-70, 0, 0, 100] | dano / dano / dano / dano | [30, 30, 20, 20] | [50, 30, 20, 0] | [50, 30, 20, 0] | **[30, 30, 20, 20]** | -1.0 → -35.0 → -1.0 |  |
| 151 | Aprendiz da Floresta | [-70, 0, 0, 100] | dano / dano / dano / dano | [30, 30, 20, 20] | [50, 30, 20, 0] | [40, 30, 0, 30] | **[30, 30, 20, 20]** | -1.0 → 2.0 → -1.0 |  |
| 155 | Batedor Escavador | [60, 0, 162, 0] | dano / dano / inv / - | [30, 40, 30, 0] | [50, 50, 0, 0] | [50, 30, 20, 0] | **[30, 40, 30, 0]** | 18.0 → 30.0 → 18.0 |  |
| 156 | Lutador Noturno | [60, 0, 163, 0] | dano / dano / inv / - | [40, 30, 30, 0] | [50, 50, 0, 0] | [40, 30, 30, 0] | **[40, 30, 30, 0]** | 24.0 → 24.0 → 24.0 |  |
| 157 | Batedor Venenoso | [60, 0, 164, 0] | dano / dano / inv / - | [20, 30, 50, 0] | [50, 50, 0, 0] | [30, 30, 20, 20] | **[20, 30, 50, 0]** | 12.0 → 18.0 → 12.0 | etapa 12 punha peso em slot sem golpe: [4] |
| 161 | Recruta Escavadora | [-30, 0, 0, 0] | dano / 0x80 / 0x800 / 0x100 | [30, 30, 20, 20] | [50, 50, 0, 0] | [50, 30, 0, 20] | **[30, 30, 20, 20]** | -9.0 → -15.0 → -9.0 |  |
| 162 | Aprendiz Noturna | [-30, 0, 0, 0] | dano / 0x80 / 0x800 / 0x100 | [30, 30, 20, 20] | [50, 50, 0, 0] | [30, 40, 30, 0] | **[30, 30, 20, 20]** | -9.0 → -9.0 → -9.0 |  |
| 163 | Batedora Venenosa | [-30, 0, 0, 0] | dano / 0x80 / 0x800 / 0x100 | [30, 30, 20, 20] | [50, 50, 0, 0] | [40, 15, 40, 5] | **[30, 30, 20, 20]** | -9.0 → -12.0 → -9.0 |  |

## O que foi verificado (estático, sobre a ROM nova)

As saídas completas estão em `verificacao\`: `integridade.txt`, `encontros.txt`, `resumo.json`, `texto\0_resumo.txt` … `5_ingles_restante.txt`, `hashes_e_bps.json` e `previa_inimigos.png`. **Resultado: 0 falhas.**

**Integridade (revisão 01 refeita):**
- Tamanho de 128 MiB igual à capacidade. Título e código `BRPE` iguais.
- **ARM9, ARM7, FNT e banner idênticos ao original.** Sem overlays.
- CRC16 do cabeçalho válido e CRC do logotipo igual.
- FAT sem sobreposição e dentro da ROM. Tamanho usado = maior fim, e cauda em 0xFF.
- 0 bytes diferentes da rc.1 fora dos arquivos alterados, das entradas deles na FAT e de 0x80/0x15E.
- **Tabelas:**
  - FR/SP/GR/IT: só `enemy_param` e `character_name` mudaram.
  - US/EN: essas duas, mais as tabelas de mensagem corrigidas.
  - `boss_param` e `player_param` idênticos.
  - `enemy_param` igual nos 6 idiomas.
  - Todos os campos de combate e recompensa iguais ao original nas 173 linhas, e `atk1`–`atk4` somam 100 em todas.

**Encontros (revisão 02 refeita + checagens novas):**
- **Grupos:** 2.143 chamadas `SetEnemyParty` (argc 15) idênticas ao original. IDs válidos em slots e tipos, e nenhum grupo vazio.
- **Saibamen:** ID 2 = "J. Sai" com `ene001_01`. Linhas 1–4 iguais à rc.1 e ao original.
- **Animações e golpes:**
  - As 151 linhas usadas têm `.chr` existente, `palno` válido e animações decodificáveis.
  - Todo slot com peso tem animação e golpe definido no `eneEff`. No original são 0 casos sem golpe; na rc.1 eram 12, na etapa 12 18 e na nova 0.
- **Invocações:** todas apontam para linhas válidas, e o invocado está pré-carregado nos grupos.
- **Aparência:**
  - Aparência única por linha.
  - Nenhum mapa com mesma cara e nome diferente.
  - Menor distância de paleta no mesmo mapa: 109.
  - Nenhuma linha trocada de tamanho 2 em grupo com mais de um inimigo.
- **Nomes:** únicos e sem Saiyajin/Saibaman/broto/pirata nos trocados.

**Texto (revisão 03 refeita, `texto\verificar_textos.py`):**
- 716/716 correções presentes.
- 0 divergências de códigos de controle em 14.439 textos mudados.
- 0 caracteres sem glifo.
- **Larguras:**
  - 0 erros.
  - 4 avisos, todos herdados: linhas manuais em que o inglês original já era mais largo (`skr02_00:49`, `c0201_01:11`, `c0903_03:14`, `c1201_00:14`).
  - Os 2 avisos de nome largo da rc.1 sumiram com os nomes novos.
- Inglês suspeito: US 0, EN 0.

## O que precisa de teste jogando (por prioridade)

Use uma cópia do save e não grave por cima do save do Switch na primeira conferência.

1. **Saibamen no cap. 14** (`c1402`–`c1409`, Ermo Páprica `nap01–03`):
   - Tenshinhan × Saibaman, Yamcha × Saibaman e os 4 restantes;
   - nomes e sprites ("J. Sai") e se a cena segue normalmente depois de cada luta.
2. **Brutamontes do Ermo** (Ermo do Espinafre `spi`, Deserto Break `kou`) e **Brutamontes Glacial** (Yunzabit `yun`):
   - sprite novo (Bandido);
   - os golpes saem com animação e dano, e nenhum turno fica "vazio".
3. **Encontro nível 52 no Vaso do Diabo (`ben`) e no Deserto (`snd`):**
   - J./C./K./T. Sai de volta, junto com Mecha Patrulheiro, Robô das Areias e Batedor Venenoso;
   - sprites e cores certos e sem travamento ao carregar a batalha.
4. **Ilha de Treinamento (`tut`)**, primeira luta: Lutador Errante com paleta nova e pesos originais [50,50,0,0].
5. **Abertura do Kuririn** (Floresta de Bambu `bam`): Arruaceiro do Bambu e Discípulo Rebelde, com paletas novas.
6. **Lutas com o Nappa** (cap. 14) e a sequência até o Vegeta (Ermo Gizard `las`, com J./K. Sai de volta).
7. **Invocações reativadas:**
   - Batedor Escavador (spi), Lutador Noturno (mut) e Batedor Venenoso (snd) chamando a "larva";
   - Atirador da Montanha (pao/kou) e Guerreira do Gelo (fur/gyu) chamando outro igual.
   - Observar a animação do golpe de invocação (é a do sprite doador), a entrada do inimigo chamado e a mensagem de falha.
8. **Castelo do Pilaf (`pir`):** Robô Sentinela, Guarda do Castelo e Capitão da Guarda (sprites, cores e golpes).
9. **Textos alterados:**
   - `c1407_00` (Piccolo Daimaoh);
   - cap. 9 (Senhor Kaioh);
   - as 2 mensagens da Rajada de Ki (est07 e outros 17 mapas);
   - tutorial de status (`btl_mes_TUT:9`, lista reordenada);
   - mensagens de item roubado e de apagar memória.
   - E as 4 linhas manuais largas herdadas.
