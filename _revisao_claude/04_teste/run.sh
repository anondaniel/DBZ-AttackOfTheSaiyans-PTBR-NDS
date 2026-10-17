# uso: run.sh prefixo nshots "passos por shot"
P=$1; N=$2; STEP=$3; S=""; L=""
for i in $(seq 1 $N); do S="$S $STEP s:$P$i"; L="$L $P$i"; done
python ctl.py seq ${INST:-coer} "$S" >/dev/null; python mont.py ver.png $L
