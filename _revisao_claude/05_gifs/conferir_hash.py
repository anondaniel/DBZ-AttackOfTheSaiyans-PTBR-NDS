"""Compara a ROM de lancamento com a copia de teste: arquivos do NitroFS por SHA-256,
bytes fora dos arquivos, e o sprite/nome do inimigo forcado.
uso: python -B conferir_hash.py <lancamento.nds> <teste.nds> <padrao_sprite> <nome_utf8>"""
import sys, hashlib, struct
sys.path.insert(0, r"..\04_teste\rom_teste")
import nds_rom
A = open(sys.argv[1], "rb").read(); B = open(sys.argv[2], "rb").read()
pad, nome = sys.argv[3], sys.argv[4].encode("utf-8")
h = lambda d: hashlib.sha256(d).hexdigest()
print("SHA-256 lancamento", h(A)); print("SHA-256 teste     ", h(B))
ca, cb = nds_rom.caminhos(A), nds_rom.caminhos(B)
assert ca == cb, "arvore de arquivos diferente"
dif = []; faixas = []
for c, fid in ca.items():
    a0, a1 = nds_rom.fat_entrada(A, fid); b0, b1 = nds_rom.fat_entrada(B, fid)
    faixas.append((b0, b1))
    if (a0, a1) != (b0, b1) or A[a0:a1] != B[b0:b1]:
        dif.append(c)
print("arquivos no NitroFS:", len(ca), "| diferentes:", len(dif))
for c in dif: print("   ", c)
# todo byte diferente deve estar dentro de um arquivo diferente ou na FAT
fat = struct.unpack_from("<I", A, 0x48)[0]; fatl = struct.unpack_from("<I", A, 0x4C)[0]
dentro = [nds_rom.fat_entrada(B, ca[c]) for c in dif] + [(fat, fat + fatl)]
fora = 0; i = 0; n = min(len(A), len(B))
import itertools
blk = 1 << 20
for o in range(0, n, blk):
    if A[o:o + blk] == B[o:o + blk]: continue
    for j in range(o, min(o + blk, n)):
        if A[j] != B[j] and not any(x <= j < y for x, y in dentro): fora += 1
print("bytes diferentes fora desses arquivos e da FAT:", fora)
print("cabecalho 0x000-0x200 igual:", A[:0x200] == B[:0x200])
for c in sorted(ca):
    if pad in c:
        print("sprite", c, h(nds_rom.ler(A, c))[:16], "==", h(nds_rom.ler(B, c))[:16], nds_rom.ler(A, c) == nds_rom.ler(B, c))
for c in sorted(ca):
    d = nds_rom.ler(A, c)
    if nome in d:
        print("nome em", c, h(d)[:16], "==", h(nds_rom.ler(B, c))[:16], d == nds_rom.ler(B, c))
