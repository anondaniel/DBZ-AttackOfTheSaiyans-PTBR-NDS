# Parser NDS/NitroFS independente (revisao).
import struct
u16 = lambda b, o: struct.unpack_from('<H', b, o)[0]
u32 = lambda b, o: struct.unpack_from('<I', b, o)[0]


def crc16(d, crc=0xFFFF):
    for x in d:
        crc ^= x
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def header(r):
    return dict(
        title=r[0:12].decode('ascii', 'replace'), code=r[12:16].decode(), maker=r[16:18].decode(),
        unitcode=r[0x12], devcap=r[0x14], chip_bytes=(128 * 1024) << r[0x14], romver=r[0x1E],
        arm9_off=u32(r, 0x20), arm9_entry=u32(r, 0x24), arm9_ram=u32(r, 0x28), arm9_size=u32(r, 0x2C),
        arm7_off=u32(r, 0x30), arm7_entry=u32(r, 0x34), arm7_ram=u32(r, 0x38), arm7_size=u32(r, 0x3C),
        fnt_off=u32(r, 0x40), fnt_size=u32(r, 0x44), fat_off=u32(r, 0x48), fat_size=u32(r, 0x4C),
        ovt9_off=u32(r, 0x50), ovt9_size=u32(r, 0x54), ovt7_off=u32(r, 0x58), ovt7_size=u32(r, 0x5C),
        banner_off=u32(r, 0x68), secure_crc=u16(r, 0x6C), used_rom=u32(r, 0x80), header_size=u32(r, 0x84),
        logo_crc=u16(r, 0x15C), hdr_crc=u16(r, 0x15E),
        hdr_crc_calc=crc16(r[:0x15E]), logo_crc_calc=crc16(r[0xC0:0x15C]))


def files(r):
    h = header(r)
    fnt, fat, nfat = h['fnt_off'], h['fat_off'], h['fat_size'] // 8
    names = {}

    def walk(did, pre):
        base = fnt + (did & 0xFFF) * 8
        p = fnt + u32(r, base)
        fid = u16(r, base + 4)
        while True:
            t = r[p]; p += 1
            if t == 0:
                break
            n = t & 0x7F
            nm = r[p:p + n].decode('latin-1'); p += n
            if t & 0x80:
                walk(u16(r, p), pre + nm + '/'); p += 2
            else:
                names[fid] = pre + nm; fid += 1
    walk(0xF000, '')
    for kind, off, size in (('overlay9', h['ovt9_off'], h['ovt9_size']), ('overlay7', h['ovt7_off'], h['ovt7_size'])):
        for i in range(size // 32):
            e = off + i * 32
            names.setdefault(u32(r, e + 0x18), f'[{kind}_{u32(r, e):04d}]')
    out = {}
    for fid in range(nfat):
        out[fid] = (names.get(fid, f'[fid {fid} sem nome]'), u32(r, fat + fid * 8), u32(r, fat + fid * 8 + 4))
    return h, out
