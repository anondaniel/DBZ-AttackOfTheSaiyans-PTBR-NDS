import sys
sys.path.insert(0, "/ds/scripts")
import nds_rom

rom = open("/ds/rom/aots.nds", "rb").read()
for lang in ["EN", "US", "FR", "SP", "GR", "IT"]:
    d = nds_rom.ler(rom, f"btl/bdat/{lang}/bdat.bin")
    print(f"{lang}: {len(d):,} bytes, primeiros: {d[:8].hex(' ')}  "
          f"{'LZ10' if d[0] == 0x10 else 'SEM compressao' if d[:4] == bytes([0x23, 0, 0, 0]) else '?'}")
