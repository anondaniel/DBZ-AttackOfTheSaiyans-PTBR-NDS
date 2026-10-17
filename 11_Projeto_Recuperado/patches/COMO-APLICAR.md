# Como aplicar o patch

Arquivo: **`aots_ptbr.bps`** (2,11 MB, formato BPS). É o patch completo:
tradução PT-BR (história, NPCs, menus e textos em imagem) + troca de inimigos.

> `versoes-antigas/aots_bichos_db.bps` é o patch antigo, só com a troca de
> inimigos e sem tradução. Não aplique os dois: o `aots_ptbr.bps` já inclui tudo.

## ROM de origem (tem que ser exatamente esta)

- Dragon Ball Z - Attack of the Saiyans (USA) (En,Fr), código `BRPE`
- 134.217.728 bytes (128 MB)
- CRC32 `a9f0b8f9`
- SHA-1 `b5d8ebbc8813db68270ea02f0e581f6005f54736`

O BPS confere o CRC32 da origem. Se a ROM for outra (outra região, versão
"trimmed", já com outro patch), o aplicador recusa em vez de gerar um jogo
corrompido.

## Aplicando

- **No navegador:** Rom Patcher JS (de Marc Robledo). Escolha a ROM, depois
  o `aots_ptbr.bps`, e clique em "Apply patch".
- **No Windows:** Floating IPS (`flips.exe`) → "Apply Patch" → escolha o
  `aots_ptbr.bps` e depois a ROM.

Aplique sempre sobre uma **cópia** da ROM original.

## Resultado esperado

- 134.217.728 bytes (mesmo tamanho da original)
- CRC32 `670e3cf1`
- SHA-1 `74f536b0780857784eadb6d5e56b717ffbca49a0`
- SHA-256 `41412a4727328d5341ba2f7d17fa567c84db137d8cd082bc32389c6d27643a5f`

## Dica ao jogar

Comece um jogo novo ou carregue um save **pelo menu do jogo** ("Continuar").
Save states do emulador feitos com a ROM original guardam os textos antigos
na memória, e algumas telas aparecem em inglês até o jogo ser recarregado.

## Como o patch foi validado

1. Gerado por `scripts/bps.py`, com um aplicador próprio. A ROM
   reconstruída é idêntica (SHA-256).
2. Validado e aplicado também com o `python-bps` (Timothy Allen), uma
   implementação independente. O resultado também é idêntico.
