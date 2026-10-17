"""Diferenca bruta dos bdat.bin rc1->coe: por tabela, e dentro de enemy_param/character_name por regiao."""
import sys, struct
sys.path.insert(0, sys.argv[1])
import nitro
P = r'C:\Projetos\09_Dragon_Ball_Z_Attack_of_the_Saiyans'
rc1 = open(P + r'\01_ROM\DBZ Attack of the Saiyans PT-BR.nds', 'rb').read()
coe = open(P + r'\12_Coerencia_Historia\DBZ Attack of the Saiyans PT-BR Coerencia.nds', 'rb').read()


def fsmap(r):
    h, f = nitro.files(r)
    return {n: r[a:z] for n, a, z in f.values()}


A, B = fsmap(rc1), fsmap(coe)
u16 = lambda t, o: struct.unpack_from('<H', t, o)[0]


def tables(b):
    n = struct.unpack_from('<I', b, 0)[0]
    offs = [struct.unpack_from('<I', b, 4 + i * 4)[0] for i in range(n + 1)]
    ini = sorted(o for o in offs if 0 < o < len(b))
    res = {}
    for i, a in enumerate(ini):
        z = ini[i + 1] if i + 1 < len(ini) else len(b)
        t = b[a:z]
        nm = t[u16(t, 6):t.index(b'\0', u16(t, 6))].decode()
        res[nm] = t
    return n, offs, res


for lang in ('EN', 'US', 'FR', 'SP', 'GR', 'IT'):
    p = f'btl/bdat/{lang}/bdat.bin'
    na, oa, ta = tables(A[p]); nb, ob, tb = tables(B[p])
    dif = [k for k in ta if ta[k] != tb[k]]
    print(lang, 'n tabelas', na, nb, '| tabelas com bytes diferentes:', dif, '| tamanho', len(A[p]), '->', len(B[p]))
    for k in ('enemy_param', 'character_name'):
        x, y = ta[k], tb[k]
        hdr = [i for i in range(0x20) if x[i] != y[i]]
        lin_off, tam, nl = u16(x, 0x0A), u16(x, 0x08), u16(x, 0x0C)
        fim_linhas = lin_off + tam * nl
        meta = [i for i in range(0x20, lin_off) if x[i] != y[i]]
        print(f'   {k}: tamanho {len(x)}->{len(y)} | cabecalho difere em {hdr} ({[(hex(u16(x,i)),hex(u16(y,i))) for i in hdr if i%2==0]}) | colunas/hash difere {len(meta)} bytes | hash_off {hex(u16(x,0x0E))} slots {u16(x,0x10)}')
