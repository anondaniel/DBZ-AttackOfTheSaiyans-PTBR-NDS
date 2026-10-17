"""Levantamento de uma ROM de Nintendo DS.

Extrai o sistema de arquivos (NitroFS), abre os pacotes NARC,
descomprime LZ10/LZ11 e classifica cada arquivo pelo formato. Depois
procura especificamente o que interessa para o hack de inimigos:

  - a tabela do bestiario (150 entradas, segundo os guias do jogo)
  - a lista de nomes dos inimigos
  - quantos sprites de personagem existem e quantos sao genericos

Nada e executado da ROM; so leitura de bytes.

uso: levantamento_nds.py <rom.nds> [pasta_saida]
"""
import json
import os
import struct
import sys
from collections import Counter, defaultdict

ROM = sys.argv[1]
SAIDA = sys.argv[2] if len(sys.argv) > 2 else "/ds/saida"
os.makedirs(SAIDA, exist_ok=True)

with open(ROM, "rb") as f:
    rom = f.read()


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


# ---------------------------------------------------------------------------
# cabecalho
# ---------------------------------------------------------------------------
titulo = rom[0x00:0x0C].rstrip(b"\x00").decode("ascii", "replace")
codigo = rom[0x0C:0x10].decode("ascii", "replace")
fabricante = rom[0x10:0x12].decode("ascii", "replace")
arm9_off, arm9_tam = u32(rom, 0x20), u32(rom, 0x2C)
arm7_off, arm7_tam = u32(rom, 0x30), u32(rom, 0x3C)
fnt_off, fnt_tam = u32(rom, 0x40), u32(rom, 0x44)
fat_off, fat_tam = u32(rom, 0x48), u32(rom, 0x4C)
ov9_off, ov9_tam = u32(rom, 0x50), u32(rom, 0x54)

print("=" * 70)
print(f"ROM: {os.path.basename(ROM)}  ({len(rom):,} bytes)")
print(f"titulo interno: {titulo!r}   codigo: {codigo}   fabricante: {fabricante}")
print(f"ARM9: 0x{arm9_off:08X} ({arm9_tam:,} b)   ARM7: 0x{arm7_off:08X} ({arm7_tam:,} b)")
print(f"overlays ARM9: {ov9_tam // 32} arquivos")
print("=" * 70)


# ---------------------------------------------------------------------------
# NitroFS: FNT (nomes) + FAT (posicoes)
# ---------------------------------------------------------------------------
def ler_fat(buf, off, tam):
    return [(u32(buf, off + i * 8), u32(buf, off + i * 8 + 4))
            for i in range(tam // 8)]


def ler_fnt(buf, off):
    """devolve {file_id: caminho}"""
    n_dirs = u16(buf, off + 6)
    caminhos = {}

    def dir_nome(dir_id, prefixo):
        base = off + (dir_id & 0x0FFF) * 8
        sub = off + u32(buf, base)
        fid = u16(buf, base + 4)
        p = sub
        while True:
            t = buf[p]
            p += 1
            if t == 0x00:
                break
            n = t & 0x7F
            nome = buf[p:p + n].decode("ascii", "replace")
            p += n
            if t & 0x80:
                sub_id = u16(buf, p)
                p += 2
                dir_nome(sub_id, prefixo + nome + "/")
            else:
                caminhos[fid] = prefixo + nome
                fid += 1

    if n_dirs:
        dir_nome(0xF000, "")
    return caminhos


fat = ler_fat(rom, fat_off, fat_tam)
nomes = ler_fnt(rom, fnt_off)
print(f"\nNitroFS: {len(fat)} entradas na FAT, {len(nomes)} com nome\n")


# ---------------------------------------------------------------------------
# compressao da BIOS: LZ10 / LZ11
# ---------------------------------------------------------------------------
def descomprimir(d):
    if len(d) < 4 or d[0] not in (0x10, 0x11):
        return None
    tam = d[1] | (d[2] << 8) | (d[3] << 16)
    if not (0 < tam <= 16 * 1024 * 1024):
        return None
    out = bytearray()
    p = 4
    lz11 = d[0] == 0x11
    try:
        while len(out) < tam:
            flags = d[p]
            p += 1
            for bit in range(8):
                if len(out) >= tam:
                    break
                if flags & (0x80 >> bit):
                    if lz11:
                        b0 = d[p]
                        ind = b0 >> 4
                        if ind == 0:
                            b1, b2 = d[p + 1], d[p + 2]
                            n = (((b0 & 0xF) << 4) | (b1 >> 4)) + 0x11
                            disp = (((b1 & 0xF) << 8) | b2) + 1
                            p += 3
                        elif ind == 1:
                            b1, b2, b3 = d[p + 1], d[p + 2], d[p + 3]
                            n = (((b0 & 0xF) << 12) | (b1 << 4) | (b2 >> 4)) + 0x111
                            disp = (((b2 & 0xF) << 8) | b3) + 1
                            p += 4
                        else:
                            b1 = d[p + 1]
                            n = ind + 1
                            disp = (((b0 & 0xF) << 8) | b1) + 1
                            p += 2
                    else:
                        b0, b1 = d[p], d[p + 1]
                        n = (b0 >> 4) + 3
                        disp = (((b0 & 0xF) << 8) | b1) + 1
                        p += 2
                    if disp > len(out):
                        return None
                    for _ in range(n):
                        out.append(out[-disp])
                else:
                    out.append(d[p])
                    p += 1
    except IndexError:
        return None
    return bytes(out[:tam])


# ---------------------------------------------------------------------------
# classificacao por formato
# ---------------------------------------------------------------------------
MAGICOS = {
    b"RGCN": "NCGR (tiles)", b"RLCN": "NCLR (paleta)", b"RECN": "NCER (celulas/sprite)",
    b"RNAN": "NANR (animacao)", b"RCSN": "NSCR (tela/mapa)", b"RFTN": "NFTR (fonte)",
    b"NARC": "NARC (pacote)", b"SDAT": "SDAT (som)", b"BMD0": "NSBMD (modelo 3D)",
    b"BTX0": "NSBTX (textura 3D)", b"BCA0": "NSBCA (anim 3D)", b"MESG": "BMG (texto)",
    b"RTFN": "NFTR (fonte)", b"RMAN": "NMAR", b"RCMN": "NMCR",
}


def classificar(d):
    if len(d) < 4:
        return "vazio/minusculo"
    m = d[:4]
    if m in MAGICOS:
        return MAGICOS[m]
    return None


def parse_narc(d):
    """devolve lista de (nome, bytes)"""
    if d[:4] != b"NARC":
        return []
    p = u16(d, 0x0C)
    blocos = {}
    for _ in range(3):
        mg = d[p:p + 4]
        tam = u32(d, p + 4)
        blocos[mg] = (p, tam)
        p += tam
    if b"BTAF" not in blocos or b"GMIF" not in blocos:
        return []
    bt, _ = blocos[b"BTAF"]
    n = u16(d, bt + 8)
    entradas = [(u32(d, bt + 12 + i * 8), u32(d, bt + 16 + i * 8)) for i in range(n)]
    gm, _ = blocos[b"GMIF"]
    base = gm + 8
    nomes_narc = {}
    if b"BTNF" in blocos:
        bn, _ = blocos[b"BTNF"]
        try:
            nomes_narc = ler_fnt(d, bn + 8)
        except Exception:
            nomes_narc = {}
    return [(nomes_narc.get(i, f"{i:04d}"), d[base + s:base + e])
            for i, (s, e) in enumerate(entradas)]


arquivos = []   # (caminho, bytes, formato, comprimido)


def registrar(caminho, dados, profundidade=0):
    fmt = classificar(dados)
    comp = None
    if fmt is None:
        dec = descomprimir(dados)
        if dec is not None:
            comp = "LZ11" if dados[0] == 0x11 else "LZ10"
            dados = dec
            fmt = classificar(dados)
    if fmt is None:
        fmt = "desconhecido"
    arquivos.append((caminho, dados, fmt, comp))
    if fmt.startswith("NARC") and profundidade < 3:
        for nome, sub in parse_narc(dados):
            registrar(f"{caminho}/{nome}", sub, profundidade + 1)


for fid, (ini, fim) in enumerate(fat):
    if fim <= ini or fim > len(rom):
        continue
    caminho = nomes.get(fid, f"<overlay_{fid:03d}>")
    registrar(caminho, rom[ini:fim])

# ---------------------------------------------------------------------------
# relatorio geral
# ---------------------------------------------------------------------------
por_fmt = Counter(f for _, _, f, _ in arquivos)
print(f"{len(arquivos)} arquivos no total (incluindo o conteudo dos NARC)\n")
print("por formato:")
for fmt, n in por_fmt.most_common():
    print(f"  {n:5}  {fmt}")

comp = Counter(c for _, _, _, c in arquivos if c)
if comp:
    print(f"\ncomprimidos: " + ", ".join(f"{k}={v}" for k, v in comp.items()))

pastas = defaultdict(lambda: Counter())
for caminho, _, fmt, _ in arquivos:
    topo = caminho.split("/")[0] if "/" in caminho else "(raiz)"
    pastas[topo][fmt] += 1
print("\npastas de primeiro nivel:")
for topo in sorted(pastas):
    tot = sum(pastas[topo].values())
    resumo = ", ".join(f"{f.split(' ')[0]}={n}" for f, n in pastas[topo].most_common(4))
    print(f"  {topo:28} {tot:5}  ({resumo})")

# ---------------------------------------------------------------------------
# 1) nomes de inimigos: procura em ASCII, UTF-16 e Shift-JIS
# ---------------------------------------------------------------------------
CHAVES = ["Saibaman", "Raditz", "Nappa", "Vegeta", "Annin", "Broly",
          "Wolf", "Bear", "Dinosaur", "Tiger", "Pterodactyl", "Eighter",
          "Princess Snake", "Red Ribbon"]
print("\n" + "=" * 70)
print("PROCURA DE NOMES DE INIMIGO")
print("=" * 70)
achados_nome = defaultdict(list)
for caminho, dados, fmt, _ in arquivos:
    for chave in CHAVES:
        for cod, rot in ((chave.encode("ascii"), "ascii"),
                         (chave.encode("utf-16-le"), "utf16")):
            if cod in dados:
                achados_nome[caminho].append(f"{chave}({rot})")
for caminho, lst in sorted(achados_nome.items(), key=lambda kv: -len(kv[1])):
    print(f"  {caminho}  <- {', '.join(sorted(set(lst)))}")
if not achados_nome:
    print("  nenhum nome em ASCII/UTF-16 — o texto deve usar codificacao "
          "propria (tabela de caracteres); proximo passo e descobri-la")

# ---------------------------------------------------------------------------
# 2) tabela do bestiario: arquivo com 150 registros de tamanho fixo
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("CANDIDATOS A TABELA DO BESTIARIO (150 entradas, segundo os guias)")
print("=" * 70)
cand = []
for caminho, dados, fmt, _ in arquivos:
    if fmt != "desconhecido":
        continue
    n = len(dados)
    for qtd in (150, 151, 152, 160):
        for cab in (0, 4, 8, 16):
            if n > cab and (n - cab) % qtd == 0:
                rec = (n - cab) // qtd
                if 8 <= rec <= 256:
                    cand.append((caminho, n, qtd, cab, rec))
for caminho, n, qtd, cab, rec in cand[:25]:
    print(f"  {caminho}: {n} b = {cab} de cabecalho + {qtd} x {rec} b")
if not cand:
    print("  nenhum arquivo de dados divide certinho em ~150 registros")

# ---------------------------------------------------------------------------
# 3) sprites de personagem vs genericos
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("GRAFICOS DE BATALHA")
print("=" * 70)
graf = [(c, f) for c, _, f, _ in arquivos if f.startswith(("NCGR", "NCER", "NANR", "NCLR"))]
por_pasta = defaultdict(Counter)
for c, f in graf:
    pasta = "/".join(c.split("/")[:-1]) or "(raiz)"
    por_pasta[pasta][f.split(" ")[0]] += 1
for pasta in sorted(por_pasta, key=lambda p: -sum(por_pasta[p].values()))[:20]:
    print(f"  {pasta:40} " + ", ".join(f"{k}={v}" for k, v in por_pasta[pasta].items()))

# ---------------------------------------------------------------------------
# grava o inventario completo
# ---------------------------------------------------------------------------
inv = [{"caminho": c, "tamanho": len(d), "formato": f, "compressao": comp}
       for c, d, f, comp in arquivos]
with open(os.path.join(SAIDA, "inventario.json"), "w", encoding="utf-8") as fo:
    json.dump({"titulo": titulo, "codigo": codigo, "arquivos": inv}, fo,
              ensure_ascii=False, indent=1)
print(f"\ninventario completo: {os.path.join(SAIDA, 'inventario.json')}")
