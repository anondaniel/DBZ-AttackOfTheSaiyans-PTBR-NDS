import inspect
import libretro

for nome in ("JoypadState", "PointerState", "Pointer"):
    obj = getattr(libretro, nome)
    print(f"== {nome} ==")
    try:
        print("  assinatura:", inspect.signature(obj))
    except (TypeError, ValueError):
        pass
    campos = getattr(obj, "__dataclass_fields__", None) or getattr(obj, "__annotations__", {})
    print("  campos:", list(campos))
    print()
