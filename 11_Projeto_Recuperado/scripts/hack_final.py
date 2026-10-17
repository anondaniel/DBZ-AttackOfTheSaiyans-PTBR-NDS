"""Monta a ROM COMPLETA do hack "bichos -> universo DB" a partir do PLANO.

  1. verificar_plano.py tem que passar (senao para)
  2. ene001_01.chr (Saibaman): mantem as 5 paletas e acrescenta as novas
  3. ene200_01.chr (inimigo cortado) vira o Soldado Saiyajin: tiles do Raditz
     com a juba cortada + uma paleta por variante; ene220_01 (chefe) intacto
  4. bdat.bin (6 idiomas): por linha do plano, sprite/paleta/tamanho/sombra/
     pesos de ataque do modelo + nome novo; balanceamento do bicho mantido
  5. confere: todas as celulas de todas as tabelas iguais ao original,
     exceto as pedidas; fora dos arquivos trocados a ROM nao muda
uso: hack_final.py [saida]
"""
import pickle
import subprocess
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import gravar_num, ler_num, tabelas_com_offset
from bdat_strings import conferir, gravar_str
from chr_paletas import com_paletas, paletas
from plano_bichos import PLANO, SAIBA, SAIBA_NOVAS, SOLDADO, saiba_var, soldado_var

SAIDA = sys.argv[1] if len(sys.argv) > 1 else "/ds/rom/aots_bichos_db.nds"
IDIOMAS = ["EN", "US", "FR", "SP", "GR", "IT"]

r = subprocess.run(["python3", "/ds/scripts/verificar_plano.py"], capture_output=True, text=True)
print(r.stdout.strip().splitlines()[-1])
assert r.returncode == 0, "plano com problemas:\n" + r.stdout

orig = open("/ds/rom/aots.nds", "rb").read()
rom = bytearray(orig)
indice = {}  # (arquivo, nome_da_paleta) -> palno

# --- Saibaman: paletas novas depois das 5 originais
c = nds_rom.ler(rom, f"btl/ene/{SAIBA}.chr")
pals = paletas(c)
usadas = sorted({p for _, a, p, _, _ in PLANO.values() if a == SAIBA and isinstance(p, str)})
for nome in usadas:
    indice[(SAIBA, nome)] = len(pals)
    pals.append(saiba_var(pals[0], *SAIBA_NOVAS[nome]))
assert len(pals) <= 16
print(f"{SAIBA}: {len(pals)} paletas |", nds_rom.substituir(rom, f"btl/ene/{SAIBA}.chr", com_paletas(c, pals)))

# --- Soldado Saiyajin no lugar de ene200_01
raditz = nds_rom.ler(rom, "btl/ene/ene220_01.chr")
d = bytearray(raditz)
novos = pickle.load(open("/ds/saida/juba/tiles_novos.pkl", "rb"))
ini = 8 + d[5] * 32
d[ini:ini + len(novos) * 32] = b"".join(novos)
p0 = paletas(raditz)[0]
vars_sold = []
for _, a, p, _, _ in sorted(PLANO.values(), key=lambda v: v[4]):
    if a == SOLDADO and p not in vars_sold:
        vars_sold.append(p)
for k, nome in enumerate(vars_sold):
    indice[(SOLDADO, nome)] = k
assert len(vars_sold) <= 16
print(f"{SOLDADO}: {len(vars_sold)} paletas {vars_sold} |",
      nds_rom.substituir(rom, f"btl/ene/{SOLDADO}.chr",
                         com_paletas(bytes(d), [soldado_var(p0, v) for v in vars_sold])))
assert nds_rom.ler(rom, "btl/ene/ene220_01.chr") == raditz, "chr do chefe Raditz mudou"

# --- tabelas
for lang in IDIOMAS:
    cam = f"btl/bdat/{lang}/bdat.bin"
    velho = bytearray(nds_rom.ler(rom, cam))
    b = bytearray(velho)
    col = tabelas_com_offset(b)["character_name"]["colunas"][0][0]
    muda = {}
    for linha, (bicho, arq, pal, mod, nome) in PLANO.items():
        b, _ = gravar_str(b, "enemy_param", linha, "file", arq)
        muda[("enemy_param", linha, "file")] = arq
        tabs = tabelas_com_offset(b)
        ep = tabs["enemy_param"]
        tm = tabs["boss_param"] if mod[0] == "b" else ep
        m = int(mod[1:])
        palno = pal if isinstance(pal, int) else indice[(arq, pal)]
        valores = {"palno": palno, "size": ler_num(b, tm, m, "size"), "shadow": ler_num(b, tm, m, "shadow")}
        pesos = [ler_num(b, tm, m, f"atk{k}") for k in range(1, 5)]
        if mod[0] == "b":  # chefe tem 6 ataques: 4 primeiros renormalizados
            tot = sum(pesos) or 1
            pesos = [round(x * 100 / tot) for x in pesos]
            pesos[0] += 100 - sum(pesos)
        valores.update({f"atk{k}": x for k, x in enumerate(pesos, 1)})
        for cc, v in valores.items():
            gravar_num(b, ep, linha, cc, v)
            muda[("enemy_param", linha, cc)] = v
        nid = ler_num(b, ep, linha, "name_id")
        b, _ = gravar_str(b, "character_name", nid - 1, col, nome)
        muda[("character_name", nid - 1, col)] = nome
    conferir(velho, b, muda)
    print(f"{lang}: {len(muda)} celulas mudaram (conferidas) |", nds_rom.substituir(rom, cam, bytes(b)))

# --- fora dos arquivos trocados, nada muda
cam = nds_rom.caminhos(rom)
trocados = [f"btl/bdat/{l}/bdat.bin" for l in IDIOMAS] + [f"btl/ene/{SAIBA}.chr", f"btl/ene/{SOLDADO}.chr"]
fid_trocados = {cam[t] for t in trocados}
fat = nds_rom.u32(rom, 0x48)
for fid in range(len(cam)):
    if fid in fid_trocados:
        continue
    a1, z1 = nds_rom.fat_entrada(orig, fid)
    a2, z2 = nds_rom.fat_entrada(rom, fid)
    assert (a1, z1) == (a2, z2) and rom[a2:z2] == orig[a1:z1], f"arquivo {fid} mudou"
open(SAIDA, "wb").write(rom)
print("todos os outros arquivos identicos ao original")
# cauda do soldado (faixa da cintura) escurecida para aparecer como cauda
r = subprocess.run(["python3", "/ds/scripts/cauda_soldado.py", SAIDA, SAIDA], capture_output=True, text=True)
assert r.returncode == 0, r.stderr
print(r.stdout.strip().splitlines()[0])
print("ROM:", SAIDA)
