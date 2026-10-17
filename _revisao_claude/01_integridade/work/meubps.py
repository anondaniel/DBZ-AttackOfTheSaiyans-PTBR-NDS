# Aplicador BPS independente (escrito do zero pela revisao), com estatisticas.
import struct, zlib
def vint(p,i):
    data=0; shift=1
    while True:
        x=p[i]; i+=1
        data+=(x&0x7f)*shift
        if x&0x80: return data,i
        shift<<=7; data+=shift
def info(p):
    assert p[:4]==b'BPS1'
    i=4; ss,i=vint(p,i); ts,i=vint(p,i); ms,i=vint(p,i); meta=p[i:i+ms]; i+=ms
    cs,ct,cp=struct.unpack_from('<III',p,len(p)-12)
    return dict(src_size=ss,tgt_size=ts,meta=meta.decode('utf-8','replace'),src_crc='%08x'%cs,tgt_crc='%08x'%ct,patch_crc='%08x'%cp,
                patch_crc_calc='%08x'%zlib.crc32(p[:-4]),body=i)
def apply(src,p):
    inf=info(p); i=inf['body']; end=len(p)-12
    out=bytearray(inf['tgt_size']); o=0; sr=0; tr=0
    st={0:0,1:0,2:0,3:0}; nb={0:0,1:0,2:0,3:0}
    while i<end:
        d,i=vint(p,i); cmd=d&3; ln=(d>>2)+1; st[cmd]+=1; nb[cmd]+=ln
        if cmd==0: out[o:o+ln]=src[o:o+ln]
        elif cmd==1: out[o:o+ln]=p[i:i+ln]; i+=ln
        elif cmd==2:
            x,i=vint(p,i); sr+=(-1 if x&1 else 1)*(x>>1); out[o:o+ln]=src[sr:sr+ln]; sr+=ln
        else:
            x,i=vint(p,i); tr+=(-1 if x&1 else 1)*(x>>1)
            for k in range(ln): out[o+k]=out[tr]; tr+=1
        o+=ln
    assert i==end, (i,end)
    return bytes(out), dict(info=inf, out_len=o, cmds=st, bytes_by_cmd=nb,
        src_crc_ok='%08x'%zlib.crc32(src)==inf['src_crc'], src_size_ok=len(src)==inf['src_size'],
        tgt_crc_ok='%08x'%zlib.crc32(out)==inf['tgt_crc'], patch_crc_ok=inf['patch_crc']==inf['patch_crc_calc'])
