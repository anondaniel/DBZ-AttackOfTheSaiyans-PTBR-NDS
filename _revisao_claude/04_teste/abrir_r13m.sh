# reabre a instancia r13m com a copia do save do Switch (Ilha de Treinamento) e carrega o jogo
cd "/c/Projetos/09_Dragon_Ball_Z_Attack_of_the_Saiyans/_revisao_claude/04_teste"
python ctl.py kill r13m >/dev/null 2>&1; sleep 1
cp saves_copias/copia_switch_savefiles_melonds.sav rom13/emu_r13map/r13map.sav
(python ctl.py start r13m rom13/emu_r13map rom13/emu_r13map/r13map.nds > log_r13m.txt 2>&1 &)
python -c "import time;time.sleep(6)"
python ctl.py seq r13m "start:100:1500 start:100:1500 start:100:2500 w:2000 a:100:2500 a:100:4500 b:100:800 b:100:800 b:100:1000 s:r13m_carregado" >/dev/null
