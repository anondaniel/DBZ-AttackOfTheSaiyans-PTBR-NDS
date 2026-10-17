# Revisão independente: integridade e diferenças (etapa 12, "Coerência")

Revisão feita em 11 e 12/10/2026, somente leitura. Nada do projeto foi alterado. Os scripts e as saídas brutas estão em `work/`:
`hashes.py`, `meubps.py`, `testa_bps.py`, `nitro.py`, `diff_fs.py`, `dados.py`, `atk.py`, `bdat_raw.py`, `grupos.py`, `conflitos.py` e os arquivos `*.txt` e `*.json`.
O aplicador BPS e o parser NDS/NitroFS foram escritos do zero para esta revisão. Do projeto, reaproveitei só o leitor `bdat.py` e, como segundo aplicador, o `bps.py`.

## Resumo

- A ROM nova, `DBZ Attack of the Saiyans PT-BR Coerencia.nds`, tem SHA-256 `130b4ad8…` e confere com o documentado. Ela é estruturalmente íntegra.
- Os três BPS reproduzem exatamente as ROMs de destino. Os três CRC32 internos de cada patch são válidos.
- Entre a rc.1 e a Coerência mudaram exatamente 27 arquivos: 21 `.chr` e 6 `bdat.bin`, como foi declarado. ARM9, ARM7, FNT, banner e roteiros (`.sb`) estão idênticos. Nenhum byte mudou fora desses arquivos e do cabeçalho.
- Nível, HP, MP, atributos, EXP, zeni, AP, itens, potência dos ataques e resistências estão idênticos nas 173 linhas de `enemy_param`.
- Porém os campos `atk1`–`atk4` não são de apresentação. Eles somam 100 em todas as 173 linhas das três ROMs, então são o percentual de escolha de cada ataque. Em 31 linhas eles mudaram na etapa 12. Ver o achado ALTO-1.
- A "ROM antiga do Switch" em `00_Original\rom_antiga_do_switch_2026-10-11\` não é PT-BR. É a ROM original em inglês, com campos de assinatura do cabeçalho zerados (MÉDIO-1).

## 1. Hashes

| Arquivo | Bytes | CRC32 | SHA-1 | SHA-256 | Identidade |
|---|---|---|---|---|---|
| `00_Original\…Saiyans.zip` → `(USA) (En,Fr).nds` | 134.217.728 | a9f0b8f9 | b5d8ebbc8813db68270ea02f0e581f6005f54736 | e310a165…f3e11b | **Original** (bate com o documentado) |
| Backup `conteiner-ds\rom\aots.nds` | 134.217.728 | a9f0b8f9 | b5d8ebbc… | e310a165… | = Original |
| `00_Original\rom_antiga_do_switch_2026-10-11\…Saiyans.nds` | 134.217.728 | **431f0f32** | b593d15cdbc540f7cd6ebcae68836cc7f21f5607 | e19ede8a0f36735ef2ac970152698bd1992ad76131a0c04562662f59ea9032b5 | Original EN com 167 bytes zerados no cabeçalho (ver MÉDIO-1). Não está documentado |
| `01_ROM\DBZ Attack of the Saiyans PT-BR.nds` | 134.217.728 | 670e3cf1 | 74f536b0780857784eadb6d5e56b717ffbca49a0 | 41412a4727328d5341ba2f7d17fa567c84db137d8cd082bc32389c6d27643a5f | **rc.1** (bate com o documentado) |
| `01_ROM\…PT-BR.zip` → `.nds` | 134.217.728 | 670e3cf1 | 74f536b0… | 41412a47… | = rc.1 |
| `07_Teste_Audio_PC\PTBR.nds` | 134.217.728 | 670e3cf1 | 74f536b0… | 41412a47… | = rc.1 |
| `10_Auditoria_Inimigos\…Saiyans.nds` | 134.217.728 | 670e3cf1 | 74f536b0… | 41412a47… | = rc.1 |
| `Downloads\melonDS-1.1-windows-x86_64\…PT-BR.nds` | 134.217.728 | 670e3cf1 | 74f536b0… | 41412a47… | = rc.1 |
| Backup `conteiner-ds\rom\aots_ptbr_img.nds` | 134.217.728 | 670e3cf1 | 74f536b0… | 41412a47… | = rc.1 |
| `12_Coerencia_Historia\…PT-BR Coerencia.nds` | 134.217.728 | fe1fe43d | abc2c10b51aa933855b086a470e52e2825d20cea | 130b4ad843d85d760c4e844de26c35021bde0b43b6c5f34d6c3c639b2f5a9edd | **Coerência** (bate com o RELATORIO_COERENCIA e o resultado_verificacao.json) |
| `11_…\patches\aots_ptbr.bps` | 2.112.001 | — | fd8adec3… | 8d3e04696a56de81734b29e3a39558a92f857994b7621a19ec13b63fc949a423 | Bate com o CHANGELOG e o backup |
| `12_…\Coerencia_sobre_PTBR_1.0.0-rc.1.bps` | 1.263.965 | — | 14e6cabd… | 25f43232578959cf18b82ee46e986cb347583b8d351f71e58301e159f06e11b1 | Sem hash documentado |
| `12_…\DBZ_PTBR_Coerencia_completo.bps` | 7.762.105 | — | ed8ae1ed… | 1d35b32302c82b5930faaf73bf4c758cf4160680b066621ce01c90ef8c7440c8 | Sem hash documentado |

Grupos iguais:
- **Original:** o `.nds` do zip e o `aots.nds` do backup.
- **rc.1:** `01_ROM` (`.nds` e zip), `07_Teste_Audio_PC`, `10_Auditoria_Inimigos`, a cópia do melonDS e o `aots_ptbr_img.nds` do backup.
- **Coerência:** só a ROM da pasta 12.
- **Avulsa:** a ROM antiga do Switch, que não é igual a nenhuma outra.

O backup inclui outras 10 ROMs de teste. Os hashes delas foram calculados (ver `work/`) e nenhuma é igual à ROM antiga do Switch.

## 2. BPS

Cada patch foi aplicado com dois aplicadores, o meu (`work/meubps.py`) e o `bps.py` do projeto. Os dois deram saídas idênticas byte a byte.

| Patch | Metadado | CRC origem | CRC destino | CRC do patch | Resultado |
|---|---|---|---|---|---|
| `aots_ptbr.bps` (original → rc.1) | (vazio) | a9f0b8f9 ✔ | 670e3cf1 ✔ | 2778f6e7 ✔ | Saída SHA-256 `41412a47…`, **idêntica à rc.1** |
| `Coerencia_sobre_PTBR_1.0.0-rc.1.bps` (rc.1 → Coerência) | "DBZ NDS - coerencia narrativa - 52 entradas - 2026-10-11" | 670e3cf1 ✔ | fe1fe43d ✔ | 6f0edc09 ✔ | Saída `130b4ad8…`, **idêntica à Coerência** |
| `DBZ_PTBR_Coerencia_completo.bps` (original → Coerência) | "DBZ NDS - PT-BR e coerencia narrativa - 2026-10-11" | a9f0b8f9 ✔ | fe1fe43d ✔ | 7dda32e3 ✔ | Saída `130b4ad8…`, **idêntica à Coerência** |
| `versoes-antigas\aots_bichos_db.bps` (extra) | (vazio) | a9f0b8f9 ✔ | 68ffeccb ✔ | ca4565ba ✔ | Saída `a296ac46…` = `aots_bichos_db.nds` do backup |

- Os três patches da entrega têm o tamanho de origem e de destino igual a 134.217.728 bytes.
- O fluxo de comandos termina exatamente no rodapé de cada patch.
- Cada patch recusa as outras ROMs como origem pelo CRC, incluindo a ROM antiga do Switch.
- O CRC32 de cada `.bps` inteiro dá 0x2144DF1C, o valor esperado quando o CRC final está correto.

## 3. Cabeçalho NDS da ROM Coerência

| Campo | Valor | Situação |
|---|---|---|
| Título / código / fabricante | `DB KAI RPG` / `BRPE` / `AF` | Igual ao original |
| Capacidade (0x14 = 0x0A) | 128 MiB, igual ao tamanho do arquivo | ✔ Nada truncado |
| ARM9 | ofs 0x4000, 0xA33B8 bytes, entrada/RAM 0x02000800/0x02000000 | ✔ Idêntico byte a byte ao original e à rc.1 |
| ARM7 | ofs 0xA7400, 0x27124 bytes | ✔ Idêntico |
| FNT | ofs 0xCE600, 0x17A6F bytes | ✔ Idêntica |
| FAT | ofs 0xE6200, 0xDB10 bytes (7.010 entradas) | ✔ Todas dentro da ROM e sem sobreposição. Os inícios novos estão alinhados a 0x200 |
| Overlays ARM9/ARM7 | nenhum (tabelas vazias) | ✔ Igual ao original |
| Banner | ofs 0xF3E00, CRC16 válido | ✔ Idêntico |
| Tamanho usado (0x80) | 0x075A8D94 = maior fim na FAT | ✔ Cauda até 128 MiB toda em 0xFF |
| CRC16 do cabeçalho (0x15E) | 0x857E, recalculado 0x857E | ✔ |
| CRC do logotipo (0x15C) | 0xCF56 | ✔ |
| CRC da área segura (0x6C) | 0xDB05 | Igual ao original |

Da rc.1 para a Coerência, no cabeçalho só mudaram 0x80–0x82 (tamanho usado) e 0x15E–0x15F (CRC16).

## 4. Diferença rc.1 → Coerência no NitroFS

Os 27 arquivos alterados. Todos foram realocados para o fim da área usada:

| Arquivo | Tamanho rc.1 → Coerência | Paletas |
|---|---|---|
| btl/bdat/EN/bdat.bin | 119.572 → 120.052 | — |
| btl/bdat/US/bdat.bin | 120.420 → 120.900 | — |
| btl/bdat/FR/bdat.bin | 112.932 → 113.412 | — |
| btl/bdat/SP/bdat.bin | 108.036 → 108.516 | — |
| btl/bdat/GR/bdat.bin | 108.308 → 108.804 | — |
| btl/bdat/IT/bdat.bin | 107.428 → 107.924 | — |
| btl/ene/ene002_01.chr | 47.862 → 47.958 | 3 → 6 |
| btl/ene/ene003_01.chr | 67.952 → 68.048 | 3 → 6 |
| btl/ene/ene004_01.chr | 89.646 → 89.710 | 3 → 5 |
| btl/ene/ene005_01.chr | 13.740 → 13.804 | 3 → 5 |
| btl/ene/ene006_01.chr | 16.034 → 16.098 | 3 → 5 |
| btl/ene/ene008_01.chr | 26.730 → 26.826 | 3 → 6 |
| btl/ene/ene010_01.chr | 40.916 → 40.948 | 3 → 4 |
| btl/ene/ene012_01.chr | 26.096 → 26.256 | 3 → 8 |
| btl/ene/ene013_01.chr | 18.036 → 18.100 | 3 → 5 |
| btl/ene/ene014_01.chr | 18.928 → 19.088 | 3 → 8 |
| btl/ene/ene016_01.chr | 13.072 → 13.168 | 3 → 6 |
| btl/ene/ene017_01.chr | 15.112 → 15.176 | 3 → 5 |
| btl/ene/ene020_01.chr | 10.796 → 10.860 | 3 → 5 |
| btl/ene/ene021_01.chr | 13.096 → 13.224 | 3 → 7 |
| btl/ene/ene022_01.chr | 17.226 → 17.258 | 3 → 4 |
| btl/ene/ene023_01.chr | 7.660 → 7.724 | 3 → 5 |
| btl/ene/ene026_01.chr | 26.892 → 26.956 | 3 → 5 |
| btl/ene/ene027_01.chr | 37.758 → 37.790 | 3 → 4 |
| btl/ene/ene045_01.chr | 47.914 → 48.010 | 3 → 6 |
| btl/ene/ene053_01.chr | 14.712 → 14.776 | 3 → 5 |
| btl/ene/ene062_01.chr | 12.606 → 12.670 | 3 → 5 |

O que confirmei no nível dos dados:
- **`.chr`:** em todos os 21 arquivos, só mudou a contagem de paletas no cabeçalho (byte 5) e foram acrescentadas paletas de 32 bytes no fim do bloco de paletas. As paletas antigas estão intactas, e tiles, células e animações estão idênticos byte a byte.
- **`bdat.bin`:** os 6 idiomas têm as 35 tabelas com estrutura idêntica.
  - Só `enemy_param` e `character_name` diferem. As outras 33 tabelas estão idênticas byte a byte, incluindo `boss_param`, `player_param`, skills e itens.
  - Os cabeçalhos e as áreas de colunas e hash das duas tabelas alteradas estão intactos.
  - `character_name` cresceu de 480 a 496 bytes por idioma, só por causa das strings. Mudaram 46 nomes; 6 dos 52 mantiveram o nome.
- **`enemy_param`:** mudaram 52 linhas, as mesmas nos 6 idiomas e com os mesmos valores. As colunas alteradas foram só `file` (33 linhas), `palno` (50), `size` (7), `shadow` (9) e `atk1`–`atk4` (31 linhas).
  - **Idênticas nas 173 linhas, tanto rc.1 → Coerência quanto original → Coerência:** power, zeni, exp, ap, item1–4, atk1_pow–atk4_pow, lv, hp, mp, str, def, rec, tec, agi, luc, sleep, bind, poison, dark, stan, panic, freez, dead, carrot, physics, slash, blast, atr_fire, atr_thunder, atr_ice, list e name_id.
  - A linha 0 (Saibaman básico) não foi alterada.
- **Roteiros:** nenhum `.sb` mudou. Reextraí as chamadas `SetEnemyParty` e deram 2.143 chamadas em 183 mapas, todas com 15 argumentos, o que confirma a contagem declarada.
- **Bytes fora dos arquivos:** nenhum byte diferente fora dos 27 arquivos (posições antigas e novas) e do cabeçalho.

## Achados por gravidade

### CRÍTICO
Nenhum. As ROMs e os patches estão íntegros e reproduzíveis, e não há truncamento nem mudança em código, roteiro ou FAT inválida.

### ALTO

**ALTO-1. `atk1`–`atk4` são a distribuição de escolha dos ataques, não um campo de apresentação. Na etapa 12 ela mudou em 31 linhas.**
- **Evidência:**
  - A soma `atk1+atk2+atk3+atk4` é 100 em todas as 173 linhas do original, da rc.1 e da Coerência (`work/atk.txt`).
  - A potência de cada slot (`atkN_pow`) continuou a do bicho original, mas o peso foi copiado do modelo. Com isso, a frequência dos ataques fortes mudou.
  - Exemplos rc.1 → Coerência:
    - Linha 104, "Atirador da Montanha": o slot 1, com pow 105, passou de 50% para 40%.
    - Linha 106: o slot 1, com pow 107, passou de 50% para 30%.
    - Linhas 155, 156 e 157: o slot 3, com pow 162 a 164, passou de 0% para 20–30%.
    - Linhas 95, 96 e 97: o slot 1, com pow 50 a 75, passou de 19% para 30–40%.
  - A média ponderada de pow muda 5 pontos ou mais em 14 linhas. Exemplos: Lutador Noturno 30,0 → 72,9 e Batedor Escavador 30,0 → 62,4.
  - Em 5 linhas (74, 76, 111, 149 e 150) há slots com pow diferente de 0 e peso 0, ou seja, ataques do bicho original que nunca são usados. Isso já vinha da rc.1 nessas linhas.
- **Impacto:** as frases "atributos de combate preservados" e "balanceamento preservado" do RELATORIO_COERENCIA e do `resultado_verificacao.json` são imprecisas. Os números ficaram iguais, mas o comportamento de ataque mudou.
  - A rc.1 também já tinha alterado esses pesos em relação ao original (43 linhas). Na Coerência, 45 linhas diferem do original.
  - A semântica exata de `atk_pow` (0 ou negativo) não foi confirmada no jogo. A média ponderada é só um indicador.
  - É provável que os pesos tenham de seguir o modelo para não pedir animação que o sprite não tem. Nesse caso, a correção seria remapear os `atkN_pow` para os slots do modelo, ou documentar a mudança de balanceamento.

### MÉDIO

**MÉDIO-1. A "ROM antiga do Switch" é a ROM original em inglês, não uma build PT-BR.**
- **Evidência:**
  - Comparada com o original, ela tem 0 arquivos diferentes e ARM9, ARM7, FAT e FNT idênticos.
  - Só 167 bytes diferem, todos em 0x33C–0xFFF do cabeçalho. Esses são os campos de HMAC e assinatura RSA, que estão zerados nela. Isso é típico de um dump ou "clean" diferente do mesmo jogo.
  - Os CRC16 do cabeçalho e do logotipo são válidos.
- **Impacto:**
  - O STATUS_RECUPERADO diz que a ROM do Switch é a rc.1. Isso vale para a cópia de `10_Auditoria_Inimigos` (19:17), mas não para esta cópia das 09:06, que não está documentada.
  - Se o save atual do Switch foi gerado com essa ROM, ele vem do jogo em inglês. O código do jogo é o mesmo (BRPE), então o formato do save deve ser compatível, mas convém registrar isso.
  - Nenhum BPS aceita essa ROM como origem: o CRC32 431f0f32 é diferente de a9f0b8f9.

**MÉDIO-2. A auditoria de encontros da etapa 12 lê só os slots `args[6:12]` e ignora a lista de tipos pré-carregados `args[2:6]`.**
- **Evidência (`work/conflitos.txt`):**
  - Em 46 grupos há IDs que aparecem só na lista de tipos: linhas 1, 140, 161, 162, 163 e 167.
  - As larvas 161, 162 e 163 estão como "mapas: []" e "Reserva" no `revisao_inimigos.json`. Na prática, elas são pré-carregadas junto com o pai, provavelmente como invocação, em 9, 8 e 6 grupos: spi*, c0602/c0607, dbg02, mut*, c1204, snd* e c1007_01.
  - O valor 1 nos slots dessas chamadas parece ser um marcador, e não o Saibaman básico.
- **Resultado:** refiz a checagem de aparência e nome incluindo os tipos e não achei nenhum conflito. Ou seja, a ROM está correta nesse ponto, mas a documentação dos mapas das larvas está errada, e a linha 1 aparece em mais grupos do que o declarado.

**MÉDIO-3. As 4 variantes originais de Saibaman (linhas 1–4: "J./C./K./T. Sai") foram trocadas globalmente.**
- Elas viraram Robô de Patrulha, Robô do Deserto, Mutante Errante e Mutante Sombrio, e aparecem em 12 a 53 mapas cada (ben*, snd*, est*, c09/c10…).
- Os dados estão corretos, mas isso tira os Saibamen "coloridos" também das áreas posteriores à chegada dos Saiyajins. O próprio relatório da etapa 12 reconhece o risco. Fica para a frente narrativa.

### BAIXO

- **BAIXO-1. Dados órfãos.**
  - A rc.1 tem 208.487 bytes não referenciados pela FAT, em 0x6FAFE00 e adiante, que sobraram de montagens anteriores.
  - A Coerência mantém as cópias antigas dos 27 arquivos nas posições originais.
  - Isso é inofensivo, porque fica fora da FAT e cabe em 128 MiB, mas aumenta os patches.
- **BAIXO-2. HMACs de whitelist desatualizados.** O cabeçalho mudou (0x80 e 0x15E) e os HMACs em 0x33C/0x378 e a assinatura RSA não foram refeitos, o que já acontecia na rc.1. Isso só importa em DSi ou 3DS com cartucho de verdade. Não afeta o melonDS nem o RetroArch.
- **BAIXO-3. Hashes antigos no `notes/hack_final.md`.** Constam `4134c05e…` e "ROM completa PT-BR `53e311f4…`", que não correspondem a nenhuma ROM existente. O valor correto da rc.1 é `41412a47…`, como já está no CHANGELOG.
- **BAIXO-4. Os dois BPS da etapa 12 não têm SHA-256 documentado.** Sugiro registrar `25f43232…` (incremental) e `1d35b323…` (completo).
- **BAIXO-5. `bdat.bin` cresceu de novo.** Cresceu mais 480 a 496 bytes por idioma, e a rc.1 já tinha crescido até 16 KB sem problema relatado. O risco de buffer é baixo, mas só um teste no jogo confirma.
