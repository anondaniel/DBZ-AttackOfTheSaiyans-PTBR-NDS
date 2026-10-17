"""Explora imagens dIMG: bitmap 8bpp linear.
Formato deduzido:
  0x00 'dIMG'  0x04 u8 ?  0x05 u8 ?  0x06 u8 largura/2  0x07 u8 altura/2
  0x08 paleta 256 cores RGB555 (512 bytes)
  0x208 pixels: largura x altura bytes (1 byte = indice da paleta), linha a linha
uso: ver_img.py <caminho_na_rom> [saida.png] [modo: linear|tiles]"""
import struct
import sys

from PIL import Image

sys.path.insert(0, "/ds/scripts")
import nds_rom
from dump_tiles import rgb


def ler_img(d):
    assert d[:4] == b"dIMG"
    w = d[6] * 2
    h = d[7] * 2
    pal = struct.unpack_from("<256H", d, 8)
    return w, h, pal, d[0x208:0x208 + w * h]


def imagem(d, modo="linear"):
    w, h, pal, px = ler_img(d)
    im = Image.new("RGB", (w, h))
    p = im.load()
    for i, v in enumerate(px):
        if modo == "linear":
            x, y = i % w, i // w
        else:  # tiles 8x8 de 64 bytes, w/8 tiles por linha
            t, r = divmod(i, 64)
            x = (t % (w // 8)) * 8 + r % 8
            y = (t // (w // 8)) * 8 + r // 8
        if x < w and y < h:
            p[x, y] = rgb(pal[v])
    return im


if __name__ == "__main__":
    caminho = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "/ds/saida/img_" + caminho.replace("/", "_") + ".png"
    modo = sys.argv[3] if len(sys.argv) > 3 else "linear"
    rom = open("/ds/rom/aots.nds", "rb").read()
    d = nds_rom.ler(rom, caminho)
    im = imagem(d, modo)
    im.resize((im.width * 2, im.height * 2), Image.NEAREST).save(out)
    w, h, _, px = ler_img(d)
    print(f"{caminho}: {w}x{h}, {len(px)} px, sobra {len(d) - 0x208 - w * h} b -> {out}")
