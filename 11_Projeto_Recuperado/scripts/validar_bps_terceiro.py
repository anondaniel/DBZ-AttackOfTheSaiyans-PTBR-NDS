"""Valida e aplica o patch com o python-bps (Timothy Allen), implementacao
independente da nossa, e compara com a ROM do hack."""
import hashlib
import os
import sys

import time

time.clock = time.perf_counter  # python-bps e de antes do Python 3.8
sys.path.insert(0, "/tmp/pb/x/python-bps-5")
import bps.apply
import bps.validate

PATCH, ORIG, HACK = sys.argv[1], "/ds/rom/aots.nds", sys.argv[2]
with open(PATCH, "rb") as p:
    bps.validate.check_stream(p)
print("validate: ok")
tmp = "/tmp/terceiro.nds"
with open(PATCH, "rb") as p, open(ORIG, "rb") as s, open(tmp, "wb") as t:
    bps.apply.apply_to_files(p, s, t)
h = lambda f: hashlib.sha256(open(f, "rb").read()).hexdigest()
a, b = h(tmp), h(HACK)
os.remove(tmp)
print("apply: ok |", "IDENTICA a ROM do hack" if a == b else f"DIFERENTE {a} x {b}")
