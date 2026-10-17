"""Planilha de revisao de um lote (CSV com BOM e ';', abre direto no Excel
em PT-BR). Colunas: n, cena/arquivo, quem fala (melhor palpite), original,
traducao, sua revisao (vazia), observacao.

"Quem fala": nos scripts, o nome de quem fala e empilhado logo antes da
fala (Msg(nome, texto)); aqui usa o ultimo nome curto que aparece antes
da fala na ordem da secao de textos do mesmo arquivo. E so um palpite.
uso: planilha_lote.py <N> <saida.csv>
"""
import csv
import json
import sys

N, SAIDA = sys.argv[1], sys.argv[2]
lote = json.load(open(f"/ds/traducao/lote{N}.json", encoding="utf-8"))
pt = json.load(open(f"/ds/traducao/lote{N}_pt.json", encoding="utf-8"))
todos = json.load(open("/ds/saida/textos_us.json", encoding="utf-8"))
nomes = {x["original"] for x in todos if x["tipo"] in ("exibido?",)} | {
    "Master Roshi", "Fortuneteller Baba", "Mr. Popo", "Dr. Briefs", "Jackie Chun", "Pupil A",
    "Pupil B", "Pupil C", "Pupil D", "Master", "Turtle"}
# quem fala: no codigo, Msg(nome, fala) aparece como
#   26 <nome> 26 <fala> <consts...> 4a <Msg>
import struct

sys.path.insert(0, "/ds/scripts")
import nds_rom
from sb import textos

rom = open("/ds/rom/aots.nds", "rb").read()
fala = {}
for c in nds_rom.caminhos(rom):
    if not (c.startswith("script/US/") and c.endswith(".sb")):
        continue
    d = nds_rom.ler(rom, c)
    if d[:4] != b"SB  ":
        continue
    offs = list(struct.unpack_from("<6I", d, 8))
    a4 = offs[4]
    hs, n = struct.unpack_from("<II", d, a4)
    base = a4 + hs + n * 4
    imps = []
    for i in range(n):
        no, _ = struct.unpack_from("<HH", d, a4 + hs + i * 4)
        imps.append(d[base + no:d.index(b"\x00", base + no)].decode())
    if "Msg" not in imps:
        continue
    msg = imps.index("Msg")
    code = d[offs[0]:offs[1]]
    ts = [t.decode("latin-1") for t in textos(d)]
    p = 0
    while (p := code.find(b"\x26", p)) != -1:
        if p + 4 < len(code) and code[p + 2] == 0x26:
            a, b = code[p + 1], code[p + 3]
            z = code[p + 4:p + 10]  # constantes (16-1f) e a chamada
            k = 0
            while k < len(z) and 0x16 <= z[k] <= 0x1F:
                k += 1
            if k + 1 < len(z) and z[k] == 0x4A and z[k + 1] == msg and a < len(ts) and b < len(ts):
                if "<p>" in ts[b] and "<p>" not in ts[a]:
                    fala.setdefault(ts[b], ts[a])
        p += 1

OBS = {
    "Paopao": "fala em português quebrado, como no original (inglês quebrado)",
}
with open(SAIDA, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["n", "cena / arquivo", "quem fala (palpite)", "original (inglês)", "tradução (1ª versão)",
                "sua revisão", "observação"])
    for k in sorted(lote, key=int):
        o = lote[k]["original"]
        arq = lote[k]["ids"][0].split(":")[1]
        quem = fala.get(o, "")
        w.writerow([k, arq + (f" (+{len(lote[k]['ids']) - 1})" if len(lote[k]["ids"]) > 1 else ""),
                    quem, o, pt[k], "", OBS.get(quem, "")])
print("ok", SAIDA)
