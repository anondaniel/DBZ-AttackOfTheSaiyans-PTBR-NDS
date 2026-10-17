"""Faixas com o nome do local ao chegar ("~West City~") em PT-BR.

Ficam em ef/esd/ceNNN_5L0.evd (NNN = 802..846, um por local; L = idioma:
0 JP, 1 US, 2 EN, 3 FR, 4 GR, 5 IT, 6 SP). O .evd e LZ10; descomprimido:
  0x0C 'EVD' ...; 0x2C: tira de nuvens (64x8); 0x22C: textura do texto,
  A3I5 64x16 (alfa = v>>5, cor = v&31); 0x62C: paleta de 32 cores.
  (ce808, ce830, ce843: textura 32x16 e paleta em 0x42C; o cabecalho diz.)
Na tela a textura aparece esticada 2x na horizontal (64 texels = 128 px) e o
texto da a volta na borda, como nas faixas de batalha.

Como nos originais, o texto fica centrado no texel 0 (da a volta na borda)
e o .esd do local diz a largura dele (u32 20.12 em 0x20 e 0x4C; 0xA6 cresce
junto). O texto novo usa a fonte pixelada de fonte_faixa.py, com contorno e
cor de cada linha lidos do original (rotulos2.estilo). Para cada local ha
alternativas em ordem de preferencia: nome inteiro com "~", nome inteiro sem
"~", nome curto. Troca US (510) e EN (520).

uso: faixas_locais.py <rom_entrada> <rom_saida> [--previa]
     faixas_locais.py <rom> --ler      (so desenha as faixas originais)"""
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "/ds/scripts")
import fonte_faixa
import nds_rom
from rotulos2 import FONTE, estilo

H, T = 16, 0x22C
W = 64  # largura da textura do arquivo atual (layout() ajusta: 64 ou 32)
PAL = 0x62C
IDIOMAS = ("510", "520")
NOMES = {  # ceNNN: [nome, alternativas mais curtas]. Lidos das faixas
    # US/FR/GR/IT/SP; os nomes seguem os ja usados no ptbr.json / cf_mes_LOC.
    "ce802": ["Floresta de Bambu"],        # Bump Forest (mapas bam)
    "ce803": ["Vaso do Diabo"],            # Devil's Toilet (ben = benjo)
    "ce804": ["Templo das Artes Marciais", "Templo Marcial"],
    "ce806": ["Cidade do Leste"],
    "ce807": ["Castelo do Cutelo"],        # Ox-King's Castle
    "ce808": ["Esgoto"],
    "ce809": ["Templo Orin"],
    "ce810": ["Casa do Goku"],
    "ce811": ["Estrada da Serpente", "Via da Serpente"],      # Snake Way
    "ce812": ["Planície Holly"],
    "ce813": ["Vila Jingle"],
    "ce814": ["Caverna dos Piratas", "Caverna Pirata"],
    "ce815": ["Casa do Kame"],
    "ce816": ["Torre Karin"],
    "ce817": ["Planeta do Senhor Kaioh", "Planeta do Kaioh"],
    "ce818": ["Deserto Break"],
    "ce819": ["Travessia Divina"],
    "ce821": ["Torre Muscle"],
    "ce822": ["Campo do Mutaito"],
    "ce824": ["Ruínas de Nemuria"],
    "ce826": ["Montanha Paozu"],
    "ce828": ["Fonte do Eremita"],
    "ce829": ["Terra Sagrada de Karin", "Terra de Karin"],
    "ce830": ["Deserto"],
    "ce832": ["Ilha de Treinamento", "Ilha de Treino"],
    "ce833": ["Cidade do Oeste"],
    "ce834": ["Planalto Yunzabit"],
    "ce835": ["Ermo do Espinafre"],
    "ce836": ["Palácio do Senhor Enma", "Palácio do Enma"],   # King Yemma's Mansion
    "ce837": ["Monte Frappe"],
    "ce838": ["Montanha 5 Elementos", "Mt. 5 Elementos", "5 Elementos"],
    "ce839": ["Vulcão Kiwi"],
    "ce840": ["Palácio da Vovó Uranai", "Palácio da Vovó"],
    "ce841": ["Mansão da Princesa", "Casa da Princesa"],       # Princess' Mansion
    "ce842": ["Floresta de Enma"],
    "ce843": ["Inferno"],                  # Hell
    "ce844": ["Castelo do Pilaf"],
    "ce845": ["Ermo Páprica"],
    "ce846": ["Ermo Gizard"],
}


def layout(u):
    """offsets do cabecalho: paleta = 0x2C + u32@0x20; textura = 0x2C + u32@0x38"""
    global W, PAL
    import struct
    PAL = 0x2C + struct.unpack_from("<I", u, 0x20)[0]
    tex = 0x2C + struct.unpack_from("<I", u, 0x38)[0]
    assert tex == T, hex(tex)
    W = (PAL - T) // H


def ler_evd(rom, c):
    d = nds_rom.ler(rom, c)
    u = nds_rom.lz10_descomprimir(d)
    u = bytearray(u[:0x0C + int.from_bytes(u[8:12], "little")])
    layout(u)
    return u


def grade(u):
    return [[u[T + y * W + x] for x in range(W)] for y in range(H)]


def inicio_texto(g):
    """coluna onde o texto comeca (fim do maior vao vazio, em circulo)"""
    ocupada = [any(g[y][x] >> 5 for y in range(H)) for x in range(W)]
    melhor, ini = 0, 0
    for x0 in range(W):
        n = 0
        while n < W and not ocupada[(x0 + n) % W]:
            n += 1
        if n > melhor:
            melhor, ini = n, x0
    return (ini + melhor) % W, W - melhor


def desenrola(g, base):
    return [[g[y][(base + x) % W] for x in range(W)] for y in range(H)]


def texto_meia_largura(texto, orig, largura_max):
    """como rotulos2.letreiro, mas com largura natural / 2 (tela estica 2x)"""
    contornos, linha = estilo(orig)
    L = len(contornos)
    ys = [y for y in range(H) if any(v >> 5 for v in orig[y])]
    y0, y1 = min(ys) + L, max(ys) - L
    hin = y1 - y0 + 1
    f = ImageFont.truetype(FONTE, 200)
    bb = f.getbbox(texto)
    m = Image.new("L", (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), 0)
    ImageDraw.Draw(m).text((10 - bb[0], 10 - bb[1]), texto, font=f, fill=255)
    m = m.crop(m.getbbox())
    nw = min(largura_max - 2 * L, max(1, round(m.width * hin / m.height / 2)))
    m = m.resize((nw, hin), Image.LANCZOS).point(lambda v: 255 if v >= 80 else 0)
    tinta = {(y0 + yy, L + xx) for yy in range(hin) for xx in range(nw) if m.getpixel((xx, yy))}
    g = [[0] * (nw + 2 * L) for _ in range(H)]
    atual = set(tinta)
    for camada in contornos:
        nova = {(y + dy, x + dx) for y, x in atual for dy in (-1, 0, 1) for dx in (-1, 0, 1)} - atual
        for y, x in nova:
            if 0 <= y < H and 0 <= x < len(g[0]):
                g[y][x] = camada
        atual |= nova
    for y, x in tinta:
        g[y][x] = linha[y]
    return g


def colunas_til(orig):
    """quantas colunas no comeco e no fim sao o "~" (so ocupam o meio da
    altura; as letras e o contorno delas vao quase do topo ao pe)"""
    ys = [y for y in range(H) if any(orig[y])]
    topo, pe = min(ys), max(ys)
    w = len(orig[0])

    def baixa(x):
        oc = [y for y in range(H) if orig[y][x]]
        return not oc or (min(oc) > topo + 2 and max(oc) < pe - 2)
    a = 0
    while a < w and baixa(a):
        a += 1
    b = 0
    while b < w and baixa(w - 1 - b):
        b += 1
    return a, b


# a paleta vai do azul-marinho (0) ao branco (31). O contorno e o do original:
# semitransparente (alfa 2), porque o jogo desenha a faixa 2x, com uma copia
# deslocada (0x20 e 0x4C do .esd); com contorno opaco uma copia apaga a outra.
CONTORNO = (2 << 5) | 4
DEGRADE = [31, 31, 31, 30, 30, 29, 28, 27, 26, 25]  # por linha da fonte: branco em cima, azul-claro embaixo


def texto_pixel(nomes, orig):
    """escolhe a primeira alternativa que cabe (com "~", sem "~", nome curto)
    e desenha na fonte pixelada: contorno azul-marinho, miolo em degrade.
    (O estilo lido por frequencia, rotulos2.estilo, pegava tons escuros no
    topo das letras e o C virava L, o O virava U.)"""
    contornos, L = (CONTORNO,), 1
    for nome in nomes:
        for til in (True, False):
            if fonte_faixa.largura(nome, til) + 2 * L <= W - 2:
                break
        else:
            continue
        break
    else:
        raise ValueError(f"nao cabe: {nomes}")
    ys = [y for y in range(H) if any(orig[y])]
    topo = max(L, max(ys) - L - 9)  # linha 9 da fonte (descendente) na ultima linha util
    tinta = {(topo + y, L + x) for y, x in fonte_faixa.tinta(nome, til)}
    g = [[0] * (fonte_faixa.largura(nome, til) + 2 * L) for _ in range(H)]
    atual = set(tinta)
    for camada in contornos:
        nova = {(y + dy, x + dx) for y, x in atual for dy in (-1, 0, 1) for dx in (-1, 0, 1)} - atual
        for y, x in nova:
            if 0 <= y < H and 0 <= x < len(g[0]):
                g[y][x] = camada
        atual |= nova
    for y, x in tinta:
        g[y][x] = (7 << 5) | DEGRADE[y - topo]
    return g, ("~%s~" % nome) if til else nome


def nova_textura(u, nomes):
    """texto novo centrado no texel 0, como os originais. Devolve textura,
    grade antiga, grade nova, largura antiga, largura nova e o texto usado."""
    g = grade(u)
    x0, larg = inicio_texto(g)
    des = desenrola(g, x0)
    # texel vazio tem alfa 0 mas indice != 0: zera, senao o estilo o toma por letra
    orig = [[v if v >> 5 else 0 for v in l[:larg]] for l in des]
    novo, usado = texto_pixel(nomes, orig)
    n = len(novo[0])
    vazio = u[T]  # valor do texel vazio (alfa 0)
    # mesmo centro do original: texel 0 nas texturas de 64, texel 16 nas de 32
    # (ce808/830/843; centrar no 0 partia "Esgoto" em dois na tela)
    ini = round(x0 + larg / 2 - n / 2)
    out = [[vazio] * W for _ in range(H)]
    for y in range(H):
        for x, v in enumerate(novo[y]):
            if v:
                out[y][(ini + x) % W] = v
    return bytes(v for l in out for v in l), orig, novo, larg, n, usado


def para_png(linhas_rgb, escala=4):
    """lista de (rotulo, grade, paleta) -> imagem esticada 2x como na tela"""
    alt = H * escala + 4
    im = Image.new("RGB", (64 * 2 * escala, alt * len(linhas_rgb)), (40, 40, 40))
    for k, (g, pal) in enumerate(linhas_rgb):
        for y in range(H):
            for x in range(len(g[0])):
                v = g[y][x]
                if v >> 5:
                    c = pal[v & 31]
                    for dy in range(escala):
                        for dx in range(2 * escala):
                            im.putpixel((x * 2 * escala + dx, k * alt + y * escala + dy), c)
    return im


def paleta(u):
    r = []
    for i in range(32):
        p = u[PAL + 2 * i] | u[PAL + 2 * i + 1] << 8
        r.append(((p & 31) * 8, (p >> 5 & 31) * 8, (p >> 10 & 31) * 8))
    return r


def familias(rom):
    return sorted({c.split("/")[-1][:5] for c in nds_rom.caminhos(rom)
                   if c.startswith("ef/esd/ce8") and c.endswith("_510.evd")})


if __name__ == "__main__":
    rom = bytearray(open(sys.argv[1], "rb").read())
    fams = familias(rom)
    if "--ler" in sys.argv:
        linhas = []
        for f in fams:
            u = ler_evd(rom, f"ef/esd/{f}_510.evd")
            g = grade(u)
            x0, _ = inicio_texto(g)
            linhas.append((desenrola(g, (x0 - 1) % W), paleta(u)))
        para_png(linhas, 3).save("/ds/saida/faixas_locais_orig.png")
        print(len(fams), "faixas ->", "/ds/saida/faixas_locais_orig.png", fams)
        sys.exit()
    faltam = [f for f in fams if f not in NOMES]
    assert not faltam, f"sem nome: {faltam}"
    previas = []
    for f in fams:
        for lg in IDIOMAS:
            c = f"ef/esd/{f}_{lg}.evd"
            u = ler_evd(rom, c)
            tex, velho, novo, larg, n, usado = nova_textura(u, NOMES[f])
            if lg == "510":
                previas += [(velho, paleta(u)), (novo, paleta(u))]
                print(f"{f} {usado}: {larg} -> {n} texels")
            u[T:T + W * H] = tex
            c2 = nds_rom.lz10_comprimir(bytes(u))
            assert nds_rom.lz10_descomprimir(c2)[:len(u)] == bytes(u)
            # .esd: 0x20 e 0x4C = largura do texto (20.12) e 0xA6 cresce com
            # ela; mantem a diferenca do original para a largura antiga
            ce = f"ef/esd/{f}_{lg}.esd"
            e = bytearray(nds_rom.ler(rom, ce))
            for o in (0x20, 0x4C):
                v = struct.unpack_from("<i", e, o)[0]
                struct.pack_into("<i", e, o, v + ((n - larg) << 12))
            a6 = struct.unpack_from("<H", e, 0xA6)[0]
            struct.pack_into("<H", e, 0xA6, min(0xFFFF, round(a6 * n / larg)))
            if "--previa" not in sys.argv:
                nds_rom.substituir(rom, c, c2)
                nds_rom.substituir(rom, ce, bytes(e))
    if "--previa" in sys.argv:
        para_png(previas, 3).save("/ds/saida/faixas_locais_previa.png")
        print("previa -> /ds/saida/faixas_locais_previa.png")
        sys.exit()
    open(sys.argv[2], "wb").write(rom)
    print(f"{len(fams)} locais x {len(IDIOMAS)} idiomas -> {sys.argv[2]}")
