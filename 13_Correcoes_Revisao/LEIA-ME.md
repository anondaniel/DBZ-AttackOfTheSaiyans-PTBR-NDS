# 13_Correcoes_Revisao — leia primeiro

Etapa 13 do DBZ Attack of the Saiyans PT-BR. Aplica as correções apontadas pelas
revisões `_revisao_claude\01_integridade`, `02_encontros` e `03_traducao`.
Nada fora desta pasta foi alterado. Os detalhes estão no `RELATORIO.md`.

## Arquivos de entrega

| Arquivo | O que é |
|---|---|
| `DBZ Attack of the Saiyans PT-BR.nds` | ROM final (hashes em `verificacao\hashes_e_bps.json` e no RELATORIO) |
| `DBZ_PTBR_etapa13_sobre_rc1.bps` | patch sobre a **rc.1** (`01_ROM`, SHA-256 `41412a47…`, CRC32 `670e3cf1`) |
| `DBZ_PTBR_etapa13_completo.bps` | patch sobre a **ROM original em inglês** (USA (En,Fr), BRPE, CRC32 `a9f0b8f9`, a mesma origem do `aots_ptbr.bps`) |

Os dois BPS foram aplicados com dois aplicadores independentes e reproduzem a ROM
final byte a byte. Cada um recusa as outras ROMs como origem.

## Como remontar (reproduzível)

```
cd scripts
python -B build.py          # rc.1 (assert SHA-256) -> ROM final
python -B gerar_bps.py      # 2 BPS + conferência + hashes de todos os BPS do projeto
python -B atualizar_ptbr.py # dados\ptbr.json com os nomes finais e textos corrigidos
python -B verificar.py      # revisões 01/02 refeitas -> verificacao\
python -B ..\texto\verificar_textos.py "..\DBZ Attack of the Saiyans PT-BR.nds" ..\verificacao\texto   # revisão 03 refeita
python -B tabelas_relatorio.py
```

Use sempre `python -B` (não grava `__pycache__` nas pastas antigas). Os scripts só
leem `00_Original`, `01_ROM`, `11_Projeto_Recuperado` e `12_Coerencia_Historia`.

## Pastas

- `scripts\` — `build.py` (montagem), `plano13.py` (as 48 linhas: modelo, nome, motivo), `dados_inimigos.py` (leitura de eneEff.bin, sprites, encontros), `verificar.py`, `gerar_bps.py`, `atualizar_ptbr.py`, `previa.py`, `tabelas_relatorio.py`, `rom_antiga_switch.py`.
- `texto\` — lista de correções de texto (`correcoes_texto.json`), mudanças do dicionário (`ptbr_mudancas.json`), verificador de textos, relatório da parte de texto e adendo do glossário.
- `dados\` — `ptbr.json` atualizado (cópia; o original em `11_Projeto_Recuperado\traducao` ficou intacto), `resultado_inimigos.json/csv`.
- `verificacao\` — saídas das verificações, prévia dos sprites (`previa_inimigos.png`), hashes.
- `trabalho\` — rascunhos da análise (desmontador ARM mínimo `armdis.py`, folhas de sprites). Pode ser apagada.

## A "ROM antiga do Switch" (`00_Original\rom_antiga_do_switch_2026-10-11`)

Não é uma build PT-BR. É a **ROM original em inglês** (USA, BRPE), igual à do zip de
`00_Original` exceto por 167 bytes do cabeçalho (0x33C–0xFFF: campos de HMAC/assinatura RSA),
que estão zerados nela. Todos os arquivos do NitroFS, ARM9 e ARM7 são idênticos ao original e o
CRC16 do cabeçalho é válido. É típico de um dump "limpo" diferente do mesmo jogo.

| Campo | Valor |
|---|---|
| Bytes | 134.217.728 |
| CRC32 | `431f0f32` |
| SHA-1 | `b593d15cdbc540f7cd6ebcae68836cc7f21f5607` |
| SHA-256 | `e19ede8a0f36735ef2ac970152698bd1992ad76131a0c04562662f59ea9032b5` |

Consequências: nenhum BPS do projeto a aceita como origem (o CRC32 não é `a9f0b8f9`); para
aplicar o patch completo use a ROM do zip de `00_Original`. Se um save do Switch foi feito com
ela, ele vem do jogo em inglês; o código do jogo é o mesmo (BRPE), então o formato do save é o
mesmo, mas teste com uma **cópia** do save. Conferência em `verificacao\rom_antiga_switch.json`.

## Testes

Nada foi instalado no Switch e nenhum save foi tocado. O que precisa ser jogado está no fim do
RELATORIO.
