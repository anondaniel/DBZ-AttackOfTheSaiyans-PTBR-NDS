"""Desenha os tiles de um .chr (dCHR) numa folha, com a paleta escolhida.

Formato deduzido:
  0x00 'dCHR'  0x04 u8 versao(2)  0x05 u8 n_paletas  0x06 u16 n_tiles
  0x08 paletas: n_paletas x 16 cores RGB555 (cor 0 = transparente)
  depois: n_tiles x 32 bytes (8x8, 4bpp, nibble baixo = pixel da esquerda)
  depois: tabela de celulas/animacao (ainda nao decodificada)

uso: dump_tiles.py <nome_chr> [paleta] [colunas] [saida.png]
"""
import struct
import sys

from PIL import Image

sys.path.insert(0, "/ds/scripts")
import nds_rom


def ler_chr(d):
    assert d[:4] == b"dCHR"
    npal, ntil = d[5], struct.unpack_from("<H", d, 6)[0]
    pals = [struct.unpack_from("<16H", d, 8 + p * 32) for p in range(npal)]
    ini = 8 + npal * 32
    tiles = [d[ini + i * 32: ini + (i + 1) * 32] for i in range(ntil)]
    return {"pals": pals, "tiles": tiles, "fim_tiles": ini + ntil * 32}


def rgb(c):
    return ((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31)


def tile_img(t, pal, fundo=(40, 40, 40)):
    im = Image.new("RGB", (8, 8))
    px = im.load()
    for y in range(8):
        for x in range(8):
            b = t[y * 4 + x // 2]
            v = (b >> 4) if x & 1 else (b & 15)
            px[x, y] = fundo if v == 0 else rgb(pal[v])
    return im


if __name__ == "__main__":
    nome = sys.argv[1]
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    cols = int(sys.argv[3]) if len(sys.argv) > 3 else 32
    out = sys.argv[4] if len(sys.argv) > 4 else f"/ds/saida/tiles_{nome}.png"
    rom = open("/ds/rom/aots.nds", "rb").read()
    d = nds_rom.ler(rom, f"btl/ene/{nome}.chr")
    c = ler_chr(d)
    n = len(c["tiles"])
    folha = Image.new("RGB", (cols * 8, ((n + cols - 1) // cols) * 8), (40, 40, 40))
    for i, t in enumerate(c["tiles"]):
        folha.paste(tile_img(t, c["pals"][p]), ((i % cols) * 8, (i // cols) * 8))
    folha = folha.resize((folha.width * 3, folha.height * 3), Image.NEAREST)
    folha.save(out)
    print(f"{nome}: {n} tiles, {len(c['pals'])} paleta(s), tiles terminam em 0x{c['fim_tiles']:x} "
          f"de {len(d)} (cauda {len(d) - c['fim_tiles']} b) -> {out}")
