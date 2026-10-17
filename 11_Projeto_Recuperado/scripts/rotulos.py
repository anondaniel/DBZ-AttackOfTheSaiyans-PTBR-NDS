"""Rotulos em imagem do menu, em PT-BR:
  MAIN MENU -> MENU    (letras do proprio jogo, centralizado)
  MEMBER    -> GRUPO   (R e U do jogo; G, O, P desenhados no mesmo estilo)
  HELP      -> DICAS   (fonte miuda de 5 linhas; AJUDA nao cabe nos 19 px)
Procura cada rotulo pelo padrao exato de pixels (indices 4bpp) em todos os
atlas dIMG (textura 4bpp, 128 bytes por linha) e folhas dCHR (tiles 8x8,
32 por linha), inclusive dentro de pacotes .a, e troca onde achar.
uso: rotulos.py <rom_entrada> <rom_saida>"""
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from fonte_grossa import HEX, _ler_atlas, _ler_chr, grade

# ---------------- fonte grossa (13 linhas, com contornos dos 2 lados)
R = ["111111..", "1777741.", "18888831", "1AA3AA41", "1BB3BB51", "1CCBCC31", "1DDDDA1.",
     "1DD4DD61", "1CC3CC61", "1BB3BB51", "19939941", "17727731", ".111111."]
U = ["1111.111", "15731771", "16931991", "17A31AA1", "18B31BB1", "19C31CC1", "1AD31DD1",
     "1AD31DD1", "19C31CC1", "18B31BB1", "15988981", "1167771.", "..1111.."]
O = [".111111.", "1167771.", "15988981", "17A31AA1", "18B31BB1", "19C31CC1", "1AD31DD1",
     "1AD31DD1", "19C31CC1", "18B31BB1", "15988981", "1167771.", ".111111."]
G = [".111111.", "1167771.", "15988981", "17A31111", "18B31...", "19C3111.", "1AD3ADD1",
     "1AD31DD1", "19C31CC1", "18B31BB1", "15988981", "1167771.", ".111111."]
P = ["111111..", "1777741.", "18888831", "1AA3AA41", "1BB3BB51", "1CCCCC31", "1DDDDA1.",
     "1DD1111.", "1CC1....", "1BB1....", "1991....", "1771....", "1111...."]


def palavra(glifos):
    """junta glifos sobrepondo 1 coluna (contorno direito de um = esquerdo do outro)"""
    linhas = list(glifos[0])
    for g in glifos[1:]:
        for r in range(13):
            a, b = linhas[r][-1], g[r][0]
            meio = "1" if "1" in (a, b) else (a if a != "." else b)
            linhas[r] = linhas[r][:-1] + meio + g[r][1:]
    return linhas


# ---------------- fonte miuda (HELP): letra '4' sobre fundo 'B'
MIUDA = {
    "D": ["44.", "4.4", "4.4", "4.4", "44."],
    "I": ["4", "4", "4", "4", "4"],
    "C": ["444", "4..", "4..", "4..", "444"],
    "A": ["444", "4.4", "444", "4.4", "4.4"],
    "S": ["444", "4..", "444", "..4", "444"],
}


def palavra_miuda(txt, largura, altura, letra, fundo):
    """letras (5 linhas) + fundo = dilatacao de 1 px em volta delas, como no jogo"""
    corpo = [""] * 5
    for k, ch in enumerate(txt):
        for r in range(5):
            corpo[r] += ("." if k else "") + MIUDA[ch][r]
    w = len(corpo[0]) + 2
    assert w <= largura, (txt, w, largura)
    x0 = (largura - w) // 2 + 1
    grid = [["."] * largura for _ in range(altura)]
    pts = [(r + 1, x0 + c) for r in range(5) for c, ch in enumerate(corpo[r]) if ch == "4"]
    for r, c in pts:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if 0 <= r + dr < altura and 0 <= c + dc < largura:
                    grid[r + dr][c + dc] = fundo
    for r, c in pts:
        grid[r][c] = letra
    return ["".join(l) for l in grid]


# ---------------- acesso a pixels
class Atlas:
    """dIMG 4bpp: w = 256 px, linhas de 128 bytes a partir de 0x208"""

    def __init__(self, d):
        self.d = bytearray(d)
        self.h = (len(d) - 0x208) // 128
        self.w = 256

    def get(self, x, y):
        b = self.d[0x208 + y * 128 + x // 2]
        return (b >> 4) if x & 1 else b & 15

    def set(self, x, y, v):
        i = 0x208 + y * 128 + x // 2
        b = self.d[i]
        self.d[i] = (b & 0x0F) | (v << 4) if x & 1 else (b & 0xF0) | v


class Folha:
    """dCHR: tiles 4bpp 8x8 em folha de 32 tiles de largura"""

    def __init__(self, d, ini=0):
        self.d = bytearray(d)
        npal, nt = d[ini + 5], struct.unpack_from("<H", d, ini + 6)[0]
        self.base = ini + 8 + npal * 32
        self.nt = min(nt, (len(d) - self.base) // 32)
        self.w, self.h = 256, ((self.nt + 31) // 32) * 8

    def _i(self, x, y):
        t = (y // 8) * 32 + x // 8
        if t >= self.nt:
            return None
        return self.base + t * 32 + (y % 8) * 4 + (x % 8) // 2

    def get(self, x, y):
        i = self._i(x, y)
        if i is None:
            return -1
        return (self.d[i] >> 4) if x & 1 else self.d[i] & 15

    def set(self, x, y, v):
        i = self._i(x, y)
        b = self.d[i]
        self.d[i] = (b & 0x0F) | (v << 4) if x & 1 else (b & 0xF0) | v


def achar(img, padrao):
    """posicoes (x, y) onde o padrao (lista de strings HEX, '.'=0) aparece"""
    ph, pw = len(padrao), len(padrao[0])
    alvo = [[HEX.index(c) if c != "." else 0 for c in l] for l in padrao]
    r = []
    for y in range(img.h - ph + 1):
        for x in range(img.w - pw + 1):
            if img.get(x, y) != alvo[0][0] or img.get(x + 1, y + 1) != alvo[1][1]:
                continue
            if all(img.get(x + c, y + l) == alvo[l][c] for l in range(ph) for c in range(pw)):
                r.append((x, y))
    return r


def pintar(img, x, y, largura, altura, novo):
    """limpa a caixa (0) e desenha 'novo' centralizado nela"""
    for l in range(altura):
        for c in range(largura):
            img.set(x + c, y + l, 0)
    nw = len(novo[0])
    x0 = x + (largura - nw) // 2
    for l, linha in enumerate(novo):
        for c, ch in enumerate(linha):
            if ch != ".":
                img.set(x0 + c, y + l, HEX.index(ch))


def trocas():
    at, ch = _ler_atlas(), _ler_chr()
    main_menu = grade(at, 114, 170, 49)            # 57 x 13
    menu = [l[28:] for l in main_menu]              # "MENU" do proprio jogo
    member = grade(ch, 186, 230, 18)                # 45 x 13 (ate o fecho do R)
    r = [("MAIN MENU", main_menu, menu), ("MEMBER", member, palavra([G, R, U, P, O]))]
    # HELP: 3 variantes de cor (letra, fundo), mesmo desenho; modelo tirado de bbg_us
    rom = open("/ds/rom/aots.nds", "rb").read()
    a = Atlas(nds_rom.ler(rom, "menu/icon/bbg_us.img"))
    modelo = ["".join(HEX[a.get(x, y)] for x in range(176, 195)) for y in range(25, 32)]
    for letra, fundo in (("4", "B"), ("4", "F"), ("9", "1")):
        antes = [l.replace("4", "L").replace("B", "G").replace("L", letra).replace("G", fundo) for l in modelo]
        r.append(("HELP", antes, palavra_miuda("DICAS", 19, 7, letra, fundo)))
    return r


def usado_pelo_us(c, todos):
    """so arquivos que a versao americana carrega: *_us, ou o base sem _us"""
    nome = c.rsplit("/", 1)[1]
    raiz, ext = nome.rsplit(".", 1)
    for lg in ("_en", "_fr", "_gr", "_it", "_sp"):
        if raiz.endswith(lg) and not raiz.endswith("_sp_us"):
            return False
    if raiz.endswith("_us"):
        return True
    return f"{c.rsplit('/', 1)[0]}/{raiz}_us.{ext}" not in todos


if __name__ == "__main__":
    rom = bytearray(open(sys.argv[1], "rb").read())
    alvo_rom = open("/ds/rom/aots.nds", "rb").read()
    lista = trocas()
    for nome, antes, depois in lista:
        print(nome, "->", len(depois[0]), "x", len(depois), "px (antes", len(antes[0]), "x", len(antes), ")")
        for l in depois:
            print("    ", l)
    mudou = {}
    todos = nds_rom.caminhos(alvo_rom)
    for c in todos:
        if not c.startswith("menu/icon/") or not usado_pelo_us(c, todos):
            continue
        d = nds_rom.ler(rom, c)
        imgs = []
        if d[:4] == b"dIMG":
            imgs.append(Atlas(d))
        elif d[:4] == b"dCHR":
            imgs.append(Folha(d))
        elif c.endswith(".a"):
            j = d.find(b"dCHR")
            buf = bytearray(d)
            while j >= 0:
                f = Folha(buf, j)
                f.d = buf  # edita o pacote inteiro
                imgs.append(f)
                j = d.find(b"dCHR", j + 4)
        for img in imgs:
            for nome, antes, depois in lista:
                for (x, y) in achar(img, antes):
                    pintar(img, x, y, len(antes[0]), len(antes), depois)
                    mudou.setdefault(c, []).append((nome, x, y))
        if c in mudou:
            novo = bytes(imgs[0].d)
            nds_rom.substituir(rom, c, novo)
    for c, l in sorted(mudou.items()):
        print(f"  {c}: {l}")
    open(sys.argv[2], "wb").write(rom)
    print("->", sys.argv[2])
