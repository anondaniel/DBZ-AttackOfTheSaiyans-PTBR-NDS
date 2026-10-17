"""Mede a largura em PIXELS de cada linha de um texto, com a largura real de
cada letra das fontes do jogo (latin0.fnt = grande, latin1.fnt = pequena).
Codigos de controle (<...>, \\1P3, \\4AA...) nao ocupam espaco; @NN (icone)
conta 10 px.

larg(texto, fonte) -> [px por linha]  (linhas separadas por <n>/<N>/<p>)
uso: largura.py <loteN.json> <loteN_pt.json> [folga%=0]
  lista os textos cuja linha traduzida mais larga passa da linha
  original mais larga (em qualquer das duas fontes)
"""
import json
import re
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

_rom = open("/ds/rom/aots.nds", "rb").read()
LARG = {f: nds_rom.ler(_rom, f"latin{f}.fnt")[:256] for f in (0, 1)}
CODIGO = re.compile(r"<[^>]*>|\\\d+(?:[PpA][0-9A-Za-z])?")


def larg(texto, fonte=1):
    linhas = re.split(r"<[nNpP]>", texto)
    res = []
    for ln in linhas:
        px = 0
        for parte in re.split(r"(@\d\d)", ln):
            if re.fullmatch(r"@\d\d", parte):
                px += 10
                continue
            for ch in CODIGO.sub("", parte):
                px += LARG[fonte][ord(ch)] if ord(ch) < 256 else 8
        res.append(px)
    return res


def _usos():
    """Quais linhas das tabelas *_mes sao NOME e quais sao DESCRICAO,
    segundo as tabelas de dados do proprio jogo (name_id/help_id em itens,
    name/help em tecnicas)."""
    from bdat import ler_container
    t = ler_container(nds_rom.ler(_rom, "btl/bdat/US/bdat.bin"))
    alvo = {"Use_Item": "use_item_mes", "Btl_Acc": "btl_acc_mes", "Pt_Eqp": "pt_eqp_mes",
            "Key_Item": "key_item_mes"}
    uso = {}
    for tab, tb in t.items():
        dst = alvo.get(tab) or ("btl_mes_BLAST" if tab.startswith(("skill_", "passive_")) else None)
        if not dst:
            continue
        for l in tb["linhas"]:
            for col, cls in (("name_id", "nome"), ("help_id", "desc"), ("name", "nome"), ("help", "desc")):
                v = l.get(col)
                if isinstance(v, int) and v > 0:
                    # name_id/help_id sao 1-based; name/help das tecnicas tambem
                    uso[(dst, v - 1)] = cls
    return uso


USOS = _usos()


def grupo(item):
    """(tabela, classe). Nas tabelas de item/tecnica a classe vem do jogo
    (nome x desc). Mensagens de batalha: tabela inteira (mesma barra).
    Demais: 'rotulo' (uma linha curta) x 'texto'."""
    o = item["original"]
    partes = item["ids"][0].split(":")
    if partes[0] == "sb":
        # fala: sem <n> o jogo quebra sozinho; com <n> cada linha tem que
        # caber na caixa (limite = linha mais larga das falas do jogo todo)
        return "script", "quebra_manual" if "<n>" in o else "auto"
    _, tab, lin, _ = partes
    if (tab, int(lin)) in USOS:
        return tab, USOS[(tab, int(lin))]
    if tab in ("btl_mes_SYS", "btl_mes_ITM"):
        return tab, "barra"
    curto = "<n>" not in o and "<p>" not in o and len(o) <= 24
    return tab, "rotulo" if curto else "texto"


if __name__ == "__main__":
    lote = json.load(open(sys.argv[1], encoding="utf-8"))
    pt = json.load(open(sys.argv[2], encoding="utf-8"))
    # limite de cada grupo = a linha ORIGINAL mais larga do grupo (o jogo ja
    # mostra essa largura sem cortar)
    limite = {}
    for k, it in lote.items():
        g = grupo(it)
        for f in (0, 1):
            limite[g, f] = max(limite.get((g, f), 0), max(larg(it["original"], f)))
    todos = json.load(open("/ds/saida/textos_us.json", encoding="utf-8"))
    for f in (0, 1):
        limite[("script", "quebra_manual"), f] = max(
            max(larg(x["original"], f)) for x in todos
            if x["fonte"] == "script" and "<n>" in x["original"] and "/dbg/" not in x["id"])
    ruins = 0
    for k in sorted(pt, key=int):
        g = grupo(lote[k])
        if g == ("script", "auto"):
            continue
        for f in (0, 1):
            lt = max(larg(pt[k], f))
            if lt > limite[g, f]:
                ruins += 1
                print(f"{k:>5} {g[0]}/{g[1]} fonte{f}: {lt}px > limite {limite[g, f]}px  {pt[k][:80]!r}")
                break
    print(f"{ruins} texto(s) passam do limite do grupo")
    for (g, f), v in sorted(limite.items()):
        if f == 1:
            print(f"   limite {g[0]}/{g[1]}: {v}px (fonte pequena), {limite[g, 0]}px (grande)")
