"""HACK: bichos viram Saibamen (lobos + ursos).

TROCAS = linha de enemy_param -> linha do Saibaman usada como modelo.
Do modelo vem o que e ligado ao DESENHO e ao NOME:
    file, palno, size, shadow, atk1..atk4 (pesos de ataque), name_id
Do bicho fica o BALANCEAMENTO: lv, hp, str, exp, zeni, drops, resistencias.

Escolha das variantes (ver notes/hack_ursos.md): cada mapa fica sem dois
inimigos diferentes com o mesmo nome.
    Monte Paozu leste: Wolf=Saibaman, Red Wolf=C. Sai -> Strong Bear=K. Sai
    Mt. Frappe:        White Wolf=J. Sai           -> Snow Bear=T. Sai
    Spinach Wastes:    sem lobos                   -> Hungry Bear=Saibaman

Confere que so as linhas trocadas (e as strings 'file' delas) mudaram,
nos 6 idiomas, e que fora dos bdat.bin so muda o CRC do cabecalho.
"""
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import (gravar_num, gravar_str_mesmo_tamanho, ler_num,
                          tabelas_com_offset)

ORIG = "/ds/rom/aots.nds"
SAIDA = sys.argv[1] if len(sys.argv) > 1 else "/ds/rom/aots_bichos_saibaman.nds"
IDIOMAS = ["EN", "US", "FR", "SP", "GR", "IT"]
SAIBA = "ene001_01"
COPIAR = ["palno", "size", "shadow", "atk1", "atk2", "atk3", "atk4", "name_id"]
# linha: (nome esperado, arquivo esperado, linha do modelo Saibaman)
TROCAS = {
    104: ("Wolf", "ene039_01", 0),         # Saibaman
    105: ("White Wolf", "ene039_01", 1),   # J. Sai
    106: ("Red Wolf", "ene039_01", 2),     # C. Sai
    113: ("Hungry Bear", "ene042_01", 0),  # Saibaman
    114: ("Snow Bear", "ene042_01", 4),    # T. Sai
    115: ("Strong Bear", "ene042_01", 3),  # K. Sai
    116: ("Dangerous Panda", "ene042_02", 0),    # Saibaman
    117: ("Snow Panda", "ene042_02", 4),         # T. Sai
    118: ("Ultimate Pandaman", "ene042_02", 3),  # K. Sai
}

rom = bytearray(open(ORIG, "rb").read())
original = bytes(rom)
nomes = None

for lang in IDIOMAS:
    caminho = f"btl/bdat/{lang}/bdat.bin"
    velho = nds_rom.ler(rom, caminho)
    assert velho[:4] == bytes([0x23, 0, 0, 0]), "bdat.bin inesperado"
    b = bytearray(velho)
    tabs = tabelas_com_offset(b)
    ep = tabs["enemy_param"]
    if lang == "EN":
        nomes = [l["en"] for l in tabs["character_name"]["linhas"]]
    for i in range(5):
        assert ep["linhas"][i]["file"] == SAIBA, "modelo nao e Saibaman"

    faixas = []
    ini = ep["off"] + ep["linhas_off"]
    pos_file = ep["col"]["file"][3]
    for i, (nome, arq, m) in TROCAS.items():
        assert ep["linhas"][i]["file"] == arq, f"{lang} linha {i}: {ep['linhas'][i]['file']}"
        if lang == "EN":
            assert nomes[ep["linhas"][i]["name_id"] - 1] == nome, (i, nome)
        a = ini + i * ep["tam_linha"]
        faixas.append((a, a + ep["tam_linha"]))
        s = ep["off"] + int.from_bytes(velho[a + pos_file:a + pos_file + 2], "little")
        faixas.append((s, s + len(arq)))
        antes = {c: ler_num(b, ep, i, c) for c in ("lv", "hp", "exp")}
        gravar_str_mesmo_tamanho(b, ep, i, "file", SAIBA)
        for c in COPIAR:
            gravar_num(b, ep, i, c, ler_num(b, ep, m, c))
        depois = {c: ler_num(b, ep, i, c) for c in ("lv", "hp", "exp")}
        assert antes == depois
        if lang == "EN":
            print(f"linha {i:3d} {nome:12s} -> {nomes[ler_num(b, ep, i, 'name_id') - 1]:9s} "
                  f"(pal {ler_num(b, ep, i, 'palno')}) | mantem nv {antes['lv']}, "
                  f"HP {antes['hp']}, EXP {antes['exp']}")

    novo = bytes(b)
    assert len(novo) == len(velho)
    diffs = [k for k in range(len(novo)) if novo[k] != velho[k]]
    fora = [k for k in diffs if not any(a <= k < z for a, z in faixas)]
    assert not fora, f"{lang}: bytes alterados fora das linhas-alvo: {fora[:10]}"
    acao = nds_rom.substituir(rom, caminho, novo)
    print(f"{lang}: {len(diffs)} bytes alterados, todos nas {len(TROCAS)} linhas | {acao}")

bdat_faixas = [nds_rom.fat_entrada(rom, nds_rom.caminhos(rom)[f"btl/bdat/{l}/bdat.bin"])
               for l in IDIOMAS]
fora = [k for k in range(len(rom)) if rom[k] != original[k]
        and not any(a <= k < z for a, z in bdat_faixas) and k not in (0x15E, 0x15F)]
assert not fora, f"ROM mudou fora dos bdat.bin: {fora[:10]}"

# a parte dos lobos tem que sair identica a ROM ja validada
lobos = open("/ds/rom/aots_lobos_saibaman.nds", "rb").read()
for lang in IDIOMAS:
    c = f"btl/bdat/{lang}/bdat.bin"
    tl = tabelas_com_offset(bytearray(nds_rom.ler(lobos, c)))["enemy_param"]["linhas"]
    tn = tabelas_com_offset(bytearray(nds_rom.ler(rom, c)))["enemy_param"]["linhas"]
    for i in (104, 105, 106):
        assert tl[i] == tn[i], f"{lang} linha {i} difere da ROM dos lobos"
print("linhas dos lobos identicas a ROM validada antes")

open(SAIDA, "wb").write(rom)
print(f"ROM: {SAIDA}")
