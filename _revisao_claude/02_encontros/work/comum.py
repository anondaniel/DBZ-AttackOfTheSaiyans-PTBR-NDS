import sys, zipfile, io, struct, hashlib
sys.dont_write_bytecode = True
BASE = r"C:/Projetos/09_Dragon_Ball_Z_Attack_of_the_Saiyans"
sys.path.insert(0, BASE + "/11_Projeto_Recuperado/scripts")
import nds_rom
from bdat import ler_container
ROM_RC1 = BASE + "/01_ROM/DBZ Attack of the Saiyans PT-BR.nds"
ROM_COE = BASE + "/12_Coerencia_Historia/DBZ Attack of the Saiyans PT-BR Coerencia.nds"
ZIP_ORIG = BASE + "/00_Original/Dragon Ball Z_ Attack of the Saiyans.zip"
_cache = {}
def rom(nome):
    if nome in _cache: return _cache[nome]
    if nome == 'rc1': d = open(ROM_RC1,'rb').read()
    elif nome == 'coe': d = open(ROM_COE,'rb').read()
    elif nome == 'orig':
        z = zipfile.ZipFile(ZIP_ORIG); n=[x for x in z.namelist() if x.lower().endswith('.nds')][0]
        d = z.read(n)
    _cache[nome]=d; return d
def sha(d): return hashlib.sha256(d).hexdigest()
def tabelas(d, lang='EN'):
    return ler_container(nds_rom.ler(d, f'btl/bdat/{lang}/bdat.bin'))
