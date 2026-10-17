# Teste jogável automatizado: ROM da etapa 13 (`13_Correcoes_Revisao`)

Data: 12/10/2026. Revisor: Claude (independente).

ROM testada: `13_Correcoes_Revisao\DBZ Attack of the Saiyans PT-BR.nds`, SHA256 `0616e6c6fdada1e5…bda3a82` (confere).

O método é o mesmo de `..\RELATORIO.md`: melonDS 1.1 do projeto numa área de trabalho oculta do Windows, entrada por mensagem direta à janela e captura por `PrintWindow`. Não houve teclas globais, foco roubado nem som, e nada foi baixado. Só usei cópias de ROM e de save, dentro de `04_teste`.

Usei dois tipos de ROM de teste, ambos derivados da ROM 13 e nunca entregues:
- `liberar_mapas.py`: abre locais no mapa-mundi.
- `forcar_grupos.py` (novo): reescreve os argumentos de `SetEnemyParty` de um mapa, com o mesmo tamanho de script, para forçar um inimigo nos encontros aleatórios.

Pontos de teste:
- Ilha de Treinamento (`tut01/02`), com o save do Switch;
- Deserto Break (`kou01_00`), com o save de jogo novo.

## Resultado por prioridade

| # | Item | Resultado |
|---|------|-----------|
| 1 | Boot, logos, título PT-BR, Novo jogo, prólogo, cap. 0, Casa do Kame (item, salvar), mapa-mundi e 1ª batalha (tutorial "Encontros"), com vitória e tela de RESULTADO | **PASSOU** |
| 2 | Cópia do save do Switch (`savefiles-melonDS`): "Carregar Dados", Ilha de Treinamento, nível 4/3/4, 0:25. Menus Grupo, Itens, Técnicas e Equipar abertos sem erro | **PASSOU** |
| 3 | Saibamen do cap. 14, com grupo forçado na ilha. Veja a nota sobre os IDs abaixo da tabela | **PASSOU parcial** |
| 3a | Ermo Páprica (`nap01_00`) liberado: o mapa abre, e houve um encontro aleatório com "Piloto Veterano". O evento de Saibaman do cap. 14 depende da história e não pôde ser acionado | Observação |
| 4 | Ex-lobo "Atirador da Montanha" (Deserto Break, natural): cerca de 60 turnos de Defender em várias lutas, mais lutas com Lutador Errante e Ladrão do Deserto. Nenhuma trava; nenhum reforço apareceu (a chance é de 20% por turno e ainda passa pelo sorteio de sucesso do golpe) | **PASSOU (sem trava)**; invocação **NÃO OBSERVADA** |
| 5 | Castelo do Pilaf: liberado, a cena com Yamcha roda e o castelo abre no campo. Não houve encontro na área externa; o portão está fechado sem a história | **NÃO TESTADO no próprio mapa** |
| 5b | Os mesmos inimigos forçados em outro mapa | **PASSOU parcial**: Robô Sentinela (robô roxo pequeno) e Capitão da Guarda (javali de armadura roxa e espada). Guarda do Castelo **NÃO CONFIRMADO** (o teste forçado travou, e trava igual na rc.1, ver achados) |
| 6 | Linhas 110/112, forçadas: "Brutamontes do Ermo" (azul) e "Brutamontes Glacial" (cinza/branco), com o sprite do Bandido e paletas distintas e corretas | **PASSOU** |
| 6b | Linha 149 "Ladrão do Deserto": apareceu natural no Deserto Break, com sprite de guarda de turbante azul e cimitarra. Lutei 30 turnos sem trava | **PASSOU** |
| 6c | Linha 150 "Xamã do Vulcão": o forçado não fez efeito (apareceu outro inimigo) | **NÃO TESTADO** |
| 7 | Faixa "‑Ilha de Treino‑" × "Ilha de Treinamento" | **Já vinha da rc.1** (detalhes abaixo da tabela) |

Nota sobre os IDs dos Saibamen. Nos encontros forçados, o ID 2 mostra **"Saibaman"** (verde, `ene001_01` paleta 0). Os demais aparecem assim:
- ID 3 = **J. Sai** (cinza);
- ID 4 = **C. Sai** (azul);
- ID 6 = **T. Sai** (rosa).

Os sprites e nomes estão corretos e são os do jogo original. O ID 5 (K. Sai) travou ao abrir a batalha forçada, mas trava **igual na rc.1** (veja achados).

Detalhes do item 7:
- Os 755 arquivos de faixa (`ef/esd/ce8xx`) são idênticos entre rc.1 e ROM 13.
- `11_Projeto_Recuperado/notes/imagens.md` lista "Ilha de Treino" entre os nomes encurtados de propósito, para caber na faixa.
- A rc.1 mostra "Ilha de Treinamento" no mapa-mundi. Não fotografei a faixa da rc.1 em jogo: o roteiro rápido caiu direto na caverna.

## Achados

- **Crítico / alto:** nenhum confirmado como regressão da etapa 13.
- **Médio (para investigar):** algumas batalhas forçadas travam em tela escura ao abrir. Ocorreu com os IDs 5 (K. Sai), 105 e 110 (Guarda do Castelo).
  - **As mesmas trocas na rc.1 travam igual:** ID 5 (2×), ID 105 (1 de 2), ID 110 no deserto (1×). O ID 2 travou 1 vez em 3 na ROM 13 e nenhuma na rc.1.
  - Portanto não é regressão da etapa 13. A causa provável é o método: forcei o inimigo onde o jogo original nunca o coloca, e isso pode estourar a memória de sprites ou de efeitos do mapa.
  - Não conclui sobre os mapas reais. Confirmar jogando com um save do cap. 14 ou do Castelo do Pilaf.
- **Observação (rótulo):** o RELATORIO da etapa 13 diz "ID 2 = J. Sai". No jogo, o ID 2 mostra "Saibaman", e J. Sai é o ID 3. O mapeamento ID→linha não é linear (para ID 15/83/111/113/119 vale linha = ID−1). Isso não afeta o jogo, porque as linhas 0–4 são iguais à rc.1 e ao original. Vale só corrigir a descrição.
- **Observação (artefato do teste):** na Ilha de Treinamento, com inimigos de corpo grande, o sprite às vezes não aparece (ex.: "Capitão da Guarda A" invisível em `27_artefato_tut_sprite_invisivel.png`). No Deserto Break o mesmo inimigo aparece normal (25). Atribuo à ROM de teste, não à ROM 13.
- **Baixo:** a faixa "Ilha de Treino" já vinha da rc.1 e foi encurtada por espaço.

## Evidências

Estão em `rom13\evidencias\`; o painel geral é `00_painel.png`. Destaques:

| Arquivos | Conteúdo |
|---|---|
| 01–07 | Boot até a 1ª batalha |
| 08–13 | Save do Switch e menus |
| 14–18 | Saibaman, J./C./T. Sai e a trava forçada do K. Sai |
| 19–21 | Encontros naturais: Piloto Veterano, Atirador da Montanha, Ladrão do Deserto |
| 22–26 | Linhas 110/112, Robô Sentinela, Capitão da Guarda e a trava do Guarda do Castelo |
| 28 | Castelo do Pilaf |
| 29 | Atirador defendendo, sem invocação |

As capturas brutas ficam em `..\capturas\` (prefixos `r13*`, `id*`, `rc1id*`, `k*`, `kou13*`, `inv*`, `f*`, `nap*`, `yun*`, `pc*`).

## Como repetir

Rodar no Git Bash a partir de `_revisao_claude\04_teste`.

1. Recopiar a ROM, apagada no fim deste teste:

   ```sh
   cp "../../13_Correcoes_Revisao/DBZ Attack of the Saiyans PT-BR.nds" rom13/emu_r13/r13.nds
   ```

2. Novo jogo: `python ctl.py start r13 rom13/emu_r13 rom13/emu_r13/r13.nds &`, depois o roteiro da seção 5 de `..\RELATORIO.md`.
3. Save do Switch:
   - copiar `saves_copias/copia_switch_savefiles_melonds.sav` para `rom13/emu_r13/r13.sav`;
   - iniciar;
   - `start` ×3, `a` ×2.
4. Inimigo forçado na Ilha de Treinamento: `bash testa_id.sh rom13/emu_r13/r13.nds <ID> <prefixo>`. Imprime `BATALHA OK` ou `TRAVOU` e fotografa os alvos.
5. Inimigo forçado no Deserto Break: `TURNOS=n bash testa_kou.sh <rom> <ID> <prefixo>`.
6. Local liberado: `bash troca_map.sh mapa1,mapa2` e tocar no ícone. Use 1–2 locais por vez, porque 8 deram tela preta.
7. Andar e registrar encontros: `SEM_A=1 python -u reconhecer.py r13m <prefixo> 40 "up:1500 left:1500 down:1500 right:1500"`.
8. Para comparar com a rc.1, passe `../../01_ROM/DBZ Attack of the Saiyans PT-BR.nds` como `<rom>`.

## Limpeza

Apaguei as minhas cópias de ROM: `coer.nds`, `coer_sav.nds`, `coer_mapas.nds`, `rc1.nds`, `r13.nds` e `r13map.nds`. Não há mais nenhum `.nds` em `04_teste`. Ficaram:
- as cópias do `melonDS.exe` (cerca de 43 MB cada) e os `.toml`;
- os saves de trabalho (`.sav` de 8 KB);
- as capturas.

O total é de cerca de 400 MB. Nada do projeto foi alterado, e o save original do Switch confere byte a byte com a cópia.
