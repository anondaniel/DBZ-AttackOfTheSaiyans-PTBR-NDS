# Hack 1 — os lobos viram Saibamen

ROM: `patches/aots_lobos_saibaman.nds`
SHA-256 `6d55989987ee65a0c040c828a460ac5ea727cc72a37745517a2b9bb4acd42a45`
Script: `scripts/lobos_saibaman.py` (parte da ROM original, `rom/aots.nds`)

## O que muda

Tabela `enemy_param`, linhas 104–106, nos 6 idiomas do `bdat.bin`:

| Linha | Antes | Depois | Paleta | Nv / HP / EXP (mantidos) |
|---|---|---|---:|---|
| 104 | Wolf | Saibaman | 0 (verde) | 8 / 70 / 96 |
| 105 | White Wolf | J. Sai | 1 | 15 / 300 / 330 |
| 106 | Red Wolf | C. Sai | 2 | 48 / 1200 / 960 |

- **Desenho**: `file` `ene039_01` → `ene001_01`, e `size`, `shadow`, `atk1-4`
  copiados do Saibaman da mesma paleta. Os `atk1-4` são **pesos** de
  escolha de ataque (somam 100), não IDs de golpe.
- **Nome**: `name_id` passa a apontar para o nome do Saibaman da mesma
  paleta. Nenhuma string foi reescrita.
- **Balanceamento**: nível, HP, força, EXP, zeni, drops e resistências
  continuam os do lobo. O Wolf nv 8 continua sendo um inimigo de nv 8,
  agora com cara de Saibaman.

São 25 bytes alterados por idioma. O script confere que todos caem nas 3
linhas de lobo (ou na string `file` delas) e que, fora dos `bdat.bin`, a
ROM só difere no CRC do cabeçalho.

## Como foi testado (melonDS, na sandbox)

Descoberta que viabilizou o teste: **o jogo relê o `bdat.bin` do cartucho
a cada batalha**. Por isso o mesmo save state (logo antes da 1ª luta, na
Training Island) pode ser carregado em ROMs diferentes, e a comparação
fica limpa.

Todas as capturas vêm do mesmo save state (`saida/comparativo_lobos.png`):

1. **ROM original**: 2× Giant Snake, desenhadas como cobras.
2. **ROM de sonda** (todas as linhas → Saibaman): as Giant Snakes aparecem
   como Saibamen, animam e atacam normal. Isso prova o mecanismo.
3. **ROM dos lobos**: as Giant Snakes **continuam cobras**. A mudança não
   vazou para outras linhas.
4. **ROM de diagnóstico** (a linha 104 já hackeada copiada sobre a linha
   da Giant Snake): aparece **"Saibaman A"**, com o sprite verde. A luta
   vai até o fim, e o EXP ganho bate com o do lobo: Yamcha recebeu 64 =
   2 × 96 ÷ 3. Isso prova que nome, sprite e stats vêm da linha do lobo.

5. **Ao vivo no Monte Paozu** (25/09): encontro aleatório gerado pelo
   próprio jogo, no mapa onde os lobos vivem. Mesmo save state e mesmo
   passo nas duas ROMs: na original aparecem **"Wolf A/B"** (2 lobos
   cinza), na do hack **"Saibaman A/B"** (2 Saibamen). Captura em
   `saida/lobos_ao_vivo_paozu.png`. Em 8 batalhas exploradas lá, 4 foram
   de "lobo", e todas vieram como Saibaman. Os outros inimigos do mapa
   (bandidos-raposa, urso, monges) continuaram normais.

### Como cheguei ao Monte Paozu

Os encontros ficam nos scripts de mapa (`script/<idioma>/cf0/<área>/*.sb`),
em chamadas `SetEnemyParty(grupo, formação, tipos…, slots…)` com o
ID do inimigo **1-based** (linha + 1). Decodificador:
`scripts/grupos_inimigos.py`. Onde cada lobo aparece:

- Wolf (105): Monte Paozu `pao01-03/05-08`, Break Wasteland `kou01-09`
- White Wolf (106): Mt. Frappe `fur02-04`, Holly Plain `hii01-04`, `gyu`, `enm`
- Red Wolf (107): Paprika Wasteland `nap01-03`, `pao05-08`

O Monte Paozu só abre no mapa-mundi no capítulo 2. Em vez de jogar a
história toda, usei uma **ROM de teste** (`patches/teste_atalho_paozu.nds`,
não é entrega). Nela o `worldmap.sb` tem um salto neutralizado:
`GetMaxFlag ≥ 110; jz +0x48` → `jz +0`, então o ícone do Monte Paozu
aparece com as coordenadas de entrada dele mesmo. Depois de entrar no
mapa, toda a exploração e as batalhas rodaram na **ROM entregue**.

Primeira tentativa errada: trocar a string `tut01_00` → `pao01_00`
levou ao mapa certo, mas com as coordenadas de entrada da Training
Island, e o personagem nasceu travado.

## Ferramentas criadas nesta etapa

- `ds.py`: toque na tela de baixo (`toca(x, y)`) e cores corrigidas
  (a captura saía com R/B trocados).
- `explorar.py`: tokens `BOTAO@N` (segura N quadros, para andar),
  `tX,Y` (toque) e `CADA=N` (captura a cada N passos).
- `cacar_batalha.py`: anda até a tela de baixo deixar de ser a do campo.
- `montagem.py`, `montar_b.sh`, `comparativo.py`: grades de capturas.
- `piloto.py` / `explorador.py`: andam sozinhos e resolvem batalha,
  diálogo e level-up (distribui os pontos e confirma o "Yes"). O
  explorador para no mapa-mundi ou após N batalhas e guarda o estado de
  antes de cada batalha.
- `ab_batalha.py`: refaz o passo exato que disparou uma batalha (semente
  fixa) em várias ROMs, para comparação A/B.
- `grupos_inimigos.py`, `disasm_sb.py`, `sb_tabelas.py`: leitura dos
  scripts `.sb` (imports, strings, bytecode).

Caminho até a 1ª luta: sala → escada → falar com a Launch → cena do
Mestre Kame → sair pela frente → tartaruga (tutorial) → descer para o
mapa-múndi → tocar em "Training Island" → andar um pouco.
Save states em `saida/`: `exp31/estado.bin` = chegada na Training Island,
`bat1/estado.bin` = logo antes da 1ª luta.
