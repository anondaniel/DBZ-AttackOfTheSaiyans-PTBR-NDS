cd "/c/Projetos/09_Dragon_Ball_Z_Attack_of_the_Saiyans/_revisao_claude/04_teste"
bash troca_map.sh pir01_00,yun01_00 >/dev/null
python ctl.py seq r13m "left:2500:400 down:2000:400 up:3500:400 t:38:384 w:1000 t:42:392 w:4500" >/dev/null
python ate_campo.py r13m 20
