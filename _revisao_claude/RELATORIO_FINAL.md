# Revisão independente (Claude) — DBZ Attack of the Saiyans PT-BR, 12/10/2026

Alvo: etapa 12 (`12_Coerencia_Historia\DBZ Attack of the Saiyans PT-BR Coerencia.nds`, SHA-256 130b4ad8…), comparada com a rc.1 (41412a47…) e o original.
Relatórios completos: `01_integridade`, `02_encontros`, `03_traducao`, `04_teste`. Correções em `..\13_Correcoes_Revisao` (RELATORIO.md, LEIA-ME.md).

## Achados na etapa 12
| Gravidade | Achado | Etapa 13 |
|---|---|---|
| CRÍTICO | Saibamen sumiram do jogo: a luta do cap. 14 usa a linha 1, que virou "Robô de Patrulha" | linhas 1–4 = rc.1 |
| ALTO | Saibamen fora dos ermos Páprica/Gizard | idem |
| ALTO | Pesos de ataque (atk1–4) trocados em 31 linhas; "balanceamento preservado" não se sustentava. Na prática, 18 linhas com peso em slot sem golpe (turno vazio) | 45/48 iguais ao original, 3 redistribuídos (±2 de média), 0 slots vazios |
| ALTO (rev. 02) | Linhas 110/112 com sprite do Fugitivo (risco de invocação) | o efeito vem de `eneEff.bin`, não do sprite: risco inexistente; trocado o sprite mesmo assim (Bandido) |
| ALTO (tradução) | "Rei Demônio Piccolo" → "Piccolo Daimaoh" | corrigido |
| MÉDIO | Corsárias no Castelo do Pilaf (pir × kai) | Robô Sentinela / Guarda do Castelo / Capitão da Guarda |
| MÉDIO | 4 pares de inimigos com cores quase iguais no mesmo mapa | paleta própria por linha, distância ≥100 |
| MÉDIO | ~73 textos (Senhor Kaioh, Enma, Chichi "Obrigada", status, concordâncias) | 140 textos corrigidos em 716 posições |
| MÉDIO | ROM antiga do Switch não documentada (original EN com assinatura zerada) | documentada no LEIA-ME |
| MÉDIO | `ptbr.json` com nomes antigos (reaplicar a tradução reverteria os nomes) | `13…\dados\ptbr.json` atualizado |
| BAIXO | nomes repetidos ("Errante" ×6), gênero, hashes de BPS faltando, falas EN-only | corrigidos; 250 falas da pasta EN traduzidas (o jogo USA só lê US/FR) |

Mudança de comportamento na 13: ex-lobos e ex-insetos voltam a chamar reforço como no jogo original (na rc.1/12 não chamavam).

## O que passou na etapa 12
Hashes e BPS exatos; só os 27 arquivos declarados mudaram; HP/nível/EXP/drops/resistências iguais nas 173 linhas; capítulos 0–13 sem Saiyajin/Saibaman fora de hora; tradução sem erro de fonte, código ou largura. Teste jogando (melonDS em área de trabalho oculta): boot, título, prólogo, 1ª batalha, substitutos no Monte Paozu e Deserto Diablo, save do Switch e menus — sem trava em 50+ batalhas.

## Etapa 13
ROM `13_Correcoes_Revisao\DBZ Attack of the Saiyans PT-BR.nds` SHA-256 0616e6c6fdada1e54d0694bd2e552be64dea3c3e592cd88ddf07b31d8bda3a82 (CRC32 51717d80), build determinístico sobre a rc.1, BPS sobre a rc.1 e sobre o original verificados. Verificações estáticas 01/02/03 refeitas: 0 falhas.
Teste jogando da 13 (`04_teste\rom13\RELATORIO.md`): sem regressão contra a rc.1. Passaram boot/1ª batalha, save do Switch e menus, Saibaman/J./C./T. Sai (grupo forçado), Brutamontes do Ermo/Glacial (110/112), Ladrão do Deserto (149), Robô Sentinela e Capitão da Guarda (forçados), ex-lobo no Deserto Break sem trava (reforço não visto em ~60 turnos). Batalhas forçadas com IDs 5, 105 e 110 (e K. Sai) travam igual na rc.1 — provável artefato do método de forçar grupo; confirmar nos mapas reais. Rótulo: no jogo o ID 2 é "Saibaman" e o J. Sai é o 3 (só documentação). "Ilha de Treino" na faixa é encurtamento proposital (igual na rc.1).

## Pendente de teste no console
Saibamen do cap. 14, abertura do Kuririn (floresta de bambu), lutas com o Nappa, reforço dos ex-lobos/ex-insetos, Castelo do Pilaf, encontro nível 52 (Vaso do Diabo/Deserto).
