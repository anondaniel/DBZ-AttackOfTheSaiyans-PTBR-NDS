"""Utilitarios compartilhados da etapa 18 / versao 13.1 (somente leitura das pastas antigas).
Copia de 13_Correcoes_Revisao/scripts/comum.py com os caminhos da pasta 18 e a ROM 13 como base."""
import sys, os, zipfile, hashlib, zlib
sys.dont_write_bytecode = True
BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
PASTA13 = os.path.join(BASE, '13_Correcoes_Revisao')
PASTA18 = os.path.join(BASE, '18_Pele_e_Texto_Boot')
SCRIPTS_PROJ = os.path.join(BASE, '11_Projeto_Recuperado', 'scripts')
if SCRIPTS_PROJ not in sys.path:
    sys.path.insert(0, SCRIPTS_PROJ)
ROM_RC1 = os.path.join(BASE, '01_ROM', 'DBZ Attack of the Saiyans PT-BR.nds')
ROM_COE = os.path.join(BASE, '12_Coerencia_Historia', 'DBZ Attack of the Saiyans PT-BR Coerencia.nds')
ROM_13 = os.path.join(PASTA13, 'DBZ Attack of the Saiyans PT-BR.nds')
ZIP_ORIG = os.path.join(BASE, '00_Original', 'Dragon Ball Z_ Attack of the Saiyans.zip')
ROM_NOVA = os.path.join(PASTA18, 'DBZ Attack of the Saiyans PT-BR.nds')
SHA_RC1 = '41412a4727328d5341ba2f7d17fa567c84db137d8cd082bc32389c6d27643a5f'
SHA_COE = '130b4ad843d85d760c4e844de26c35021bde0b43b6c5f34d6c3c639b2f5a9edd'
SHA_13 = '0616e6c6fdada1e54d0694bd2e552be64dea3c3e592cd88ddf07b31d8bda3a82'
CRC_ORIG = 0xa9f0b8f9

def sha256(d): return hashlib.sha256(d).hexdigest()
def crc32(d): return zlib.crc32(d) & 0xffffffff

_cache = {}
def rom(nome):
    if nome in _cache: return _cache[nome]
    if nome == 'rc1':
        d = open(ROM_RC1, 'rb').read(); assert sha256(d) == SHA_RC1
    elif nome == 'coe':
        d = open(ROM_COE, 'rb').read(); assert sha256(d) == SHA_COE
    elif nome == '13':
        d = open(ROM_13, 'rb').read(); assert sha256(d) == SHA_13, 'ROM 13 diferente da esperada'
    elif nome == 'orig':
        z = zipfile.ZipFile(ZIP_ORIG)
        n = [x for x in z.namelist() if x.lower().endswith('.nds')][0]
        d = z.read(n); assert crc32(d) == CRC_ORIG
    elif nome == 'nova':
        d = open(ROM_NOVA, 'rb').read()
    else:
        d = open(nome, 'rb').read()
    _cache[nome] = d
    return d
