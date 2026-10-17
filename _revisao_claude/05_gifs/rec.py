"""Grava a janela oculta do melonDS em quadros PNG (so quando muda) com horario.
uso: python rec.py <inst> <pasta_saida> [segundos_max]
Para parar: criar o arquivo <pasta_saida>/STOP. Captura so a tela DS (38..614 da area cliente)."""
import sys, os, time
import raw
inst, out = sys.argv[1], sys.argv[2]
dur = float(sys.argv[3]) if len(sys.argv) > 3 else 900
os.makedirs(out, exist_ok=True)
t0 = time.time(); last = None; n = 0
with open(os.path.join(out, "log.txt"), "a") as log:
    while time.time() - t0 < dur and not os.path.exists(os.path.join(out, "STOP")):
        try:
            im = raw.raw(inst)
        except BaseException:
            time.sleep(0.2); continue
        im = im.crop((0, im.size[1] - 576, 384, im.size[1]))
        b = im.tobytes(); t = time.time() - t0
        if b != last:
            im.save(os.path.join(out, f"{n:05d}.png"), compress_level=1)
            log.write(f"{n:05d} {t:.3f} {t0 + t:.3f}\n"); log.flush(); n += 1; last = b
print("quadros", n, flush=True)
