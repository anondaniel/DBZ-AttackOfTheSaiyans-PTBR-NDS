"""Folha de previa: cada linha do plano (sprite final) ao lado das outras
variantes do mesmo sprite que aparecem nos mesmos mapas. uso: python -B previa.py [rom]"""
import sys, os, json
sys.dont_write_bytecode = True
from comum import *
from dados_inimigos import *
from PIL import Image, ImageDraw, ImageFont
from render_quadros import desenha
from plano13 import PLANO13

def main(rom_path=None, saida=None):
    d = rom(rom_path or 'nova')
    ep = enemy_rows(d, 'US')
    G = encontros(d); mp = mapas_por_linha(G)
    try: font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 11)
    except OSError: font = ImageFont.load_default()
    rows = sorted(PLANO13)
    W, H, N = 130, 150, 6
    sheet = Image.new('RGB', (W * N, H * len(rows)), (24, 28, 36)); dr = ImageDraw.Draw(sheet)
    cache = {}
    def img(i):
        e = ep[i]; f = e['file']
        if f not in cache:
            raw = nds_rom.ler(d, f'btl/ene/{f}.chr'); c = ler_chr(raw); an = ler_anims(raw, c['fim_tiles'], [])
            cache[f] = (c, an)
        c, an = cache[f]
        return desenha(an[0][0], c['tiles'], c['pals'][e['palno']]).crop((15, 10, 145, 160))
    for y, r in enumerate(rows):
        viz = [i for i, e in enumerate(ep) if i != r and e['_nome'] and e['file'] == ep[r]['file'] and mp[i] & mp[r]]
        outros = [i for i, e in enumerate(ep) if i != r and e['_nome'] and e['file'] == ep[r]['file'] and i not in viz]
        for x, i in enumerate(([r] + viz + outros)[:N]):
            sheet.paste(img(i), (x * W, y * H))
            cor = (255, 255, 0) if i == r else ((255, 120, 120) if i in viz else (170, 170, 170))
            dr.text((x * W + 2, y * H + 2), f"{i}: {ep[i]['_nome']}", font=font, fill=cor)
    saida = saida or os.path.join(PASTA13, 'verificacao', 'previa_inimigos.png')
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    sheet.save(saida)
    print('previa:', saida, sheet.size)

if __name__ == '__main__':
    main(*(sys.argv[1:3]))
