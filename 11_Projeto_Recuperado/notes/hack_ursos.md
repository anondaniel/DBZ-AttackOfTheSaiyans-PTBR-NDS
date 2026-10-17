# Hack 2: ursos e pandas também viram Saibamen

ROM: `patches/aots_bichos_saibaman.nds` (lobos + ursos + pandas)
SHA-256 `242dc672cacf94374bad918b2a6bc3a4c9fe5dbb099a33ec9ec88253e5da64fc`
Script: `scripts/hack_saibaman.py` (parte da ROM original e aplica a
tabela `TROCAS` inteira; os lobos saem idênticos à ROM validada antes)
Checagem de nomes por mapa: `scripts/conflitos.py`

## O que muda

| Linha | Antes | Depois | Nv / HP / EXP (mantidos) | Onde vive |
|---|---|---|---|---|
| 104 | Wolf | Saibaman | 8 / 70 / 96 | Monte Paozu, Break Wasteland |
| 105 | White Wolf | J. Sai | 15 / 300 / 330 | Mt. Frappe, Holly Plain |
| 106 | Red Wolf | C. Sai | 48 / 1200 / 960 | Paprika Wasteland, Paozu leste |
| 113 | Hungry Bear | Saibaman | 18 / 880 / 810 | Spinach Wastes |
| 114 | Snow Bear | T. Sai | 15 / 720 / 780 | Mt. Frappe |
| 115 | Strong Bear | K. Sai | 46 / 3050 / 3600 | Muscle Tower, Paozu leste |
| 116 | Dangerous Panda | Saibaman | 8 / 150 / 156 | Bamboo Forest |
| 117 | Snow Panda | T. Sai | 21 / 920 / 840 | Holly Plain, `gyu`, `enm` |
| 118 | Ultimate Pandaman | K. Sai | 43 / 3000 / 2700 | Pirate Cave |

Do modelo Saibaman vêm `file`, `palno`, `size`, `shadow`, `atk1-4` e
`name_id`. Do bicho fica todo o resto. São 76 bytes por idioma, todos
nas 9 linhas.

### Regra das variantes

O sprite do Saibaman tem só 5 paletas/nomes (Saibaman, J., C., K., T. Sai)
e são 9 bichos, então nomes repetem entre áreas. A regra é que **nenhum
mapa tenha dois inimigos diferentes com o mesmo nome**, contando também
os Saibamen de verdade (J./C./K./T. Sai aparecem em encontros aleatórios
em `ben`, `est`, `ges`, `las`, `nap`, `pao`, `snd` e cenas `c02`-`c15`).

`conflitos.py` lê os grupos de todos os scripts e confere isso. Resultado
da tabela atual: **sem conflitos**.

### Descoberta: o id 1 nos scripts é "vazio"

Nos `SetEnemyParty`, os tipos não usados vêm preenchidos com `1`, e a
formação 2 usa `1` no primeiro slot. O id 1 seria o Saibaman comum
(linha 0), mas ele **nunca** aparece como tipo de grupo em nenhum script.
Nos scripts, `1` é o marcador de vazio. A primeira versão do checador
tratou esse 1 como Saibaman e acusou conflito falso em Spinach Wastes.

## Como foi testado

`scripts/diag_bichos.py` usa uma batalha real do Monte Paozu (1 lobo,
save state `pz5/p0027_pre.bin`, refeita pelo `ab_batalha.py`) como palco.
Para cada bicho, copia a linha dele sobre a linha do Wolf: a linha
original na ROM original ("antes") e a linha hackeada na ROM do hack
("depois"). Captura em `saida/ursos_pandas_antes_depois.png`. Os 6 saem
com o sprite e o nome certos dos dois lados.

Tropeço: a primeira grade usou a batalha de **2** lobos. Ursos e pandas
são tamanho 2 (lobo é 1), e nessa formação o jogo pôs os dois bichos
fora da tela: a coluna "antes" saiu sem sprite, só com a etiqueta do
nome. Nos mapas deles, ursos e pandas sempre vêm sozinhos (formação 1).

Ao vivo no mapa próprio: Spinach Wastes foi alcançado pelo atalho de
teste, mas nas explorações só apareceu javali. Paozu leste ainda não
tem encontros nesse ponto da história. Um urso ao vivo ainda não foi
visto.

### Não é urso

O homem-urso de espada que aparece no Monte Paozu é o **"Bandit"**
(linha 26, `ene010_01`), um humanoide. Não foi mexido.
