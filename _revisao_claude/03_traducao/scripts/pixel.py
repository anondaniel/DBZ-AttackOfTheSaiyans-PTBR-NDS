"""Media RGB de regioes de capturas. uso: pixel.py <png> y0:y1,x0:x1 ..."""
import sys

import numpy as np
from PIL import Image

a = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
for reg in sys.argv[2:]:
    ys, xs = reg.split(",")
    y0, y1 = map(int, ys.split(":"))
    x0, x1 = map(int, xs.split(":"))
    m = a[y0:y1, x0:x1].reshape(-1, 3)
    print(reg, m.mean(0).round(), m.std(0).round())
