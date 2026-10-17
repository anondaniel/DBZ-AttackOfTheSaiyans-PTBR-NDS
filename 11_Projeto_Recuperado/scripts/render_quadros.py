"""Remonta os quadros de animacao de um .chr (dCHR) a partir da tabela de
celulas, sem emulador, para validar o formato e mapear o desenho.

Tabela (depois dos tiles), deduzida do ene220_01:
  u16 n_anim, u16 0, u16 off[n_anim]  (relativos a tabela+4)
  animacao = sequencia de quadros ate um byte 00:
    u8 n_pecas, u8 ?,
    n_pecas x [s8 x, s8 y, u8 tile, u8 attr]
      attr: bits 7-6 tamanho, 3-2 formato (0 quadrado, 1 largo, 2 alto),
            bits 1-0 = bits 8-9 do numero do tile (hipotese)
    u8 k, k registros de 3 bytes (tempo/hitbox? ainda nao usados)
uso: render_quadros.py <nome_chr> [paleta] [max_quadros]
"""
import struct
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/ds/scripts")
import nds_rom
from dump_tiles import ler_chr, tile_img

DIM = {  # (tamanho, formato) -> (w, h) em pixels
    (0, 0): (8, 8), (1, 0): (16, 16), (2, 0): (32, 32), (3, 0): (64, 64),
    (0, 1): (16, 8), (1, 1): (32, 8), (2, 1): (32, 16), (3, 1): (64, 32),
    (0, 2): (8, 16), (1, 2): (8, 32), (2, 2): (16, 32), (3, 2): (32, 64),
}


# tamanho (em bytes, contando o opcode) dos registros depois das pecas.
# Todos os vistos tem 3. (O "a5 de 4 bytes" era o enchimento de alinhamento.)
TAM_REG = {}
import os as _os
FLIP_CURTO = _os.environ.get("FLIP_CURTO", "1") == "1"


def ler_anims(d, fim_tiles, erros=None):
    """Cada quadro comeca em endereco PAR (relativo a tabela+4; um 00 de
    enchimento completa o anterior). Formatos:
      curto: u8 n, u8 ex, n x [s8 x, s8 y, u8 tile_lo, u8 attr]
      longo: u8 0x10, u8 ex, u8 0, u8 n, n x OAM de 6 bytes (attr0 y/formato,
             attr1 x/flip/tamanho, attr2 tile)
    Depois das pecas: u8 k e k registros de 3 bytes. Quadro que comeca com
    00 = fim da animacao."""
    t = d[fim_tiles:]
    n = struct.unpack_from("<H", t, 0)[0]
    offs = list(struct.unpack_from(f"<{n}H", t, 4))
    limites = offs[1:] + [len(t) - 4]
    anims = []
    for ai, (o, zz) in enumerate(zip(offs, limites)):
        p, z = 4 + o, 4 + zz
        quadros = []
        while p < z and t[p] != 0 and len(quadros) < 64:
            pecas = []
            longo = t[p] == 0x10
            if longo:
                extra, npc = t[p + 1], t[p + 3]
                p += 4
                for i in range(npc):
                    a0, a1, a2 = struct.unpack_from("<HHH", t, p + i * 6)
                    y = a0 & 0xFF
                    y = y - 256 if y > 127 else y
                    x = a1 & 0x1FF
                    x = x - 512 if x > 255 else x
                    forma, tam = a0 >> 14, a1 >> 14
                    hflip, vflip = bool(a1 & 0x1000), bool(a1 & 0x2000)
                    at = (tam << 6) | (forma << 2)
                    pecas.append((x, y, a2 & 0x3FF, at, hflip, vflip))
                p += npc * 6
            else:
                npc, extra = t[p], t[p + 1]
                for i in range(npc):
                    x, y, tl, at = struct.unpack_from("<bbBB", t, p + 2 + i * 4)
                    # bit 4 = espelho horizontal, bit 5 = vertical (hipotese
                    # conferida visualmente: sem isso a animacao 0 sai embaralhada)
                    hf = bool(at & 0x10) if FLIP_CURTO else False
                    vf = bool(at & 0x20) if FLIP_CURTO else False
                    pecas.append((x, y, tl | ((at & 3) << 8), at, hf, vf))
                p += 2 + npc * 4
            k = t[p]
            p += 1
            regs = []
            for _ in range(k):
                op = t[p]
                tr = TAM_REG.get(op, 3)
                regs.append(t[p:p + tr])
                p += tr
            quadros.append({"pecas": pecas, "extra": extra, "regs": regs, "longo": longo})
            if (p - 4) & 1:  # alinha o proximo quadro
                p += 1
        if p != z and not all(b == 0 for b in t[p:z]) and erros is not None:
            erros.append(f"anim {ai}: parou em 0x{p:x}, limite 0x{z:x} ({t[p:p + 8].hex(' ')})")
        anims.append(quadros)
    return anims


def desenha(quadro, tiles, pal, escala=1):
    im = Image.new("RGB", (160, 160), (60, 60, 60))
    for x, y, tl, at, hf, vf in reversed(quadro["pecas"]):  # a 1a peca fica por cima
        w, h = DIM[(at >> 6, (at >> 2) & 3)]
        bloco = Image.new("RGB", (w, h))
        masc = Image.new("L", (w, h))
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
        im.paste(bloco, (80 + x, 140 + y), masc)
    return im


def mascara(t):
    m = Image.new("L", (8, 8))
    px = m.load()
    for y in range(8):
        for x in range(8):
            b = t[y * 4 + x // 2]
            v = (b >> 4) if x & 1 else (b & 15)
            px[x, y] = 0 if v == 0 else 255
    return m


if __name__ == "__main__":
    nome = sys.argv[1]
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    d = nds_rom.ler(open("/ds/rom/aots.nds", "rb").read(), f"btl/ene/{nome}.chr")
    c = ler_chr(d)
    erros = []
    anims = ler_anims(d, c["fim_tiles"], erros)
    print(nome, "animacoes:", [len(a) for a in anims])
    for e in erros:
        print("  ", e)
    linhas = []
    for ai, a in enumerate(anims):
        linhas.append([(f"a{ai} q{qi} ({len(q['pecas'])}p x{q['extra']:02x})", desenha(q, c["tiles"], c["pals"][p]))
                       for qi, q in enumerate(a[:mx])])
    W, H = 160, 172
    g = Image.new("RGB", (W * mx, H * len(linhas)), (20, 20, 20))
    dr = ImageDraw.Draw(g)
    for li, lin in enumerate(linhas):
        for qi, (rot, im) in enumerate(lin):
            g.paste(im, (qi * W, li * H + 12))
            dr.text((qi * W + 2, li * H), rot, fill=(255, 255, 0))
    g.save(f"/ds/saida/quadros_{nome}.png")
    print("ok", f"/ds/saida/quadros_{nome}.png")
