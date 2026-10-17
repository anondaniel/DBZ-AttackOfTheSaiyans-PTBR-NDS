from encontros import *
import collections, pickle
r = chamadas(rom('coe'))
pickle.dump(r, open('chamadas_coe.pkl','wb'))
fo = collections.Counter(x['args'][1] for x in r); print('formacoes', fo)
# ids > 173
big = [x for x in r if any(isinstance(v,int) and v>173 for v in x['args'][2:12])]
print('ids>173', len(big)); 
for x in big[:10]: print(x['mapa'], x['args'])
print(collections.Counter(tuple(type(v).__name__ for v in x['args'][12:]) for x in r))
# ids 2-5
for x in r:
    s=x['args'][6:12]
    if any(v in (2,3,4,5) for v in s) or any(v in (2,3,4,5) for v in x['args'][2:6]):
        print('SAI', x['mapa'], x['args'])
