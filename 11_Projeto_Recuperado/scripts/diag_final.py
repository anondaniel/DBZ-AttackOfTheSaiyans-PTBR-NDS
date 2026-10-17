"""Confere no jogo TODAS as linhas do plano na ROM final: para cada uma,
copia a linha (ja hackeada) sobre a do Wolf e refaz a batalha real de 1
lobo (pz5/p0027_pre.bin). Guarda o quadro com a etiqueta do alvo e monta
uma folha de contato com o nome esperado embaixo de cada captura.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import tabelas_com_offset
from plano_bichos import PLANO

HACK = "/ds/rom/aots_bichos_db.nds"
OUT = "/ds/saida/diag_final"
os.makedirs(OUT, exist_ok=True)
base = open(HACK, "rb").read()
ok = []
for linha, (bicho, arq, pal, mod, nome) in sorted(PLANO.items(), key=lambda kv: kv[0]):
    png = f"{OUT}/l{linha:03d}.png"
    if os.path.exists(png):
        ok.append((linha, bicho, nome))
        continue
    rom = bytearray(base)
    if linha != 104:
        for lang in ["EN", "US", "FR", "SP", "GR", "IT"]:
            c = f"btl/bdat/{lang}/bdat.bin"
            b = bytearray(nds_rom.ler(rom, c))
            ep = tabelas_com_offset(b)["enemy_param"]
            ini, t = ep["off"] + ep["linhas_off"], ep["tam_linha"]
            b[ini + 104 * t:ini + 105 * t] = b[ini + linha * t:ini + (linha + 1) * t]
            nds_rom.substituir(rom, c, bytes(b))
    caminho = f"/ds/rom/df_{linha}.nds"
    open(caminho, "wb").write(rom)
    r = subprocess.run(["python3", "/ds/scripts/ab_batalha.py", "/ds/saida/pz5/p0027_pre.bin",
                        "27", "3", f"{OUT}/tmp", caminho], capture_output=True, text=True)
    os.remove(caminho)
    alvo = f"{OUT}/tmp/df_{linha}_alvo.png"
    if "ok" in r.stdout and os.path.exists(alvo):
        os.replace(alvo, png)
        ok.append((linha, bicho, nome))
        print(linha, bicho, "->", nome, "ok", flush=True)
    else:
        print(linha, bicho, "FALHOU", r.stdout[-300:], flush=True)

w, h, cols = 256, 192, 6
g = Image.new("RGB", (w * cols, (h + 24) * ((len(ok) + cols - 1) // cols)), (20, 20, 20))
dr = ImageDraw.Draw(g)
for i, (linha, bicho, nome) in enumerate(ok):
    x, y = (i % cols) * w, (i // cols) * (h + 24)
    g.paste(Image.open(f"{OUT}/l{linha:03d}.png").convert("RGB").crop((0, 0, w, h)), (x, y))
    dr.text((x + 4, y + h + 2), f"{bicho} -> {nome}", fill=(255, 255, 0))
g.save("/ds/saida/folha_contato_final.png")
print(f"{len(ok)}/{len(PLANO)} ok -> /ds/saida/folha_contato_final.png")
