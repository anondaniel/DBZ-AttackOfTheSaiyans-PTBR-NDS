"""Controle do melonDS.exe numa AREA DE TRABALHO OCULTA do Windows (CreateDesktop).

Nada aparece na area de trabalho do usuario, nada rouba o foco, nenhuma tecla global:
- entrada: PostMessage(WM_KEYDOWN/WM_KEYUP) direto na janela do melonDS;
- imagem: PrintWindow da janela na area oculta.

Uso:
  python ctl.py start <inst> <pasta_emu> <rom>
  python ctl.py shot  <inst> <saida.png>
  python ctl.py key   <inst> <tecla>[+<tecla>] [ms_segura] [ms_depois] [repet]
  python ctl.py seq   <inst> "a:100:400 down:80:300 ..."
  python ctl.py kill  <inst>
Teclas (mapa do melonDS.toml): a b x y start select up down left right l r f1..f8 sf1..sf8
"""
import ctypes, ctypes.wintypes as W, json, os, sys, time
from pathlib import Path

u32 = ctypes.WinDLL("user32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
g32 = ctypes.WinDLL("gdi32", use_last_error=True)
try:
    u32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except Exception:
    u32.SetProcessDPIAware()
AQUI = Path(__file__).parent
ESTADO = AQUI / "estado_inst.json"

GENERIC_ALL = 0x10000000
WM_KEYDOWN, WM_KEYUP = 0x100, 0x101
VK = {"a": 0x41, "b": 0x42, "x": 0x58, "y": 0x59, "start": 0x0D, "select": 0x20,
      "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27, "l": 0x51, "r": 0x57,
      "shift": 0x10, "ff": 0x09}
for i in range(1, 9):
    VK[f"f{i}"] = 0x6F + i
EXT = {0x26, 0x28, 0x25, 0x27}


def estado():
    return json.loads(ESTADO.read_text()) if ESTADO.exists() else {}


def desk_name(inst):
    return f"ClaudeDBZ_{inst}"


class STARTUPINFO(ctypes.Structure):
    _fields_ = [("cb", W.DWORD), ("lpReserved", W.LPWSTR), ("lpDesktop", W.LPWSTR),
                ("lpTitle", W.LPWSTR), ("dwX", W.DWORD), ("dwY", W.DWORD),
                ("dwXSize", W.DWORD), ("dwYSize", W.DWORD), ("dwXCountChars", W.DWORD),
                ("dwYCountChars", W.DWORD), ("dwFillAttribute", W.DWORD), ("dwFlags", W.DWORD),
                ("wShowWindow", W.WORD), ("cbReserved2", W.WORD), ("lpReserved2", ctypes.c_void_p),
                ("hStdInput", W.HANDLE), ("hStdOutput", W.HANDLE), ("hStdError", W.HANDLE)]


class PROCINFO(ctypes.Structure):
    _fields_ = [("hProcess", W.HANDLE), ("hThread", W.HANDLE), ("dwProcessId", W.DWORD),
                ("dwThreadId", W.DWORD)]


u32.CreateDesktopW.restype = W.HANDLE
u32.OpenDesktopW.restype = W.HANDLE


def start(inst, pasta, rom):
    h = u32.CreateDesktopW(desk_name(inst), None, None, 0, GENERIC_ALL, None)
    if not h:
        raise SystemExit(f"CreateDesktop falhou {ctypes.get_last_error()}")
    si = STARTUPINFO(); si.cb = ctypes.sizeof(si)
    si.lpDesktop = "WinSta0\\" + desk_name(inst)
    pi = PROCINFO()
    exe = str(Path(pasta).resolve() / "melonDS.exe")
    cmd = f'"{exe}" "{Path(rom).resolve()}"'
    ok = k32.CreateProcessW(exe, ctypes.create_unicode_buffer(cmd), None, None, False, 0,
                            None, str(Path(pasta).resolve()), ctypes.byref(si), ctypes.byref(pi))
    if not ok:
        raise SystemExit(f"CreateProcess falhou {ctypes.get_last_error()}")
    e = estado(); e[inst] = {"pid": pi.dwProcessId}; ESTADO.write_text(json.dumps(e))
    print("pid", pi.dwProcessId, flush=True)
    # mantem a area oculta viva enquanto o emulador roda
    k32.WaitForSingleObject(W.HANDLE(pi.hProcess), 0xFFFFFFFF)
    code = W.DWORD(); k32.GetExitCodeProcess(W.HANDLE(pi.hProcess), ctypes.byref(code))
    print("saiu", hex(code.value), flush=True)


def janela(inst):
    pid = estado()[inst]["pid"]
    hd = u32.OpenDesktopW(desk_name(inst), 0, False, GENERIC_ALL)
    if not hd:
        raise SystemExit("OpenDesktop falhou")
    u32.SetThreadDesktop(W.HANDLE(hd))
    achadas = []
    PROC = ctypes.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)

    def cb(hwnd, lp):
        p = W.DWORD(); u32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
        if p.value == pid and u32.IsWindowVisible(hwnd):
            n = ctypes.create_unicode_buffer(256); u32.GetWindowTextW(hwnd, n, 256)
            r = W.RECT(); u32.GetWindowRect(hwnd, ctypes.byref(r))
            achadas.append((hwnd, n.value, r.right - r.left, r.bottom - r.top))
        return True
    u32.EnumDesktopWindows(W.HANDLE(hd), PROC(cb), 0)
    achadas.sort(key=lambda t: -(t[2] * t[3]))
    return achadas


def principal(inst):
    js = janela(inst)
    for h, n, w, hh in js:
        if "melonDS" in n:
            return h, n, js
    return (js[0][0], js[0][1], js) if js else (None, None, js)


def lparam(vk, up):
    sc = u32.MapVirtualKeyW(vk, 0)
    lp = 1 | (sc << 16)
    if vk in EXT:
        lp |= 1 << 24
    if up:
        lp |= (1 << 30) | (1 << 31)
    return lp


def key(inst, teclas, segura=100, depois=300, repet=1):
    h, _, _ = principal(inst)
    vks = [VK[t] for t in teclas.split("+")]
    for _ in range(repet):
        for v in vks:
            u32.PostMessageW(h, WM_KEYDOWN, v, lparam(v, False))
        time.sleep(segura / 1000)
        for v in reversed(vks):
            u32.PostMessageW(h, WM_KEYUP, v, lparam(v, True))
        time.sleep(depois / 1000)


def shot(inst, saida):
    from PIL import Image
    h, n, js = principal(inst)
    r = W.RECT(); u32.GetClientRect(h, ctypes.byref(r))
    w, hh = r.right, r.bottom
    hdc = u32.GetDC(h)
    mdc = g32.CreateCompatibleDC(hdc)
    bmp = g32.CreateCompatibleBitmap(hdc, w, hh)
    g32.SelectObject(mdc, bmp)
    ok = u32.PrintWindow(h, mdc, 1 | 2)  # PW_CLIENTONLY | PW_RENDERFULLCONTENT
    class BIH(ctypes.Structure):
        _fields_ = [("biSize", W.DWORD), ("biWidth", W.LONG), ("biHeight", W.LONG),
                    ("biPlanes", W.WORD), ("biBitCount", W.WORD), ("biCompression", W.DWORD),
                    ("biSizeImage", W.DWORD), ("a", W.LONG), ("b", W.LONG), ("c", W.DWORD), ("d", W.DWORD)]
    bi = BIH(); bi.biSize = ctypes.sizeof(BIH); bi.biWidth = w; bi.biHeight = -hh
    bi.biPlanes = 1; bi.biBitCount = 32
    buf = ctypes.create_string_buffer(w * hh * 4)
    g32.GetDIBits(mdc, bmp, 0, hh, buf, ctypes.byref(bi), 0)
    g32.DeleteObject(bmp); g32.DeleteDC(mdc); u32.ReleaseDC(h, hdc)
    img = Image.frombuffer("RGBA", (w, hh), buf, "raw", "BGRA", 0, 1).convert("RGB")
    if hh > 576 and w == 384:
        img = img.crop((0, hh - 576, 384, hh))
    img.save(saida)
    print("ok" if ok else "PrintWindow=0", w, hh, n)


def seq(inst, s):
    for passo in s.split():
        p = passo.split(":")
        if p[0] == "s":
            shot(inst, str(AQUI / "capturas" / (p[1] + ".png"))); continue
        if p[0] in ("d", "u"):
            h, _, _ = principal(inst); v = VK[p[1]]
            u32.PostMessageW(h, WM_KEYDOWN if p[0] == "d" else WM_KEYUP, v, lparam(v, p[0] == "u")); continue
        if p[0] == "t":  # t:x:y em coords da captura 384x576 (cima+baixo)
            h, _, _ = principal(inst)
            r = W.RECT(); u32.GetClientRect(h, ctypes.byref(r))
            x = int(p[1]); y = int(p[2]) + (r.bottom - 576)
            lp = (y << 16) | x
            u32.PostMessageW(h, 0x200, 0, lp); time.sleep(0.05)
            u32.PostMessageW(h, 0x201, 1, lp); time.sleep(0.15)
            u32.PostMessageW(h, 0x202, 0, lp); time.sleep(0.5); continue
        if p[0] == "w":
            time.sleep(int(p[1]) / 1000); continue
        key(inst, p[0], int(p[1]) if len(p) > 1 else 100, int(p[2]) if len(p) > 2 else 300,
            int(p[3]) if len(p) > 3 else 1)


def kill(inst):
    pid = estado()[inst]["pid"]
    os.system(f"taskkill /PID {pid} /F >nul 2>&1")
    print("encerrado", pid)


if __name__ == "__main__":
    c, inst = sys.argv[1], sys.argv[2]
    a = sys.argv[3:]
    if c == "start":
        start(inst, a[0], a[1])
    elif c == "shot":
        shot(inst, a[0])
    elif c == "key":
        key(inst, a[0], *(int(x) for x in a[1:]))
    elif c == "seq":
        seq(inst, a[0])
    elif c == "go":
        seq(inst, a[0]); shot(inst, a[1])
    elif c == "list":
        print(janela(inst))
    elif c == "kill":
        kill(inst)
