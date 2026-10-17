from comum import *
import re,sys
d=rom(sys.argv[1])
for f in sys.argv[2:]:
    b=nds_rom.ler(d,f)
    s=[m.group().decode('latin-1') for m in re.finditer(rb"[ -~\xa0-\xff]{6,}", b)]
    s=[x for x in s if ' ' in x]
    print('==',f, len(s)); print('\n'.join(s[:80]))
