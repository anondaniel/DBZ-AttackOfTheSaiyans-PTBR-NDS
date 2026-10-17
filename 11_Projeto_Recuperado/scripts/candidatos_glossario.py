"""Candidatos a glossario: nomes de personagem, locais, golpes, itens,
quem fala nos dialogos, e termos em maiuscula que se repetem."""
import collections
import json
import re

itens = json.load(open("/ds/saida/textos_us.json", encoding="utf-8"))
por_tipo = collections.defaultdict(list)
for it in itens:
    por_tipo[it["tipo"]].append(it["original"])


def uniq(xs):
    return sorted(set(xs), key=xs.index)


print("== character_name:", " | ".join(uniq(por_tipo["character_name"])))
print("\n== exibido? (palavra unica nos scripts):", " | ".join(uniq(por_tipo["exibido?"])))
print("\n== exibido (nos scripts):", " | ".join(uniq(por_tipo["exibido"]))[:3000])
for k in ("cf_mes_LOC", "btl_mes_BLAST", "use_item_mes", "key_item_mes", "btl_acc_mes", "pt_eqp_mes"):
    xs = [s for it in itens if it["tipo"] == k for s in [it["original"]] if len(s) < 40]
    print(f"\n== {k} (curtos):", " | ".join(uniq(xs))[:2500])
# termos capitalizados frequentes nos dialogos
cont = collections.Counter()
for s in por_tipo["dialogo"]:
    s = re.sub(r"<[^>]*>", " ", s)
    for m in re.findall(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-z]+(?:[ -][A-Z][a-z]+)*)", s):
        cont[m] += 1
comuns = {"I", "The", "You", "We", "He", "She", "It", "They", "What", "Hey", "But", "And", "Oh", "Yes", "No"}
print("\n== termos capitalizados mais frequentes nos dialogos:")
print(" | ".join(f"{k} {v}" for k, v in cont.most_common(220) if k not in comuns))
