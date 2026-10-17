"""Imagens dIMG / dIMP (fundos e atlas de menu), reimplementado a partir da
rotina do ARM9 em 0x0200a6c0 (descompressor) e 0x0200a85c (cabecalho).

Cabecalho (8 bytes):
  0x00 'dIMG' ou 'dIMP'
  0x04 u8 escala: 0 -> largura=[6]*2, altura=[7]*2 ; 1 -> [6]*8, [7]*8
  0x05 u8 tipo de paleta: indice em (256, 32, 4, 16, 256, 0, 8, 0) cores
  0x06 u8 largura/escala   0x07 u8 altura/escala
  0x08 paleta RGB555 (n cores)
  depois: pixels 8bpp (1 byte = indice), linha a linha
    dIMG: crus;  dIMP: comprimidos (LZ proprio, ver descomprimir)
"""
import struct
import sys

sys.path.insert(0, "/ds/scripts")

NPAL = (256, 32, 4, 16, 256, 0, 8, 0)
_rom9 = None


def _tabelas():
    """As 3 tabelas de bytes com sinal e a de trocas, lidas do ARM9."""
    global _rom9
    if _rom9 is None:
        rom = open("/ds/rom/aots.nds", "rb").read()
        off, _, load, size = struct.unpack_from("<IIII", rom, 0x20)
        arm9 = rom[off:off + size]

        def sb(a, n):
            return list(struct.unpack_from(f"<{n}b", arm9, a - load))
        _rom9 = (sb(0x209B10C, 32), sb(0x209B12C, 32), sb(0x209B14C, 8),
                 list(arm9[0x209B156 - load:0x209B156 - load + 14]))
    return _rom9


def _dist(largura):
    a, c, b, troca = _tabelas()
    t = a[:] + [b[i >> 5] * largura + c[i & 31] for i in range(32, 256)]
    for k, j in zip(range(2, 16), troca):
        t[k], t[j] = t[j], t[k]
    return t


def descomprimir(src, largura, altura, i=0):
    t = _dist(largura)
    fim = largura * altura
    o = bytearray([src[i]])
    i += 1
    while len(o) < fim:
        c = src[i]
        i += 1
        if c < 0x10:  # c+1 literais
            o += src[i:i + c + 1]
            i += c + 1
        elif c == 0x10:  # repete o ultimo byte n+3 vezes
            o += bytes([o[-1]]) * (src[i] + 3)
            i += 1
        elif c < 0x20:
            pass  # nao usado pelo jogo
        else:
            if c < 0x80:
                d, n, lit = t[c & 15], (c >> 4) + 1, 0
            else:
                d, n, lit = t[src[i]], (c & 15) + 3, (c >> 4) & 7
                i += 1
            p = len(o) + d
            for _ in range(n):
                o.append(o[p])
                p += 1
            o += src[i:i + lit]
            i += lit
    return bytes(o[:fim]), i


def ler(d):
    """-> dict(tipo, largura, altura, paleta[list RGB555], pixels bytes, fim)"""
    assert d[:4] in (b"dIMG", b"dIMP"), d[:4]
    esc = 2 if d[4] == 0 else 8
    w, h = d[6] * esc, d[7] * esc
    npal = NPAL[d[5]]
    pal = list(struct.unpack_from(f"<{npal}H", d, 8))
    ini = 8 + npal * 2
    if d[:4] == b"dIMG":
        px, fim = d[ini:ini + w * h], ini + w * h
    else:
        px, fim = descomprimir(d, w, h, ini)
    return {"tipo": d[:4], "largura": w, "altura": h, "paleta": pal, "pixels": px, "fim": fim}


def para_png(img, caminho, escala=1):
    from PIL import Image
    from dump_tiles import rgb
    im = Image.new("RGB", (img["largura"], img["altura"]))
    im.putdata([rgb(img["paleta"][v]) if v < len(img["paleta"]) else (255, 0, 255) for v in img["pixels"]])
    if escala != 1:
        im = im.resize((im.width * escala, im.height * escala), 0)
    im.save(caminho)


if __name__ == "__main__":
    import nds_rom
    rom = open("/ds/rom/aots.nds", "rb").read()
    for c in sys.argv[1:]:
        d = nds_rom.ler(rom, c)
        img = ler(d)
        out = "/ds/saida/imp_" + c.replace("/", "_") + ".png"
        para_png(img, out)
        print(f"{c}: {img['tipo'].decode()} {img['largura']}x{img['altura']} pal={len(img['paleta'])} "
              f"consumiu {img['fim']} de {len(d)} -> {out}")
