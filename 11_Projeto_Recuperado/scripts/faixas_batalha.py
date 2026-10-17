"""Faixas de fim de batalha (Victory!! / Defeat / Escape) em PT-BR.
Ficam no pacote etc/pe.zea ('azEF'): tabela de entradas de 16 bytes
(id, ESD = off|tam<<24 em unidades de 0x100, EVD idem, tamanho do EVD
descomprimido); o EVD e LZ10. As entradas US sao 0xFA065/066 (vitoria),
0xFA06F/070 (derrota), 0xFA079/07A (fuga). Em cada EVD, a tira do texto e
uma textura A3I5 128x32 em 0x802C, que se repete na horizontal (o texto da
a volta na borda). A tira e desenrolada, redesenhada com rotulos2.letreiro
(estilo lido do original: contorno + degrade por linha), inclinada como o
original (italico) e enrolada de volta.
uso: faixas_batalha.py <rom_entrada> <rom_saida> [--previa]"""
import struct
import sys

from PIL import Image

sys.path.insert(0, "/ds/scripts")
import nds_rom
from rotulos2 import letreiro

W, H, T = 128, 32, 0x802C
FAIXAS = {  # id: (texto, italico)
    0xFA065: ("Vitória!!", 0.30), 0xFA066: ("Vitória!!", 0.30),
    0xFA06F: ("Derrota", 0.0), 0xFA070: ("Derrota", 0.0),
    0xFA079: ("Fuga!", 0.30), 0xFA07A: ("Fuga!", 0.30),
}
VAZIO = 0x06


def entradas(z):
    n = struct.unpack_from("<I", z, 4)[0]
    return {struct.unpack_from("<I", z, 16 + k * 16)[0]: (16 + k * 16, struct.unpack_from("<4I", z, 16 + k * 16))
            for k in range(n)}


def evd(z, e):
    o = (e[2] & 0xFFFFFF) * 0x100
    return nds_rom.lz10_descomprimir(z[o:o + (e[2] >> 24) * 0x100 + 0x200])[:e[3] & 0xFFFFFF]


def centro_circular(g):
    """coluna onde comeca o maior vao vazio (o texto fica do outro lado)"""
    ocupada = [any((g[y][x] >> 5) for y in range(H)) for x in range(W)]
    melhor, ini = 0, 0
    for x0 in range(W):
        n = 0
        while n < W and not ocupada[(x0 + n) % W]:
            n += 1
        if n > melhor:
            melhor, ini = n, x0
    return (ini + melhor) % W, W - melhor   # inicio do texto, largura ocupada


def nova_tira(tira, texto, inclina):
    g = [[tira[y * W + x] for x in range(W)] for y in range(H)]
    x0, larg = centro_circular(g)
    # desenrola: coluna 0 do grid = x0 - 4
    base = (x0 - 4) % W
    des = [[g[y][(base + x) % W] for x in range(W)] for y in range(H)]
    orig = [[v if (v >> 5) else 0 for v in l] for l in des]
    novo = letreiro(texto, [l[:larg + 8] for l in orig])
    if inclina:  # italico: desloca cada linha para a direita conforme sobe
        h = len(novo)
        novo = [[0] * int(inclina * (h - 1 - y)) + l for y, l in enumerate(novo)]
        wmax = max(len(l) for l in novo)
        novo = [l + [0] * (wmax - len(l)) for l in novo]
    out = [[VAZIO] * W for _ in range(H)]
    for y in range(H):
        for x, v in enumerate(novo[y][:W]):
            if v:
                out[y][(base + x) % W] = v
    return bytes(v for l in out for v in l), des, novo


if __name__ == "__main__":
    rom = bytearray(open(sys.argv[1], "rb").read())
    z = bytearray(nds_rom.ler(rom, "etc/pe.zea"))
    ents = entradas(bytes(z))
    previas = []
    for i, (texto, inc) in FAIXAS.items():
        pos, e = ents[i]
        u = bytearray(evd(bytes(z), e))
        tira, des, novo = nova_tira(bytes(u[T:T + W * H]), texto, inc)
        u[T:T + W * H] = tira
        previas.append((texto, bytes(u[T:T + W * H]), bytes(evd(bytes(nds_rom.ler(open("/ds/rom/aots.nds", "rb").read(), "etc/pe.zea")), e)[T:T + W * H])))
        c = nds_rom.lz10_comprimir(bytes(u))
        assert nds_rom.lz10_descomprimir(c)[:len(u)] == bytes(u)
        unid = (len(c) + 0xFF) // 0x100
        velho_off, velho_tam = e[2] & 0xFFFFFF, e[2] >> 24
        if unid <= velho_tam:
            off = velho_off
        else:  # nao cabe: vai para o fim do pacote
            off = (len(z) + 0xFF) // 0x100
            z += b"\x00" * (off * 0x100 - len(z))
            z += b"\x00" * (unid * 0x100)
        assert unid < 256
        z[off * 0x100:off * 0x100 + unid * 0x100] = c + b"\x00" * (unid * 0x100 - len(c))
        struct.pack_into("<I", z, pos + 8, off | (unid << 24))
        print(f"{hex(i)} {texto}: {len(c)} bytes ({'no lugar' if off == velho_off else 'fim do pacote'})")
    if "--previa" in sys.argv:
        im = Image.new("RGB", (W * 2 + 10, len(previas) * (H + 4)), (40, 40, 40))
        for k, (t, novo, velho) in enumerate(previas):
            for j, dados in enumerate((velho, novo)):
                for p, v in enumerate(dados):
                    a = v >> 5
                    im.putpixel((j * (W + 10) + p % W, k * (H + 4) + p // W),
                                (40, 40, 40) if not a else ((v & 31) * 8, (v & 31) * 8, 90))
        im.resize((im.width * 4, im.height * 4), 0).save("/ds/saida/faixas_previa.png")
        print("previa -> /ds/saida/faixas_previa.png")
        sys.exit()
    print(nds_rom.substituir(rom, "etc/pe.zea", bytes(z)))
    open(sys.argv[2], "wb").write(rom)
    print("->", sys.argv[2])
