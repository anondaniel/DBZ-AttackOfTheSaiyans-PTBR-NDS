"""Fonte grossa com degrade dos rotulos de menu ("MAIN MENU", "MEMBER").
Letras tiradas do proprio jogo (atlas menu_us.img e folha menu_sp_us.chr),
13 linhas de altura (contorno + 11 + contorno), indices 4bpp.
Cada glifo = colunas [contorno esquerdo + corpo]; o contorno da direita e
o esquerdo do proximo (ou FECHO no fim)."""
import sys

sys.path.insert(0, "/ds/scripts")

HEX = ".123456789ABCDEF"


def _ler_atlas():
    import imp
    import nds_rom
    rom = open("/ds/rom/aots.nds", "rb").read()
    px = imp.ler(nds_rom.ler(rom, "menu/icon/menu_us.img"))["pixels"]
    return lambda x, y: (px[y * 128 + x // 2] >> 4) if x & 1 else (px[y * 128 + x // 2] & 15)


def _ler_chr():
    import nds_rom
    from dump_tiles import ler_chr
    rom = open("/ds/rom/aots.nds", "rb").read()
    T = ler_chr(nds_rom.ler(rom, "menu/icon/menu_sp_us.chr"))["tiles"]

    def f(x, y):
        b = T[(y // 8) * 32 + x // 8][(y % 8) * 4 + (x % 8) // 2]
        return (b >> 4) if x & 1 else b & 15
    return f


def grade(f, x0, x1, y0):
    return ["".join(HEX[f(x, y0 + r)] for x in range(x0, x1 + 1)) for r in range(13)]


def separar(g):
    """corta nas colunas de contorno vertical (linhas 1..11 todas '1')"""
    cols = [x for x in range(len(g[0])) if all(g[r][x] == "1" for r in range(1, 12))]
    fim = max(x for x in range(len(g[0])) if any(g[r][x] != "." for r in range(13))) + 1
    cols = cols + [fim]
    return [[linha[a:b] for linha in g] for a, b in zip(cols, cols[1:])]


if __name__ == "__main__":
    for nome, f, x0, x1, y0 in (("MAIN MENU", _ler_atlas(), 114, 171, 49), ("MEMBER", _ler_chr(), 186, 232, 18)):
        g = grade(f, x0, x1, y0)
        partes = separar(g)
        print(nome, len(partes), "glifos")
        for k, p in enumerate(partes):
            print(" glifo", k, "largura", len(p[0]))
            for linha in p:
                print("   ", linha)
