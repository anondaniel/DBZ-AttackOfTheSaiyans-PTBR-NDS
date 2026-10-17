import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'C:/Projetos/09_Dragon_Ball_Z_Attack_of_the_Saiyans/18_Pele_e_Texto_Boot/scripts')  # comum.rom('nova') = ROM 13.1
from comum import rom
from dados_inimigos import enemy_rows
import nds_rom
from PIL import Image
from dump_tiles import ler_chr, tile_img
from render_quadros import ler_anims, DIM, mascara

def render(d_rom, file, palno):
    """Primeiro quadro da animacao 0, fundo transparente. Ancora: centro x=160, pes y=180 (canvas 320x320, sem corte)."""
    raw = nds_rom.ler(d_rom, f'btl/ene/{file}.chr')
    c = ler_chr(raw)
    errs = []
    an = ler_anims(raw, c['fim_tiles'], errs)
    if errs or not an or not an[0]:
        raise RuntimeError(f'{file}: anim erro {errs} anims={len(an) if an else None}')
    quadro, tiles, pal = an[0][0], c['tiles'], c['pals'][palno]
    canvas = Image.new('RGBA', (480, 480), (0, 0, 0, 0))
    for x, y, tl, at, hf, vf in reversed(quadro['pecas']):
        if y > 32:  # Y do OAM e de 8 bits e da a volta: +126 e -130 (asas acima da cabeca)
            y -= 256
        w, h = DIM[(at >> 6, (at >> 2) & 3)]
        bloco = Image.new('RGB', (w, h)); masc = Image.new('L', (w, h))
        for ty in range(h // 8):
            for tx in range(w // 8):
                i = tl + ty * (w // 8) + tx
                if i < len(tiles):
                    bloco.paste(tile_img(tiles[i], pal, fundo=(0, 0, 0)), (tx * 8, ty * 8))
                    masc.paste(mascara(tiles[i]), (tx * 8, ty * 8))
        if hf:
            bloco, masc = bloco.transpose(Image.FLIP_LEFT_RIGHT), masc.transpose(Image.FLIP_LEFT_RIGHT)
        if vf:
            bloco, masc = bloco.transpose(Image.FLIP_TOP_BOTTOM), masc.transpose(Image.FLIP_TOP_BOTTOM)
        canvas.paste(bloco, (240 + x, 300 + y), masc)
    return canvas


ANC_X, ANC_Y = 240, 300
def dados_linhas():
    import csv
    return list(csv.DictReader(open('C:/Projetos/09_Dragon_Ball_Z_Attack_of_the_Saiyans/13_Correcoes_Revisao/dados/resultado_inimigos.csv', encoding='utf-8-sig')))

if __name__ == '__main__':
    orig = rom('orig'); nova = rom('nova')
    eo = enemy_rows(orig, 'EN'); en = enemy_rows(nova, 'US')
    x0 = y0 = 10**9; x1 = y1 = -10**9
    for r in dados_linhas():
        i = int(r['linha'])
        for d, e in ((orig, eo[i]), (nova, en[i])):
            im = render(d, e['file'], e['palno'])
            b = im.getbbox()
            x0 = min(x0, b[0]); y0 = min(y0, b[1]); x1 = max(x1, b[2]); y1 = max(y1, b[3])
    print('union bbox', x0, y0, x1, y1, 'rel a ancora: x', x0-ANC_X, x1-ANC_X, 'y', y0-ANC_Y, y1-ANC_Y)
