#!/bin/sh
# Instala as ferramentas do projeto DS DENTRO do sandbox.
# Fontes oficiais apenas: buildbot do libretro e PyPI.
set -e
mkdir -p /ds/tools
cd /ds/tools

echo "== nucleo melonDS DS (buildbot.libretro.com) =="
curl -sS -fL -o melondsds_libretro.so.zip \
  https://buildbot.libretro.com/nightly/linux/x86_64/latest/melondsds_libretro.so.zip
ls -la melondsds_libretro.so.zip
sha256sum melondsds_libretro.so.zip
python3 - <<'EOF'
import zipfile
z = zipfile.ZipFile("melondsds_libretro.so.zip")
for i in z.infolist():
    print(f"  conteudo: {i.filename} ({i.file_size:,} bytes)")
z.extractall(".")
EOF
ls -la melondsds_libretro.so
sha256sum melondsds_libretro.so

echo
echo "== dependencias do nucleo =="
ldd melondsds_libretro.so | grep -i "not found" || echo "  todas as bibliotecas encontradas"

echo
echo "== libretro.py (PyPI) =="
pip install --quiet --disable-pip-version-check libretro.py 2>&1 | tail -3
pip show libretro.py 2>/dev/null | grep -E "^(Name|Version|Home-page|Author)"
