# uso: bash troca_map.sh mapa1,mapa2  -> regera a ROM de teste da etapa 13 e reabre a instancia r13m ate o mapa-mundi
cd "/c/Projetos/09_Dragon_Ball_Z_Attack_of_the_Saiyans/_revisao_claude/04_teste"
python ctl.py kill r13m >/dev/null 2>&1; sleep 1
python rom_teste/liberar_mapas.py rom13/emu_r13/r13.nds rom13/emu_r13map/r13map.nds "$1" | grep "script/cf/"
cp emu_coer/coer.sav rom13/emu_r13map/r13map.sav
(python ctl.py start r13m rom13/emu_r13map rom13/emu_r13map/r13map.nds > log_r13m.txt 2>&1 &)
python -c "import time;time.sleep(6)"
python ctl.py seq r13m "start:100:1500 start:100:1500 start:100:2500 w:2000 a:100:2500 a:100:4500 b:100:800 b:100:800 b:100:1000 right:1500:300 down:2000:5000 s:mapa_mundi" >/dev/null
