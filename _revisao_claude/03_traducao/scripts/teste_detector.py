"""Confere o detector de campo/batalha do piloto em capturas conhecidas."""
import sys

from PIL import Image

sys.path.insert(0, "/ds/scripts")
sys.argv = ["x", "", "", "/tmp/x", ""]
src = open("/ds/scripts/piloto.py").read()
exec(src[:src.index("n_bat = 0")])  # so as funcoes

casos = {
    "/ds/saida/l2/p0010.png": ("campo", True, False),
    "/ds/saida/exp27/q0012.png": ("campo kame", True, False),
    "/ds/saida/exp17/q0007.png": ("dialogo", False, False),
    "/ds/saida/exp32/q0015.png": ("batalha roda", False, True),
    "/ds/saida/exp32/q0021.png": ("batalha paineis", False, True),
    "/ds/saida/exp29/final.png": ("mapa mundi", False, False),
}
ok = True
for arq, (rot, c, b) in casos.items():
    im = Image.open(arq).convert("RGB")
    rc, rb = no_campo(im), em_batalha(im)
    st = "ok" if (rc, rb) == (c, b) else "ERRO"
    ok &= st == "ok"
    print(f"{st:4s} {rot:16s} campo={rc} batalha={rb}")
print("TUDO OK" if ok else "FALHOU")
