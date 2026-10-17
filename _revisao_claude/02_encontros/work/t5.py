from comum import *
import re
d=rom('orig')
for f in ('script/EN/cf/worldmap.sb','script/EN/cf/world_01.sb'):
    b=nds_rom.ler(d,f)
    print('==',f)
    print(' | '.join(m.group().decode() for m in re.finditer(rb"[ -~]{3,}", b)))
