from pathlib import Path
import sys, io, contextlib, json, ast, re, collections
BASE = Path(__file__).resolve().parents[1]
SCRIPTS = BASE / '11_Projeto_Recuperado/scripts'
sys.path.insert(0, str(SCRIPTS))
import nds_rom
from bdat import ler_container
from plano_bichos import PLANO

ROM = BASE / '01_ROM/DBZ Attack of the Saiyans PT-BR.nds'
def encontros():
    code = (SCRIPTS / 'grupos_inimigos.py').read_text(encoding='utf-8')
    code = code.replace('"/ds/rom/aots.nds"', repr(str(ROM)))
    old = sys.argv
    sys.argv = ['grupos_inimigos.py']
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(code, 'grupos_inimigos.py', 'exec'), {})
    sys.argv = old
    result = []
    for line in out.getvalue().splitlines():
        m = re.match(r'(\S+)\s+@(\S+) argc=15 (\[.*\])', line)
        if m:
            args = ast.literal_eval(m[3])
            result.append({'mapa': m[1], 'offset': int(m[2],16), 'ids': [x-1 for x in args[6:12] if isinstance(x,int) and 1 < x <= 173]})
    return result

if __name__ == '__main__':
    rom = ROM.read_bytes()
    tables = ler_container(nds_rom.ler(rom,'btl/bdat/EN/bdat.bin'))
    ep = tables['enemy_param']['linhas']
    names = tables['character_name']['linhas']
    groups = encontros()
    report = []
    for row, data in sorted(PLANO.items()):
        maps = sorted({g['mapa'] for g in groups if row in g['ids']})
        report.append({'linha':row,'original':data[0],'atual':data[4],'sprite':ep[row]['file'],'paleta':ep[row]['palno'],'mapas':maps})
        print(row, data[0], '->', data[4], ':', ','.join(maps))
    (Path(__file__).parent/'encontros_antes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (Path(__file__).parent/'grupos.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\nMODELOS DISPONÍVEIS')
    for row, e in enumerate(ep):
        if e['name_id'] and row not in PLANO:
            print(row, names[e['name_id']-1].get('en'), e['file'], e['palno'], 'size',e['size'])
