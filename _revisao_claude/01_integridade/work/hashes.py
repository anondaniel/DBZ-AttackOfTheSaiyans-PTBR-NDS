import hashlib, zlib, zipfile, json, sys, os
P=r'C:\Projetos\09_Dragon_Ball_Z_Attack_of_the_Saiyans'
files=[
 ('ORIG zip/(USA)(En,Fr).nds', ('zip', P+r'\00_Original\Dragon Ball Z_ Attack of the Saiyans.zip','Dragon Ball Z - Attack of the Saiyans (USA) (En,Fr).nds')),
 ('00_Original/rom_antiga_do_switch_2026-10-11', P+r'\00_Original\rom_antiga_do_switch_2026-10-11\Dragon Ball Z - Attack of the Saiyans.nds'),
 ('01_ROM/DBZ Attack of the Saiyans PT-BR.nds', P+r'\01_ROM\DBZ Attack of the Saiyans PT-BR.nds'),
 ('01_ROM zip/DBZ...PT-BR.nds', ('zip', P+r'\01_ROM\DBZ Attack of the Saiyans PT-BR.zip','DBZ Attack of the Saiyans PT-BR.nds')),
 ('07_Teste_Audio_PC/PTBR.nds', P+r'\07_Teste_Audio_PC\PTBR.nds'),
 ('10_Auditoria_Inimigos/Dragon Ball Z - Attack of the Saiyans.nds', P+r'\10_Auditoria_Inimigos\Dragon Ball Z - Attack of the Saiyans.nds'),
 ('12_Coerencia_Historia/DBZ ... PT-BR Coerencia.nds', P+r'\12_Coerencia_Historia\DBZ Attack of the Saiyans PT-BR Coerencia.nds'),
 ('Downloads/melonDS-1.1/DBZ Attack of the Saiyans PT-BR.nds', r'C:\Users\Administrador\Downloads\melonDS-1.1-windows-x86_64\DBZ Attack of the Saiyans PT-BR.nds'),
 ('Backup conteiner-ds/rom/aots.nds', r'C:\Users\Administrador\Downloads\DBZ-DS_2026-10-01\conteiner-ds\rom\aots.nds'),
 ('Backup conteiner-ds/rom/aots_ptbr_img.nds', r'C:\Users\Administrador\Downloads\DBZ-DS_2026-10-01\conteiner-ds\rom\aots_ptbr_img.nds'),
 ('patch 11/aots_ptbr.bps', P+r'\11_Projeto_Recuperado\patches\aots_ptbr.bps'),
 ('patch 12/Coerencia_sobre_PTBR_1.0.0-rc.1.bps', P+r'\12_Coerencia_Historia\Coerencia_sobre_PTBR_1.0.0-rc.1.bps'),
 ('patch 12/DBZ_PTBR_Coerencia_completo.bps', P+r'\12_Coerencia_Historia\DBZ_PTBR_Coerencia_completo.bps'),
]
out=[]
for name,src in files:
    if isinstance(src,tuple):
        d=zipfile.ZipFile(src[1]).read(src[2])
    else:
        d=open(src,'rb').read()
    r=dict(nome=name,bytes=len(d),crc32='%08x'%zlib.crc32(d),sha1=hashlib.sha1(d).hexdigest(),sha256=hashlib.sha256(d).hexdigest(),md5=hashlib.md5(d).hexdigest())
    out.append(r); print(r['nome'],r['bytes'],r['crc32'],r['sha1'],r['sha256'])
json.dump(out,open(sys.argv[1],'w'),indent=1)
