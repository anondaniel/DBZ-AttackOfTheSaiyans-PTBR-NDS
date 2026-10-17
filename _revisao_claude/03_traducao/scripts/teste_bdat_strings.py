"""Testes do escritor de strings em todos os bdat.bin reais."""
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import tabelas_com_offset
from bdat_strings import conferir, gravar_str

rom = open("/ds/rom/aots.nds", "rb").read()
for lang in ["EN", "US", "FR", "SP", "GR", "IT"]:
    orig = bytearray(nds_rom.ler(rom, f"btl/bdat/{lang}/bdat.bin"))
    tabs = tabelas_com_offset(orig)
    col = tabs["character_name"]["colunas"][0][0]
    wolf = tabs["character_name"]["linhas"][113][col]

    # 1) menor: no lugar
    b, r1 = gravar_str(orig, "character_name", 113, col, "Sai")
    conferir(orig, b, {("character_name", 113, col): "Sai"})
    assert len(b) == len(orig)

    # 2) maior, ultima tabela
    b, r2 = gravar_str(orig, "character_name", 113, col, "Saiyan Soldier")
    conferir(orig, b, {("character_name", 113, col): "Saiyan Soldier"})

    # 3) maior, tabela do MEIO (enemy_param.file), forca empurrar 34 tabelas
    longo = "x" * 40
    b3, r3 = gravar_str(orig, "enemy_param", 5, "file", longo)
    conferir(orig, b3, {("enemy_param", 5, "file"): longo})

    # 4) varias seguidas (acumula crescimento)
    b4 = orig
    muda = {}
    for i, txt in [(113, "Saiyan Soldier"), (114, "Saiyan Elite Soldier"), (115, "Saiyan Captain")]:
        b4, _ = gravar_str(b4, "character_name", i, col, txt)
        muda[("character_name", i, col)] = txt
    b4, _ = gravar_str(b4, "enemy_param", 104, "file", "ene220_01")  # mesmo tamanho
    muda[("enemy_param", 104, "file")] = "ene220_01"
    conferir(orig, b4, muda)
    print(f"{lang} (coluna '{col}', era {wolf!r}): 1) {r1} | 2) {r2} | 3) {r3} | "
          f"4) ok, {len(orig)} -> {len(b4)} b")
print("TODOS OS TESTES OK")
