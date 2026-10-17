"""Extrai TODOS os textos traduziveis (pasta/idioma US, a que o jogo le)
para /ds/saida/textos_us.json e mostra a contagem.

Fontes:
  bdat (btl/bdat/US/bdat.bin): colunas de string das tabelas de mensagem
    e de nomes (as colunas 'name'/'file' tecnicas ficam de fora)
  scripts (script/US/**/*.sb): secao 2. Classificacao de cada string:
    dialogo  - contem <p> (caixa de fala)
    exibido  - texto "de gente": tem espaco ou maiuscula, so ASCII
               imprimivel/Latin-1, sem '_', sem parenteses de funcao,
               nao comeca com '#' ou '==='; ex.: nomes de local e de quem fala
    interno  - identificadores (funcoes, mapas, sprites, debug): NAO traduzir
"""
import collections
import json
import re
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from bdat import ler_container
from sb import textos

rom = open("/ds/rom/aots.nds", "rb").read()
itens = []

# ---- tabelas
TABELAS_TEXTO = re.compile(r"^(btl_mes_|cf_mes_|use_item_mes|btl_acc_mes|pt_eqp_mes|key_item_mes|character_name)")
t = ler_container(nds_rom.ler(rom, "btl/bdat/US/bdat.bin"))
for nome, tb in t.items():
    if not TABELAS_TEXTO.match(nome):
        continue
    cols = [c[0] for c in tb["colunas"] if c[2] == 7]
    for i, l in enumerate(tb["linhas"]):
        for c in cols:
            v = l.get(c, "")
            if v and v.strip():
                itens.append({"id": f"bdat:{nome}:{i}:{c}", "fonte": "tabela", "tipo": nome,
                              "original": v})


def classifica(s):
    if "<p>" in s or "<k>" in s:
        return "dialogo"
    if s.startswith(("#", "===")) or "_" in s or "(" in s or ")" in s:
        return "interno"
    if any(ord(ch) < 32 or 127 <= ord(ch) < 160 for ch in s):
        return "interno"
    if re.fullmatch(r"[A-Za-z0-9]+", s):  # palavra unica: identificador ou nome?
        return "exibido?" if s[0].isupper() and not re.search(r"\d", s) and not s.isupper() else "interno"
    if " " in s or "'" in s or "!" in s or "?" in s or "." in s:
        return "exibido"
    return "interno"


cam = nds_rom.caminhos(rom)
for c in sorted(cam):
    if not (c.startswith("script/US/") and c.endswith(".sb")):
        continue
    d = nds_rom.ler(rom, c)
    if d[:4] != b"SB  ":
        continue
    for i, b in enumerate(textos(d)):
        s = b.decode("latin-1")
        k = classifica(s)
        if k != "interno" and s.strip():
            itens.append({"id": f"sb:{c[len('script/US/'):]}:{i}", "fonte": "script", "tipo": k,
                          "original": s})

json.dump(itens, open("/ds/saida/textos_us.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

pal = lambda s: len(re.findall(r"[A-Za-z']+", re.sub(r"<[^>]*>", " ", s)))
por = collections.defaultdict(lambda: [0, 0, set()])
for it in itens:
    k = (it["fonte"], it["tipo"] if it["fonte"] == "script" else it["tipo"].split("_")[0] + "_" + it["tipo"].split("_")[1] if "_" in it["tipo"] else it["tipo"])
    por[k][0] += 1
    por[k][1] += pal(it["original"])
    por[k][2].add(it["original"])
tot_p = sum(v[1] for v in por.values())
for k, (n, p, uni) in sorted(por.items()):
    print(f"{k[0]:7s} {k[1]:18s} {n:6d} textos ({len(uni):5d} unicos) {p:7d} palavras")
unicos = {it["original"] for it in itens}
print(f"TOTAL: {len(itens)} textos, {len(unicos)} unicos, {tot_p} palavras "
      f"({sum(pal(s) for s in unicos)} em textos unicos)")
