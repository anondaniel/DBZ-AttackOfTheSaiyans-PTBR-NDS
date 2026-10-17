#!/bin/sh
# Remonta a entrega inteira: verifica o plano, monta a ROM, gera o patch BPS
# e valida o patch com o aplicador proprio e com o python-bps.
# uso: entrega.sh [linhas_para_retestar_no_jogo separadas por espaco]
set -e
cd /ds
python3 scripts/hack_final.py /ds/rom/aots_bichos_db.nds | grep -E "SEM|problema|EN:|identicos|ROM:"
for l in "$@"; do rm -f "saida/diag_final/l$(printf %03d "$l").png"; done
if [ $# -gt 0 ]; then
  python3 scripts/diag_final.py 2>&1 | grep -E " ok|FALHOU|/48"
fi
python3 scripts/bps.py criar rom/aots.nds rom/aots_bichos_db.nds saida/aots_bichos_db.bps
python3 scripts/bps.py aplicar rom/aots.nds saida/aots_bichos_db.bps /tmp/p1.nds
cmp /tmp/p1.nds rom/aots_bichos_db.nds && echo "aplicador proprio: identica"
rm -f /tmp/p1.nds
python3 scripts/validar_bps_terceiro.py saida/aots_bichos_db.bps rom/aots_bichos_db.nds
sha256sum rom/aots_bichos_db.nds
