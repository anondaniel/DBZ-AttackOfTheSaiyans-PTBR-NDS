import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, 'C:/Projetos/09_Dragon_Ball_Z_Attack_of_the_Saiyans/18_Pele_e_Texto_Boot/scripts')  # comum.rom('nova') = ROM 13.1
from comum import rom
from dados_inimigos import enemy_rows
from sprites import render, ANC_X, ANC_Y, dados_linhas
from PIL import Image, ImageDraw, ImageFont

OUT = 'C:/Projetos/09_Dragon_Ball_Z_Attack_of_the_Saiyans/18_Pele_e_Texto_Boot/midia/antes_depois'
os.makedirs(OUT, exist_ok=True)
XW0, XW1 = -90, 110
PW = XW1 - XW0
BG = (24, 28, 36); PANEL = (44, 50, 64); TXT = (240, 240, 240); SUB = (168, 178, 198); ACC = (255, 200, 90)
LOG_W = 1060; TEXT_W = 560; M = 16; HEAD = 84; MIN_H = 92

def font(size, bold=False):
    p = 'C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf'
    try:
        return ImageFont.truetype(p, size)
    except OSError:
        return ImageFont.load_default()

orig = rom('orig'); nova = rom('nova')
eo = enemy_rows(orig, 'EN'); en = enemy_rows(nova, 'US')
entradas = []
for r in dados_linhas():
    i = int(r['linha'])
    a = render(orig, eo[i]['file'], eo[i]['palno'])
    b = render(nova, en[i]['file'], en[i]['palno'])
    ba, bb = a.getbbox(), b.getbbox()
    for bx in (ba, bb):
        assert bx[0] - ANC_X >= XW0 and bx[2] - ANC_X <= XW1, (i, bx)
    y0 = min(ba[1], bb[1]) - ANC_Y - 6
    y1 = max(ba[3], bb[3]) - ANC_Y + 6
    entradas.append(dict(linha=i, animal=eo[i]['_nome'], antes=r['nome_rc1'], depois=r['nome_final'],
                         a=a, b=b, y0=y0, y1=y1,
                         fo=(eo[i]['file'], eo[i]['palno']), fn=(en[i]['file'], en[i]['palno'])))

def painel(sp, y0, y1, S):
    H = y1 - y0
    base = Image.new('RGBA', (PW, H), PANEL + (255,))
    base.alpha_composite(sp.crop((ANC_X + XW0, ANC_Y + y0, ANC_X + XW1, ANC_Y + y1)))
    return base.convert('RGB').resize((round(PW * S), round(H * S)), Image.NEAREST)

def gerar(lista, S, saida, titulo, subtitulo, publico=False):
    px = lambda v: round(v * S)
    rows_h = [max(e['y1'] - e['y0'], MIN_H) + 16 for e in lista]
    H_total = px(HEAD) + sum(px(h) for h in rows_h) + px(10)
    img = Image.new('RGB', (px(LOG_W), H_total), BG)
    d = ImageDraw.Draw(img)
    f_t, f_sub, f_h = font(px(20), True), font(px(13)), font(px(12), True)
    f_b, f_m, f_s = font(px(17), True), font(px(14)), font(px(13))
    d.text((px(M), px(10)), titulo, font=f_t, fill=TXT)
    d.text((px(M), px(38)), subtitulo, font=f_sub, fill=SUB)
    xa = M; xs = M + PW + 44; xt = xs + PW + 24
    d.text((px(xa), px(64)), 'JOGO ORIGINAL' if publico else 'ORIGINAL (jogo base)', font=f_h, fill=ACC)
    d.text((px(xs), px(64)), 'TRADUÇÃO PT-BR' if publico else 'VERSÃO 13.1 (nova)', font=f_h, fill=ACC)
    d.text((px(xt), px(64)), 'ORIGINAL  →  PT-BR' if publico else 'NOME: rc.1  →  13.1', font=f_h, fill=ACC)
    y = HEAD
    for e, rh in zip(lista, rows_h):
        top = y
        pa = painel(e['a'], e['y0'], e['y1'], S); pb = painel(e['b'], e['y0'], e['y1'], S)
        py = top + 8
        img.paste(pa, (px(xa), px(py)))
        img.paste(pb, (px(xs), px(py)))
        ax = px(M + PW + 6); ay = px(py + (e['y1'] - e['y0']) / 2 - 10)
        d.text((ax, ay), '→', font=font(px(22), True), fill=ACC)
        ty = px(top + 8)
        tx = px(xt)
        if publico:
            d.text((tx, ty), e['depois'], font=f_b, fill=TXT)
            d.text((tx, ty + px(24)), f"no lugar de: {e['animal']}", font=f_m, fill=SUB)
        else:
            d.text((tx, ty), f"{e['antes']}  →  {e['depois']}", font=f_b, fill=TXT)
            d.text((tx, ty + px(22)), f"Linha {e['linha']} · animal original: {e['animal']}", font=f_m, fill=SUB)
            d.text((tx, ty + px(42)), f"Original: {e['fo'][0]} pal. {e['fo'][1]}   |   13.1: {e['fn'][0]} pal. {e['fn'][1]}", font=f_s, fill=SUB)
            mudou = 'Sprite trocado' if e['fo'][0] != e['fn'][0] else 'Mesmo sprite, paleta nova'
            d.text((tx, ty + px(60)), mudou, font=f_s, fill=ACC)
        if px(xt + TEXT_W) > img.width:
            print('AVISO texto largo', e['linha'], d.textlength(f"{e['antes']}  →  {e['depois']}", font=f_b) / S)
        d.line([(0, px(top + rh) - 1), (img.width, px(top + rh) - 1)], fill=(60, 68, 84), width=1)
        y = top + rh
    img.save(saida)
    print(saida, img.size)

gerar(entradas, 1.0, os.path.join(OUT, 'antes_depois_inimigos.png'),
      'DBZ Attack of the Saiyans PT-BR v13.1: inimigos trocados (48 linhas)',
      'Original = sprite e paleta do jogo base. 13.1 = sprite e paleta novos (pele dos humanos corrigida). Linhas 1-4 (Saibamen) voltaram ao original e não entram.')
for k in range(0, len(entradas), 8):
    lote = entradas[k:k + 8]
    gerar(lote, 1.5, os.path.join(OUT, f'antes_depois_{k // 8 + 1:02d}.png'),
          f'Inimigos trocados: bloco {k // 8 + 1} de 6 (linhas {lote[0]["linha"]} a {lote[-1]["linha"]})',
          'Original = sprite e paleta do jogo base. 13.1 = sprite e paleta novos.')

PUB = os.path.join(OUT, 'forum'); os.makedirs(PUB, exist_ok=True)
for k in range(0, len(entradas), 12):
    lote = entradas[k:k + 12]; n = k // 12 + 1
    gerar(lote, 1.0, os.path.join(PUB, f'inimigos_{n}.png'),
          f'Inimigos novos ({n} de {-(-len(entradas) // 12)})',
          'Os animais do jogo original viraram adversários coerentes com a história.', publico=True)
