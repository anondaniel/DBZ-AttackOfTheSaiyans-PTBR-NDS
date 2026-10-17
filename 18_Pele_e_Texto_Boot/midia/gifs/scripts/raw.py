import sys, ctypes, ctypes.wintypes as W
import ctl
from PIL import Image
def raw(inst):
    h, n, js = ctl.principal(inst)
    r = W.RECT(); ctl.u32.GetClientRect(h, ctypes.byref(r))
    w, hh = r.right, r.bottom
    hdc = ctl.u32.GetDC(h); mdc = ctl.g32.CreateCompatibleDC(hdc)
    bmp = ctl.g32.CreateCompatibleBitmap(hdc, w, hh); ctl.g32.SelectObject(mdc, bmp)
    ok = ctl.u32.PrintWindow(h, mdc, 1 | 2)
    class BIH(ctypes.Structure):
        _fields_ = [("biSize", W.DWORD), ("biWidth", W.LONG), ("biHeight", W.LONG),
                    ("biPlanes", W.WORD), ("biBitCount", W.WORD), ("biCompression", W.DWORD),
                    ("biSizeImage", W.DWORD), ("a", W.LONG), ("b", W.LONG), ("c", W.DWORD), ("d", W.DWORD)]
    bi = BIH(); bi.biSize = ctypes.sizeof(BIH); bi.biWidth = w; bi.biHeight = -hh; bi.biPlanes = 1; bi.biBitCount = 32
    buf = ctypes.create_string_buffer(w * hh * 4)
    ctl.g32.GetDIBits(mdc, bmp, 0, hh, buf, ctypes.byref(bi), 0)
    ctl.g32.DeleteObject(bmp); ctl.g32.DeleteDC(mdc); ctl.u32.ReleaseDC(h, hdc)
    return Image.frombuffer("RGBA", (w, hh), buf, "raw", "BGRA", 0, 1).convert("RGB")
if __name__ == "__main__":
    raw(sys.argv[1]).save(sys.argv[2])
