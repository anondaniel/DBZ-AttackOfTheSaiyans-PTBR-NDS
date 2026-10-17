# uso: bash testa_id.sh <rom_base> <spec_tipo> <prefixo> [turnos]
#  spec_tipo: "X" = todos os grupos da Ilha de Treinamento viram o inimigo de ID X (1 ou 2 iguais);
#             ou uma spec completa do forcar_grupos.py (contendo "=")
cd "/c/Projetos/09_Dragon_Ball_Z_Attack_of_the_Saiyans/_revisao_claude/04_teste"
BASE=$1; X=$2; PREF=$3; TURNOS=${4:-0}
case "$X" in *=*) SPEC="$X";; *) SPEC="2283=$X/$X,$X; 2305=$X/$X,$X; 2330=$X/$X; 2351=$X/$X; 2377=$X/$X,$X; 2402=$X/$X; 2510=$X/$X,$X,$X; 2532=$X/$X,$X; 2559=$X/$X,$X; 2584=$X/$X; 2605=$X/$X";; esac
python ctl.py kill r13m >/dev/null 2>&1; sleep 1
cp "$BASE" rom13/emu_r13map/r13map.nds
for m in tut01_00 tut02_00; do
  python -B rom_teste/forcar_grupos.py rom13/emu_r13map/r13map.nds rom13/emu_r13map/tmp.nds $m "$SPEC" | grep -c "NAO CABE" | sed "s/^/$m nao_cabe=/"
  mv rom13/emu_r13map/tmp.nds rom13/emu_r13map/r13map.nds
done
bash abrir_r13m.sh
python ctl.py seq r13m "left:1500:300 down:600:300" >/dev/null
python -u uma_batalha.py r13m "$PREF" 80 $TURNOS 2>&1 | grep RESULTADO
