# Textos em imagem (PT-BR)

## Formatos decifrados

Rotinas lidas no ARM9 com o `capstone`, que foi inspecionado e roda só no contêiner via PYTHONPATH, sem instalação:
- **0x0200a85c**: lê o cabeçalho.
- **0x0200a6c0**: descomprime.

| Formato | Uso | Layout |
|---|---|---|
| `dIMG` | atlas de textura dos menus (`menu/icon/*.img`) | 8 B de cabeçalho + paleta + pixels **4bpp lineares, 256 px de largura (128 B/linha)** |
| `dIMP` | fundos de tela cheia (`menu/bg`, `etc`) | 8 B + paleta 256 cores + pixels **8bpp comprimidos** |
| `dMAP` | cartões de título (`fld/map/CNN/CNN_9999us.map`) | 16 B (u32 em 0x08 = fim dos dados comprimidos) + paleta 256 + pixels 8bpp comprimidos + cauda de 384 B |
| `dCHR` | folhas de sprite | já documentado (tiles 4bpp) |

**Cabeçalho `dIMG`/`dIMP`:**
- Byte 4: escala (0 → largura = [6]×2 e altura = [7]×2; 1 → ×8).
- Byte 5: tipo de paleta, que indexa (256, 32, 4, 16, 256, 0, 8, 0).

**Compressão (LZ próprio).** A tabela tem 256 distâncias. As 32 primeiras vêm de uma lista fixa. As demais são `b[i>>5]*largura + c[i&31]`, com 14 trocas. Códigos:
- `00-0F`: literais.
- `10 n`: repete o último byte.
- `20-7F`: cópia curta.
- `8X i`: cópia longa + literais.

Reimplementado em `scripts/imp.py` (leitura) e `scripts/imp_comprimir.py` (compressor guloso, ida e volta conferida).

## O que foi traduzido

**Títulos dos 17 capítulos** (`scripts/titulos.py`):
- O fundo limpo sai de `titulo_fundo.py`. Por pixel, usa a cor das versões de idioma (jp, en, fr, gr, it, sp, us) que não têm letreiro ali. Letreiro é branco ou preto não compartilhado por 6 das 7 versões. O resto é preenchido pelos vizinhos.
- O texto novo usa DejaVu Sans Bold condensada a 82%, branco com contorno preto, nas mesmas alturas das linhas originais.
- A imagem volta a ter 256 cores e é recomprimida.

**Rótulos do menu** (`scripts/rotulos.py`). O script procura o padrão exato de pixels e troca só nos arquivos que a versão US carrega:
- MAIN MENU → **MENU**, com as letras do próprio jogo (`menu_us.img`).
- MEMBER → **GRUPO**. R e U são do jogo; G, O e P foram desenhados no mesmo estilo (`menu_sp_us.chr`, `sp_cloth_us.a`).
- HELP → **DICAS**, na fonte miúda de 5 linhas numa caixa de 19 px. "AJUDA" precisaria de 21 px. Está em 6 atlas (`bbg_us`, `sbg_us`, `dbg`, `ubg`, `shop`, `soubi_bg`), em 3 variantes de cor.

**Aplicação:** `scripts/imagens.py <rom> <saida>` (rótulos + títulos).

**Conferido no emulador:** cartão do prólogo em PT e menu com "GRUPO"/"MENU" (`notes/menu_ptbr.png`). O "DICAS" das telas de batalha e status não foi visto no jogo, só nos atlas.

## Como achar a origem de um gráfico

`scripts/quem_na_vram.py <estado.bin>` procura os tiles de cada arquivo gráfico da ROM na seção GPU do save state. Foi assim que o menu apontou para `menu_us.img` (textura) e `menu_sp_us.chr`.

## Segunda leva (26/09)

- `scripts/rotulos2.py`:
  - RESERVE → **RESERVA**; ATTACKER → **ATACANTE** (fonte miúda em caixa, 4x5); FILE → **JOGO**.
  - ITEMS ACQUIRED → **ITENS OBTIDOS**; BATTLE RESULTS → **RESULTADO**; BONUS POINTS!! → **PONTOS EXTRAS!!**.
  - LEVEL UP! (grande e pequeno) → **NÍVEL +1!**.
  - Continue → **Continuar**; New Game → **Novo Jogo** (normal e realçado).
  - Os letreiros grandes usam fonte vetorial encaixada na caixa. O contorno (1 ou 2 camadas) e a cor de cada linha são lidos do original.
- `scripts/rotulos3.py`: siglas dos ícones de atributo Pw Df Rc Tc Sp Lk → **Po De Cu Té Ve So** (em `menu_sp_us`, `rsp_us` e `sp_cloth_us.a`). Os ícones são 16x16 (não 15).
- `scripts/faixas_batalha.py`: faixas de fim de batalha **Vitória!!**, **Derrota**, **Fuga!**.
  - Ficam em `etc/pe.zea` (pacote `azEF`). Entradas de 16 B: id, ESD, EVD (offset|tamanho<<24, em unidades de 0x100) e tamanho descomprimido. O EVD é LZ10.
  - As entradas US são 0xFA065/066, 0xFA06F/070 e 0xFA079/07A. O id = 0xFA000 + 100×idioma + tipo.
  - A tira do texto é textura **A3I5 128x32** em 0x802C do EVD e se repete na horizontal. O script desenrola, redesenha (itálico) e enrola de volta.
  - Achado pela VRAM: a textura estava na RAM junto a um cabeçalho "EVD". Nenhum arquivo solto tinha esses bytes, porque a busca antiga olhava só a seção GPU do save state; a cópia de trabalho fica na RAM principal.
- Os formatos de textura seguem o DS. O byte 5 do cabeçalho `dIMG`/`dIMP` é o formato: 1 = A3I5 (32 cores + alfa de 3 bits), 2 = 4 cores, 3 = 16 cores, 4 = 256 cores, 6 = A5I3. Os atlas de menu são 4bpp.
- Tudo entra por `scripts/imagens.py`.
- Conferido no emulador: tela de título, "Vitória!!", RESULTADO, ITENS OBTIDOS (`notes/imagens_leva2.png`).
- **ATACANTE / RESERVA / JOGO** conferidos no emulador em 26/09 (`notes/menu_emulador.png`):
  - ATACANTE e RESERVA ficam na tela Menu > **Trocar** (formação de luta). Estado `saida/menu3/estado.bin` (menu aberto em Opções) + `down a`.
  - JOGO é a etiqueta miúda (16x6) do arquivo na tela **Salvar**. Só se chega nela por um **CC Point**; o da ilha do Kame fica logo à direita de onde o jogo carrega.
  - Para os textos da tela saírem em PT, o estado precisa ter carregado o jogo pela tela de título com a ROM PT. Estados antigos (ex.: `ur11/s22`) trazem as tabelas em inglês na RAM. Usei `derrota_estado.py` (agora grava `estado_fim.bin` depois de voltar ao campo) + `right@20 a a`.
  - Parei na pergunta "Sobrescrever arquivo?" sem confirmar.
- Com isso, todos os textos em imagem traduzidos já foram vistos no jogo.
- **NÍVEL +1!** (grande e pequeno), **PONTOS EXTRAS!** e as siglas **Po De Cu Té Ve So** conferidos no emulador em 26/09 (`notes/nivel_emulador.png`).
  - Feito com `scripts/diag_nivel.py`: ROM de teste em que o inimigo da batalha gravada (linha 104) dá 3000 de EXP. O grupo sobe do nível 1 ao 5; a ROM de teste é apagada no fim.
  - O teste achou o botão Y "Tentar de Novo" cortado na borda; virou "Refazer" (ver `notes/traducao.md`).
- **Fuga!** e **Derrota** conferidos no emulador em 26/09 (`notes/faixas_emulador.png`):
  - Fuga: `scripts/batalha_teste.py` com `right right a` para cada um dos 3 personagens. "Fugir" fica 2 casas à direita de "Atacar" na roda, e a fuga deu certo no 1º turno.
  - Derrota: `scripts/derrota_estado.py`. O estado é salvo dentro da batalha (`batalha_fim.py` com `SALVA_EM=12 PARA=1`) e o HP dos 3 é zerado.
    - No save state do melonDS, os registros de batalha do grupo ficam a cada 0x24C a partir de 0xcde08 (u32: HP atual, HP mostrado, HP máximo, 0, KI...).
    - Os registros em 0x10293fe/0x1029bfe são a cópia de campo; mexer neles não afeta a batalha.
  - Não funcionou: HP 1 (o grupo regenera ~10 por turno e esse inimigo quase não acerta) e inimigo com atributos de chefe (copiar os ataques da linha 7 fez o inimigo nunca acertar). `scripts/diag_derrota.py` guarda essa tentativa (ROM de teste apagada no fim).
  - Depois da faixa, a derrota volta à tela de título (fluxo normal de game over).

## Ainda em inglês (imagem)

## Faixas de nome de local ("~West City~"): traduzidas em 28/09

Script: `scripts/faixas_locais.py`, que entra em `imagens.py`. Fonte: `scripts/fonte_faixa.py`. Imagem: `notes/faixas_locais_emulador.png`.

**Onde ficam.**
- É imagem, não texto: trocar "West City" na RAM não muda a faixa. A tabela `cf_mes_LOC`, que alimenta o rótulo do mapa-mundi, não é usada.
- Arquivos `ef/esd/ceNNN_5L0.evd` (textura) + `.esd` (parâmetros). São 39 locais completos (`ce802`–`ce846`).
- L = 0 JP, 1 US (é o que o jogo carrega), 2 EN, 3 FR, 4 GR, 5 IT, 6 SP. Troquei US e EN.

**Formato do .evd** (LZ10; descomprimido, offsets = 0x2C + campo do cabeçalho):
- Paleta: u32 em 0x20.
- Textura A3I5 64×16 em 0x22C: alfa = v>>5, cor = v&31. A paleta vai do azul-marinho (0) ao branco (31).
- `ce808`, `ce830` e `ce843` têm textura 32×16.
- Na tela, 1 texel = 2 px na horizontal.

**Como o jogo posiciona.**
- O texto fica **centrado no texel 0** e dá a volta na borda (x0 + largura/2 ≈ 64 em todos).
- O `.esd` tem a largura do texto em u32 20.12 em 0x20 e 0x4C. As duas diferem de 1 porque a faixa é desenhada **duas vezes**, uma cópia deslocada.
- O u16 em 0xA6 cresce com a largura.
- O script soma a diferença de largura nesses campos e escala o 0xA6.

**Contorno.**
- O contorno do original é **semitransparente** (alfa 2, índice 4); com contorno opaco, uma cópia apaga a outra e as letras viram listras.
- O miolo é degradê opaco (índices 31→25). O estilo lido por frequência (`rotulos2.estilo`) punha tom escuro no topo das letras.

**Fonte.**
- Vetorial espremida ficou ilegível. Usei fonte pixelada própria: maiúsculas com 9 linhas, altura-x de 6, letras de 3 texels, *kerning* automático e "~" de 3 texels.

**Textos.** Em ordem de preferência: nome inteiro com "~", nome inteiro sem "~", nome curto.
- Encurtados:
  - "Templo Marcial"
  - "Via da Serpente"
  - "Caverna Pirata"
  - "Planeta do Kaioh"
  - "Terra de Karin"
  - "Ilha de Treino"
  - "Palácio do Enma"
  - "Mt. 5 Elementos"
  - "Palácio da Vovó"
  - "Casa da Princesa"
- "Bump Forest" = "Floresta de Bambu", como já estava no `ptbr.json`.

**Conferido no emulador.** "~Cidade do Oeste~" em Cidade do Oeste, com a ROM final. As outras só na prévia: mesmo código e mesmo formato.

**Correção de 28/09 (esgoto).**
- Nas texturas de 32 texels (`ce808` Esgoto, `ce830` Deserto, `ce843` Inferno) o texto do original fica centrado no **texel 16**, não no 0. Centrado no 0, "Esgoto" saía partido na tela ("oto  Esg").
- Agora o texto novo usa o mesmo centro do original (x0 + largura/2). Isso também moveu 1 texel 20 faixas de 64, que agora batem exatamente com o centro original.
- Conferido no emulador (`notes/esgoto_emulador.png`): "~Sewers~" → "Esgoto", e Cidade do Oeste continua certa.
- Como chegar ao esgoto: ROM de teste `scripts/teste_atalho_esgoto.py`. Ela troca "wst01_00" por "ges01_00" no `worldmap.sb` (o ícone da Cidade do Oeste leva ao esgoto).
  - O mapa-mundi precisa ser aberto de novo depois de carregar a ROM, porque os pontos de clique ficam na RAM.
  - Rota: `exp27` → `down@20x3:2 nadax6:60`, 10× `left@30:20`, 2× `down@30:20`, 3× `up@30:20`, 2× `right@30:20`, 2× `up@30:30`, e tocar 191,140 duas vezes.
- Patch refeito: ROM resultante SHA-256 `07fb3bdb29cb2500e539e46dccd6d7b213903678849c5dd835e5944a49d086f3`.

Depois da segunda leva, continuam de propósito:
- **NEXT, HP, LV, AP, KI, EXP**: abreviações de RPG, fonte de traço duplo sem espaço para acento em "PRÓX".
- **ALL**: caixa de 16 px; "TODOS" ou "TUDO" não cabem.
- **MISS / TOTAL**: letras avulsas (`dmgnum.chr`) combinadas pelo código.
- **Sparking!**: nome de sistema, igual ao "Sparking Combo" nos menus.
- **Logo "Attack of the Saiyans"** e **CAPSULE** (marca).
- **Tela de licença** "Licensed by Nintendo" e o texto legal em inglês.

Lista antiga (antes da segunda leva):

- `menu_us.img`: RESERVE, ATTACKER, FILE, NEXT, "HP LV AP", "KI EXP".
- `titlesp_us.chr`: New Game, Continue.
- `menu_sp_us.chr`: ALL e os ícones Pw Df Re Tc Sp Lk.
- `rsp_us.chr`: LEVEL UP!.
- `bsp.chr`: Sparking!.
- `bbg_us`/`rbg_us`: ITEMS ACQUIRED, BATTLE RESULTS, BONUS POINTS!!.
- Logo "Attack of the Saiyans" (`etc/title_us.imp`).
- CAPSULE (marca, fica).

~~Pendência pequena: pontinhos do letreiro antigo nos títulos C07 e C00~~: resolvido em 29/09 (`LIMPA_SOBRAS` e `limpar_sobras()` em `scripts/titulos.py`).
- Causa: nas áreas do letreiro US antigo que o texto novo não cobre, às vezes só 1 versão de idioma estava "livre". A borda cinza antisserrilhada do letreiro dela passava como fundo: manchas cinza e um traço preto no C07. No C00, as 7 versões têm texto na faixa da 2ª linha, e a difusão vizinho-a-vizinho fazia riscos verticais.
- Correção: nessas áreas, a cor só vale se ≥ 2 versões concordam exatamente. O resto é interpolado (1/distância) do fundo confiável mais próximo nas 4 direções.
- Aplicado só aos capítulos 0 e 7; os outros 15 títulos não mudam.
