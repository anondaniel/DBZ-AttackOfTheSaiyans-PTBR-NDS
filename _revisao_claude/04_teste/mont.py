import sys
from PIL import Image
out=sys.argv[1]; ims=[Image.open(f'capturas/{n}.png') for n in sys.argv[2:]]
ims=[i.resize((256,384),Image.NEAREST) if i.size==(384,576) else i for i in ims]
W=sum(i.width for i in ims)+4*(len(ims)-1); H=max(i.height for i in ims)
m=Image.new('RGB',(W,H),(255,0,255)); x=0
for i in ims: m.paste(i,(x,0)); x+=i.width+4
m.save(out)
