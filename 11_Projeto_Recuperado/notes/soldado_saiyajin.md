# Soldado Saiyajin (sprite novo a partir do Raditz)

Scripts: `montar_soldado_chr.py` (monta e instala), `cortar_juba.py`,
`soldado_paletas.py`, `chr_paletas.py`; teste: `teste_soldado.py`
Captura: `saida/soldado_final_zoom.png`, luta em `saida/teste_soldado2/luta/montagem.png`

## Formato .chr (dCHR), decodificado

- `0x00` "dCHR", `0x04` u8 = 2, `0x05` u8 **n_paletas**, `0x06` u16 **n_tiles**
- `0x08` paletas: n × 16 cores RGB555 (cor 0 transparente)
- tiles: n × 32 bytes (8×8, 4bpp, nibble baixo = pixel da esquerda)
- tabela de animações: `u16 n_anim, u16 0, u16 off[n]` (relativos a +4).
  Cada quadro começa em endereço **par** (um `00` de enchimento completa o
  anterior). Um quadro que começa com `00` marca o fim da animação.
  - curto: `n, ex`, n × `[s8 x, s8 y, tile_lo, attr]`. No attr: bits 7-6
    tamanho, 5 espelho vertical, 4 espelho horizontal, 3-2 formato,
    1-0 = bits altos do tile
  - longo: `10, ex, 00, n`, n × OAM de 6 bytes (attr0/attr1/attr2 do DS)
  - depois das peças: `k` + k registros de 3 bytes (tempo/efeitos, não usados)
- Validado: os 98 quadros do Raditz remontados fora do jogo (`render_quadros.py`)
  batem com o que aparece na batalha.

## O que foi feito

- **Arquivo próprio:** grava em `ene200_01.chr`, um inimigo cortado (robô/
  alienígena com animações). Nada no jogo aponta para ele: nenhuma tabela
  nem string no executável, só a tabela de nomes de arquivo. O
  `ene220_01.chr` do chefe Raditz não é tocado (o script confere).
- **Juba cortada** nos tiles. Em cada um dos 98 quadros, o cabelo (cores 1
  e 2) a mais de 12 px do rosto sai, ilhas soltas saem e a borda do corte
  ganha contorno. O pixel de tile usado por vários quadros é decidido pela
  maioria dos quadros; em empate, fica como estava. 7.944 pixels mudaram.
  11 quadros (a7 q12-22) não têm rosto e não votam.
- **3 paletas:** cabelo preto, macacão azul e cor da variante (rosa, amarelo,
  preto) nas cores douradas + lente do scouter.

## Observações

- O "dourado" do Raditz não é só a ombreira. É ombreira + abas do quadril +
  detalhe das botas, então os três ganham a cor da variante. Separar só a
  ombreira exige remapear pixels quadro a quadro.
- Em 2 quadros de ataque sobra um tufo fino em pé sobre a cabeça.
- Testado em batalha: o soldado anda, ataca, dá dano e a luta segue normal.
