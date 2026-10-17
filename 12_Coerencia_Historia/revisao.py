"""Revisão narrativa das 48 trocas, sobre a ROM PT-BR já validada.

Não modifica roteiro, encontros, chefes, estatísticas, saves ou código executável.
Todas as trocas passam a usar personagens terrestres ou guardiões genéricos.
As versões canônicas de Saibamen nos IDs originais continuam intactas.
"""
from pathlib import Path
import sys, json, hashlib, colorsys, collections, csv
from auditar import BASE, SCRIPTS, ROM, encontros
sys.path.insert(0, str(SCRIPTS))
import nds_rom
from bdat import ler_container
from bdat_escrita import tabelas_com_offset, gravar_num, ler_num
from bdat_strings import gravar_str, conferir
from chr_paletas import paletas, com_paletas, rgb555
from plano_bichos import PLANO

OUT = Path(__file__).resolve().parent
# linha: (modelo de enemy_param, novo nome, justificativa)
REVISAO = {
 1:(167,'Robô de Patrulha','Variante original de Saibaman aparece em Paozu antes da invasão; vira autômato terrestre.'),
 2:(168,'Robô do Deserto','Variante original aleatória vira autômato, sem antecipar os Saibamen.'),
 3:(140,'Mutante Errante','Variante original aleatória vira experimento humanoide, não um invasor Saiyajin.'),
 4:(141,'Mutante Sombrio','Variante original aleatória vira experimento humanoide, não um invasor Saiyajin.'),
 74:(11,'Mecha Patrulheiro','Máquina terrestre; não presume um exército ativo da Red Ribbon.'),
 75:(12,'Mecha de Combate','Máquina terrestre sem vínculo com eventos futuros.'),
 76:(71,'Guardião Errante','Humanoide genérico compatível com as várias regiões que compartilham este ID.'),
 80:(56,'Lutador Errante','Retira as servas da Princesa Serpente do tutorial do Kuririn e do deserto.'),
 81:(60,'Guarda da Mansão','Mantém a serva somente nos encontros da Mansão da Princesa.'),
 82:(38,'Corsária Venenosa','A caverna dos piratas recebe uma corsária, sem antecipar a Princesa Serpente.'),
 95:(32,'Batedor do Ermo','Batedor terrestre no ermo e deserto, sem tropas Saiyajins.'),
 96:(39,'Batedora do Deserto','Bandida adaptada ao deserto, sem tropas Saiyajins.'),
 97:(34,'Mercenário de Elite','Mercenário terrestre nas áreas iniciais e tardias que compartilham o ID.'),
 98:(8,'Piloto Renegado','Veículo terrestre, sem atribuir cada patrulha a uma facção específica.'),
 99:(9,'Piloto Mercenário','Veículo terrestre; preserva o inimigo substituído.'),
 100:(10,'Piloto Veterano','Veículo terrestre nas regiões de fim de jogo.'),
 101:(56,'Arruaceiro do Bambu','Lutador terrestre no prólogo de Kuririn, sem antecipar os Saiyajins.'),
 102:(27,'Mercenário da Neve','Bandido terrestre na montanha gelada.'),
 103:(69,'Guardião da Floresta','Guardião místico na Floresta de Enma; retira o soldado dimensional.'),
 104:(32,'Atirador da Montanha','Atirador terrestre em Paozu e no deserto, antes e depois de Raditz.'),
 105:(24,'Guerreira Errante','Figura humana sem facção ou tecnologia futura; ID compartilhado entre regiões.'),
 106:(34,'Atirador Veterano','Veterano terrestre também nas áreas tardias; não acrescenta Saibamen.'),
 107:(14,'Desertor Red Ribbon','Mantém os remanescentes terrestres, sem antecipar outra saga.'),
 108:(15,'Espião Red Ribbon','Mantém remanescentes coerentes com Torre Muscle e Yunzabit.'),
 109:(40,'Sentinela Pirata','Troca a afiliação Red Ribbon por pirata na caverna dos piratas.'),
 110:(35,'Brutamontes do Ermo','Brutamontes humano, sem armadura ou identificação Saiyajin.'),
 111:(57,'Lutador Veterano','Lutador terrestre no Campo do Mutaito.'),
 112:(36,'Brutamontes Glacial','Humano terrestre em Yunzabit.'),
 113:(63,'Saqueador do Ermo','Saqueador terrestre no Ermo do Espinafre.'),
 114:(25,'Bandida Glacial','Bandida terrestre no Monte Frappe.'),
 115:(58,'Mestre Errante','Lutador experiente no Campo do Mutaito e nas visitas tardias a Paozu.'),
 116:(53,'Discípulo Expulso','Discípulo hostil no começo do jogo, sem invasão alienígena antecipada.'),
 117:(70,'Guardião Peregrino','Guardião genérico, sem Saibaman ou tropa de uma saga futura.'),
 118:(38,'Corsária Veterana','Inimigo humano da caverna dos piratas.'),
 119:(5,'Robô Patrulheiro','Máquina sem afiliação pirata forçada na Fonte do Eremita.'),
 120:(6,'Robô da Caverna','Máquina da caverna sem nova história de ocupação pirata.'),
 121:(7,'Robô das Areias','Máquina no deserto, sem afiliação pirata forçada.'),
 131:(125,'Vampiro Errante','Vampiro genérico, sem afirmar que é o lutador nomeado da Vovó Uranai.'),
 132:(126,'Vampiro Sanguinário','Vampiro genérico em regiões com criaturas sobrenaturais.'),
 133:(127,'Vampiro Ancião','Retira o título de rei; não cria personagem importante fora do roteiro.'),
 134:(44,'Capanga da Caverna','Humano de lança; não afirma que o Grupo do Coelho ocupa a caverna.'),
 135:(45,'Capanga da Fonte','Humano de lança na fonte, sem organização inventada.'),
 136:(46,'Capanga Sombrio','Humano hostil nos esgotos.'),
 149:(17,'Recruta Renegado','Soldado terrestre renegado no deserto.'),
 150:(18,'Soldado Incendiário','Soldado terrestre no vulcão, sem tropa Saiyajin.'),
 151:(50,'Aprendiz da Floresta','Aprendiz humanoide na Floresta de Enma, sem Red Ribbon no além.'),
 155:(62,'Batedor Escavador','Explorador terrestre no Ermo do Espinafre.'),
 156:(54,'Lutador Noturno','Lutador terrestre no Campo do Mutaito.'),
 157:(33,'Batedor Venenoso','Atirador terrestre do deserto, sem Saibaman.'),
 161:(23,'Recruta Escavador','Reserva substituída também; não reintroduz brotos de Saibaman.'),
 162:(51,'Aprendiz Noturno','Reserva substituída também; mantém a família de lutadores.'),
 163:(40,'Batedora Venenosa','Reserva substituída também; mantém a família de batedores terrestres.'),
}

def sha(data): return hashlib.sha256(data).hexdigest()

def nova_paleta(p, row):
    """Recolore roupas frias/saturadas, preservando transparência e tons de pele.
    O índice é exclusivo e a comparação abaixo impede paletas idênticas.
    """
    result = list(p)
    for i,c in enumerate(p):
        r,g,b=(c&31)/31,((c>>5)&31)/31,((c>>10)&31)/31
        h,s,v=colorsys.rgb_to_hsv(r,g,b)
        if i and s>.25 and h>.17 and v>.12:
            rr,gg,bb=colorsys.hsv_to_rgb((h+(row%11+1)*.037)%1,s,v)
            result[i]=rgb555(round(rr*31),round(gg*31),round(bb*31))
    return result

def build():
    before=ROM.read_bytes()
    assert sha(before)=='41412a4727328d5341ba2f7d17fa567c84db137d8cd082bc32389c6d27643a5f'
    rom=bytearray(before)
    paths=nds_rom.caminhos(before)
    # O índice NitroFS permanece igual nesta revisão.
    nds_rom.caminhos=lambda _: paths
    base=ler_container(nds_rom.ler(before,'btl/bdat/EN/bdat.bin'))
    ep=base['enemy_param']['linhas']
    assert set(REVISAO)==set(PLANO)|{1,2,3,4}
    groups=encontros()
    maps={i:sorted({g['mapa'] for g in groups if i in g['ids']}) for i in REVISAO}
    pals_by_file={}
    chosen={}
    for row,(model,name,reason) in sorted(REVISAO.items()):
        src=ep[model]
        file=src['file']
        path=f'btl/ene/{file}.chr'
        if path not in pals_by_file:
            pals_by_file[path]=paletas(nds_rom.ler(before,path))
        pals=pals_by_file[path]
        p=nova_paleta(pals[src['palno']],row)
        # Se o desenho não tem roupa fria, mantém o desenho original e muda
        # uma cor não transparente o mínimo necessário para separar variantes.
        while p in pals:
            k=max(range(1,16),key=lambda i: sum((p[i]>>s)&31 for s in (0,5,10)))
            c=p[k]; p[k]=(c&~31)|(((c&31)+1)%32)
        assert len(pals)<16, (file,len(pals))
        chosen[row]=(file,len(pals))
        pals.append(p)
        assert src['size']<=ep[row]['size'], (row,src['size'],ep[row]['size'])
        assert len(name.encode('latin-1'))<=23
    changed=[]
    for path,pals in pals_by_file.items():
        old=nds_rom.ler(before,path)
        new=com_paletas(old,pals)
        assert new[8+len(pals)*32:]==old[8+old[5]*32:]
        nds_rom.substituir(rom,path,new)
        changed.append(path)
    report=[]
    for lang in ('EN','US','FR','SP','GR','IT'):
        path=f'btl/bdat/{lang}/bdat.bin'
        old=nds_rom.ler(before,path)
        b=bytearray(old); changes={}
        for row,(model,name,reason) in sorted(REVISAO.items()):
            tables=tabelas_com_offset(b)
            table=tables['enemy_param']
            file,pal=chosen[row]
            b,_=gravar_str(b,'enemy_param',row,'file',file)
            changes['enemy_param',row,'file']=file
            tables=tabelas_com_offset(b); table=tables['enemy_param']
            values={'palno':pal}
            for col in ('size','shadow','atk1','atk2','atk3','atk4'):
                values[col]=ler_num(b,table,model,col)
            for col,val in values.items():
                gravar_num(b,table,row,col,val)
                changes['enemy_param',row,col]=val
            nid=ler_num(b,table,row,'name_id')
            col=tables['character_name']['colunas'][0][0]
            # Nome próprio de cada entrada, nunca reutiliza o nome do modelo.
            assert sum(e['name_id']==nid for e in table['linhas'])==1
            b,_=gravar_str(b,'character_name',nid-1,col,name)
            changes['character_name',nid-1,col]=name
        conferir(old,b,changes)
        nds_rom.substituir(rom,path,b)
        changed.append(path)
    after=bytes(rom)
    # Todos os arquivos fora da lista permitida, inclusive roteiros/chefes/som,
    # devem permanecer byte a byte iguais.
    for path,fid in paths.items():
        a,z=nds_rom.fat_entrada(before,fid); aa,zz=nds_rom.fat_entrada(after,fid)
        if path not in changed:
            assert before[a:z]==after[aa:zz],path
    assert before[nds_rom.u32(before,0x20):nds_rom.u32(before,0x20)+nds_rom.u32(before,0x2c)]==after[nds_rom.u32(after,0x20):nds_rom.u32(after,0x20)+nds_rom.u32(after,0x2c)]
    assert nds_rom.u16(after,0x15e)==nds_rom.crc16(after[:0x15e])
    updated=ler_container(nds_rom.ler(after,'btl/bdat/EN/bdat.bin'))
    new_ep=updated['enemy_param']['linhas']
    names=updated['character_name']['linhas']
    def app(i):return new_ep[i]['file'],new_ep[i]['palno']
    def nm(i):return names[new_ep[i]['name_id']-1]['en'] if new_ep[i]['name_id'] else ''
    for group in groups:
        ids=set(group['ids'])
        for i in ids:
            for j in ids:
                if i!=j and (i in REVISAO or j in REVISAO):
                    assert app(i)!=app(j) or nm(i)==nm(j),(group,i,j)
                    assert nm(i)!=nm(j) or app(i)==app(j),(group,i,j)
        for i in ids & REVISAO.keys():
            assert not any(x in nm(i).lower() for x in ('saiyajin','saibaman','broto'))
    assert new_ep[0]==ep[0], 'Saibaman básico canônico alterado'
    for row,(model,name,reason) in sorted(REVISAO.items()):
        font=nds_rom.ler(after,'latin1.fnt')[:256]
        width=sum(font[ord(c)] for c in name)
        assert width<=175,(name,width)
        previous=PLANO.get(row,('Variante de Saibaman original',None,None,None,base['character_name']['linhas'][ep[row]['name_id']-1]['en']))
        report.append({'linha':row,'animal_original':previous[0],'nome_anterior':previous[4],'nome_revisado':name,'sprite':chosen[row][0],'paleta':chosen[row][1],'modelo':model,'largura_px':width,'mapas':maps[row],'motivo':reason})
    output=OUT/'DBZ Attack of the Saiyans PT-BR Coerencia.nds'
    output.write_bytes(after)
    (OUT/'revisao_inimigos.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    with (OUT/'revisao_inimigos.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=report[0].keys());w.writeheader();w.writerows(report)
    result={'base_sha256':sha(before),'rom_sha256':sha(after),'rom_bytes':len(after),'inimigos_revisados':len(report),'animais_substituidos':48,'variantes_originais_revisadas':4,'mapas_com_encontros':len({g['mapa'] for g in groups}),'grupos_conferidos':len(groups),'arquivos_alterados':changed,'roteiros_identicos':True,'balanceamento_preservado':True,'saibaman_basico_preservado':True,'teste_jogavel':'Pendente; verificações estruturais e renderização não substituem teste no console.'}
    (OUT/'resultado_verificacao.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return output

if __name__=='__main__':build()
