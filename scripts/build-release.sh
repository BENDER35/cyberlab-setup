#!/usr/bin/env bash
# Genera dist/cyberlab-setup-vX.Y.Z.zip con el codigo fuente del proyecto.
# Uso: ./scripts/build-release.sh 1.0.0
set -euo pipefail

VERSION="${1:-1.0.0}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"
NAME="cyberlab-setup-v${VERSION}"
STAGE="$DIST/$NAME"
ZIP="$DIST/${NAME}.zip"

rm -rf "$STAGE" "$ZIP" "$DIST/SHA256SUMS"
mkdir -p "$STAGE"

copy_file() {
    local rel="$1"
    case "$rel" in
        dist/*|.git/*|*.log|*.zip|*.sha256|*.token|*.pem|*.key|.env*) return 0 ;;
    esac
    mkdir -p "$STAGE/$(dirname "$rel")"
    cp "$ROOT/$rel" "$STAGE/$rel"
}

if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    while IFS= read -r -d '' rel; do copy_file "$rel"; done < <(git -C "$ROOT" ls-files -z)
else
    while IFS= read -r rel; do copy_file "$rel"; done < <(
        cd "$ROOT" && find . -type f \
          -not -path './.git/*' -not -path './dist/*' -not -name '*.log' \
          | sed 's#^\./##'
    )
fi

# El ZIP debe incluir la carpeta raiz para evitar mezclar archivos al descomprimir.
(cd "$DIST" && zip -q -r "$NAME.zip" "$NAME")
(cd "$DIST" && sha256sum "$NAME.zip" > SHA256SUMS)

echo "ZIP: $ZIP"
echo "SHA256: $(cut -d' ' -f1 "$DIST/SHA256SUMS")"
echo "Tamano: $(du -h "$ZIP" | cut -f1)"
