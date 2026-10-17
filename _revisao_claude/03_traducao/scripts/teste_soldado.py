"""TESTE (nao e entrega) do soldado saiyajin montado (ene200_01.chr).

Em cada ROM de teste o Wolf (linha 104) usa file=ene200_01, palno 0..2 e o
nome "Soldado Saiyajin" (tamanho/sombra/pesos de ataque do Raditz). Refaz a
batalha de 1 lobo: guarda o quadro do alvo e ~20 s de luta (para ver as
animacoes de ataque com o cabelo cortado).
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import gravar_num, ler_num, tabelas_com_offset
from bdat_strings import gravar_str
from montar_soldado_chr import instalar

OUT = "/ds/saida/teste_soldado2"
os.makedirs(OUT, exist_ok=True)
base = bytearray(open("/ds/rom/aots.nds", "rb").read())
print("chr:", instalar(base))

for pal in range(3):
    rom = bytearray(base)
    for lang in ["EN", "US", "FR", "SP", "GR", "IT"]:
        cam = f"btl/bdat/{lang}/bdat.bin"
        b = bytearray(nds_rom.ler(rom, cam))
        col = tabelas_com_offset(b)["character_name"]["colunas"][0][0]
        b, _ = gravar_str(b, "enemy_param", 104, "file", "ene200_01")
        b, _ = gravar_str(b, "character_name", 113, col, "Soldado Saiyajin")
        tabs = tabelas_com_offset(b)
        ep, bp = tabs["enemy_param"], tabs["boss_param"]
        for cc in ("size", "shadow"):
            gravar_num(b, ep, 104, cc, ler_num(b, bp, 13, cc))
        pesos = [ler_num(b, bp, 13, f"atk{k}") for k in range(1, 5)]
        tot = sum(pesos)
        pesos = [round(x * 100 / tot) for x in pesos]
        pesos[0] += 100 - sum(pesos)
        for k, x in enumerate(pesos, 1):
            gravar_num(b, ep, 104, f"atk{k}", x)
        gravar_num(b, ep, 104, "palno", pal)
        gravar_num(b, ep, 104, "hp", 3000)  # so no teste: aguentar e atacar
        nds_rom.substituir(rom, cam, bytes(b))
    caminho = f"/ds/rom/soldado2_p{pal}.nds"
    open(caminho, "wb").write(rom)
    r = subprocess.run(["python3", "/ds/scripts/ab_batalha.py", "/ds/saida/pz5/p0027_pre.bin",
                        "27", "3", OUT, caminho], capture_output=True, text=True)
    print("paleta", pal, "ok" if "ok" in r.stdout else "FALHOU " + r.stdout[-300:])
    if pal == 0:  # luta mais longa so numa, para ver os ataques
        subprocess.run(["python3", "/ds/scripts/explorar.py", caminho, f"{OUT}/luta",
                        "down+left@60:2 a@6x60:24", "/ds/saida/pz5/p0027_pre.bin"],
                       capture_output=True, env={**os.environ, "CADA": "3"})
    os.remove(caminho)

z = Image.new("RGB", (3 * 120, 130), (20, 20, 20))
for i in range(3):
    im = Image.open(f"{OUT}/soldado2_p{i}_alvo.png").convert("RGB").crop((20, 45, 140, 175))
    z.paste(im, (i * 120, 0))
z.resize((z.width * 3, z.height * 3), Image.NEAREST).save("/ds/saida/soldado_final_zoom.png")
print("ok")
