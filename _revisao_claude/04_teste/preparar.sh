#!/bin/sh
# Prepara uma instancia de teste para OUTRA ROM (nada fora desta pasta e alterado).
# uso: bash preparar.sh <inst> <caminho_da_rom.nds> [save_para_copiar.sav]
# Ex.: bash preparar.sh corr "../../13_Correcoes_Revisao/<ROM>.nds" emu_coer/coer.sav
set -e
cd "$(dirname "$0")"
INST=$1; ROM=$2; SAV=$3
mkdir -p "emu_$INST"
cp emu_coer/melonDS.exe "emu_$INST/"
cp emu_sav/melonDS.toml "emu_$INST/"            # volume 0, Tab=acelerar, Q/W=L/R
cp "$ROM" "emu_$INST/$INST.nds"
[ -n "$SAV" ] && cp "$SAV" "emu_$INST/$INST.sav"
sha256sum "emu_$INST/$INST.nds"
echo "Iniciar (em segundo plano, area de trabalho oculta):"
echo "  python ctl.py start $INST emu_$INST emu_$INST/$INST.nds &"
