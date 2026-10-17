from revisao import OUT, REVISAO, BASE, SCRIPTS
import sys,json
sys.path.insert(0,str(BASE/'09_Save_Atalho/nton_deps'))
from PIL import Image,ImageDraw,ImageFont
import nds_rom
from dump_tiles import ler_chr
from render_quadros import ler_anims,desenha

rom=(OUT/'DBZ Attack of the Saiyans PT-BR Coerencia.nds').read_bytes()
rows=json.loads((OUT/'revisao_inimigos.json').read_text(encoding='utf-8'))
sheet=Image.new('RGB',(8*180,((len(rows)+7)//8)*190),(24,28,36))
draw=ImageDraw.Draw(sheet)
try:font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
except OSError:font=ImageFont.load_default()
animations={}
for n,row in enumerate(rows):
    data=nds_rom.ler(rom,'btl/ene/'+row['sprite']+'.chr')
    c=ler_chr(data)
    errors=[]; anims=ler_anims(data,c['fim_tiles'],errors)
    assert not errors,(row,errors)
    assert anims and anims[0]
    im=desenha(anims[0][0],c['tiles'],c['pals'][row['paleta']])
    x,y=(n%8)*180,(n//8)*190
    sheet.paste(im,(x+10,y+23))
    draw.text((x+4,y+3),f"{row['linha']}: {row['nome_revisado']}",font=font,fill=(240,240,240))
    animations[row['sprite']]=[len(a) for a in anims]
sheet.save(OUT/'previa_inimigos.png')
(OUT/'animacoes_conferidas.json').write_text(json.dumps(animations,indent=2),encoding='utf-8')
print(len(rows),'previews; animações decodificadas:',len(animations))
