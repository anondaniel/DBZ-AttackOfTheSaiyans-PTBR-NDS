# uso: bash testa_kou.sh <rom_base> <ID> <prefixo>  -> todos os grupos aleatorios do Deserto (kou01_00) viram o ID dado
cd "/c/Projetos/09_Dragon_Ball_Z_Attack_of_the_Saiyans/_revisao_claude/04_teste"
BASE=$1; X=$2; PREF=$3
python ctl.py kill r13m >/dev/null 2>&1; sleep 1
python rom_teste/liberar_mapas.py "$BASE" rom13/emu_r13map/tmp0.nds kou01_00 | grep "script/cf/"
python -B rom_teste/forcar_grupos.py rom13/emu_r13map/tmp0.nds rom13/emu_r13map/r13map.nds kou01_00 "TODOS=$X" | grep -c "^ok" | sed 's/^/grupos trocados: /'
rm -f rom13/emu_r13map/tmp0.nds
cp emu_coer/coer.sav rom13/emu_r13map/r13map.sav
(python ctl.py start r13m rom13/emu_r13map rom13/emu_r13map/r13map.nds > log_r13m.txt 2>&1 &)
python -c "import time;time.sleep(6)"
python ctl.py seq r13m "start:100:1500 start:100:1500 start:100:2500 w:2000 a:100:2500 a:100:4500 b:100:800 b:100:800 b:100:1000 right:1500:300 down:2000:5000 up:1500:400 left:2000:400 down:1500:400 s:kou_nav" >/dev/null
python - <<'PY'
import ctl
from PIL import Image
im=Image.open(ctl.AQUI/'capturas'/'kou_nav.png')
# o icone do Deserto Break fica na tela de baixo; tenta as duas posicoes vistas
for x,y in [(87,426),(246,372)]:
    pass
PY
python ctl.py seq r13m "t:87:426 w:1000 t:92:432 w:4500" >/dev/null
python ate_campo.py r13m 20 >/dev/null
python ctl.py seq r13m "up:800:300" >/dev/null
python -u uma_batalha.py r13m "$PREF" 80 ${TURNOS:-0} | grep RESULTADO
