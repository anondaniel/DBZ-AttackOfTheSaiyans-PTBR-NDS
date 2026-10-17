#!/bin/sh
# lista o pacote python-bps baixado e mostra setup.py e o aplicador, para
# ler antes de instalar
cd /tmp/pb || exit 1
tar tzf python-bps-5.tar.gz
mkdir -p x && tar xzf python-bps-5.tar.gz -C x
echo "=== setup.py"
cat x/python-bps-5/setup.py
echo "=== grep de coisas suspeitas (rede, subprocess, exec)"
grep -rnE "urllib|socket|requests|subprocess|os\.system|exec\(|eval\(|base64" x/python-bps-5 || echo "nada encontrado"
