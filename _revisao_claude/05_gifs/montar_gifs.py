"""Monta GIFs a partir dos quadros gravados (frames/s1, com horario em log.txt).
Amostragem fixa (fps) com o quadro mais recente em cada instante; quadros iguais se fundem.
Segmentos: (t_ini, t_fim, hold_s) -> se hold_s > 0, mostra o quadro de t_ini por hold_s segundos (tela parada)."""
import bisect, os, sys
from PIL import Image
SRC = "frames/s1"
L = [l.split() for l in open(os.path.join(SRC, "log.txt"))]
T = [float(t) for _, t in L]; N = [n for _, n in [(a, b) for a, b in L]]
N = [a for a, _ in L]
LIMITE = 2_000_000

def quadro(t):
    return bisect.bisect_right(T, t) - 1

def sequencia(segs, fps_mult=1.0):
    out = []  # (indice_do_quadro, duracao_s)
    for ini, fim, hold, fps in segs:
        if hold > 0:
            out.append((quadro(ini), hold)); continue
        fps = fps * fps_mult
        n = int(round((fim - ini) * fps))
        for k in range(n):
            out.append((quadro(ini + k / fps), 1 / fps))
    # funde repetidos consecutivos
    fund = []
    for i, d in out:
        if fund and fund[-1][0] == i:
            fund[-1] = (i, fund[-1][1] + d)
        else:
            fund.append((i, d))
    return fund

def monta(segs, saida, cores=256, mult_lista=(1.0, 0.8, 0.6, 0.5)):
    for mult in mult_lista:
        fps = mult
        seq = sequencia(segs, mult)
        ids = sorted(set(i for i, _ in seq))
        ref = [ids[int(j * (len(ids) - 1) / 7)] for j in range(8)] if len(ids) > 8 else ids
        mont = Image.new("RGB", (384 * len(ref), 576))
        for j, i in enumerate(ref):
            mont.paste(Image.open(os.path.join(SRC, f"{i:05d}.png")).convert("RGB"), (j * 384, 0))
        pal = mont.quantize(colors=cores, method=Image.Quantize.FASTOCTREE)
        frames = []
        for i, _ in seq:
            im = Image.open(os.path.join(SRC, f"{i:05d}.png")).convert("RGB")
            frames.append(im.quantize(palette=pal, dither=Image.Dither.NONE))
        durs = [max(20, int(round(d * 1000))) for _, d in seq]
        frames[0].save(saida, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=1)
        tam = os.path.getsize(saida)
        print(f"{os.path.basename(saida)}: mult={mult} cores={cores} quadros={len(frames)} duracao={sum(durs)/1000:.1f}s bytes={tam}", flush=True)
        if tam <= LIMITE:
            return True
    return False

if __name__ == "__main__":
    dest = sys.argv[1]
    os.makedirs(dest, exist_ok=True)
    # 01: aviso (parado) -> logos -> titulo PT-BR
    monta([(1.2, 1.2, 1.5, 0), (46.9, 56.0, 0, 5), (65.5, 72.0, 0, 5)],
          os.path.join(dest, "01_abertura_logos_titulo_ptbr.gif"), cores=128)
    monta([(80.0, 100.0, 0, 10)], os.path.join(dest, "02_inicio_prologo_ptbr.gif"))
