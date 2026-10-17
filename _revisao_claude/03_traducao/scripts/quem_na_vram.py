"""Quais arquivos graficos da ROM estao carregados num save state?
Procura os tiles de cada dCHR (4bpp, 32 bytes) e de cada atlas dIMG/dIMP
(8bpp, recortado em tiles 8x8 de 64 bytes) dentro do estado serializado.
uso: quem_na_vram.py <estado.bin> [min_tiles]"""
import struct
import sys

sys.path.insert(0, "/ds/scripts")
import imp
import nds_rom

_e = open(sys.argv[1], "rb").read()
_g = _e.find(b"GPU")  # a VRAM fica na secao da GPU, no fim do estado
_v = _e[_g:]
est = set()
for _k in range(0, len(_v) - 64, 4):
    est.add(_v[_k:_k + 32])
    est.add(_v[_k:_k + 64])
minimo = int(sys.argv[2]) if len(sys.argv) > 2 else 8
rom = open("/ds/rom/aots.nds", "rb").read()


def tiles_chr(d, ini=0):
    npal, nt = d[ini + 5], struct.unpack_from("<H", d, ini + 6)[0]
    base = ini + 8 + npal * 32
    return [d[base + i * 32: base + i * 32 + 32] for i in range(nt) if base + i * 32 + 32 <= len(d)]


def tiles_atlas(img):
    w, h, px = img["largura"], img["altura"], img["pixels"]
    r = []
    for ty in range(0, h - 7, 8):
        for tx in range(0, w - 7, 8):
            r.append(b"".join(px[(ty + y) * w + tx:(ty + y) * w + tx + 8] for y in range(8)))
    return r


res = []
for c in nds_rom.caminhos(rom):
    if c.startswith(("script/", "snd")):
        continue
    d = nds_rom.ler(rom, c)
    try:
        if d[:4] == b"dCHR":
            ts = tiles_chr(d)
        elif d[:4] in (b"dIMG", b"dIMP"):
            ts = tiles_atlas(imp.ler(d))
        else:
            continue
    except Exception:
        continue
    uteis = [t for t in set(ts) if len(set(t)) > 2]
    achou = sum(1 for t in uteis if t in est)
    if achou >= minimo:
        res.append((achou, len(uteis), c))
for a, n, c in sorted(res, reverse=True):
    print(f"{a:5d}/{n:<5d} {c}")
