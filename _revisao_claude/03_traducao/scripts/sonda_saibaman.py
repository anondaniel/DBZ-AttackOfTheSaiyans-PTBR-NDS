"""ROM de SONDA: todo inimigo comum usa o grafico do Saibaman.

Nao e o hack final — e o teste de mecanismo. Seja qual for a primeira
batalha do jogo, se aparecer Saibaman, trocar o campo 'file' funciona.

Copia do Saibaman (linha 0) apenas o que e ligado ao DESENHO:
  file, size, shadow, atk1..atk4  (animacoes de ataque podem ser do sprite)
Mantem o que e de BALANCEAMENTO: lv, hp, str, exp, drops, resistencias.

Aplica nos 6 idiomas, porque ainda nao sei qual pasta o jogo le com o
firmware embutido do emulador.
"""
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import (gravar_num, gravar_str_mesmo_tamanho, ler_num,
                          tabelas_com_offset)

ORIG = "/ds/rom/aots.nds"
SAIDA = sys.argv[1] if len(sys.argv) > 1 else "/ds/rom/sonda_saibaman.nds"
IDIOMAS = ["EN", "US", "FR", "SP", "GR", "IT"]
COPIAR = ["size", "shadow", "atk1", "atk2", "atk3", "atk4"]

rom = bytearray(open(ORIG, "rb").read())

for lang in IDIOMAS:
    caminho = f"btl/bdat/{lang}/bdat.bin"
    comp = nds_rom.ler(rom, caminho)
    # bdat.bin NAO e comprimido (conferido nos 6 idiomas: comeca com o
    # proprio cabecalho do contêiner, 23 00 00 00)
    assert comp[:4] == bytes([0x23, 0, 0, 0]), "bdat.bin inesperado"
    b = bytearray(comp)
    tabs = tabelas_com_offset(b)
    ep = tabs["enemy_param"]
    modelo = {c: ler_num(b, ep, 0, c) for c in COPIAR}
    trocados = 0
    for i in range(ep["n_linhas"]):
        velho = gravar_str_mesmo_tamanho(b, ep, i, "file", "ene001_01")
        for c, v in modelo.items():
            gravar_num(b, ep, i, c, v)
        # paleta: o Saibaman tem 5 (0..4); fica dentro da faixa valida
        pal = ler_num(b, ep, i, "palno")
        gravar_num(b, ep, i, "palno", pal % 5)
        trocados += 1
    novo = bytes(b)
    assert len(novo) == len(comp), "tamanho mudou"
    acao = nds_rom.substituir(rom, caminho, novo)
    print(f"{lang}: {trocados} inimigos -> ene001_01 | {len(comp)} -> {len(novo)} b | {acao}")

# confere lendo de volta da ROM montada
for lang in IDIOMAS:
    b = nds_rom.ler(rom, f"btl/bdat/{lang}/bdat.bin")
    ep = tabelas_com_offset(bytearray(b))["enemy_param"]
    arquivos = {l["file"] for l in ep["linhas"]}
    assert arquivos == {"ene001_01"}, f"{lang}: sobrou {arquivos}"
print("conferido: todos os idiomas leem de volta so ene001_01")

open(SAIDA, "wb").write(rom)
print(f"ROM de sonda: {SAIDA}")
