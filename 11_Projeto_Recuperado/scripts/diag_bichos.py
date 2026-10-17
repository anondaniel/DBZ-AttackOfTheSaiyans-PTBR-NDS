"""DIAGNOSTICO (nao e entrega): mostra cada bicho, antes e depois do hack,
na mesma batalha real do Monte Paozu (a de 2 lobos, save state
pz5/p0122_pre.bin), copiando a linha do bicho por cima da linha do Wolf
(104), que e a que essa batalha le do cartucho.

  antes  = ROM original com linha 104 := linha ORIGINAL do bicho
  depois = ROM do hack   com linha 104 := linha HACKEADA do bicho

Saida: /ds/saida/diag_bichos/<linha>_{antes,depois}_{inicio,alvo}.png
"""
import os
import subprocess
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import tabelas_com_offset

ORIG = "/ds/rom/aots.nds"
HACK = "/ds/rom/aots_bichos_saibaman.nds"
# batalha usada como palco: por padrao a de 1 lobo (passo 27). Ursos e
# pandas sao tamanho 2; na batalha de 2 lobos (passo 122) o jogo os
# posiciona fora da tela. Nos mapas deles eles sempre vem sozinhos.
PASSO = os.environ.get("PASSO", "27")
PRE = f"/ds/saida/pz5/p{int(PASSO):04d}_pre.bin"
OUT = os.environ.get("OUT", "/ds/saida/diag_bichos")
LINHAS = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else \
    [113, 114, 115, 116, 117, 118]
os.makedirs(OUT, exist_ok=True)


def monta(base, linha, saida):
    rom = bytearray(open(base, "rb").read())
    for lang in ["EN", "US", "FR", "SP", "GR", "IT"]:
        c = f"btl/bdat/{lang}/bdat.bin"
        b = bytearray(nds_rom.ler(rom, c))
        ep = tabelas_com_offset(b)["enemy_param"]
        ini, t = ep["off"] + ep["linhas_off"], ep["tam_linha"]
        b[ini + 104 * t:ini + 105 * t] = b[ini + linha * t:ini + (linha + 1) * t]
        nds_rom.substituir(rom, c, bytes(b))
    open(saida, "wb").write(rom)


for linha in LINHAS:
    for fase, base in (("antes", ORIG), ("depois", HACK)):
        rom = f"/ds/rom/diag_{linha}_{fase}.nds"
        monta(base, linha, rom)
        r = subprocess.run(["python3", "/ds/scripts/ab_batalha.py", PRE, PASSO, "3",
                            f"{OUT}/tmp", rom], capture_output=True, text=True)
        ok = "ok" in r.stdout
        nome = os.path.basename(rom)[:-4]
        for s in ("inicio", "alvo"):
            if os.path.exists(f"{OUT}/tmp/{nome}_{s}.png"):
                os.replace(f"{OUT}/tmp/{nome}_{s}.png", f"{OUT}/{linha}_{fase}_{s}.png")
        os.remove(rom)
        print(linha, fase, "ok" if ok else "FALHOU\n" + r.stdout[-500:])
