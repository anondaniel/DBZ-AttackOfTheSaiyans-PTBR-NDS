"""Primeiro boot da ROM de DS no melonDS DS, sem janela.

Roda N quadros, salva a tela em PNG e mostra o log do nucleo — para ver
se ele pede BIOS, se cai no renderizador por software, etc.

uso: boot_ds.py <rom> <quadros> <saida.png>
"""
import logging
import sys

import numpy as np
from PIL import Image
from libretro import SessionBuilder

ROM = sys.argv[1] if len(sys.argv) > 1 else "/ds/rom/aots.nds"
QUADROS = int(sys.argv[2]) if len(sys.argv) > 2 else 600
SAIDA = sys.argv[3] if len(sys.argv) > 3 else "/ds/saida/boot.png"
CORE = "/ds/tools/melondsds_libretro.so"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("core")

OPCOES = {
    # renderizador por software: nao ha GPU no container
    b"melonds_render_mode": b"software",
    # sem BIOS/firmware: usa a implementacao embutida do melonDS
    b"melonds_sysfile_mode": b"builtin",
    b"melonds_console_mode": b"ds",
    b"melonds_boot_mode": b"direct",
    b"melonds_jit_enable": b"disabled",
}

builder = (SessionBuilder.defaults(CORE)
           .with_content(ROM)
           .with_options(OPCOES)
           .with_log(log))

with builder.build() as s:
    av = s.video
    for i in range(QUADROS):
        s.run()
    shot = s.video.screenshot()
    print("screenshot:", type(shot), getattr(shot, "width", None), getattr(shot, "height", None))

if shot is None:
    print("sem imagem")
    sys.exit(1)

# converte o buffer para imagem, tolerando o formato de pixel
w, h = shot.width, shot.height
buf = np.frombuffer(bytes(shot.data), dtype=np.uint8)
print("bytes do buffer:", buf.size, "pitch:", getattr(shot, "pitch", None),
      "formato:", getattr(shot, "pixel_format", None))
bpp = buf.size // (w * h)
img = buf[: w * h * bpp].reshape(h, w, bpp)
if bpp == 4:
    # XRGB8888 em little-endian = B G R X
    img = img[:, :, [2, 1, 0]]
elif bpp == 2:
    v = img.view(np.uint16).reshape(h, w)
    r = ((v >> 11) & 0x1F) << 3
    g = ((v >> 5) & 0x3F) << 2
    b = (v & 0x1F) << 3
    img = np.dstack([r, g, b]).astype(np.uint8)
Image.fromarray(img.astype(np.uint8)).save(SAIDA)
print(f"tela salva: {SAIDA} ({w}x{h}, {bpp} bytes/pixel)")
