# Teste jogável automatizado: DBZ Attack of the Saiyans PT-BR "Coerência"

Data: 11 e 12/10/2026. Revisor: Claude (independente).
ROM testada: `12_Coerencia_Historia\DBZ Attack of the Saiyans PT-BR Coerencia.nds`
(SHA256 `130b4ad8…a9edd`, confere com o RELATORIO_COERENCIA.md). Referência: rc.1 de `01_ROM` (SHA256 `41412a47…3a5f`, confere).

## 1. Meio de teste: sem janela visível e sem roubar o foco

Neste PC não há core libretro de DS para Windows. O RetroArch só tem os `.info` do melonDS/DeSmuME, e o harness `11_Projeto_Recuperado/scripts/ds.py` usa um `.so` de Linux que roda num sandbox que não existe aqui. `09_Save_Atalho` contém só as dependências do gerador de NSP, e `07_Teste_Audio_PC` usa o melonDS com janela. Não baixei nada.

A solução usa o **melonDS 1.1 que já está no projeto**: copiei `07_Teste_Audio_PC\melonDS.exe` para esta pasta e o executei numa **área de trabalho oculta do Windows** (`CreateDesktop`/`CreateProcess` com `lpDesktop`):
- nenhuma janela aparece na área de trabalho do usuário e nada rouba o foco;
- a entrada vai por `PostMessage(WM_KEYDOWN/UP)` e por toque (`WM_LBUTTONDOWN`) direto na janela do emulador, sem teclas globais;
- a imagem vem de `PrintWindow`;
- o som está desligado: `melonDS.toml` próprio com `Volume = 0` e microfone desativado;
- Tab = acelerar, Q/W = L/R. ROMs e saves são cópias dentro de `04_teste`.

Arquivos: `ctl.py` (controle), `explorar.py`/`reconhecer.py` (andar, detectar batalha, fotografar os nomes dos alvos e lutar ou fugir), `mont.py` (painel de capturas), `preparar.sh` (nova instância), `rom_teste/liberar_mapas.py` (ROM de teste, ver item 2).

Limite: a captura é por tempo real, não quadro a quadro. Não usei save states.

## 2. Resultados por item

| # | Item | Resultado |
|---|------|-----------|
| 1 | Boot, avisos, título PT-BR, Novo jogo, prólogo (Shenlong), título do cap. 0, cena na Casa do Kame, mapa-mundi por toque, Ilha de Treino, 1ª batalha (roteirizada) | **PASSOU** |
| 2a | 1ª batalha (`c0002_01`): **"Lutador Errante B"** substitui a antiga Serva da Princesa. Sprite humano de quimono azul, paleta íntegra, ataques/vitória/itens/nível normais | **PASSOU** |
| 2b | Encontros aleatórios da ilha/caverna (cap. 0): Lutador Errante, Ex-Sargento RR, Saqueador, soldados de capacete (inimigos originais) | **PASSOU** (sem travas, cerca de 25 batalhas) |
| 2c | Monte Paozu (`pao01_00`, ROM de teste): **"Atirador da Montanha" / "Atirador da Montanha A"** (antigo Lobo), sozinho e misturado a Guarda/Soldado Coelho, Bandido e Raposa Ladra | **PASSOU** (17 batalhas, sem trava) |
| 2d | Deserto Diablo (`kou01_00`, ROM de teste): **"Lutador Errante"** e **"Recruta Renegado"** (antigo Tumble Bug), com sprites e nomes corretos | **PASSOU** (7 batalhas) |
| 2e | Robô de Patrulha, Piloto Renegado e as outras ~44 entradas | **NÃO TESTADO** (não sorteadas nas batalhas feitas) |
| 3 | Save do usuário (cópia de `09_Save_Atalho\savefiles-melonDS\…sav`) carregado: Ilha de Treinamento, nível 4/3/4, 0:25. Menus Grupo, Itens, Técnicas e Equipar abertos sem erro. Mapa-mundi conferido com o save novo | **PASSOU** |
| 3b | Os outros dois saves (`Downloads\…PT-BR.sav` e `save_atual_standalone`) só têm cabeçalho, sem jogo gravado | Observação |
| 4a | Abertura do Kuririn: cap. 0 até a caverna da ilha | **PASSOU parcial** (a caverna do gás não foi concluída; a floresta de bambu `bam01_00`, com Arruaceiro do Bambu e Discípulo Expulso, não foi alcançada) |
| 4b | Batalhas posteriores com o Nappa | **NÃO TESTADO** (nenhum save chega lá; exigiria a campanha inteira) |
| 5 | Comparação com a rc.1 | **NÃO FEITA**: nada pareceu errado. A instância `emu_rc1` ficou pronta |

Sobre a ROM de teste: `rom_teste/liberar_mapas.py`, a mesma técnica do `teste_atalho_mapas.py` do autor, gera a partir da ROM Coerência uma cópia com outros locais liberados no mapa-mundi. Só o `worldmap.sb` muda; os encontros são os da ROM testada. Liberar 8 locais de uma vez deixou a tela preta ao abrir o mapa. Com 2 locais (`kou01_00,pao01_00`) funcionou. Use poucos locais por vez.

## 3. Achados por gravidade

- **Crítico / alto:** nenhum. Em mais de 50 batalhas não houve trava, sprite corrompido, paleta errada nem nome cortado.
- **Médio:** nenhum confirmado.
- **Baixo:** a faixa de entrada do local diz "‑Ilha de Treino‑", enquanto o mapa-mundi e o save dizem "Ilha de Treinamento" (evidências 05 e 05b). Provavelmente vem da tradução anterior; não conferi na rc.1.
- **Observação de coerência:** "Atirador da Montanha" aparece no mesmo grupo dos soldados do Grupo do Coelho no Monte Paozu. É aceitável, mas lembra que os IDs compartilhados não diferenciam as fases.
- **Observação de jogo (não é bug):** o gás roxo da caverna mata o grupo sem a Máscara de Gás (botão R). Houve Derrota e o jogo voltou ao título. O save não foi afetado.

## 4. Evidências

Estão em `evidencias\`; o painel geral é `00_painel.png`. Destaques: 01 título, 02 prólogo, 03 cap. 0, 06/07 Lutador Errante B, 08 vitória, 10–14 save e menus, 18/19 Atirador da Montanha, 20/21 Lutador Errante e Recruta Renegado, 22/23 locais liberados. As capturas brutas, por rodada, estão em `capturas\`.

## 5. Como repetir este roteiro em outra ROM (ex.: `13_Correcoes_Revisao`)

Rodar no Git Bash a partir de `_revisao_claude\04_teste`. Tudo fica nesta pasta; o original não é tocado.

```sh
cd /c/Projetos/09_Dragon_Ball_Z_Attack_of_the_Saiyans/_revisao_claude/04_teste
# 1) instância nova com a ROM corrigida (+ opcional: save de partida, sempre CÓPIA)
bash preparar.sh corr "../../13_Correcoes_Revisao/<ROM>.nds" emu_coer/coer.sav
# 2) iniciar na área de trabalho oculta (deixar em segundo plano)
python ctl.py start corr emu_corr emu_corr/corr.nds &
# 3) comandos básicos
python ctl.py shot corr capturas/x.png             # captura (384x576, as 2 telas)
python ctl.py seq  corr "a:100:1500 down:800:300 s:nome t:258:398 d:ff u:ff w:1000"
#    a/b/x/y/start/select/up/down/left/right/l/r: tecla:ms_segura:ms_depois
#    s:nome = captura em capturas/nome.png | t:x:y = toque (coords da captura)
#    d:ff / u:ff = segura/solta acelerar | w:ms = espera
# 4) andar no campo registrando batalhas (fotografa o nome de cada alvo; foge, ou "lutar")
python -u reconhecer.py corr pref 40 "up:1500 left:1500 down:1500 right:1500"
python -u explorar.py   corr pref 40 "right:900 left:900"   # luta tudo e distribui nível
python ctl.py kill corr
```

Roteiro usado:
1. Novo jogo. No título, `start` três vezes e `a`; avançar o texto com `d:ff` e `a` repetido.
2. Na Casa do Kame, falar com o Mestre Kame (`up` + `a`) e sair pela porta (`left+down`).
3. Do lado de fora, `right` e `down` levam ao mapa-mundi. Tocar duas vezes na ilha ao sul (`t:262:402`, com a visão do mapa da evidência 24).
4. Andar na ilha até a batalha roteirizada (Lutador Errante B).
5. O ponto "C" da Casa do Kame salva (`a`, `up`, `a`).
6. Para mapas avançados: `python rom_teste/liberar_mapas.py emu_corr/corr.nds emu_map/coer_mapas.nds kou01_00,pao01_00`, carregar um save de Casa do Kame e tocar no ícone novo do mapa.

Para comparar com a rc.1, a instância `emu_rc1` já está pronta: `python ctl.py start rc1 emu_rc1 emu_rc1/rc1.nds &`.

Cuidados:
- `reconhecer.py`/`explorar.py` decidem pelas cores do painel (batalha = azul em (15,330); roda de comandos em (15,470); "Atacar" selecionado = laranja em (170,462)).
- Para fugir, a roda vai em Atacar e depois `right` duas vezes.
- Prompts Sim/Não precisam de cerca de 1,5 s antes de `up`.
- Duas instâncias ao mesmo tempo funcionam. Encerre-as com `kill`, porque o `start` em segundo plano mantém a área oculta viva.

## 6. O que fica pendente

Falta conferir:
- floresta de bambu (`bam01_00`, Arruaceiro do Bambu e Discípulo Expulso), que pede concluir a caverna da ilha (Máscara de Gás com R) e seguir para o cap. 1;
- encontros de Paozu com Robô de Patrulha e Piloto Renegado;
- caverna dos piratas, Enma e mapas do Nappa (`nap01_00` não abriu junto com os outros 8; tente sozinho);
- batalhas com o Nappa, que exigem a campanha ou um save avançado.
