# Estado recuperado — DBZ Attack of the Saiyans (NDS)

Auditoria em 11/10/2026.

## Localização e confirmação

O backup estava em `C:\Users\Administrador\Downloads\DBZ-DS_2026-10-01`.
O repositório foi restaurado do bundle Git para `../11_Projeto_Recuperado`.
Commit recuperado: `75116fc`, versão `1.0.0-rc.1`, de 29/09/2026.

A ROM copiada do Switch em `../10_Auditoria_Inimigos` e a ROM de `../01_ROM`
têm o mesmo SHA-256 da versão final documentada no backup:
`41412a4727328d5341ba2f7d17fa567c84db137d8cd082bc32389c6d27643a5f`.
Portanto a ROM atualmente usada no Switch inclui tradução e substituições de inimigos.

## Alterações recuperadas

- 48 entradas de inimigos substituídas, em 16 famílias.
- Lobos, ursos, pandas, insetos e larvas: variantes de Saibamen e brotos.
- Avestruzes/dodôs, tigres e javalis: variantes de soldados Saiyajins.
- Cães e lagartas: soldados Red Ribbon.
- Morcegos: vampiros; caranguejos: capangas do Grupo do Coelho.
- Cobras: servas da Princesa Serpente.
- Aves de rapina: aviadores Red Ribbon; peixes: robôs piratas; dragões: robôs Red Ribbon.
- Soldado Saiyajin em arquivo próprio, derivado de Raditz, com nove paletas e cauda escurecida.
- Segundo os registros, nível, HP, EXP, drops e resistências dos inimigos originais foram preservados.
- Tradução de textos, menus e elementos gráficos incluída no patch completo.

## Validação registrada, ainda não repetida nesta auditoria

As notas registram teste das 48 entradas em batalhas, correções de três paletas
e checagem de conflitos em 183 mapas. Isso não equivale a uma campanha completa.

## Pendências registradas

- Primeira jogada completa do início ao fim.
- Conferência de muitos NPCs, 36 das 39 faixas de local e títulos dos capítulos 0 e 7.
- Revisão dos nomes marcados com dúvida no glossário.
- Tufo de cabelo do soldado em dois quadros de ataque.
- Cor de variantes compartilhada entre ombreiras, abas da cintura e botas.
- Captura de ursos/pandas substituídos em seus mapas próprios.

## Referências locais

- `../11_Projeto_Recuperado/CHANGELOG.md`
- `../11_Projeto_Recuperado/notes/hack_final.md`
- `../11_Projeto_Recuperado/scripts/plano_bichos.py`
- Patch completo: `../11_Projeto_Recuperado/patches/aots_ptbr.bps`

Nenhuma ROM ou save do Switch foi alterado nesta auditoria.
