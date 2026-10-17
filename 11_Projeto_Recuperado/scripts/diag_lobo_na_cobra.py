"""ROM de DIAGNOSTICO (nao e entrega): parte da ROM dos lobos e copia a
linha 104 (Wolf, ja hackeado) por cima da linha 80 (Giant Snake), que e a
1a luta do jogo. Assim da para ver na tela, sem andar o mapa todo ate um
lobo, exatamente o que o jogo monta a partir da linha do lobo hackeada:
sprite, paleta, nome (name_id) e stats de lobo nv 8.
"""
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import tabelas_com_offset

BASE = "/ds/rom/aots_lobos_saibaman.nds"
SAIDA = "/ds/rom/diag_lobo_na_cobra.nds"
rom = bytearray(open(BASE, "rb").read())
for lang in ["EN", "US", "FR", "SP", "GR", "IT"]:
    caminho = f"btl/bdat/{lang}/bdat.bin"
    b = bytearray(nds_rom.ler(rom, caminho))
    ep = tabelas_com_offset(b)["enemy_param"]
    assert ep["linhas"][104]["file"] == "ene001_01"
    assert ep["linhas"][80]["file"] == "ene031_01"
    ini = ep["off"] + ep["linhas_off"]
    t = ep["tam_linha"]
    b[ini + 80 * t:ini + 81 * t] = b[ini + 104 * t:ini + 105 * t]
    nds_rom.substituir(rom, caminho, bytes(b))
    l = tabelas_com_offset(b)["enemy_param"]["linhas"][80]
    print(lang, {k: l[k] for k in ("name_id", "file", "palno", "lv", "hp")})
open(SAIDA, "wb").write(rom)
print("ROM:", SAIDA)
