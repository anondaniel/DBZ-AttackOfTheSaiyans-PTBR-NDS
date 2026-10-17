"""Cartoes de titulo de capitulo em PT-BR (fld/map/CNN/CNN_9999us.map e en).
Fundo limpo (titulo_fundo.py) + letreiro novo no mesmo estilo (branco,
contorno preto de 1 px, fonte negrito condensada), nas mesmas alturas das 2
linhas originais; paleta de 256 cores refeita; recomprimido (imp_comprimir).
uso: titulos.py [NN ...]  -> /ds/saida/titulos/CNN_9999us.map + previa_CNN.png"""
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "/ds/scripts")
import imp
import nds_rom
from imp_comprimir import comprimir
from titulo_fundo import e_letreiro, fundo, ler_map

FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TITULOS = {
    0: ("O Momento da Partida!", "Rumo a Alturas Ainda Maiores..."),
    1: ("Retomem o Templo!", "A Volta Emocionada do Kuririn"),
    2: ("A Sokidan Mortal do Yamcha!", "Quem Está no Esconderijo?"),
    3: ("Tenshinhan, o Todo-Poderoso", "O Ataque Supremo Multiforma!"),
    4: ("Um Novo Salto Adiante!", "O Torneio Caótico"),
    5: ("O Cutelo em Apuros?!", "Vestido de Noiva em Chamas"),
    6: ("O Lutador Mais Forte", "Raditz Aparece!"),
    7: ("Não Chore, Gohan!", "A Primeira Batalha"),
    8: ("Um Novo Salto Adiante!", "Rumo ao Kami-Sama"),
    9: ("O Espanto do Senhor Enma!", "Luta no Outro Mundo"),
    10: ("As Esferas Perdidas!", "Um Longo Caminho até a Vitória"),
    11: ("Aguente Firme, Gohan!", "O Treino Duro do Piccolo"),
    12: ("Mostrem do que São Capazes!", "O Pulso dos Lutadores"),
    13: ("A Técnica Suprema!", "O Poder da Genki Dama"),
    14: ("Os Saiyajins Chegaram!", "Um Confronto Todo-Poderoso"),
    15: ("Batalhas Além do Infinito!", "Poder Explosivo Liberado!"),
    16: ("O Fim da Batalha Feroz...", "A Chave É o Lar do Piccolo"),
}
BRANCO, PRETO = (255, 255, 255), (16, 16, 16)
LARG_MAX = 244


def centros(ys):
    """centro vertical das 2 linhas de texto da versao US (ys = linhas com letreiro)"""
    grupos, atual = [], [ys[0]]
    for y in ys[1:]:
        if y - atual[-1] > 2:
            grupos.append(atual)
            atual = [y]
        else:
            atual.append(y)
    grupos.append(atual)
    grupos = sorted(grupos, key=len, reverse=True)[:2]
    return sorted((g[0] + g[-1]) / 2 for g in grupos)


def letreiro(texto, alt=14):
    """imagem RGBA do texto: branco, contorno preto, condensado"""
    f = ImageFont.truetype(FONTE, alt)
    bx = f.getbbox(texto)
    w, h = bx[2] - bx[0] + 4, bx[3] - bx[1] + 4
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((2 - bx[0], 2 - bx[1]), texto, font=f, fill=255)
    # condensa para lembrar a fonte original (estreita)
    cw = int(w * 0.82)
    m = m.resize((cw, h), Image.LANCZOS).point(lambda v: 255 if v >= 110 else 0)
    if cw > LARG_MAX:
        m = m.resize((LARG_MAX, h), Image.LANCZOS).point(lambda v: 255 if v >= 110 else 0)
    w = m.width
    out = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))
    mp = m.load()
    op = out.load()
    for y in range(h):
        for x in range(w):
            if mp[x, y]:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        op[x + 1 + dx, y + 1 + dy] = PRETO + (255,)
    for y in range(h):
        for x in range(w):
            if mp[x, y]:
                op[x + 1, y + 1] = BRANCO + (255,)
    return out


# Capitulos em que sobravam pontinhos do letreiro antigo fora do texto novo
# (C07: manchas cinza nas pontas da 1a linha; C00: restos na areia sob a 2a).
LIMPA_SOBRAS = {0, 7}


def limpar_sobras(rom, n, out, w, h, pegada):
    """Onde o letreiro US antigo estava e o novo nao cobre: so aceita a cor
    se >= 2 versoes de idioma sem texto ali concordam exatamente; o resto e
    preenchido pela media dos vizinhos. (Com 1 versao so, a borda cinza
    antisserrilhada do letreiro dela passava como fundo.)"""
    import collections

    from dump_tiles import rgb
    from titulo_fundo import mascara, versoes
    vs = versoes(rom, n)
    cores = {lg: [rgb(v[2][p]) for p in v[3]] for lg, v in vs.items()}
    comum = [collections.Counter(cores[lg][i] for lg in cores) for i in range(w * h)]
    masc = {lg: mascara(c, w, h, (20, 172), comum) for lg, c in cores.items()}

    def dilata(conj, r):
        return {(y + dy) * w + (x + dx) for i in conj for y, x in [divmod(i, w)]
                for dy in range(-r, r + 1) for dx in range(-r, r + 1)
                if 0 <= y + dy < h and 0 <= x + dx < w}
    antigo = dilata({i for i in range(w * h) if masc["us"][i]}, 1)
    area = antigo - dilata(pegada, 1)
    out = list(out)
    pend = set()
    for i in area:
        votos = collections.Counter(cores[lg][i] for lg in cores if not masc[lg][i])
        cor, nv = votos.most_common(1)[0] if votos else (None, 0)
        if nv >= 2:
            out[i] = cor
        else:
            pend.add(i)
    # fundo confiavel: fora do letreiro antigo, ou com >= 2 versoes de acordo.
    # Cada buraco recebe a media, pesada por 1/distancia, do pixel confiavel
    # mais proximo nas 4 direcoes (a difusao vizinho-a-vizinho fazia riscos).
    ruim = (antigo - area) | pend  # sob o texto novo o fundo tambem e duvidoso
    novos = {}
    for i in pend:
        y, x = divmod(i, w)
        soma, peso = [0.0, 0.0, 0.0], 0.0
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            yy, xx, d = y + dy, x + dx, 1
            while 0 <= yy < h and 0 <= xx < w and yy * w + xx in ruim:
                yy, xx, d = yy + dy, xx + dx, d + 1
            if 0 <= yy < h and 0 <= xx < w:
                c = out[yy * w + xx]
                for k in range(3):
                    soma[k] += c[k] / d
                peso += 1 / d
        if peso:
            novos[i] = tuple(int(round(s / peso)) for s in soma)
    for i, c in novos.items():
        out[i] = c
    print(f"C{n:02d}: {len(area)} pixels de sobra revistos, {len(pend)} interpolados")
    return out


def montar(rom, n):
    w, h, out, ys, _ = fundo(rom, n)
    textos = []
    for (texto, yc) in zip(TITULOS[n], centros(ys)):
        l = letreiro(texto)
        # recorta a caixa util (sem margem transparente)
        bb = l.getbbox()
        l = l.crop(bb)
        textos.append((l, ((w - l.width) // 2, int(round(yc - l.height / 2)))))
    if n in LIMPA_SOBRAS:
        pegada = set()
        for l, (x0, y0) in textos:
            a = l.getchannel("A").load()
            pegada |= {(y0 + y) * w + x0 + x for y in range(l.height) for x in range(l.width)
                       if a[x, y] and 0 <= y0 + y < h and 0 <= x0 + x < w}
        out = limpar_sobras(rom, n, out, w, h, pegada)
    im = Image.new("RGB", (w, h))
    im.putdata(out)
    for l, pos in textos:
        im.paste(l, pos, l)
    return im


def para_map(rom, n, im):
    """quantiza em 256 cores (indice 0 = cor 0 original) e monta o dMAP"""
    base = nds_rom.ler(rom, f"fld/map/C{n:02d}/C{n:02d}_9999us.map")
    q = im.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal_rgb = q.getpalette()[:255 * 3]
    px = bytes(v + 1 for v in q.get_flattened_data())
    pal = [struct.unpack_from("<H", base, 0x10)[0]]
    for k in range(255):
        r, g, b = pal_rgb[3 * k:3 * k + 3]
        pal.append((r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10))
    z = comprimir(px, im.width)
    fim_velho = struct.unpack_from("<I", base, 8)[0]
    cauda = base[fim_velho:]
    novo = bytearray(base[:0x10]) + struct.pack("<256H", *pal) + z
    struct.pack_into("<I", novo, 8, len(novo))
    novo += cauda
    # confere: o jogo vai descomprimir exatamente estes pixels
    back, fim = imp.descomprimir(bytes(novo), im.width, im.height, 0x210)
    assert back == px and fim == struct.unpack_from("<I", novo, 8)[0]
    return bytes(novo), px, pal


if __name__ == "__main__":
    import os
    from dump_tiles import rgb
    rom = open("/ds/rom/aots.nds", "rb").read()
    ns = [int(a) for a in sys.argv[1:]] or list(TITULOS)
    os.makedirs("/ds/saida/titulos", exist_ok=True)
    for n in ns:
        im = montar(rom, n)
        d, px, pal = para_map(rom, n, im)
        open(f"/ds/saida/titulos/C{n:02d}_9999us.map", "wb").write(d)
        prev = Image.new("RGB", im.size)
        prev.putdata([rgb(pal[v]) for v in px])
        prev.save(f"/ds/saida/titulos/previa_C{n:02d}.png")
        print(f"C{n:02d}: {len(d)} bytes (antes {len(nds_rom.ler(rom, f'fld/map/C{n:02d}/C{n:02d}_9999us.map'))})")
