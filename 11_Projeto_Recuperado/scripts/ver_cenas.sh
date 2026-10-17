#!/bin/sh
# para cada cena: ROM de teste que abre a cena pelo icone da Ilha de
# Treinamento, entra, fotografa as caixas de dialogo
# uso: ver_cenas.sh <rom_base> <cena> [<cena> ...]
base=$1; shift
for c in "$@"; do
  python3 /ds/scripts/teste_cena.py "$base" "$c" /ds/rom/teste_cena.nds >/dev/null
  CADA=100 python3 /ds/scripts/explorar.py /ds/rom/teste_cena.nds /ds/saida/cena_$c \
    "down@20x3:2 nada:60 t176,148:40 nada:40 t176,148:40 nadax4:60" /ds/saida/exp27/estado.bin >/dev/null 2>&1
  python3 /ds/scripts/ler_dialogos.py /ds/rom/teste_cena.nds /ds/saida/cena_$c/estado.bin /ds/saida/cena_$c 40 700 2>&1 | tail -1
  PREF=c python3 /ds/scripts/montagem.py /ds/saida/cena_$c 5 1 2>&1 | tail -1
done
