"""uso: python montar2.py <pasta_quadros> <saida.gif> "<ini>-<fim>@<fps>[,...]" [cores] [limite_bytes]
Amostra em tempo real (horario do log); quadros iguais consecutivos se fundem.
Se passar do limite, reduz o fps (x0.8, x0.65, x0.5)."""
import bisect, os, sys
from PIL import Image
src, saida, segs_txt = sys.argv[1:4]
cores = int(sys.argv[4]) if len(sys.argv) > 4 else 256
LIM = int(sys.argv[5]) if len(sys.argv) > 5 else 2_000_000
L = [l.split() for l in open(os.path.join(src, "log.txt"))]
T = [float(x[1]) for x in L]; N = [x[0] for x in L]
segs = []
for s in segs_txt.split(","):
    r, f = s.split("@"); a, b = r.split("-"); segs.append((float(a), float(b), float(f)))
def seq(mult):
    out = []
    for a, b, f in segs:
        f *= mult; n = int(round((b - a) * f))
        for k in range(n):
            out.append((bisect.bisect_right(T, a + k / f) - 1, 1 / f))
    fund = []
    for i, d in out:
        if fund and fund[-1][0] == i: fund[-1] = (i, fund[-1][1] + d)
        else: fund.append((i, d))
    return fund
for mult in (1.0, 0.8, 0.65, 0.5):
    sq = seq(mult)
    ids = sorted(set(i for i, _ in sq))
    ref = [ids[int(j * (len(ids) - 1) / 9)] for j in range(10)] if len(ids) > 10 else ids
    mont = Image.new("RGB", (384 * len(ref), 576))
    for j, i in enumerate(ref): mont.paste(Image.open(os.path.join(src, N[i] + ".png")).convert("RGB"), (j * 384, 0))
    pal = mont.quantize(colors=cores, method=Image.Quantize.FASTOCTREE)
    fr = [Image.open(os.path.join(src, N[i] + ".png")).convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE) for i, _ in sq]
    durs = [max(20, int(round(d * 1000))) for _, d in sq]
    fr[0].save(saida, save_all=True, append_images=fr[1:], duration=durs, loop=0, disposal=1)
    tam = os.path.getsize(saida)
    print(f"{os.path.basename(saida)} mult={mult} cores={cores} quadros={len(fr)} dur={sum(durs)/1000:.1f}s bytes={tam} 1o_quadro={N[sq[0][0]]}@{T[sq[0][0]]:.2f}s")
    if tam <= LIM: break
