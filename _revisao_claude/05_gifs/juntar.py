"""Junta trechos de varias gravacoes numa linha do tempo unica.
uso: python juntar.py <saida> "<pasta>:<ini>-<fim>" ... (cada trecho entra em sequencia)"""
import sys, os, shutil, bisect
out = sys.argv[1]; shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
log = []; base = 0.0; n = 0
for tr in sys.argv[2:]:
    pasta, r = tr.rsplit(":", 1); a, b = map(float, r.split("-"))
    L = [l.split() for l in open(os.path.join(pasta, "log.txt"))]
    T = [float(x[1]) for x in L]
    k0 = max(0, bisect.bisect_right(T, a) - 1)
    for k in range(k0, len(L)):
        if T[k] >= b: break
        t = base + max(0.0, T[k] - a)
        shutil.copy(os.path.join(pasta, L[k][0] + ".png"), os.path.join(out, f"{n:05d}.png"))
        log.append(f"{n:05d} {t:.3f}"); n += 1
    base += b - a
open(os.path.join(out, "log.txt"), "w").write("\n".join(log) + "\n")
print("quadros", n, "duracao", base)
