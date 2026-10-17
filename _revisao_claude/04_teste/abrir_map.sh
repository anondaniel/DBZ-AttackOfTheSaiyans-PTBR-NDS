cd "/c/Projetos/09_Dragon_Ball_Z_Attack_of_the_Saiyans/_revisao_claude/04_teste"
(python ctl.py start map emu_map emu_map/coer_mapas.nds > log_map.txt 2>&1 &)
python -c "import time;time.sleep(5)"
python ctl.py seq map "start:100:1500 start:100:1500 start:100:2500 w:2000 a:100:2500 a:100:4000 b:100:800 b:100:800 b:100:1000 s:mo0 right:1500:300 down:2000:4000 s:mo1" >/dev/null
python mont.py ver.png mo0 mo1
