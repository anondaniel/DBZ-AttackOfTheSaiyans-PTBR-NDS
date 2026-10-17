"""Compressor para o LZ proprio das imagens dIMP/dMAP (inverso de
imp.descomprimir). Guloso: em cada posicao escolhe o maior casamento entre
as 256 distancias da tabela do jogo; senao repeticao do ultimo byte; senao
literal. Formato dos codigos:
  00-0F        c+1 literais
  10 n         repete o ultimo byte n+3 vezes (3..258)
  20-7F        copia (c>>4)+1 bytes (3..8) da distancia t[c&15]
  8X/..FX i    copia (c&15)+3 bytes (3..18) da distancia t[i], seguidos de
               (c>>4)&7 literais (0..7)
O primeiro byte vai cru."""
import sys

sys.path.insert(0, "/ds/scripts")
from imp import _dist, descomprimir


def comprimir(px, largura):
    t = _dist(largura)
    n = len(px)
    out = bytearray([px[0]])
    i = 1
    lit = bytearray()

    def solta_literais():
        nonlocal lit
        while lit:
            k = min(16, len(lit))
            out.append(k - 1)
            out.extend(lit[:k])
            lit = lit[k:]

    while i < n:
        # repeticao do ultimo byte
        r = 0
        while i + r < n and r < 258 and px[i + r] == px[i - 1]:
            r += 1
        # melhor copia pela tabela
        mel, mel_len = -1, 0
        for k, d in enumerate(t):
            p = i + d
            if p < 0 or d >= 0:
                continue
            L = 0
            lim = 18 if k >= 16 or True else 8
            while L < lim and i + L < n and px[p + L] == px[i + L]:
                L += 1
            if L > mel_len:
                mel, mel_len = k, L
        if r >= 3 and r >= mel_len:
            solta_literais()
            out += bytes([0x10, r - 3])
            i += r
        elif mel_len >= 3:
            solta_literais()
            if mel < 16 and mel_len <= 8:
                out.append(((mel_len - 1) << 4) | mel)  # 0x20..0x7F
            else:
                out += bytes([0x80 | (mel_len - 3), mel])
            i += mel_len
        else:
            lit.append(px[i])
            i += 1
    solta_literais()
    return bytes(out)


if __name__ == "__main__":
    # teste de ida e volta com um fundo do jogo
    import nds_rom
    import imp
    rom = open("/ds/rom/aots.nds", "rb").read()
    for c in sys.argv[1:]:
        d = nds_rom.ler(rom, c)
        img = imp.ler(d)
        z = comprimir(img["pixels"], img["largura"])
        back, fim = descomprimir(z, img["largura"], img["altura"])
        print(c, "original", len(d) - 0x208, "novo", len(z), "ida e volta", back == img["pixels"], fim == len(z))
