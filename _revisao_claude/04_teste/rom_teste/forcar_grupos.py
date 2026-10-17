"""ROM de TESTE (nao e entrega): troca os inimigos de grupos de encontro de um mapa,
mantendo o tamanho do script (reescreve so os 15 argumentos do SetEnemyParty com
codificacoes de mesmo comprimento total). Para ver em batalha linhas que so
aparecem em mapas avancados.

uso: python forcar_grupos.py <rom_base> <saida> <mapa> "<pos>=<ids_tipos>/<ids_slots>[/<arg1>]; ..."
  ids: ID do inimigo = linha + 1 (ex.: J. Sai = 2). Ex.:
  "2283=2/2,2; 2305=3,4/3,4/3"
  sem <pos>: lista os grupos do mapa.
"""
import struct, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import nds_rom


def toks(code, a, z):
    out = []; p = a
    while p < z:
        op = code[p]
        if op == 0x14: out.append(code[p + 1]); p += 2
        elif op == 0x15: out.append((code[p + 1] << 8) | code[p + 2]); p += 3
        elif op == 0x13: out.append(struct.unpack_from('>I', code, p + 1)[0]); p += 5
        elif 0x16 <= op <= 0x1f: out.append(op - 0x16); p += 1
        elif op == 0x24: out.append(None); p += 1
        else: return None
    if p != z:
        return None
    return out


def imports(d, offs):
    a4 = offs[4]
    hs, n = struct.unpack_from('<II', d, a4)
    base = a4 + hs + n * 4
    r = []
    for i in range(n):
        no, _ = struct.unpack_from('<HH', d, a4 + hs + i * 4)
        r.append(d[base + no:d.index(b'\x00', base + no)].decode())
    return r


def grupos(d):
    offs = list(struct.unpack_from('<6I', d, 8))
    k = imports(d, offs).index('SetEnemyParty')
    res = []
    p = offs[0]
    while True:
        p = d.find(bytes([0x4a, k]), p, offs[1])
        if p == -1:
            break
        if d[p - 2] == 0x14 and d[p - 1] == 15:
            for s in range(p - 3, p - 80, -1):
                t = toks(d, s, p - 2)
                if t is not None and len(t) == 15:
                    res.append((p, s, t)); break
        p += 2
    return res


def tamanhos(v):
    if v is None: return [1]
    if 0 <= v <= 9: return [1, 2, 3, 5]
    if v <= 127: return [2, 3, 5]
    if v <= 0x7fff: return [3, 5]
    return [5]


def cod(v, n):
    if v is None: return b'\x24'
    if n == 1: return bytes([0x16 + v])
    if n == 2: return bytes([0x14, v])
    if n == 3: return bytes([0x15, v >> 8, v & 255])
    return b'\x13' + struct.pack('>I', v)


def codificar(args, L):
    esc = [0] * len(args)  # indice em tamanhos()
    tot = lambda: sum(tamanhos(a)[e] for a, e in zip(args, esc))
    while tot() < L:
        for i, a in enumerate(args):
            if esc[i] + 1 < len(tamanhos(a)) and tot() + tamanhos(a)[esc[i] + 1] - tamanhos(a)[esc[i]] <= L:
                esc[i] += 1; break
        else:
            return None
    if tot() != L:
        return None
    return b''.join(cod(a, tamanhos(a)[e]) for a, e in zip(args, esc))


if __name__ == '__main__':
    BASE, SAIDA, MAPA = sys.argv[1:4]
    spec = sys.argv[4] if len(sys.argv) > 4 else ''
    rom = bytearray(open(BASE, 'rb').read())
    cams = [c for c in nds_rom.caminhos(rom) if c.endswith('/' + MAPA + '.sb')]
    mud = {}
    todos = None
    if spec.startswith('TODOS='):
        todos = int(spec.split('=')[1]); spec = ''
    for item in [x.strip() for x in spec.split(';') if x.strip()]:
        pos, r = item.split('=')
        partes = r.split('/')
        tipos = [int(x) for x in partes[0].split(',')]
        slots = [int(x) for x in partes[1].split(',')]
        arg1 = int(partes[2]) if len(partes) > 2 else None
        mud[int(pos)] = (tipos, slots, arg1)
    for c in cams:
        d = bytearray(nds_rom.ler(rom, c))
        for p, s, t in grupos(d):
            if todos is not None and t[12] is None:
                nslots = len([v for v in t[6:12] if v])
                mud[p] = ([todos], [todos] * nslots, None)
            if not mud:
                print(c, p, t); continue
            if p not in mud:
                continue
            tipos, slots, arg1 = mud[p]
            n = list(t)
            if arg1 is not None: n[1] = arg1
            n[2:6] = (tipos + [1, 1, 1, 1])[:4]
            n[6:12] = (slots + [0] * 6)[:6]
            b = codificar(n, p - 2 - s)
            if b is None:
                print('NAO CABE', c, p, n); continue
            assert toks(b, 0, len(b)) == n
            d[s:p - 2] = b
            print('ok', c, p, n)
        if mud:
            nds_rom.substituir(rom, c, bytes(d))
    if mud or todos is not None:
        open(SAIDA, 'wb').write(rom)
        print('ROM:', SAIDA)
