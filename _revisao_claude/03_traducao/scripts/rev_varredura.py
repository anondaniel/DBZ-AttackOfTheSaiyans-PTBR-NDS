"""Varreduras automaticas sobre saida/pt_unicos.json + fontes da ROM nova."""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from rev_wrap import linhas_pagina, paginas, wpal

S = os.path.join(os.path.dirname(__file__), "..", "saida")
U = json.load(open(os.path.join(S, "pt_unicos.json"), encoding="utf-8"))
N = json.load(open(os.path.join(S, "textos_novo.json"), encoding="utf-8"))
O = json.load(open(os.path.join(S, "textos_orig.json"), encoding="utf-8"))
out = open(os.path.join(S, "varredura.txt"), "w", encoding="utf-8")


def p(*a):
    print(*a, file=out)


MARCA = re.compile(r"<[^>]*>|%[ds]|\\\d+(?:[PpA][0-9A-Za-z])?|@\d\d")
limpa = lambda s: MARCA.sub(" ", s)

# ---------- 1. fonte: glifos
p("== 1. COBERTURA DA FONTE ==")
for fn, bpg in (("latin0.fnt", 15), ("latin1.fnt", 10)):
    f = bytes.fromhex(N["fnt"][fn])
    g = lambda c: f[256 + c * bpg:256 + (c + 1) * bpg]
    listra = g(0x8D)
    usados = collections.Counter()
    for u in U:
        for ch in u["pt"]:
            if ord(ch) >= 0x80:
                usados[ord(ch)] += len(u["ids"])
    ruins = []
    for c, k in sorted(usados.items()):
        gl = g(c)
        if gl == listra or not any(gl):
            ruins.append((hex(c), chr(c) if c >= 0xA0 else repr(chr(c)), k))
    p(fn, "caracteres >=0x80 usados:", "".join(chr(c) if c >= 0xA0 else f"[{c:02X}]" for c in sorted(usados)))
    p(fn, "sem glifo (listra/vazio):", ruins)

# ---------- 2. marcacoes EN x PT
p("\n== 2. MARCACOES (EN x PT) ==")
for u in U:
    if u["en"] == "(extra)":
        continue
    a, b = collections.Counter(MARCA.findall(u["en"])), collections.Counter(MARCA.findall(u["pt"]))
    if a != b:
        p(u["ids"][0], dict(a - b), dict(b - a), repr(u["pt"][:100]))
    # tags malformadas
    if re.search(r"<[^>]*$|^[^<]*>|<<|>>", u["pt"]) or u["pt"].count("<") != u["pt"].count(">"):
        p("TAG MALFORMADA", u["ids"][0], repr(u["pt"][:100]))

# ---------- 3. ingles restante
p("\n== 3. PALAVRAS EM INGLES DENTRO DO PT ==")
EN = r"\b(the|you|your|you're|and|is|are|it's|I'm|don't|can't|with|this|that|what|where|here|there|have|has|was|will|just|get|got|not|of|to|for|my|me|we|he|she|they|let's|okay|ok|yes|yeah|hey|wow|oh|please|thanks|thank|sorry|boss|guys|item|items|skill|skills|level|attack|defense|power|speed|use|used|equip|save|load|new|game|continue|press|button|select|cancel|back|next|menu|status)\b"
cont = collections.Counter()
for u in U:
    t = limpa(u["pt"])
    for m in re.finditer(EN, t, flags=re.I):
        w = m.group(0)
        cont[w.lower()] += 1
        if w.lower() not in ("ok", "oh", "next", "menu", "status", "item", "hey", "wow"):
            p(u["ids"][0], w, "|", t[max(0, m.start() - 40):m.end() + 40])
p("contagem:", cont.most_common())

# ---------- 4. frances
p("\n== 4. FRANCES ==")
FR = r"\b(le|les|des|une|vous|est|avec|pour|dans|qui|nous|mais|tu es|je suis|c'est|n'est|ça|où)\b"
for u in U:
    t = limpa(u["pt"])
    for m in re.finditer(FR, t):
        w = m.group(0)
        if w in ("mais",):  # 'mais' existe em PT
            continue
        p(u["ids"][0], w, "|", t[max(0, m.start() - 40):m.end() + 40])

# ---------- 5. nomes e termos
p("\n== 5. NOMES E TERMOS (contagem de variantes, por ocorrencia de texto unico) ==")
VAR = {
    "Kuririn": r"Kuririn|Krillin|Kurilin",
    "Tenshinhan": r"Tenshinhan|Tenshin\b|\bTien\b|Ten Shin Han",
    "Chaos/Chaozu": r"Chaos|Chaozu|Chaoz\b|Chiaotzu|Chao\b",
    "Mestre Kame": r"Mestre Kame|Kame-[Ss]ennin|Mestre Roshi|\bRoshi\b|Kame\b",
    "Kaioh": r"Senhor Kaioh|Sr\.? Kaioh|Kaioh|Kaio\b|Kaiô|King Kai|Rei Kai",
    "Kami-Sama": r"Kami-Sama|Kami-sama|Kami Sama|Kamisama|\bKami\b",
    "Popo": r"Sr\. Popo|Senhor Popo|Mr\. Popo|\bPopo\b",
    "Karin": r"Mestre Karin|Karin|Korin",
    "Enma": r"Senhor Enma|Enma|Yemma|Emma\b",
    "Uranai": r"Vovó Uranai|Uranai|\bBaba\b",
    "Cutelo": r"Cutelo|Ox-King|Rei Cutelo|Gyuumaou|Rei Boi",
    "Chichi": r"Chichi|Chi-Chi|Chi Chi",
    "Lunch": r"Lunch|Launch",
    "Saiyajin": r"Saiyajin|Saiyajins|Saiyan|Saiyans|Sayajin|Saiyajim",
    "Kakarotto": r"Kakarotto|Kakarot\b|Kakaroto",
    "Oozaru": r"Oozaru|Ozaru|Ôzaru|Macaco Gigante|Great Ape",
    "Saibaman": r"Saibaman|Saibamen|Saibaimen|Saibaiman|Saibai",
    "Esferas": r"Esferas? do Drag[aã]o|Dragon Balls?|Esferas?\b",
    "Shenlong": r"Shenlong|Shenron|Shen Long",
    "Semente": r"Semente dos Deuses|Sementes dos Deuses|Senzu",
    "Nuvem": r"Nuvem Voadora|Kinto[- ]?un|Nimbus",
    "Red Ribbon": r"Red Ribbon|Fita Vermelha|\bRR\b",
    "Coelho": r"Grupo do Coelho|Gangue do Coelho|Bando do Coelho|Coelho Monstro|Monster Carrot",
    "Serpente": r"Princesa Serpente|Princesa Cobra|Princess Snake|Princesa\b",
    "Piccolo Daimaoh": r"Piccolo Daimaoh|Daimaoh|Daimao\b|Rei Piccolo|King Piccolo",
    "Namek": r"Namekusei|namekuseijin|Namek\b|Namekiano",
    "Numero 8": r"Número 8|Numero 8|N° 8|Eighter|Hatchan|Oitão",
    "Shen": r"Mestre Shen|Tsuru|Grou",
    "Torneio": r"Torneio de Artes Marciais|Tenkaichi Budokai|Torneio\b",
    "Kamehameha": r"Kamehameha|Kame-hame-ha",
    "Genki Dama": r"Genki Dama|Bomba de Esp[ií]rito|Spirit Bomb",
    "Makankosappo": r"Makankosappo|Makankōsappō|Canhão",
    "Kaioken": r"Kaioken|Kaio-ken|Kaiouken",
    "Scouter": r"Scouter|Rastreador|Detector",
    "Kami-Sama templo": r"Templo de Kami-Sama|Palácio de Kami|Templo do Kami",
    "Yajirobe": r"Yajirobe|Yajirobi|Yajiroba",
    "Mestre Mutaito": r"Mutaito",
    "Jackie Chun": r"Jackie Chun|Jackie Chan",
    "Bastao": r"Bastão Mágico|Nyoibo|Power Pole|Bastão\b",
    "Kienzan": r"Kienzan|Disco Destruidor",
    "Taiyoken": r"Taiyoken|Taiyou?ken|Explosão Solar",
}
for nome, rx in VAR.items():
    c = collections.Counter()
    for u in U:
        for m in re.findall(rx, limpa(u["pt"])):
            c[m] += len(u["ids"])
    p(f"{nome:18s}", dict(c.most_common()))

# ---------- 6. ortografia: padroes comuns
p("\n== 6. PADROES DE ORTOGRAFIA/GRAMATICA ==")
PAD = {
    "sem acento": r"\b(voce|voces|nao|entao|tambem|ja|so|ate|porem|alguem|ninguem|irmao|coracao|mae|pai\b(?=s)|aqui|tambem|e voce|esta bem|agua|lugar|nivel|unico|ultimo|proximo|rapido|facil|dificil|possivel|impossivel|tecnica|tecnicas|forca|ferias|poder\w*ao|ataque\w*ao|serio|necessario|historia|camara|pagina|numero|ola|obrigad[ao]s?\b(?!x))\b",
    "acento indevido": r"\b(pôr isso|pára|pêlo|vôo|enjôo|idéia|heróico|assembléia|jóia|platéia|européia|bóia|apóio|lêem|crêem|dêem|vêem|tranqüilo|freqüente|cinqüenta|lingüiça|agüentar|conseqüência)\b",
    "mal/mau": r"\b(mau humor|mal elemento|mau-humor|muito mau\b|tão mal\b(?! ))",
    "a gente + vamos": r"\ba gente vamos\b|\ba gente fomos\b|\ba gente somos\b",
    "agente/derrepente/concerteza": r"\b(agente vai|agente pode|derrepente|concerteza|de repente\b(?!$)xx|enfim\b(?!$)xx|a fim de\b(?!$)xx)",
    "há/a tempo": r"\b(a muito tempo|a anos|a dias|a séculos|à muito|à anos|faz anos que|fazem anos|fazem dias|haviam muitos|houveram)\b",
    "crase suspeita": r"\b(à (?:ele|ela|eles|elas|você|vocês|mim|ti|um|uma|todos|nada|partir|pé|cavalo|lápis|seu|meu|este|esse|isso|isto|aquilo)|à (?:[a-zé]+ar|[a-z]+er|[a-z]+ir)\b)",
    "por que/porque": r"\b(porque\?|por que não\b.*\bporque\b|\bpor quê\b(?! *[?!.…])|porquê\b)",
    "mais/mas": r"\b(mais (?:eu|você|ele|ela|não|o|a)\b(?=.*,))",
    "onde/aonde": r"\baonde (?:está|estão|fica|ficam|estava|mora)\b",
    "seje/menas": r"\b(seje|menas|mendigo de|iorgute|beneficiente|previlégio|excessão|exitar|extende|mortandela|asterístico|cabeleleiro|bicicreta|poblema|tóchico)\b",
    "pra mim fazer": r"\bpara mim (?:fazer|ir|ver|lutar|ficar|treinar|pegar|levar|achar|usar|ajudar|ser)\b|\bpra mim (?:fazer|ir|ver|lutar|ficar|treinar|pegar|levar|achar|usar|ajudar|ser)\b",
    "hífen pós-reforma": r"\b(auto-[a-z]+|anti-[b-gi-z][a-z]+|super-[b-gi-qs-z][a-z]+|micro-[a-z]+|semi-[a-z]+|extra-[a-z]+|contra-[a-z]+|infra-[a-z]+|ultra-[a-z]+|mini-[a-z]+|pára-quedas|para-quedas|dia-a-dia|fim-de-semana|por-do-sol|mão-de-obra)\b",
    "minúscula após ponto": r"[.!?] +[a-zà-ú]",
    "espaço antes de pontuação": r" [,.!?;:](?![.])",
    "sem espaço após vírgula": r",[A-Za-zÀ-ú]",
    "pontuação duplicada": r"(?<!\.)\.\.(?!\.)|,,|!\.|\?\.|\.!|,\.|\.,",
    "letra repetida 3x (não interjeição)": r"\b[a-zà-ú]*([bcdfgjklmnpqtvxz])\1\1[a-zà-ú]*\b",
    "palavra repetida": r"\b(\w+) \1\b",
}
for nome, rx in PAD.items():
    p(f"-- {nome}")
    k = 0
    for u in U:
        t = limpa(u["pt"])
        for m in re.finditer(rx, t, flags=re.I if nome not in ("minúscula após ponto",) else 0):
            k += 1
            if k <= 80:
                p("  ", u["ids"][0], "|", t[max(0, m.start() - 35):m.end() + 35].replace("\n", " "))
    p(f"   total {k}")

# ---------- 7. tratamento tu/voce
p("\n== 7. TU x VOCE ==")
for u in U:
    t = limpa(u["pt"])
    tu = re.findall(r"\b(tu|teu|tua|teus|tuas|contigo|ti)\b", t, flags=re.I)
    vc = re.findall(r"\b(você|vocês|seu|sua|te)\b", t, flags=re.I)
    if tu:
        p(u["ids"][0], "tu-forms:", tu, "voce-forms:", vc[:5], "|", t[:140])

# ---------- 8. pontuacao final EN x PT
p("\n== 8. PONTUACAO FINAL DIFERENTE (pagina a pagina) ==")
k = 0
for u in U:
    if "<p>" not in u["en"] or u["en"] == "(extra)":
        continue
    pe, pp = paginas(u["en"]), paginas(u["pt"])
    if len(pe) != len(pp):
        p("NUMERO DE PAGINAS DIFERE", u["ids"][0], len(pe), len(pp))
        continue
    for a, b in zip(pe, pp):
        fa = re.sub(r"<[^>]*>", "", a).rstrip()[-1:]
        fb = re.sub(r"<[^>]*>", "", b).rstrip()[-1:]
        if fa in "!?" and fb not in "!?" or (fa == "." and fb in "!?" and False):
            k += 1
            if k <= 60:
                p("  ", u["ids"][0], repr(a[-40:]), "->", repr(b[-40:]))
p("total", k)
out.close()
print("ok")
