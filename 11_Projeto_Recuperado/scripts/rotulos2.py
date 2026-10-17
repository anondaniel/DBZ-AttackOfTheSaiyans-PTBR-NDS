"""Segunda leva de rotulos em imagem (PT-BR), depois de rotulos.py:
  menu_us.img : RESERVE -> RESERVA, ATTACKER -> ATACANTE (fonte miuda em caixa)
                FILE -> JOGO (fonte miuda com fundo em dilatacao, como o HELP)
  bbg_us.img  : ITEMS ACQUIRED -> ITENS OBTIDOS, BATTLE RESULTS -> RESULTADO
  rbg_us.img  : BONUS POINTS!! -> PONTOS EXTRAS!!
  rsp_us.chr  : LEVEL UP! (grande e pequeno) -> NIVEL +1!
  titlesp_us  : Continue -> Continuar, New Game -> Novo Jogo (normal e realcado)
Letreiros grandes: fonte vetorial (DejaVu Sans Bold) encaixada na caixa do
original; o contorno (1 ou 2 camadas) e a cor de cada linha sao lidos do
proprio letreiro original. Cada rotulo e procurado pelo padrao exato em
todos os arquivos que a versao US usa e trocado onde aparecer.
uso: rotulos2.py <rom_entrada> <rom_saida> [--previa]"""
import collections
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "/ds/scripts")
import nds_rom
from fonte_grossa import HEX
from rotulos import Atlas, Folha, MIUDA, achar, palavra_miuda, usado_pelo_us

FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# fonte miuda 4x5 em caixa (RESERVE/ATTACKER); '#' = letra
CAIXA = {
    "R": ["####", "#..#", "####", "#.#.", "#..#"],
    "E": ["####", "#...", "###.", "#...", "####"],
    "S": ["####", "#...", "####", "...#", "####"],
    "V": ["#..#", "#..#", "#..#", ".##.", ".##."],
    "A": [".##.", "#..#", "####", "#..#", "#..#"],
    "T": ["####", ".##.", ".##.", ".##.", ".##."],
    "C": ["####", "#...", "#...", "#...", "####"],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
}
MIUDA.update({
    "J": [".4", ".4", ".4", ".4", "44"],
    "O": ["444", "4.4", "4.4", "4.4", "444"],
    "G": ["444", "4..", "4.4", "4.4", "444"],
})


def ler_grade(img, x0, y0, x1, y1):
    return [[img.get(x, y) for x in range(x0, x1 + 1)] for y in range(y0, y1 + 1)]


def caixa(texto, largura, altura, letra, fundo):
    """caixa cheia de 'fundo' com letras 4x5 separadas por 1 coluna"""
    corpo = [""] * 5
    for k, ch in enumerate(texto):
        for r in range(5):
            corpo[r] += ("." if k else "") + CAIXA[ch][r]
    w = len(corpo[0])
    assert w + 2 <= largura, (texto, w + 2, largura)
    g = [[fundo] * largura for _ in range(altura)]
    x0 = (largura - w) // 2
    for r in range(5):
        for c, ch in enumerate(corpo[r]):
            if ch == "#":
                g[1 + r][x0 + c] = letra
    return g


def estilo(orig):
    """do letreiro original: indices do contorno (1 ou 2 camadas) e a cor
    de preenchimento de cada linha"""
    h, w = len(orig), len(orig[0])
    viz = lambda y, x: [(y + dy, x + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx)]
    dentro = lambda y, x: 0 <= y < h and 0 <= x < w

    def v(y, x):
        return orig[y][x] if dentro(y, x) else 0
    anel1 = {(y, x) for y in range(h) for x in range(w) if orig[y][x] and any(v(a, b) == 0 for a, b in viz(y, x))}
    c1 = collections.Counter(orig[y][x] for y, x in anel1).most_common(1)[0][0]
    anel2 = {(y, x) for y in range(h) for x in range(w) if orig[y][x] and (y, x) not in anel1
             and any((a, b) in anel1 for a, b in viz(y, x))}
    c2 = collections.Counter(orig[y][x] for y, x in anel2).most_common(1)[0][0] if anel2 else None
    duas = c2 is not None and c2 != c1 and sum(1 for p in anel2 if orig[p[0]][p[1]] == c2) > 0.5 * len(anel2)
    borda = anel1 | (anel2 if duas else set())
    linha = []
    for y in range(h):
        cs = collections.Counter(orig[y][x] for x in range(w) if orig[y][x] and (y, x) not in borda
                                 and orig[y][x] not in (c1, c2 if duas else -1))
        linha.append(cs.most_common(1)[0][0] if cs else None)
    # linhas sem miolo herdam a vizinha
    for y in range(h):
        if linha[y] is None:
            prox = [linha[j] for j in sorted(range(h), key=lambda j: abs(j - y)) if linha[j] is not None]
            linha[y] = prox[0] if prox else c1
    return (c2, c1) if duas else (c1,), linha


def letreiro(texto, orig):
    """grade nova (mesmo tamanho) com o texto no estilo do original"""
    h, w = len(orig), len(orig[0])
    contornos, linha = estilo(orig)
    L = len(contornos)
    # linhas e colunas uteis do original (fora do vazio)
    ys = [y for y in range(h) if any(orig[y])]
    y0, y1 = min(ys) + L, max(ys) - L
    hin, win = y1 - y0 + 1, w - 2 * L
    f = ImageFont.truetype(FONTE, 200)
    bb = f.getbbox(texto)
    m = Image.new("L", (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), 0)
    ImageDraw.Draw(m).text((10 - bb[0], 10 - bb[1]), texto, font=f, fill=255)
    m = m.crop(m.getbbox())
    esc = hin / m.height
    nw = min(win, max(1, round(m.width * esc)))
    m = m.resize((nw, hin), Image.LANCZOS).point(lambda v: 255 if v >= 120 else 0)
    tinta = set()
    x0 = L + (win - nw) // 2
    for yy in range(hin):
        for xx in range(nw):
            if m.getpixel((xx, yy)):
                tinta.add((y0 + yy, x0 + xx))
    g = [[0] * w for _ in range(h)]
    atual = set(tinta)
    for camada in contornos:  # (interna, externa): a interna encosta na letra
        nova = {(y + dy, x + dx) for y, x in atual for dy in (-1, 0, 1) for dx in (-1, 0, 1)} - atual
        for y, x in nova:
            if 0 <= y < h and 0 <= x < w:
                g[y][x] = camada
        atual |= nova
    for y, x in tinta:
        g[y][x] = linha[y]
    return g


def para_str(g):
    return ["".join(HEX[v] if v else "." for v in l) for l in g]


# (arquivo modelo, caixa x0,y0,x1,y1, tipo, texto)
TRABALHOS = [
    ("menu/icon/menu_us.img", (61, 41, 96, 47), "caixa", "RESERVA"),
    ("menu/icon/menu_us.img", (58, 49, 100, 55), "caixa", "ATACANTE"),
    ("menu/icon/menu_us.img", (176, 32, 191, 38), "miuda", "JOGO"),
    ("menu/icon/bbg_us.img", (144, 147, 225, 167), "ttf", "ITENS OBTIDOS"),
    ("menu/icon/bbg_us.img", (145, 170, 242, 190), "ttf", "RESULTADO"),
    ("menu/icon/rbg_us.img", (145, 97, 234, 109), "ttf", "PONTOS EXTRAS!!"),
    ("menu/icon/rsp_us.chr", (1, 2, 124, 30), "ttf", "NÍVEL +1!"),
    ("menu/icon/rsp_us.chr", (1, 32, 63, 47), "ttf", "NÍVEL +1!"),
    ("menu/icon/titlesp_us.chr", (1, 0, 70, 14), "ttf", "Continuar"),
    ("menu/icon/titlesp_us.chr", (81, 0, 152, 14), "ttf", "Continuar"),
    ("menu/icon/titlesp_us.chr", (0, 16, 80, 30), "ttf", "Novo Jogo"),
    ("menu/icon/titlesp_us.chr", (81, 16, 161, 30), "ttf", "Novo Jogo"),
]


def abrir(d):
    return Atlas(d) if d[:4] == b"dIMG" else Folha(d)


def montar(rom):
    r = []
    for arq, (x0, y0, x1, y1), tipo, texto in TRABALHOS:
        img = abrir(nds_rom.ler(rom, arq))
        orig = ler_grade(img, x0, y0, x1, y1)
        w, h = x1 - x0 + 1, y1 - y0 + 1
        if tipo == "caixa":
            c = collections.Counter(v for l in orig for v in l if v)
            fundo = orig[0][0]
            letra = [k for k, _ in c.most_common() if k != fundo][0]
            novo = caixa(texto, w, h, letra, fundo)
        elif tipo == "miuda":
            c = collections.Counter(v for l in orig for v in l if v)
            (fundo, _), (letra, _) = c.most_common(2)
            novo = [[HEX.index(ch) if ch != "." else 0 for ch in l]
                    for l in palavra_miuda(texto, w, h, HEX[letra], HEX[fundo])]
        else:
            novo = letreiro(texto, orig)
        r.append((arq, texto, para_str(orig), para_str(novo)))
    return r


if __name__ == "__main__":
    rom = bytearray(open(sys.argv[1], "rb").read())
    orig_rom = open("/ds/rom/aots.nds", "rb").read()
    trabalhos = montar(orig_rom)
    if "--previa" in sys.argv:
        E = 4
        alt = sum(len(a) * E + 8 for _, _, a, _ in trabalhos)
        larg = max(len(a[0]) for _, _, a, _ in trabalhos) * E * 2 + 30
        im = Image.new("RGB", (larg, alt), (40, 40, 60))
        dr = ImageDraw.Draw(im)
        y = 0
        for arq, texto, antes, depois in trabalhos:
            for k, g in enumerate((antes, depois)):
                x0 = k * (len(g[0]) * E + 20)
                for l, linha in enumerate(g):
                    for c, ch in enumerate(linha):
                        if ch != ".":
                            v = HEX.index(ch)
                            cor = (v * 17, v * 17, v * 17) if v != 1 else (20, 10, 10)
                            dr.rectangle((x0 + c * E, y + l * E, x0 + c * E + E - 1, y + l * E + E - 1), fill=cor)
            y += len(antes) * E + 8
        im.save("/ds/saida/rotulos2_previa.png")
        print("previa -> /ds/saida/rotulos2_previa.png")
        sys.exit()
    todos = nds_rom.caminhos(orig_rom)
    mudou = {}
    for c in todos:
        if not c.startswith("menu/icon/") or not usado_pelo_us(c, todos):
            continue
        d = nds_rom.ler(rom, c)
        if d[:4] not in (b"dIMG", b"dCHR"):
            continue
        img = abrir(d)
        for arq, texto, antes, depois in trabalhos:
            for (x, y) in achar(img, antes):
                for l, linha in enumerate(depois):
                    for k, ch in enumerate(linha):
                        img.set(x + k, y + l, HEX.index(ch) if ch != "." else 0)
                mudou.setdefault(c, []).append((texto, x, y))
        if c in mudou:
            nds_rom.substituir(rom, c, bytes(img.d))
    for c, l in sorted(mudou.items()):
        print(f"  {c}: {l}")
    faltou = {t for _, t, _, _ in trabalhos} - {t for l in mudou.values() for t, _, _ in l}
    print("nao achados:", faltou or "nenhum")
    open(sys.argv[2], "wb").write(rom)
    print("->", sys.argv[2])
