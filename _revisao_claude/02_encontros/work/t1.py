from encontros import *
import collections
r = chamadas(rom('coe'))
print(len(r), collections.Counter(x['argc'] for x in r))
print(len({x['mapa'] for x in r}))
for x in r[:15]: print(x['mapa'], x['argc'], x['args'])
import re
print(collections.Counter(re.sub(r'\d.*','',x['mapa']) for x in r))
