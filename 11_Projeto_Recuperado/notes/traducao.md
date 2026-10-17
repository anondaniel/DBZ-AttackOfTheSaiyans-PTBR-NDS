# Tradução PT-BR: processo e andamento

## Tamanho

~5.800 textos únicos, ~55 mil palavras (diálogos ~48 mil). Por capítulo,
em lotes. Glossário: `notes/glossario.md` (dublagem brasileira, aprovado).

## Processo (scripts em `scripts/`)

1. `extrair_textos.py`: tira os textos exibíveis da pasta **US** (a que o
   jogo lê), separando identificadores internos.
2. `lote.py N <regex>`: monta o lote (textos únicos, sem japonês nem
   depuração) → `traducao/loteN.txt/json`.
3. A tradução vai em `traducao/loteN_pt.json`.
4. `aplicar_traducao.py validar`: exige as mesmas marcações (`<p> <k> <n>
   <c=#..> <w=..> <d> <t>…`, `%d/%s`, `\24P3`, `@37`) na mesma quantidade,
   só caracteres Latin-1 e nenhum espaço duplo; acumula em
   `traducao/ptbr.json` (original → tradução).
5. `aplicar_traducao.py rom`: aplica em todos os scripts US e EN,
   casando pelo texto original.
6. `planilha_lote.py N`: planilha de revisão (CSV `;` com BOM, abre no
   Excel). "Quem fala" vem do código (`Msg(nome, fala)`), não de palpite.
7. Patch: `bps.py criar` + validação com o `python-bps`.

## Cuidado verificado: nomes curtos como identificador

Textos como "Turtle" ou "Krillin" aparecem como etiqueta de quem fala
(`Msg`). O risco era o mesmo texto servir de identificador para outra
função. `uso_strings.py` mostrou que todos vão para `Msg`, `Select`,
`SetClickPoint` ou `Box`. Os poucos "suspeitos" eram bytes de operando
de outra instrução (falso positivo da busca por padrão). Confirmado
jogando: a cena do exame do Mestre Kame rodou inteira em PT-BR.

## Lote 1: Prólogo + Capítulo 1 + Casa do Kame + Ilha de Treinamento + mapa-múndi

- 358 textos únicos, ~3.950 palavras → 3.621 ocorrências em 659 scripts
- (patch próprio substituído pelo `aots_ptbr.bps`, que inclui os lotes 1 e 2)
- Planilha: `traducao/revisao_lote1.csv`
- Testado no jogo: abertura, Lunch acordando o grupo, exame do Mestre Kame
  (21 caixas), tutorial da Ilha de Treinamento.
  Atenção: save state de **antes** da cena começar. Um estado salvo no
  meio da cena já tem o script em inglês na memória.

## Lote 2: menus, itens, golpes, mensagens de batalha, lojas, objetivos, nomes

- 1.368 textos únicos (todas as tabelas de texto) → 1.380 células na pasta US
- **Largura medida em pixels** (`scripts/largura.py`), com a largura real de
  cada letra das duas fontes. Limite de cada grupo = a maior linha original
  do grupo (nome de item, descrição, barra de batalha…). O grupo de cada
  linha vem das próprias tabelas do jogo (`name_id`/`help_id`). 67
  textos foram encurtados (ex.: "Esfera 4 Estrelas", "Kimono Pesado").
  3 ficaram poucos pixels acima (nomes de inimigo com limite folgado).
- A aplicação nas tabelas usa o escritor BDAT (textos maiores, `conferir`
  exige que nenhuma outra célula mude).
- Nas **tabelas** vale qualquer tradução; nos **scripts** só as que vieram
  de script (palavra de menu como "Item" pode ser identificador lá).
- Testado no jogo: menu de campo (Itens, Técnicas, Equipar, descrições),
  roda de batalha ("Atacar"), tutorial de batalha ("Fugindo"), botões
  da tela de baixo (Pular, Seguir, Acel., Escolher, Ajuda das cápsulas).
- Patch atual: `patches/aots_ptbr.bps` (597 KB; lotes 1 e 2 + hack dos
  bichos). SHA-256 do resultado
  `321233115ae1a2489d3186996c2196fe3e3bc17ef96a39f5b76ebeee0459a096`
- Planilha: `traducao/revisao_lote2.csv`

## Lote 3: Capítulo 2 (Yamcha e o Coelho Monstro)

- 57 textos, ~690 palavras. Planilha: `traducao/revisao_lote3.csv`
- Testado no jogo pelas 4 cenas (`c0201_00`, `c0201_02`, `c0202_00`, `c0203_00`),
  abertas direto por uma ROM de teste (`scripts/teste_cena.py`: o ícone da
  Ilha de Treinamento passa a abrir a cena). 85 caixas conferidas.
- Trocadilho shabby/shaggy virou chiqueiro/cheiroso.
- **Bug achado e corrigido:** o nome de quem fala ("Monster Carrot") ficava
  em inglês, porque a tradução veio de uma tabela. Agora todo nome usado
  como falante (1º argumento de `Msg`) é traduzido nos scripts também.
- Patch: `patches/aots_ptbr.bps` (623 KB, lotes 1–3 + hack), SHA-256
  `230c86e1f1b81f23ac35aa8625a6e112bafa20c65b03794768821d85961e878a`

## Lote 4: Capítulos 3 e 4 (Tenshinhan e Mutaito; 23° Torneio, Goku x Piccolo Jr.)

- 310 textos, ~3.380 palavras. Planilha: `traducao/revisao_lote4.csv`
- 8 cenas conferidas no jogo (`c0301_00`, `c0302_02`, `c0303_01`, `c0401_00`,
  `c0401_03`, `c0401_04`, `c0402_02`, `c0402_04`), ~250 caixas.
- Patch: `patches/aots_ptbr.bps` (757 KB, lotes 1–4 + hack), SHA-256
  `d26575c42455dc5c127c71123582a001f9044e33c0d091e59544d8134d041db4`

## Lote 5: Capítulos 5 e 6 (casamento, Fornalha Mágica; Raditz e a morte do Goku)

- 629 textos, ~7.660 palavras. Planilha: `traducao/revisao_lote5.csv`
- 8 cenas conferidas no jogo (`c0501_02`, `c0503_01`, `c0505_00`, `c0603_00`,
  `c0604_00`, `c0607_00`, `c0608_01`, `c0609_00`), ~280 caixas.
- `conferir_identificadores.py`: OK (585 scripts).
- Patch: `patches/aots_ptbr.bps` (890 KB, lotes 1–5 + hack), SHA-256
  `14e3f42c4cb34b030956e228648d96605dbba756511aeb50f38d65834fc205c3`

## Lote 6: Capítulos 7 e 8 (Gohan no ermo; Kuririn e a Chichi, Lunch, Torre Karin)

- 475 textos, ~5.430 palavras. Planilha: `traducao/revisao_lote6.csv`
- A partir do cap. 8 as falas têm quebra de linha manual (`<n>`): o jogo
  não requebra essas linhas, então cada uma tem que caber na caixa.
  `largura.py` agora mede falas também (limite global das falas com `<n>`
  do jogo: 380 px na fonte pequena). Esse limite é frouxo; o das falas
  deste lote é 162 px e foi o usado (4 falas encurtadas).
- `scripts/juntar_lote.py N`: junta `loteN_pt_a/b/c.json` e confere cobertura.
- 8 cenas conferidas no jogo (`c0702_00`, `c0704_00`, `c0705_03`, `c0802_00`,
  `c0803_01`, `c0804_01`, `c0806_03`, `c0808_01`), ~280 caixas.
- Corrigido depois da planilha: "Yajiroba, né?" é fala do Kuririn (não da
  Bulma), então a resposta virou "seu bobo".
- `conferir_identificadores.py`: OK (611 scripts).
- Patch: `patches/aots_ptbr.bps` (997 KB, lotes 1–6 + hack), SHA-256
  `2e41e7561f74ba15f97d4692ad8d3e3621acf6a04962e3b05f36d6b5f76e778d`

## Lotes 7 a 10: Capítulos 9 a 16 (fim da história + créditos)

| Lote | Capítulos | Textos | Palavras |
|---|---|---|---|
| 7 | 9–10 (Estrada da Serpente, Kaioh; busca das Esferas, Pilaf) | 601 | ~5.880 |
| 8 | 11–13 (Gohan em Nemuria; Shen; Genki Dama, Goku revivido) | 283 | ~3.280 |
| 9 | 14 (Saiyajins chegam, Saibamen, Nappa) | 401 | ~3.950 |
| 10 | 15–16 (Vegeta, Oozaru, final, créditos) | 462 | ~4.450 |

- `scripts/largura_falas.py`: limite = linha mais larga das falas com `<n>`
  do próprio lote. Nenhuma fala passou.
- Correção no aplicador: tradução **igual** ao original (nomes como "Mez",
  "Suno", nomes nos créditos) não gera mais cópia/repontamento; antes o
  `conferir_identificadores` acusava 6 repontamentos inúteis em `hel04_00`.
- `conferir_identificadores.py`: OK (685 scripts, 16 repontamentos).
- Patch: `patches/aots_ptbr.bps` (1,35 MB, lotes 1–10 + hack), SHA-256
  `29e7a184cffcdb82dc3463f9434078cc623df914642f6c34373e1d38a4af90a2`
- **Toda a história (prólogo + capítulos 0 a 16) está traduzida.** Falta o
  texto dos NPCs e eventos de mapa (~8 mil palavras: `bud`, `wst`, `jin`,
  `skr`, `ura`, `est`, `gok`...).
- 16 cenas conferidas no jogo (2 por capítulo, do `c0901_01` ao final
  `c1606_00` com créditos), ~560 caixas. Tabela de missões alinhada para
  "Árvore do Enma".

## Lote 11: NPCs e eventos dos mapas

- 683 textos, ~8.600 palavras (vilas, Torneio, Cidade do Oeste, Torre Karin,
  Outro Mundo, placas e objetos). Planilha: `traducao/revisao_lote11.csv`
- Depois dele, `lote.py` não acha mais nenhum texto de script em inglês, e
  não sobra texto de tabela sem tradução.
- `conferir_identificadores.py`: OK (790 scripts).
- **Conferido no emulador em 28/09, andando na Cidade do Leste (`est01`)**
  (`notes/npcs_emulador.png`): 2 falas de NPC (casal na rua) e 2 textos de
  objeto (barraca, oficina), todos em PT.
  - Como chegar lá: ROM de teste com locais do mapa-mundi liberados
    (`scripts/teste_atalho_mapas.py <rom> <saida> est01_00,wst01_00`,
    apagada depois). Partindo de `saida/exp27/estado.bin` (ilha do Kame),
    andar para baixo abre o mapa-mundi, e dois toques no ícone entram na cidade.
  - Liberar `bam02_00`, `bud01_00` ou `jin01_00` junto deixa o mapa-mundi
    preto (um deles quebra o script). `est01` e `wst01` funcionam.
  - O save carregado pela tela de título (`derrota9/estado_fim.bin`) ainda
    não pode sair da ilha (flag da história), por isso usei o `exp27`. Ele
    tem as tabelas do `bdat` em inglês na RAM, e por isso "Obtained Skill
    Fruit!" sai em inglês. As falas vêm do script do mapa, lido da ROM ao
    entrar, e saem em PT.

## Imagens (títulos de capítulo, MENU, GRUPO, DICAS)

Ver `notes/imagens.md`. Patch final `patches/aots_ptbr.bps` (2,0 MB: texto
completo + imagens + hack), SHA-256 da ROM resultante
`41412a4727328d5341ba2f7d17fa567c84db137d8cd082bc32389c6d27643a5f`
(29/09: + 39 faixas de nome de local, com a correção do centro das faixas
de 32 texels, + "Tenshinhan" estreito no painel de batalha, + limpeza das
sobras nos títulos C00 e C07; patch de 2,11 MB, validado pelo aplicador
próprio e pelo
`python-bps`). Versão anterior (26/09, com
"Refazer"): `cce0c216726243af283092e2b99271efffb1909f81859f615ac978ecaa31028e`.

Correção de 26/09: o botão Y da tela de pontos extras ("Try Again", tabela
de dicas de botão do `bdat`) estava "Tentar de Novo" e saía cortado na
borda da tela. Virou **"Refazer"**, que cabe e diz o que o botão faz
(refazer a distribuição de pontos). Visto no emulador (`notes/nivel_emulador.png`).

## Problemas achados no lote 4 (corrigidos)

1. **º e ª não existem na fonte** (0xBA/0xAA são glifo de listras; também
   ¤¥¦§¬¯²³µ¶¸¹¼½¾Þþ). "23º" virou "23°", "1ª parada" virou "Primeira
   parada". O validador agora recusa esses caracteres.
2. **Nome de personagem também é identificador.** `Control("Chi-Chi", 2)` e
   `PcLock("Krillin")` usam o nome para achar o ator na cena. Traduzir a
   string quebraria a cena. Agora, quando o nome também serve de
   identificador, o original fica e a tradução entra como texto novo; só
   as falas (`Msg(nome, fala)`, padrão exato) apontam para ele. 16 falas
   repontadas. `scripts/conferir_identificadores.py` confere que todo
   identificador ficou intacto e que o código só mudou nesses 16 bytes.
   A cena da caverna (`PcLock("Krillin")`) roda até a luta.
3. **Primeira versão da checagem varria bytes crus** e achava "usos" no
   meio de operandos numéricos. Trocada por padrões exatos.
4. 20 nomes de falante que nenhum lote tinha isolado (Chichi, Senhor
   Kaioh, Senhor Enma, Cutelo…) foram adicionados (`scripts/correcoes.py`).

Observação de teste: cenas abertas a partir de save state feito com a ROM
original mostram botões/menus em inglês (as tabelas vêm do save). Em boot
novo aparecem em português.

## Pendências

- ~~Título de capítulo, MAIN MENU, MEMBER, HELP~~: feitos (ver
  `notes/imagens.md`; os títulos ficam em `fld/map/CNN/CNN_9999us.map`, não
  em `.ima`). Restam outros rótulos em imagem, listados lá.
- **Ícones do menu são imagem**,
  como o título de capítulo (e o nome no painel de batalha, que é fonte
  própria em maiúsculas estilizadas; os nomes aparecem certos lá).
- ~~"Tenshinhan" encosta no "LV" no painel de batalha~~: resolvido em 28/09
  (`scripts/tenshinhan_estreito.py`, `notes/tenshinhan_emulador.png`).
  - O painel usa a fonte **pequena** (`latin1.fnt`) com contorno e +1 px
    por letra, e centra o nome num ponto fixo. O nome ocupava 57 px.
  - Criei versões de 3 px de n, h, a, e (avanço 4) em códigos sem uso
    (0x81, 0x86, 0x87, 0x89, que eram o glifo de listras). No `latin0` esses
    códigos são cópias exatas das letras normais.
  - Só o "Tenshinhan" da `character_name` (US e EN) usa esses códigos.
    Ficou com 50 px, com folga antes do "LV".
  - Nome inteiro mantido. O menu GRUPO mostra o nome um pouco mais estreito,
    legível; diálogos não mudam (vêm dos scripts).
  - Para testar: save state antigo guarda fontes e tabelas na RAM. Para ver
    a mudança no menu, é preciso carregar o jogo pela tela de título
    (`derrota_estado.py` → `estado_fim.bin`).
- Itens "?" do glossário (Cutelo, Mestre Shen, Número 8, Punho do Lobo…)
  esperam confirmação.
- Cena da caverna com o Jackie Chun (`c0002_01`) e Capítulo 1 (Templo
  Orin, Paopao) ainda não foram jogados na versão traduzida.
