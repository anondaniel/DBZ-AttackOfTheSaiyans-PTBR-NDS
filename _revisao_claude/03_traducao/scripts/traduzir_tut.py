"""TESTE da reinsercao de dialogos com tamanho livre: traduz as falas do
Kuririn na Training Island (tut01_00.sb, indices 14-25) para PT-BR e grava
nas pastas US (a que o jogo le) e EN. Parte da ROM original.
"""
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom
from sb import com_textos, textos

PT = {
    14: "<p>Hmm? Tem alguma coisa aqui perto...<k>",
    15: "<p>Opa! Calma, calma, calma!<k>",
    16: ("<p>Ufa! Que susto. Ainda bem que eles não eram muito fortes.<k>"
         "<p>Vencendo batalhas, você ganha Zeni (dinheiro) e experiência.<k>"
         "<p>Também ganha AP, os Pontos de Habilidade.<k>"
         "<p>Nosso nível sobe quando juntamos pontos de experiência suficientes...<k>"
         "<p>E com os AP dá para aprender técnicas novas e aprimorar as antigas.<k>"
         "<p>Escolha Skill no menu para usar seus AP. Experimente!<k>"
         "<p>Quanto mais inimigos você enfrentar, mais forte vai ficar! Continue assim "
         "e a gente vai ficar tão forte quanto o Goku!<k>"),
    17: "<p>Tem mais alguma coisa por perto...<k>",
    18: "<p>Uau! Um fantasma!<k>",
    19: "<p>Está vendo aquela pedra piscando? Chegue perto dela e use uma rajada de ki para destruí-la.<k>",
    20: "<p>Aperte o Botão B quando ela estiver piscando para começar a concentrar o seu poder.<k>",
    21: "<p>Quando o seu poder estiver no máximo, o medidor de ki vai acender.<k>",
    22: "<p>Solte o Botão B e você vai disparar uma rajada de ki!<k>",
    23: "<p>Vamos lá, tente!<k>",
    24: "<p>Foi bom, né? Você pode usar rajadas de ki para quebrar os obstáculos no caminho.<k>",
    25: "<p>Espera aí! Eu ainda não terminei de falar.<k>",
}

SAIDA = sys.argv[1] if len(sys.argv) > 1 else "/ds/rom/teste_tut_ptbr.nds"
rom = bytearray(open("/ds/rom/aots.nds", "rb").read())
for lang in ("US", "EN"):
    c = f"script/{lang}/cf0/tut/tut01_00.sb"
    d = nds_rom.ler(rom, c)
    ts = textos(d)
    for i, t in PT.items():
        assert ts[i].startswith(b"<p>"), (lang, i, ts[i][:20])
        ts[i] = t.encode("latin-1")
    novo = com_textos(d, ts)
    assert textos(novo) == ts
    print(f"{c}: {len(d)} -> {len(novo)} b |", nds_rom.substituir(rom, c, novo))
open(SAIDA, "wb").write(rom)
print("ROM:", SAIDA)
