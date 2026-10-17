"""Controlador do emulador de DS (melonDS DS via libretro.py), sem janela.

    with DS("/ds/rom/aots.nds") as ds:
        ds.espera(300)
        ds.aperta("a")
        ds.tela().save("x.png")
        estado = ds.salvar()      # bytes do save state
        ds.carregar(estado)

As duas telas do DS saem empilhadas: 256x384 (cima em y 0-191).
"""
import ctypes
import logging

import numpy as np
from PIL import Image
from libretro import JoypadState, SessionBuilder
from libretro.api.input.pointer import Pointer, PointerState
from libretro.drivers.input.iterable import PortState

CORE = "/ds/tools/melondsds_libretro.so"
OPCOES = {
    b"melonds_render_mode": b"software",
    b"melonds_sysfile_mode": b"builtin",
    b"melonds_console_mode": b"ds",
    b"melonds_boot_mode": b"direct",
    b"melonds_jit_enable": b"disabled",
}


class DS:
    def __init__(self, rom, log=False):
        self._botoes = {}
        self.quadro = 0

        self._toque = None  # (x, y) na tela de BAIXO, em pixels do DS

        def entradas():
            while True:
                pad = JoypadState(**self._botoes)
                if self._toque is None:
                    yield pad
                else:
                    # libretro: -32767..32767 sobre o quadro inteiro (256x384,
                    # tela de baixo em y 192-383)
                    x, y = self._toque
                    px = int((x + 0.5) / 256 * 65534) - 32767
                    py = int((y + 192 + 0.5) / 384 * 65534) - 32767
                    yield PortState(joypad=pad, pointer=PointerState(
                        (Pointer(px, py, True),)))

        b = (SessionBuilder.defaults(CORE)
             .with_content(rom)
             .with_options(OPCOES)
             .with_input(entradas))
        if log:
            logging.basicConfig(level=logging.INFO)
            b = b.with_log(logging.getLogger("core"))
        self._builder = b

    def __enter__(self):
        self._ctx = self._builder.build()
        self.s = self._ctx.__enter__()
        return self

    def __exit__(self, *a):
        return self._ctx.__exit__(*a)

    # ---- tempo e botoes ----
    def espera(self, n=1):
        for _ in range(n):
            self.s.run()
            self.quadro += 1

    def aperta(self, *botoes, segura=6, depois=20):
        self._botoes = {b: True for b in botoes}
        self.espera(segura)
        self._botoes = {}
        self.espera(depois)

    def toca(self, x, y, segura=6, depois=20):
        """Toque na tela de baixo, em (x, y) de 0-255 x 0-191."""
        self._toque = (x, y)
        self.espera(segura)
        self._toque = None
        self.espera(depois)

    # ---- tela ----
    def tela(self):
        shot = self.s.video.screenshot()
        w, h = shot.width, shot.height
        buf = np.frombuffer(bytes(shot.data), dtype=np.uint8)
        # o screenshot do libretro.py ja vem em ordem R,G,B,X (com [2,1,0]
        # a pele da Launch saia azul)
        img = buf[: w * h * 4].reshape(h, w, 4)[:, :, [0, 1, 2]]
        return Image.fromarray(img.copy())

    # ---- save state ----
    def salvar(self):
        core = self.s.core
        buf = bytearray(core.serialize_size())   # libretro.py exige buffer gravavel
        if core.serialize(buf) is False:
            raise RuntimeError("serialize falhou")
        return bytes(buf)

    def carregar(self, dados):
        if self.s.core.unserialize(bytearray(dados)) is False:
            raise RuntimeError("unserialize falhou")
