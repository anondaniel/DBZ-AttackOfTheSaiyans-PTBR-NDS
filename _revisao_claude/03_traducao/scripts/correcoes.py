"""Correcoes pontuais no acumulado (ptbr.json) e nos loteN_pt.json:
- caracteres sem glifo na fonte (º, ª) -> formas que existem
- nomes de quem fala que nenhum lote tinha isolado
"""
import glob
import json

TROCA = {"23º": "23°", "1º ataque": "1° ataque", "Ex-1º": "Ex-1°", "Nº": "N°",
         "1ª parada": "Primeira parada"}
FALANTES = {
    "Bandit A": "Bandido A", "Bandit B": "Bandido B", "Bulma & Krillin": "Bulma e Kuririn",
    "Chi-Chi": "Chichi", "Farmer": "Fazendeiro", "Goku & Bulma": "Goku e Bulma",
    "Guide": "Guia", "King Kai": "Senhor Kaioh", "King Yemma": "Senhor Enma",
    "Krillin & Gohan": "Kuririn e Gohan", "Krillin & Roshi": "Kuririn e Kame",
    "Master Shen": "Mestre Shen", "Ox-King": "Cutelo", "Ox-King & Chi-Chi": "Cutelo e Chichi",
    "Piccolo & Gohan": "Piccolo e Gohan", "Robot": "Robô", "Servant": "Servo",
    "Shu & Mai": "Shu e Mai", "Soldier": "Soldado", "Sweeper": "Faxineiro",
}


def fix(d):
    n = 0
    for k, v in d.items():
        w = v
        for a, b in TROCA.items():
            w = w.replace(a, b)
        if w != v:
            d[k] = w
            n += 1
    return n


for f in glob.glob("/ds/traducao/lote*_pt*.json"):
    d = json.load(open(f, encoding="utf-8"))
    n = fix(d)
    if n:
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print(f, n)
acum = json.load(open("/ds/traducao/ptbr.json", encoding="utf-8"))
print("acumulado:", fix(acum))
acum.update(FALANTES)
json.dump(acum, open("/ds/traducao/ptbr.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("falantes adicionados:", len(FALANTES))
