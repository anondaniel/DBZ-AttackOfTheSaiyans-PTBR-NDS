"""HACK 1: os lobos viram Saibamen.

Linhas de enemy_param com file == ene039_01 (Wolf, White Wolf, Red Wolf).

Copia do Saibaman o que e ligado ao DESENHO (mesmo conjunto validado na
ROM de sonda, onde as cobras apareceram como Saibamen e lutaram normal):
    file, size, shadow, atk1..atk4
Nome: name_id aponta para a variante de Saibaman da MESMA paleta
    (paleta p do ene001_01 <-> linha p do Saibaman: 0 Saibaman,
     1 J. Sai, 2 C. Sai...), entao cor e nome batem.
Mantem o BALANCEAMENTO do lobo: lv, hp, str, exp, zeni, drops,
resistencias -- o lobo nv 8 continua sendo um inimigo de nv 8.

Confere no fim que SO essas linhas mudaram, byte a byte, nos 6 idiomas.
"""
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import (gravar_num, gravar_str_mesmo_tamanho, ler_num,
                          tabelas_com_offset)

ORIG = "/ds/rom/aots.nds"
SAIDA = sys.argv[1] if len(sys.argv) > 1 else "/ds/rom/aots_lobos_saibaman.nds"
IDIOMAS = ["EN", "US", "FR", "SP", "GR", "IT"]
DESENHO = ["size", "shadow", "atk1", "atk2", "atk3", "atk4"]
ALVO = "ene039_01"
SAIBA = "ene001_01"

rom = bytearray(open(ORIG, "rb").read())
original = bytes(rom)
linhas_alvo = None

for lang in IDIOMAS:
    caminho = f"btl/bdat/{lang}/bdat.bin"
    velho = nds_rom.ler(rom, caminho)
    assert velho[:4] == bytes([0x23, 0, 0, 0]), "bdat.bin inesperado"
    b = bytearray(velho)
    ep = tabelas_com_offset(b)["enemy_param"]

    saiba = [i for i, l in enumerate(ep["linhas"]) if l["file"] == SAIBA]
    alvo = [i for i, l in enumerate(ep["linhas"]) if l["file"] == ALVO]
    assert len(saiba) == 5 and len(alvo) == 3, (saiba, alvo)
    if linhas_alvo is None:
        linhas_alvo = alvo
    assert alvo == linhas_alvo, f"{lang}: linhas diferentes {alvo}"

    # variante de Saibaman por paleta
    por_pal = {ler_num(b, ep, i, "palno"): i for i in saiba}
    for i in alvo:
        pal = ler_num(b, ep, i, "palno")
        modelo = por_pal[pal]
        antes = {c: ler_num(b, ep, i, c) for c in DESENHO + ["name_id", "lv", "hp"]}
        gravar_str_mesmo_tamanho(b, ep, i, "file", SAIBA)
        for c in DESENHO + ["name_id"]:
            gravar_num(b, ep, i, c, ler_num(b, ep, modelo, c))
        if lang == "EN":
            print(f"linha {i}: pal {pal} -> modelo linha {modelo} | antes {antes}")
            print(f"          depois name_id={ler_num(b, ep, i, 'name_id')} "
                  f"lv={ler_num(b, ep, i, 'lv')} hp={ler_num(b, ep, i, 'hp')} "
                  f"atk={[ler_num(b, ep, i, f'atk{k}') for k in range(1, 5)]}")

    novo = bytes(b)
    assert len(novo) == len(velho)
    # so os bytes das linhas-alvo (e as strings 'file' delas) podem mudar
    ini_linhas = ep["off"] + ep["linhas_off"]
    faixas = [(ini_linhas + i * ep["tam_linha"], ini_linhas + (i + 1) * ep["tam_linha"])
              for i in alvo]
    # + a string do campo file de cada linha-alvo (offset u16 relativo a tabela)
    pos_file = ep["col"]["file"][3]
    for a, _ in list(faixas):
        s = ep["off"] + int.from_bytes(velho[a + pos_file:a + pos_file + 2], "little")
        faixas.append((s, s + len(ALVO)))
    diffs = [k for k in range(len(novo)) if novo[k] != velho[k]]
    fora = [k for k in diffs if not any(a <= k < z for a, z in faixas)]
    assert not fora, f"{lang}: bytes alterados fora das linhas-alvo: {fora[:10]}"
    acao = nds_rom.substituir(rom, caminho, novo)
    print(f"{lang}: {len(diffs)} bytes alterados, todos nas 3 linhas de lobo | {acao}")

# fora dos bdat.bin, a ROM so pode diferir no CRC do cabecalho
bdat_faixas = []
for lang in IDIOMAS:
    fid = nds_rom.caminhos(rom)[f"btl/bdat/{lang}/bdat.bin"]
    bdat_faixas.append(nds_rom.fat_entrada(rom, fid))
fora = [k for k in range(len(rom)) if rom[k] != original[k]
        and not any(a <= k < z for a, z in bdat_faixas) and k not in (0x15E, 0x15F)]
assert not fora, f"ROM mudou fora dos bdat.bin: {fora[:10]}"

open(SAIDA, "wb").write(rom)
print(f"ROM: {SAIDA}")
