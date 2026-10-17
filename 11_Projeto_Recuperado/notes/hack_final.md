# Hack completo: bichos → universo DB (com nomes em PT-BR)

Patch: `patches/versoes-antigas/aots_bichos_db.bps` (68 KB, BPS; só o hack, sem tradução).
O patch de entrega é `patches/aots_ptbr.bps`, que já inclui este hack (ver `patches/COMO-APLICAR.md`).
ROM: `patches/aots_bichos_db.nds`
SHA-256 `4134c05e19683ab9fb879325654d24c744a86c8d5aa865382c53d78719ee20d6`
Montagem: `scripts/hack_final.py` (lê `scripts/plano_bichos.py`)
Checagem antes de montar: `scripts/verificar_plano.py`
Checagem no jogo: `scripts/diag_final.py`, folha em `saida/folha_contato_final.png`

## Regras

- Personagem com nome (chefe) não aparece em luta aleatória. Oozaru,
  Vegeta, Piccolo e Raditz ficam de fora; o Soldado Saiyajin é um sprite
  novo, derivado do Raditz, em arquivo próprio.
- O balanceamento é sempre o do bicho original (nível, HP, EXP, drops,
  resistências).
- Nomes com acento: as duas fontes do jogo têm o Latin-1 completo e o texto aceita (testado em batalha e em diálogo, ver `notes/fonte.md`).
  de que a fonte os tenha.
- Em um mesmo mapa, dois inimigos diferentes não podem ter a mesma cara ou
  o mesmo nome, contando os inimigos originais que continuam lá.
- Sprite grande (tamanho 2) só vai para bicho que sempre luta sozinho.

## Tabela

| Família | Vira | Nomes |
|---|---|---|
| Lobos | Saibaman (cores originais) | Saibaman · Saibaman Glacial · Saibaman Rubro |
| Ursos | Saibaman | Saibaman Faminto · Saibaman das Neves · Saibaman Feroz |
| Pandas | Saibaman | Saibaman do Bambu · Saibaman da Nevasca · Saibaman Supremo |
| Insetos | Saibaman, cores novas (areia/noite/veneno) | Saibaman Escavador · Saibaman Noturno · Saibaman Venenoso |
| Larvas | Saibaman, cores novas claras | Broto Escavador · Broto Noturno · Broto Venenoso |
| Avestruz/dodô | Soldado Saiyajin rosa/amarelo/preto | Batedor Saiyajin · Batedor do Deserto · Elite Saiyajin |
| Tigres | Soldado laranja/branco/roxo | Soldado Saiyajin · Soldado Glacial · Soldado Dimensional |
| Javalis | Soldado marrom/vermelho/gelo | Brutamontes Saiyajin · Brutamontes Campeão · Brutamontes Glacial |
| Cães | Soldado Red Ribbon (ene005) | Desertor Red Ribbon · Espião Red Ribbon · Sentinela Red Ribbon |
| Lagartas | Soldado Red Ribbon (ene006) | Recruta Red Ribbon · Recruta Incendiário · Recruta Veterano |
| Morcegos | Vampiro (Vovó Uranai) | Vampiro · Vampiro Sanguinário · Rei Vampiro |
| Caranguejos | Grupo do Coelho | Capanga · Capanga Gigante · Capanga Sombrio |
| Cobras | Servos da Princesa Serpente | Serva da Princesa · Guarda da Mansão · Serva Venenosa |
| Aves de rapina | Piloto Red Ribbon (ene003) | Aviador Red Ribbon · Aviador Azul RR · Aviador Sombrio RR |
| Peixes | Robô da Caverna dos Piratas | Robô Pirata · Robô Pirata Selvagem · Robô Pirata das Areias |
| Dragões | Robô Red Ribbon (ene004) | Robô Alado RR · Robô de Assalto RR · Robô Ártico RR |

## O que o verificador pegou

3 choques da primeira versão, cada um com o dono original do sprite no
mesmo mapa:
- Mansion Snake ficaria igual à Princess' Guard (mansão da Princesa Serpente)
- Spy Dog, igual ao Red Ribbon Survivor (Muscle Tower)
- Wild Fish, igual ao Skull Robot (caverna de Kai)

Resolvido trocando a paleta (2, 0 e 0). Resultado: 48 linhas × 183
mapas, sem problemas.

## O que muda no cartucho

- `ene001_01.chr`: 5 paletas originais + 6 novas (os Saibamen de verdade
  continuam iguais)
- `ene200_01.chr`: Soldado Saiyajin, com 9 paletas (arquivo de um inimigo
  cortado; nada no jogo o usava)
- `bdat.bin` dos 6 idiomas: 432 células conferidas por idioma
- Todo o resto do cartucho é idêntico ao original (o script confere
  arquivo por arquivo). O `ene220_01.chr` do chefe Raditz está intacto.

## Checagem no jogo

As 48 linhas passaram (`diag_final.py`): cada uma aparece com o sprite, a
cor e o nome certos numa batalha real. A folha revelou 3 nomes que não
batiam com a cor: o "Saibaman Rubro" usava a paleta 2 original, que é
**azul**, e os dois "da neve" usavam a paleta 4, **rosa**. Ganharam
paletas próprias (vermelha e azul-gelo; o Saibaman agora tem 13) e foram
retestados. As outras 45 capturas são da montagem anterior: a correção
só acrescentou paletas e mudou essas 3 linhas.

## Ajuste de nome

"Capanga Coelho" virou só "Capanga": o sprite do Grupo do Coelho (`ene016_01`) é um guerreiro de lança, sem cara de coelho. ROM remontada e linha retestada no jogo.

## Cauda do soldado (26/09)

A cauda enrolada na cintura (herdada do Raditz) era pintada com os tons de
pele (índices 9/A/B) e parecia barriga. `scripts/cauda_soldado.py` a deixa
marrom-escura (9→B, A→B, B→1): acha a faixa fina de pele com contorno
escuro em cima e embaixo, na altura da cintura, em 78 dos 98 quadros (os
outros são de costas/caído). 77 pixels de tile trocados; vale para as 9
cores. Roda no fim do `hack_final.py`. Antes/depois:
`notes/soldado_cauda_antes_depois.png`.

Novo SHA-256 da ROM do hack: `a296ac4687d96fe865de9aa2e01b5ee3fdeb4e973f38de6ad833a821da32365d`
(patch `aots_bichos_db.bps`, 68,9 KB). ROM completa PT-BR:
`53e311f402b52845a7516ddcb2824b58f4d2a9a85199dcaa637e1ebc80d686cd`.

## Pendências conhecidas


- A cor da variante pinta ombreiras, abas do quadril e detalhes das botas
  do soldado (é a mesma cor no desenho do Raditz).
- Tufo fino de cabelo em pé em 2 quadros de ataque do soldado.
- Urso/panda "ao vivo" no mapa próprio ainda não foi capturado. A
  checagem no jogo usa a batalha real do Monte Paozu com a linha copiada.
