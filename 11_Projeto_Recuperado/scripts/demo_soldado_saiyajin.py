"""DEMO do escritor de nomes: o Wolf (linha 104) vira um soldado saiyajin
com o sprite do Raditz, e o NOME DO PROPRIO LOBO (character_name[113])
e reescrito com tamanho livre. Balanceamento do lobo mantido.

uso: demo_soldado_saiyajin.py <nome> [saida]
"""
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import gravar_num, ler_num, tabelas_com_offset
from bdat_strings import conferir, gravar_str

NOME = sys.argv[1]
SAIDA = sys.argv[2] if len(sys.argv) > 2 else "/ds/rom/demo_soldado.nds"
BOSS = 13  # Raditz em boss_param

rom = bytearray(open("/ds/rom/aots.nds", "rb").read())
for lang in ["EN", "US", "FR", "SP", "GR", "IT"]:
    c = f"btl/bdat/{lang}/bdat.bin"
    orig = bytearray(nds_rom.ler(rom, c))
    tabs = tabelas_com_offset(orig)
    col = tabs["character_name"]["colunas"][0][0]
    b, acao = gravar_str(orig, "enemy_param", 104, "file", "ene220_01")
    b, acao = gravar_str(b, "character_name", 113, col, NOME)
    tabs = tabelas_com_offset(b)
    ep, bp = tabs["enemy_param"], tabs["boss_param"]
    muda = {("enemy_param", 104, "file"): "ene220_01",
            ("character_name", 113, col): NOME}
    pesos = [ler_num(b, bp, BOSS, f"atk{k}") for k in range(1, 5)]
    tot = sum(pesos)
    pesos = [round(p * 100 / tot) for p in pesos]
    pesos[0] += 100 - sum(pesos)
    for k, p in enumerate(pesos, 1):
        gravar_num(b, ep, 104, f"atk{k}", p)
        muda[("enemy_param", 104, f"atk{k}")] = p
    for cc in ("palno", "size", "shadow"):
        v = ler_num(b, bp, BOSS, cc)
        gravar_num(b, ep, 104, cc, v)
        muda[("enemy_param", 104, cc)] = v
    conferir(orig, b, muda)
    print(lang, nds_rom.substituir(rom, c, bytes(b)), f"| nome: {acao}")
# confere lendo de volta da ROM montada
for lang in ["EN", "US", "FR", "SP", "GR", "IT"]:
    tabs = tabelas_com_offset(bytearray(nds_rom.ler(rom, f"btl/bdat/{lang}/bdat.bin")))
    col = tabs["character_name"]["colunas"][0][0]
    assert tabs["character_name"]["linhas"][113][col] == NOME
    assert tabs["enemy_param"]["linhas"][104]["file"] == "ene220_01"
open(SAIDA, "wb").write(rom)
print("ROM:", SAIDA)
