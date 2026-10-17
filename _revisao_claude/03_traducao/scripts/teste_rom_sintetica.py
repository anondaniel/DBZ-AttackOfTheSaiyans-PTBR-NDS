"""Monta uma ROM de DS minima, com estrutura real, para validar o
levantamento antes de ter a ROM verdadeira.

Cobre os caminhos que costumam quebrar: subpasta na FNT, arquivo
comprimido em LZ10 E em LZ11 (com as tres variantes de comprimento),
NARC com arquivos dentro, tabela de 150 registros e nomes em UTF-16.

Se o levantamento achar tudo isso, o extrator esta certo.
"""
import struct
import sys

SAIDA = sys.argv[1] if len(sys.argv) > 1 else "/ds/teste.nds"


def lz10_literal(d):
    """LZ10 so com literais: valido e simples"""
    out = bytearray([0x10, len(d) & 0xFF, (len(d) >> 8) & 0xFF, (len(d) >> 16) & 0xFF])
    for i in range(0, len(d), 8):
        out.append(0x00)
        out += d[i:i + 8]
    return bytes(out)


def lz11_com_referencias(d):
    """LZ11 exercitando as tres formas de comprimento. Os dados de teste
    sao construidos para ter repeticoes longas nos lugares certos."""
    out = bytearray([0x11, len(d) & 0xFF, (len(d) >> 8) & 0xFF, (len(d) >> 16) & 0xFF])
    # 8 literais iniciais
    out.append(0x00)
    out += d[0:8]
    p = 8
    # bloco de flags: ref curta (ind>=2), ref media (ind=0), ref longa (ind=1)
    # d foi montado como: 8 bytes base + repeticoes do bloco
    refs = []
    # curta: 5 bytes, disp 8
    n = 5
    disp = 8
    refs.append(bytes([((n - 1) << 4) | ((disp - 1) >> 8), (disp - 1) & 0xFF]))
    p += n
    # media: 0x20 bytes, disp 8   (0x11..0x110)
    n = 0x20
    m = n - 0x11
    refs.append(bytes([(m >> 4) & 0x0F, ((m & 0xF) << 4) | ((disp - 1) >> 8), (disp - 1) & 0xFF]))
    p += n
    # longa: 0x130 bytes, disp 8  (0x111..0x10110)
    n = 0x130
    m = n - 0x111
    refs.append(bytes([0x10 | ((m >> 12) & 0x0F), (m >> 4) & 0xFF,
                       ((m & 0xF) << 4) | ((disp - 1) >> 8), (disp - 1) & 0xFF]))
    p += n
    # um byte de flags cobre 8 blocos: 3 referencias (bits 1) e depois
    # 5 LITERAIS (bits 0) no mesmo grupo. Emitir um byte de flags novo
    # logo apos as referencias desalinha o decodificador — foi o bug da
    # primeira versao deste teste.
    resto = d[p:]
    out.append(0b11100000)
    for r in refs:
        out += r
    out += resto[:5]
    resto = resto[5:]
    for i in range(0, len(resto), 8):
        out.append(0x00)
        out += resto[i:i + 8]
    return bytes(out)


def narc(arquivos):
    dados = bytearray()
    fat = bytearray()
    for a in arquivos:
        ini = len(dados)
        dados += a
        fat += struct.pack("<II", ini, len(dados))
        while len(dados) % 4:
            dados.append(0xFF)
    btaf = b"BTAF" + struct.pack("<IHH", 12 + len(fat), len(arquivos), 0) + fat
    btnf_corpo = struct.pack("<IHH", 4, 0, 1)
    btnf = b"BTNF" + struct.pack("<I", 8 + len(btnf_corpo)) + btnf_corpo
    gmif = b"GMIF" + struct.pack("<I", 8 + len(dados)) + dados
    corpo = btaf + btnf + gmif
    cab = b"NARC" + struct.pack("<HHIHH", 0xFFFE, 0x0100, 16 + len(corpo), 16, 3)
    return cab + corpo


# ---- conteudo dos arquivos ----
ncgr = b"RGCN" + bytes(60)
nclr = b"RLCN" + bytes(28)
bestiario = bytes(range(256)) * 0 + b"\x00" * 4 + bytes((i * 7) & 0xFF for i in range(150 * 24))
texto = "Saibaman\x00Wolf\x00Raditz\x00".encode("utf-16-le")
# dados para o LZ11: 8 bytes base e depois muita repeticao
base = b"ABCDEFGH"
lz11_dados = base + (base * 80)[:5 + 0x20 + 0x130] + b"fim-do-arquivo!!"

arquivos = [
    ("btl/enemy/ncgr_comprimido.bin", lz10_literal(ncgr)),
    ("btl/enemy/pacote.narc", narc([nclr, bestiario])),
    ("msg/nomes.bin", texto),
    ("lz11_teste.bin", lz11_com_referencias(lz11_dados)),
]

# ---- FNT: raiz -> btl/ -> enemy/, raiz -> msg/, e um arquivo na raiz ----
# ids de diretorio: F000 raiz, F001 btl, F002 enemy, F003 msg
# ids de arquivo em ordem: enemy/0, enemy/1, msg/2, raiz/3
def sub_entrada_dir(nome, did):
    return bytes([0x80 | len(nome)]) + nome.encode() + struct.pack("<H", did)


def sub_entrada_arq(nome):
    return bytes([len(nome)]) + nome.encode()


sub_raiz = sub_entrada_arq("lz11_teste.bin") + sub_entrada_dir("btl", 0xF001) \
    + sub_entrada_dir("msg", 0xF003) + b"\x00"
sub_btl = sub_entrada_dir("enemy", 0xF002) + b"\x00"
sub_enemy = sub_entrada_arq("ncgr_comprimido.bin") + sub_entrada_arq("pacote.narc") + b"\x00"
sub_msg = sub_entrada_arq("nomes.bin") + b"\x00"

# primeiro id de arquivo de cada pasta
# ordem da FAT: 0 enemy/ncgr, 1 enemy/narc, 2 msg/nomes, 3 lz11_teste
subs = [(sub_raiz, 3, 4), (sub_btl, 0, 0xF000), (sub_enemy, 0, 0xF001), (sub_msg, 2, 0xF000)]
main = bytearray()
off = 8 * len(subs)
corpos = bytearray()
for s, first, parent in subs:
    main += struct.pack("<IHH", off + len(corpos), first, parent)
    corpos += s
fnt = bytes(main + corpos)

ordem = [arquivos[0][1], arquivos[1][1], arquivos[2][1], arquivos[3][1]]

rom = bytearray(0x4000)
rom[0:12] = b"TESTE DS\x00\x00\x00\x00"
rom[12:16] = b"TEST"
rom[16:18] = b"01"
p = len(rom)
fnt_off = p
rom += fnt
while len(rom) % 4:
    rom.append(0xFF)
fat_off = len(rom)
rom += bytes(8 * len(ordem))
pos = []
for d in ordem:
    ini = len(rom)
    rom += d
    pos.append((ini, len(rom)))
    while len(rom) % 4:
        rom.append(0xFF)
for i, (a, b) in enumerate(pos):
    struct.pack_into("<II", rom, fat_off + i * 8, a, b)
struct.pack_into("<II", rom, 0x40, fnt_off, len(fnt))
struct.pack_into("<II", rom, 0x48, fat_off, 8 * len(ordem))

with open(SAIDA, "wb") as f:
    f.write(rom)
print(f"ROM sintetica: {SAIDA} ({len(rom)} bytes)")

# confere as duas compressoes BYTE A BYTE contra o original, usando o
# descompressor do proprio levantamento
fonte = open("/ds/scripts/levantamento_nds.py").read()
ini = fonte.index("def descomprimir")
fim = fonte.index("# ---", ini)
ns = {}
exec(fonte[ini:fim], ns)
descomprimir = ns["descomprimir"]

ok10 = descomprimir(arquivos[0][1]) == ncgr
ok11 = descomprimir(arquivos[3][1]) == lz11_dados
print(f"LZ10 ida e volta: {'OK' if ok10 else 'FALHOU'}")
print(f"LZ11 ida e volta: {'OK' if ok11 else 'FALHOU'} "
      f"(curta, media e longa: {len(lz11_dados)} bytes)")
if not (ok10 and ok11):
    sys.exit(1)
