# Revisão independente da tradução PT-BR: DBZ Attack of the Saiyans (NDS, BRPE)

Frente: **tradução**. Revisão feita em 11 e 12/10/2026. Trabalhei só nesta pasta e não alterei nada no projeto.

- **ROM revisada:** `12_Coerencia_Historia\DBZ Attack of the Saiyans PT-BR Coerencia.nds`
- **Base de comparação:** ROM original USA (En,Fr), extraída do zip de `00_Original` para `rom\orig.nds`
- **Fonte das traduções:** `11_Projeto_Recuperado\traducao\ptbr.json` e os `lote*_pt*.json`

## Resumo

- **A ROM corresponde aos arquivos de tradução.** Nas pastas US e EN, 11.273 de 11.289 ocorrências com tradução estão exatamente como em `ptbr.json`. Das 16 que sobram, 6 são identificadores preservados de propósito (a tradução entrou como texto extra). As outras 10 estão só no script de depuração `dbg01_00`, que não aparece no jogo.
- **Nenhum resto de inglês visível na pasta US.** O que ficou em inglês são nomes próprios, interjeições, nomes nos créditos, o título do jogo e alguns termos de menu aceitáveis em PT (lista na seção 2). Não há francês.
- **Ortografia limpa.** Passei as 6.080 palavras distintas pelo corretor pt-BR do Word. Nenhum erro ortográfico real: as 460 palavras não reconhecidas são nomes, onomatopeias, abreviações e nomes dos créditos.
- **Fonte e códigos de controle sem problema.** Todo caractere usado tem glifo nas duas fontes, e não há código de controle quebrado (0 divergências EN × PT em 5.392 textos únicos).
- **Nenhum estouro pelo modelo de largura.** Nenhuma página passa de 3 linhas além do que o original já tinha, e nenhum texto de tabela passa da maior largura original do seu grupo. Ficam 8 linhas manuais largas para conferir no emulador (seção 4).
- **Achados de qualidade:** cerca de 165 itens, nenhum grave de sentido. São 1 ALTO (nome fora do glossário), cerca de 50 MÉDIO e cerca de 105 BAIXO. A maior parte é consistência de termos nas tabelas, "Kaioh" sem "Senhor", tratamento você/vocês, algumas concordâncias e frases truncadas.
- **Qualidade geral: alta.** O texto é natural e o glossário foi seguido em mais de 95% dos casos.

## 1. O que foi verificado e como

Scripts de revisão em `scripts\` (cópias dos scripts do projeto, mais os meus `rev_*.py`); saídas em `saida\`.

| Verificação | Método | Resultado |
|---|---|---|
| Extração da ROM nova e da original | `rev_extrair.py` (usa `nds_rom`, `sb`, `bdat` do projeto): 1.500 scripts `.sb` (US, EN, FR) e 6.846 células das tabelas `bdat` | ok |
| ROM × `ptbr.json` | `rev_comparar.py` → `saida\comparacao.json` | 11.273/11.289 iguais; 6 identificadores preservados; 10 divergências só em `dbg01_00` (depuração) |
| Texto mudado sem tradução no dicionário | idem | 0 |
| Inglês restante (US) | classificação do próprio extrator + lista de interjeições (`saida\ingles_dialogo.txt`) | só nomes, interjeições e créditos (seção 2) |
| Francês | regex de palavras francesas na pasta US | 0 |
| Pasta EN | idem | 53 falas em inglês, variantes que só existem na EN; o jogo USA lê a US (BAIXO, ver seção 2) |
| Cobertura da fonte | glifos de `latin0.fnt` e `latin1.fnt` da ROM nova, comparados com o glifo de listras | todos os caracteres usados têm glifo; 0x81/86/87/89 só no "Tenshinhan" estreito |
| Códigos de controle | contagem de `<..>`, `%d/%s`, `\NN..`, `@NN` em EN × PT; tags malformadas | 0 divergências |
| Ortografia | corretor do Word pt-BR via COM (`rev_spell.ps1`) nas 6.080 palavras distintas | nenhum erro real (`saida\spell_word.txt`) |
| Padrões gramaticais | regex de erros comuns: crase, há/a, mal/mau, hífen, pontuação, tu/você (`rev_varredura.py` → `saida\varredura.txt`) | nada sistemático |
| Nomes e termos | contagem das variantes de 40 nomes (`saida\varredura.txt` §5, `saida\nomes_contexto.txt`) | seção 3 |
| Largura e linhas | `rev_larguras.py` → `saida\larguras.txt` | seção 4 |
| Leitura humana | os 5.392 textos únicos da ROM, lidos em 6 fatias (`saida\fatia1..6.txt` → `saida\achados_fatia1..6.txt`) | seção 5 |
| Nomes da etapa 12 | `revisao_inimigos.csv` × `character_name` da ROM | os 52 nomes revisados estão na ROM, US = EN; sem duplicata indevida |

## 2. Inglês que ficou na ROM (pasta US)

**Mantido de propósito ou aceitável:**
- nomes próprios (Goku, Piccolo, Bulma, Annin, Suno, Mez, Goz, Hakkake…);
- interjeições ("Huff... huff...", "Hm?", "Arf! Arf!", "Hoy hoy hoy!");
- nomes nos créditos e o título "Dragon Ball Z: Attack of the Saiyans";
- nas tabelas: Kamehameha, Masenko, Rengeki, CHA-LA / HEAD-CHA-LA, Perfume, Scouter (glossário), Menu, Status, Combos, Normal, Mono, OK, Total, Item;
- os nomes dos idiomas e "Language Select description text" no `cf_mes_MENU`, que parecem não ser usados.

**Pontos de atenção:**

| Texto | Local | Sugestão | Grav. |
|---|---|---|---|
| "Kamehame Fever" | `cf_mes_COMBO` | "Febre Kamehame", ou manter se for nome oficial do combo | BAIXO |
| "Huff... huff..." (5 cenas) | ex. `c0402_00:11` | "Ufa... ufa..." | BAIXO |
| 53 falas inteiras em inglês | pasta **EN** (ex. "Yo! Hey, it's me!…", "Lets hurry and go find Eighter!") | Sem efeito no jogo USA, que lê a pasta US. Se algum dia a EN for usada, traduzir. | BAIXO |

## 3. Consistência de nomes e termos

Variantes contadas por ocorrência. Fora as exceções da tabela abaixo, o glossário é seguido à risca:
- **Sem variante:** Kuririn (225), Tenshinhan (172), Chaos (72), Chichi (107), Lunch (48), Cutelo (38), Kakarotto (64), Número 8 (27), Shenlong, Genki Dama (24), Piccolo Daimaoh (10 no diálogo principal).
- **Quase sem variante:** Mestre Kame (133), Kami-Sama (135), Sr. Popo (86), Saiyajin (91).

| Inconsistência | Onde | Sugestão | Grav. |
|---|---|---|---|
| "Rei Demônio Piccolo" | `c1407_00:34` | "Piccolo Daimaoh" | **ALTO** |
| "Rei Demônio" solto | `c0401_03:19`, `c0704_01:15`, item "Selo do Rei Demônio" | "Piccolo Daimaoh" / "Selo do Daimaoh" | MÉDIO |
| "Kaioh" sem "Senhor" (8×, quase tudo fala do Goku no cap. 9) | `c0903_02:20`, `c0905_02:16`, `c0907_00:11`, `c0907_01:17/35/47`, `c0907_02:8`, `c0908_01:10` | "Senhor Kaioh" (como na dublagem); o vocativo "O senhor é hilário, Kaioh!" é o mais estranho | MÉDIO |
| "Floresta **de** Enma" / "Árvores **de** Enma" × "Floresta/Árvore **do** Enma" (diálogos) | `cf_mes_QUEST:48`, `cf_mes_LOC:8/9`, `key_item_mes:45/47` | "do Enma" | MÉDIO |
| "Kami" sem "-Sama" | `c1001_00:30` ("treino com o Kami?"); `c0901_01:29` ("Kami da Terra", aceitável) | "Kami-Sama" | MÉDIO |
| "Uranai" sem "Vovó" | `c1001_00:36` ("Palácio da Uranai"); `c0003_00:20` ("Minha irmã Uranai", aceitável) | "Palácio da Vovó Uranai" | MÉDIO |
| "Kuririn e Kame" (rótulo de quem fala) | `c0803_01:20` | "Kuririn e M. Kame" (72 px, cabe; o maior rótulo original tem 81 px) | MÉDIO |
| "Turbante do Popo" | `btl_acc_mes:196` | "Turbante do Sr. Popo" | MÉDIO |
| "Corp. Cápsula", "Mont. Paozu", "Caverna do Mt. Frappe" | `cf_mes_QUEST:25/30`, `cf_mes_LOC:10` | "Corporação Cápsula" (se couber), "Montanha Paozu", "Caverna do Monte Frappe" | MÉDIO |
| "Semente(s)" e "Super Semente" sem "dos Deuses" | `cf_mes_QUEST:33`, `key_item_mes:17`, `use_item_mes:56` | completar onde couber | BAIXO |
| rabo (cap. 6, `kam01`) × cauda (cap. 7, 14, 15) | ex. `c0705_03:24/25` | escolher um termo (a maioria usa "cauda") | BAIXO |
| "Escola Tsuru" × "Mestre Shen" × "Golpe Garça-Lobo" × "Escola Tartaruga" | `c0301_00:15`, `krd03_00:32` | "Escola do Mestre Shen" ou "Escola Garça", conforme a decisão do glossário | BAIXO |
| "namekuseijin" minúsculo × "Saiyajin" maiúsculo | cap. 14 e 16 | padronizar a caixa | BAIXO |
| "Monte Frappe" × "Montanha Paozu"; "Deserto Break" × "Ermo Páprica/Gizard" | mapa-múndi | só se quiser uniformizar (os nomes estão no glossário) | BAIXO |
| "Mutaito" sem "Mestre" | `krd03_00:32` | "Mestre Mutaito" | BAIXO |
| Termos de status: Escuro/Escuridão, Pânico/Confusão, emboscada/ataque surpresa | `btl_mes_TUT:9`, `use_item_mes:74`, `btl_mes_SYS:58` | um nome por status | MÉDIO |
| "Corrente+" / "ataque em corrente" (chain) | `btl_mes_BLAST:18-19`, `btl_acc_mes:97-101, 201` | "Encadeamento" / "ataque encadeado" | MÉDIO |
| "Requer: %s Nv%d" | `cf_mes_MENU:107` | "LV%d" (LV é mantido no resto do jogo) | MÉDIO |
| Comando "Técnica" (tutorial) × "Especial" (menu de batalha) | `btl_mes_TUT:3` × `btl_mes_SYS:14/48` | usar o nome que aparece na tela | MÉDIO |
| "Gangue do Coelho" (o glossário não tem a entrada; a dúvida citava "Grupo do Coelho") | `c0202_00:16/17` | manter "Gangue do Coelho" e registrar no glossário | BAIXO |

**Nomes novos da etapa 12** (52 entradas revistas):
- Estão todos na ROM (US = EN), com gênero coerente e sem erro de ortografia.
- O mais largo tem 90 px; o maior nome original tem 92 px.
- **Observações (BAIXO):**
  - repetição de sufixos: "Errante" 6×, "Veterano" 4×, além de "Patrulheiro / de Patrulha";
  - pares quase iguais: "Batedor Venenoso" × "Batedora Venenosa", "Desertor da RR" × "Desertor Red Ribbon";
  - grafia da Red Ribbon mista nos nomes: "RR" e "Red Ribbon".
- **Risco de processo (MÉDIO):** os nomes da etapa 12 não estão em `ptbr.json`, que ainda tem os nomes antigos ("Robô Alado RR", "Saibaman Glacial"…). Se `aplicar_traducao.py rom` for rodado de novo sobre a base, ele grava os nomes antigos. Atualizar `ptbr.json` ou documentar a ordem dos passos.

## 4. Limites técnicos (largura, linhas, fonte)

**Modelo de quebra das falas:**
- fonte pequena `latin1`;
- quebra automática por palavra em 196 px (tabela de avanços);
- `<n>` força a quebra;
- calibrado com as capturas `notes\cena_c1408_03.png` e `cena_c0803_01.png`: linhas de 188 e 191 px couberam; 202, 205 e 234 px quebraram.

**Resultados:**
- **Páginas:** nenhuma página traduzida ficou com mais de 3 linhas e mais linhas que o original. O original já tem cerca de 22 páginas de 4 linhas (tutoriais longos), e a tradução tem o mesmo número.
- **Linhas manuais com `<n>` acima de 196 px:** 8. A nota do projeto diz que o jogo não requebra essas linhas; se for assim, elas podem passar da borda. Em 4 delas o inglês já era tão largo ou mais (240–280 px) e funcionava. Conferir no emulador:

| Linha PT (px) | Local | EN (px) | Grav. |
|---|---|---|---|
| "Agora você destrói objetos que piscam em branco!" (216) | `est07_00:15` e mais 17 mapas | 191 | MÉDIO |
| "Agora você destrói todos os objetos quebráveis!" (211) | `est07_00:16` e mais 17 mapas | ~185 | MÉDIO |
| "Eu sou o ogro mais forte depois do Senhor Enma!" (205) | `c0903_03:14` | 217 | BAIXO |
| "Aqueles caras fugiram para o Castelo do Pilaf." (201) | `god01_00:23` | <196 | BAIXO |
| `c1201_00:13/14` (243/247), `c0201_01:11` (240), `skr02_00:49` (218) | — | 211–280 | BAIXO |

Se precisar encurtar, as sugestões são "Agora destrói o que pisca em branco!" e "Agora destrói tudo o que quebra!".

- **Rótulos de quem fala:** o maior em PT é "Princesa Serpente" (77 px); o maior original tem 81 px.
- **Tabelas** (itens, golpes, menus, missões, lojas, nomes): nenhuma célula passa da maior largura original do grupo (mesma tabela e coluna), nas duas fontes.
- **Fonte:** os caracteres usados são `°ÀÁÂÃÉÊÍÓÔàáâãçéêíóôõú` e os códigos estreitos do Tenshinhan. Todos têm glifo. "º" e "ª" não têm glifo, e o uso de "°" como ordinal ("23° Torneio", "1° ataque", "N°3") é a solução certa (não é erro).
- **Códigos de controle:** todos íntegros. "depre-<n>dada" (`cf_mes_QUEST:48`) é uma hifenização manual aceitável.

## 5. Tabela de problemas de texto

A lista completa, com cerca de 165 itens, está em `saida\achados_fatia1..6.txt`. Abaixo vão o ALTO, os MÉDIO e uma seleção dos BAIXO; os itens de nome já estão na seção 3.

| Texto atual | Sugestão | Local / ID | Grav. |
|---|---|---|---|
| "Os últimos momentos do Rei Demônio Piccolo..." | "...do Piccolo Daimaoh..." | `cf1/c14/c1407_00:34` | ALTO |
| "Atenção, todos! **Obrigado** por virem celebrar o meu casamento!" (fala da Chichi) | "Obrigad**a**" | `c05/c0508_01:9` | MÉDIO |
| "E quem liga pro que vocês estavam?" | "...pro que vocês andaram fazendo?" | `c10/c1001_00:43` | MÉDIO |
| "Esta técnica pega emprestad**a** um pouco da energia" | "pega emprestad**o**" | `c13/c1304_00:33` | MÉDIO |
| "Mas o símbolo escrito **nela** é o meu." (antecedente: "umas roupas") | "nelas" | `c07/c0705_03:27` | MÉDIO |
| "Há calor... e bondade **nelas**." (sem antecedente) | "...bondade nisso." | `c03/c0301_00:17` | MÉDIO |
| "Que bom te ver vivo ainda!" (EN "alive again") | "Que bom te ver vivo de novo!" | `c04/c0401_00:41` | MÉDIO |
| "Vou usar só a força para apagar o fogo!" (EN "just enough") | "Vou usar só a força necessária para apagar o fogo!" | `c05/c0501_04:22` | MÉDIO |
| "Vocês estão muito, muito além das suas forças!" | "Isso está muito além das suas forças!" | `c06/c0607_00:79` | MÉDIO |
| "para vencê-lo e aqueles dois amigos dele..." | "para vencer ele e aqueles dois amigos dele..." | `c06/c0605_00:37` | MÉDIO |
| "estou pasma que vocês acharam mesmo um ovo" | "estou pasma de vocês terem achado mesmo um ovo" | `c05/c0505_00:30` | MÉDIO |
| "Ei, que tal assim, senhora? ... **você** se importa..." | "a senhora se importa..." | `c05/c0506_00:23` | MÉDIO |
| "Ele pediu pra eu dizer pra não se preocuparem!" (falando só com a Chichi) | "...pra você não se preocupar com eles!" | `c08/c0802_00:29` | MÉDIO |
| "O Kami-Sama vai treinar vocês.<n>E eu também." (o Yajirobe será treinado) | "...E a mim também." | `c08/c0803_02:21` | MÉDIO |
| "Pode ser que não dê<n>para vencer..." (EN "too close to call") | "O resultado pode ser<n>imprevisível..." | `c09/c0901_01:38` | MÉDIO |
| "Soube que você chegou aqui e está implorando pra você ir..." (sujeito ambíguo) | "Ele soube que você chegou e não para de implorar pra você ir..." | `c09/c0907_03:26` | MÉDIO |
| "Entre nele e você vai parar..." (fala aos três) | "Entrem nele e vocês vão parar..." | `c09/c0907_03:51` | MÉDIO |
| "com as suas Esferas do Dragão e as minhas, somo sete!" | "...juntando com as minhas, terei as sete!" | `c10/c1008_02:27` | MÉDIO |
| "Se eu morrer de novo, venho te visitar!" (Goku usa "o senhor" na cena) | "...venho visitar o senhor!" | `c13/c1307_00:30` | MÉDIO |
| "Não tem jeito...!" (EN "There's no way...!", descrença) | "Não pode ser...!" | `c15/c1506_00:35` | MÉDIO |
| "Você já capturou todos os monstros." / "todo tipo..." (o resto da cena usa "vocês") | "Vocês já capturaram..." | `cf0/god/god03_00:13/16` | MÉDIO |
| "O mestre virou mesmo o aluno!" | "O aluno superou o mestre!" | `god03_00:16` | MÉDIO |
| "você esquiva dos ataques" | "você se esquiva dos ataques" | `skr02_00:64` | MÉDIO |
| "Pra bem ou pra mal" | "Pro bem ou pro mal" | `kos04_00:15` | MÉDIO |
| "Minha irmã Uranai me deu **isto**... para usá-**la**" | "...me deu esta bola..." | `c00/c0003_00:20` | MÉDIO |
| "\<i\> roubado." (item feminino fica errado) | "Roubaram: \<i\>." | `btl_mes_SYS:8` | MÉDIO |
| "HP/Ki de \<t\> todo restaurado." / "Ki do grupo todo restaurado." | "...totalmente restaurados." | `btl_mes_ITM:22/30` | MÉDIO |
| "Acessórios, de lojas e masmorras, dá para equipá-los..." (anacoluto) | "Os Acessórios, achados em lojas e masmorras, podem ser equipados..." | `cf_mes_TUT:5` | MÉDIO |
| "Reiniciando a memória." / "Falha ao reiniciar" (é apagar os dados) | "Formatando a memória..." / "Falha ao apagar" | `cf_mes_MENU:120-122` | MÉDIO |
| "Sou um mercador viajante, onde quer que os artistas marciais... precisem de mim." | "...e vou aonde os artistas marciais precisarem de mim." | `cf_mes_SHOP:32` | MÉDIO |
| "faz mais do que só lacrimejar os olhos" | "...do que fazer os olhos lacrimejarem" | `cf_mes_COMBO:27` | MÉDIO |
| "Pena Cauda Fênix" | "Pena da Cauda de Fênix" | `use_item_mes:62` | MÉDIO |
| "Pode ser vendida por bom dinheiro" (também em Rubi/Diamante) | "Vale um bom dinheiro na venda" | `use_item_mes:197` (6×) | MÉDIO |
| "Vira inimigos vencidos em cenoura." | "Transforma inimigos vencidos em cenouras." | `pt_eqp_mes:15` | MÉDIO |
| "virar o ataque normal um ataque em corrente" | "transformar o ataque normal em ataque encadeado" | `btl_acc_mes:201` | MÉDIO |
| "Usar Coisa do Bubbles?" | "Usar a Coisa do Bubbles?" | `for01_00:16` | BAIXO |
| "...Ei, maninho!" / "Boa ideia, maninho!" (big bro) | "mano" | `c11/c1105_01:19/24` | BAIXO |
| "Buááááá!" (grito de queda) | "Aaaaahhh!" | `c11/c1103_00:13` | BAIXO |
| "Dizem que tem uns 1 milhão de quilômetros." | "cerca de um milhão de quilômetros" | `c09/c0902_00:21` | BAIXO |
| "Pai!" (o Gohan diz "Papai" no resto) | "Papai!" | `c10/c1002_03:10` | BAIXO |
| "Deixe de ser idiota, Kakarotto." (flashback com tradução diferente da original da cena) | igualar a `c0604_00` | `c07/c0705_03:18` | BAIXO |
| "Remédio Karin", "Joia Coelho Monstro", "Bênção Shenlong", "Pulseira Revide" | pôr a preposição ("do"/"de") se couber | tabelas de itens | BAIXO |

**Item que discordo da leitura em fatias:** o botão "Refazer" (`cf_mes_MENU:25`) foi uma decisão documentada do projeto, porque "Tentar de Novo" saía cortado na tela de pontos. Não é erro.

## 6. Itens "?" do glossário: recomendação

| Termo | Atual | Recomendação |
|---|---|---|
| Ox-King | Cutelo | **Manter.** É o nome da dublagem clássica ("Rei Cutelo"). Usado 38× sem variante. |
| Master Shen | Mestre Shen | **Manter** (forma da dublagem BR). Padronizar "Escola Tsuru" para "Escola do Mestre Shen" ou "Escola Garça" (combina com "Golpe Garça-Lobo"). |
| Eighter | Número 8 | **Manter.** É descritivo, a dublagem também usou numeração, e está consistente (27×). |
| General White | General White | **Manter.** Nome próprio, 2×. |
| Monster Carrot | Coelho Monstro | **Manter.** Consistente (8×) e cabe no rótulo (66 px). Registrar "Gangue do Coelho" (Usagi-dan) no glossário. |
| Pilaf's / Ox-King's Castle | Castelo do Pilaf / do Cutelo | **Manter** (segue os nomes acima). |
| Wolf Fang Fist | Punho do Lobo (+ "Neo Punho do Lobo") | **Manter.** É curto e claro. Opcional: "Punho do Lobo Neo" soa mais natural. |
| Hellzone / Light Grenade | Granada Infernal / Granada de Luz | **Manter.** "Granada Infernal" é a forma conhecida no Brasil. |
| Chiaotzu (fora da lista "?") | Chaos | **Manter "Chaos"** (dublagem BR, 72× sem variante). "Chaozu" não aparece no texto; só o pedido de revisão usa essa forma. |

## 7. Recomendações finais (por prioridade)

1. Corrigir o ALTO ("Rei Demônio Piccolo") e os MÉDIO de diálogo da seção 5. São cerca de 25 strings, todas de script.
2. Uniformizar os termos das tabelas: Enma "do", status, chain/encadear, "Nv" → "LV", Técnica/Especial, gênero de "roubado" e "vendida".
3. Completar "Senhor Kaioh", "Kami-Sama", "Vovó Uranai", "Sr. Popo" e "M. Kame" no rótulo.
4. Conferir no emulador as 2 mensagens de nível da Rajada de Ki (`est07_00:15/16`), que aparecem em 18 mapas.
5. Atualizar `ptbr.json` com os nomes da etapa 12 antes de qualquer nova aplicação do texto.
6. Fora desta frente (gráficos e jogo): as 36 faixas de local e os títulos dos capítulos 0 e 7 ainda dependem de verificação visual, e as falas de NPC fora da Cidade do Leste ainda precisam ser jogadas. Pela leitura de texto, as falas de NPC (lote 11) estão traduzidas e sem problemas graves.
