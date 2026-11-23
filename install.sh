#!/usr/bin/env sh
# Instalador CyberLab para Linux y macOS.
# Uso: ./install.sh --profile core --yes
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON=""

for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Error: se necesita Python 3. Instalalo con tu gestor de paquetes." >&2
    echo "  Linux : sudo apt install python3   (o dnf/pacman/zypper)" >&2
    echo "  macOS : brew install python@3.12  (o instalar desde python.org)" >&2
    exit 2
fi

if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
    echo "Error: se necesita Python >= 3.8 (detectado: $("$PYTHON" --version 2>&1))." >&2
    exit 2
fi

exec "$PYTHON" "$SCRIPT_DIR/install.py" "$@"
