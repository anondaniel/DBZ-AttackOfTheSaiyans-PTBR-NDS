"""TESTE: dialogo (.sb) aceita acento? Troca, com o MESMO tamanho em bytes,
a primeira fala do Kuririn na Training Island em todas as pastas de idioma
que a tem. Sem mexer em ponteiro."""
import sys

sys.path.insert(0, "/ds/scripts")
import nds_rom

VELHO = b"Mmm? There's something nearby..."
NOVO = "Hã? Há algo aqui... é ação já!!".encode("latin-1")
NOVO = NOVO[:len(VELHO)].ljust(len(VELHO), b" ")
assert len(NOVO) == len(VELHO)
rom = bytearray(open("/ds/rom/aots.nds", "rb").read())
n = 0
for c in nds_rom.caminhos(rom):
    if c.endswith("tut01_00.sb"):
        d = nds_rom.ler(rom, c)
        if VELHO in d:
            nds_rom.substituir(rom, c, d.replace(VELHO, NOVO))
            n += 1
            print("trocado em", c)
print(n, "arquivo(s); texto novo:", NOVO.decode("latin-1"))
open("/ds/rom/teste_dialogo.nds", "wb").write(rom)
