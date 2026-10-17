"""Confere o PLANO contra os encontros reais de todos os scripts, ANTES de
montar a ROM. Por mapa (nome do script de encontro):
  A) mesma aparencia (sprite+paleta) com nomes diferentes
  B) mesmo nome com aparencias diferentes
  C) sprite de tamanho maior que o do bicho, se o bicho aparece em grupo
Tambem confere que cada linha do plano e mesmo o bicho esperado.
"""
import ast
import collections
import re
import subprocess
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat import ler_container
from plano_bichos import PLANO

rom = open("/ds/rom/aots.nds", "rb").read()
t = ler_container(nds_rom.ler(rom, "btl/bdat/EN/bdat.bin"))
ep, bp = t["enemy_param"]["linhas"], t["boss_param"]["linhas"]
nomes = [l["en"] for l in t["character_name"]["linhas"]]


def nome_orig(i):
    nid = ep[i]["name_id"]
    return nomes[nid - 1] if nid else ""


def modelo(m):
    return (ep if m[0] == "e" else bp)[int(m[1:])]


erros = []
for i, (bicho, arq, pal, mod, novo) in PLANO.items():
    if nome_orig(i) != bicho:
        erros.append(f"linha {i}: esperava {bicho!r}, e {nome_orig(i)!r}")
    if mod[0] == "e" and modelo(mod)["file"] != arq:
        erros.append(f"linha {i}: modelo {mod} usa {modelo(mod)['file']}, plano diz {arq}")


def aparencia(i):
    if i in PLANO:
        _, arq, pal, _, novo = PLANO[i]
        return (arq, pal), novo
    return (ep[i]["file"], ep[i]["palno"]), nome_orig(i)


saida = subprocess.run(["python3", "/ds/scripts/grupos_inimigos.py"], capture_output=True, text=True).stdout
por_mapa = collections.defaultdict(set)
grupo_de = collections.defaultdict(list)  # linha -> tamanhos de grupo em que aparece
for ln in saida.splitlines():
    m = re.match(r"(\S+)\s+@\S+ argc=15 (\[.*\])", ln)
    if not m:
        continue
    args = ast.literal_eval(m.group(2))
    # ids > n_linhas sao chefes (boss_param): fora desta conferencia
    slots = [v - 1 for v in args[6:12] if isinstance(v, int) and 1 < v <= len(ep)]
    for s in slots:
        por_mapa[m.group(1)].add(s)
        grupo_de[s].append(len(slots))

for mapa, linhas in sorted(por_mapa.items()):
    por_ap, por_nome = collections.defaultdict(set), collections.defaultdict(set)
    for i in linhas:
        ap, nm = aparencia(i)
        por_ap[ap].add(nm)
        por_nome[nm].add(ap)
    for ap, nms in por_ap.items():
        if len(nms) > 1:
            erros.append(f"A {mapa}: aparencia {ap} com nomes {sorted(nms)}")
    for nm, aps in por_nome.items():
        if len(aps) > 1:
            erros.append(f"B {mapa}: nome {nm!r} com aparencias {sorted(map(str, aps))}")

for i, (bicho, arq, pal, mod, novo) in PLANO.items():
    tam_sprite, tam_bicho = modelo(mod)["size"], ep[i]["size"]
    if tam_sprite > tam_bicho and max(grupo_de[i] or [1]) > 1:
        erros.append(f"C linha {i} {bicho}: sprite tamanho {tam_sprite} > {tam_bicho} e aparece em grupo "
                     f"de ate {max(grupo_de[i])}")

print(f"{len(PLANO)} linhas no plano, {len(por_mapa)} mapas conferidos")
for e in sorted(set(erros)):
    print(" ", e)
print("SEM PROBLEMAS" if not erros else f"{len(set(erros))} problema(s)")
sys.exit(1 if erros else 0)
