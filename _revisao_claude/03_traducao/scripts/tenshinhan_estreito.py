""""Tenshinhan" encostava no "LV" no painel de batalha: o painel centra o nome
num ponto fixo, com a fonte PEQUENA (latin1.fnt, 8x10) + contorno + 1 px a
mais por letra, e ele ficava com 57 px.

Em vez de encurtar o nome (a tabela character_name serve tambem os menus),
cria versoes de 3 px de largura de n, h, a, e em codigos livres das fontes
(0x81, 0x86, 0x87, 0x89: hoje sao o glifo de listras) e usa esses codigos so
no "Tenshinhan" da character_name (US e EN). Fica com 50 px.
- latin1.fnt (a do painel): glifos redesenhados, avanco 4 (era 5).
- latin0.fnt (10x12): copia exata das letras normais, para que qualquer
  texto com a fonte grande mostre o nome igual a antes.
uso: tenshinhan_estreito.py <rom_entrada> <rom_saida>"""
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat_escrita import gravar_str_mesmo_tamanho, tabelas_com_offset

NOVOS = {  # letra: (codigo livre, desenho 3 px nas linhas 4-8 do latin1)
    "n": (0x81, ["##.", "#.#", "#.#", "#.#", "#.#"]),
    "h": (0x86, ["##.", "#.#", "#.#", "#.#", "#.#"]),
    "a": (0x87, ["##.", "..#", ".##", "#.#", ".##"]),
    "e": (0x89, [".#.", "#.#", "###", "#..", ".##"]),
}
HASTE = {"h": [2, 3]}  # linhas extras com "#.." (haste do h)
FONTES = {"latin0.fnt": (10, 12, 15), "latin1.fnt": (8, 10, 10)}


def glifo_latin1(letra, desenho):
    W, H, nb = FONTES["latin1.fnt"]
    linhas = ["." * W] * H
    for y in HASTE.get(letra, []):
        linhas[y] = "#".ljust(W, ".")
    for k, l in enumerate(desenho):
        linhas[4 + k] = l.ljust(W, ".")
    bits = "".join(linhas).ljust(nb * 8, ".")
    return int("".join("1" if c == "#" else "0" for c in bits), 2).to_bytes(nb, "big")


def fonte(rom, arq):
    W, H, nb = FONTES[arq]
    d = bytearray(nds_rom.ler(rom, arq))
    listras = (d[0x81], d[256 + 0x81 * nb:256 + 0x82 * nb])  # glifo de "codigo sem uso"
    for letra, (cod, desenho) in NOVOS.items():
        assert (d[cod], d[256 + cod * nb:256 + (cod + 1) * nb]) == listras, f"{arq} {hex(cod)} nao esta livre"
        o = ord(letra)
        if arq == "latin1.fnt":
            d[256 + cod * nb:256 + (cod + 1) * nb] = glifo_latin1(letra, desenho)
            d[cod] = d[o] - 1
        else:
            d[256 + cod * nb:256 + (cod + 1) * nb] = d[256 + o * nb:256 + (o + 1) * nb]
            d[cod] = d[o]
    nds_rom.substituir(rom, arq, bytes(d))


def nome(rom):
    novo = "".join(chr(NOVOS[c][0]) if c in NOVOS else c for c in "Tenshinhan")
    for lang in ("US", "EN"):
        c = f"btl/bdat/{lang}/bdat.bin"
        b = bytearray(nds_rom.ler(rom, c))
        t = tabelas_com_offset(b)["character_name"]
        col = [c for c in t["colunas"] if c[2] == 7][0][0]  # "us" no US, "en" no EN
        linhas = [l for l in range(t["n_linhas"])
                  if b[t["off"] + struct.unpack_from("<H", b, t["off"] + t["linhas_off"] + l * t["tam_linha"] + t["col"][col][3])[0]:].startswith(b"Tenshinhan\x00")]
        assert len(linhas) == 1, (lang, linhas)
        velho = gravar_str_mesmo_tamanho(b, t, linhas[0], col, novo)
        assert velho == "Tenshinhan"
        nds_rom.substituir(rom, c, bytes(b))
        print(f"{c}: linha {linhas[0]} -> {novo.encode('latin-1').hex(' ')}")


if __name__ == "__main__":
    rom = bytearray(open(sys.argv[1], "rb").read())
    for arq in FONTES:
        fonte(rom, arq)
    nome(rom)
    open(sys.argv[2], "wb").write(rom)
    print("->", sys.argv[2])
