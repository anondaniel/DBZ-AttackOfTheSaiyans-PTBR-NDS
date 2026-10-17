import sys, zipfile, hashlib, zlib, json
sys.path.insert(0, sys.argv[1])
import meubps
sys.path.insert(1, r'C:\Projetos\09_Dragon_Ball_Z_Attack_of_the_Saiyans\11_Projeto_Recuperado\scripts')
import bps as bps_projeto
P=r'C:\Projetos\09_Dragon_Ball_Z_Attack_of_the_Saiyans'
orig=zipfile.ZipFile(P+r'\00_Original\Dragon Ball Z_ Attack of the Saiyans.zip').read('Dragon Ball Z - Attack of the Saiyans (USA) (En,Fr).nds')
rc1=open(P+r'\01_ROM\DBZ Attack of the Saiyans PT-BR.nds','rb').read()
coe=open(P+r'\12_Coerencia_Historia\DBZ Attack of the Saiyans PT-BR Coerencia.nds','rb').read()
antiga=open(P+r'\00_Original\rom_antiga_do_switch_2026-10-11\Dragon Ball Z - Attack of the Saiyans.nds','rb').read()
sh=lambda d: hashlib.sha256(d).hexdigest()
casos=[('aots_ptbr.bps',P+r'\11_Projeto_Recuperado\patches\aots_ptbr.bps',orig,rc1,'original->rc.1'),
 ('Coerencia_sobre_PTBR_1.0.0-rc.1.bps',P+r'\12_Coerencia_Historia\Coerencia_sobre_PTBR_1.0.0-rc.1.bps',rc1,coe,'rc.1->Coerencia'),
 ('DBZ_PTBR_Coerencia_completo.bps',P+r'\12_Coerencia_Historia\DBZ_PTBR_Coerencia_completo.bps',orig,coe,'original->Coerencia'),
 ('aots_bichos_db.bps (antigo)',P+r'\11_Projeto_Recuperado\patches\versoes-antigas\aots_bichos_db.bps',orig,None,'original->hack antigo')]
res=[]
for nome,path,src,esperado,desc in casos:
    p=open(path,'rb').read()
    out,st=meubps.apply(src,p)
    r=dict(patch=nome,desc=desc,**{k:v for k,v in st.items()})
    r['saida_sha256']=sh(out); r['saida_crc32']='%08x'%zlib.crc32(out)
    r['igual_esperado']= (out==esperado) if esperado is not None else None
    try:
        out2=bps_projeto.aplicar(src,p); r['bps_projeto_igual']=(out2==out)
    except AssertionError as e: r['bps_projeto_igual']='ERRO '+str(e)
    # origem errada deve ser rejeitada
    for nm,alt in (('original',orig),('rc1',rc1),('antiga_switch',antiga)):
        if alt is src: continue
        r['rejeita_origem_'+nm]= '%08x'%zlib.crc32(alt)!=st['info']['src_crc']
    res.append(r); print(json.dumps(r,indent=1,default=str))
json.dump(res,open(sys.argv[2],'w'),indent=1,default=str)
