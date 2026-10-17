"""Terceira leva: siglas de atributo nos icones redondos (menu_sp_us.chr e
copias): Pw Df Rc Tc Sp Lk -> Po De Cu Te Ve So (Poder, Defesa, Cura,
Tecnica, Velocidade, Sorte, como nos menus). Apaga as letras (miolo do
circulo) com a cor de fundo e desenha as novas em indice 1 (escuro) com
sombra azul (2) a direita/abaixo, como o original.
uso: rotulos3.py <rom_entrada> <rom_saida> [--previa]"""
import collections
import sys

from PIL import Image

sys.path.insert(0, "/ds/scripts")
import nds_rom
from dump_tiles import ler_chr, rgb
from fonte_grossa import HEX
from rotulos import Folha, achar, usado_pelo_us

MAI = {  # 8 linhas
    "P": ["####.", "##.##", "##.##", "####.", "##...", "##...", "##...", "##..."],
    "D": ["####.", "##.##", "##.##", "##.##", "##.##", "##.##", "##.##", "####."],
    "C": [".####", "##...", "##...", "##...", "##...", "##...", "##...", ".####"],
    "T": ["#####", "#####", ".###.", ".###.", ".###.", ".###.", ".###.", ".###."],
    "V": ["##.##", "##.##", "##.##", "##.##", "##.##", "##.##", ".###.", "..#.."],
    "S": [".####", "##...", "##...", ".###.", "...##", "...##", "...##", "####."],
}
MIN = {  # 5 linhas (base alinhada com a maiuscula), acento nas linhas de cima
    "o": [".##.", "#..#", "#..#", "#..#", ".##."],
    "e": [".##.", "#..#", "####", "#...", ".###"],
    "u": ["#..#", "#..#", "#..#", "#..#", ".###"],
    "é": [".##.", "#..#", "####", "#...", ".###"],
}
SIGLAS = ["Po", "De", "Cu", "Té", "Ve", "So"]
X0, PASSO, Y0 = 136, 16, 0          # icones 16x16 na folha menu_sp_us
LET = {1, 2, 4, 5, 7, 8}            # indices usados nas letras originais


def glifo(sigla):
    a, b = sigla
    g = [["."] * 12 for _ in range(8)]
    ma, mi = MAI[a], MIN[b]
    wa, wb = len(ma[0]), len(mi[0])
    x = 1 + (10 - (wa + 1 + wb)) // 2  # miolo = colunas 3..12 do icone
    for r in range(8):
        for c in range(wa):
            if ma[r][c] == "#":
                g[r][x + c] = "#"
    for r in range(5):
        for c in range(wb):
            if mi[r][c] == "#":
                g[3 + r][x + wa + 1 + c] = "#"
    if b == "é":
        g[0][x + wa + 1 + 2] = "#"
        g[1][x + wa + 1 + 1] = "#"  # acento agudo
    assert all(g[r][0] == "." and g[r][11] == "." for r in range(8)), sigla
    return g


def icone_novo(orig, sigla):
    """orig: 16x16 indices; troca o miolo (linhas 4-11, colunas 2-13)"""
    novo = [list(l) for l in orig]
    fundo = collections.Counter(orig[y][x] for y in range(3, 13) for x in range(2, 14)
                                if orig[y][x] not in LET and orig[y][x]).most_common(1)[0][0]
    borda = {3, 11, 12, 14, 15}  # sombreado do anel (B, C, E, F, 3) nas colunas das pontas
    for y in range(4, 13):
        for x in range(2, 14):
            if (x in (2, 13) or y == 12) and orig[y][x] in borda:
                continue
            novo[y][x] = fundo
    g = glifo(sigla)
    for r in range(8):
        for c in range(12):
            if g[r][c] == "#":
                y, x = 4 + r, 2 + c
                novo[y][x] = 1
    return novo


def trabalhos(rom):
    f = Folha(nds_rom.ler(rom, "menu/icon/menu_sp_us.chr"))
    r = []
    for k, s in enumerate(SIGLAS):
        x0 = X0 + k * PASSO
        orig = [[f.get(x0 + x, Y0 + y) for x in range(16)] for y in range(16)]
        r.append((s, orig, icone_novo(orig, s)))
    return r


def s(g):
    return ["".join(HEX[v] if v else "." for v in l) for l in g]


if __name__ == "__main__":
    orig_rom = open("/ds/rom/aots.nds", "rb").read()
    tr = trabalhos(orig_rom)
    if "--previa" in sys.argv:
        c = ler_chr(nds_rom.ler(orig_rom, "menu/icon/menu_sp_us.chr"))
        im = Image.new("RGB", (6 * 17, 34), (40, 40, 40))  # 1 px de folga entre icones
        for k, (sig, a, b) in enumerate(tr):
            for row, g in ((0, a), (17, b)):
                for y in range(16):
                    for x in range(16):
                        if g[y][x]:
                            im.putpixel((k * 17 + x, row + y), rgb(c["pals"][1][g[y][x]]))
        im.resize((im.width * 8, im.height * 8), 0).save("/ds/saida/icones_previa.png")
        print("previa -> /ds/saida/icones_previa.png")
        sys.exit()
    rom = bytearray(open(sys.argv[1], "rb").read())
    todos = nds_rom.caminhos(orig_rom)
    mudou = {}
    for c in todos:
        if not c.startswith("menu/icon/") or not usado_pelo_us(c, todos):
            continue
        d = nds_rom.ler(rom, c)
        imgs = []
        if d[:4] == b"dCHR":
            imgs.append(Folha(d))
        elif c.endswith(".a"):
            buf = bytearray(d)
            j = d.find(b"dCHR")
            while j >= 0:
                f = Folha(buf, j)
                f.d = buf
                imgs.append(f)
                j = d.find(b"dCHR", j + 4)
        for img in imgs:
            for sig, a, b in tr:
                for (x, y) in achar(img, s(a)):
                    for yy in range(16):
                        for xx in range(16):
                            img.set(x + xx, y + yy, b[yy][xx])
                    mudou.setdefault(c, []).append((sig, x, y))
        if c in mudou:
            nds_rom.substituir(rom, c, bytes(imgs[0].d))
    for c, l in sorted(mudou.items()):
        print(f"  {c}: {l}")
    open(sys.argv[2], "wb").write(rom)
    print("->", sys.argv[2])
