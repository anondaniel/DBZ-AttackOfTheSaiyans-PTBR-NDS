#!/bin/sh
# montagem dos quadros bNN.png de uma pasta de cacar_batalha
cd "$1" || exit 1
for f in b*.png; do cp "$f" "q$f"; done
python3 /ds/scripts/montagem.py "$1" "${2:-6}" 0
rm -f qb*.png
