#!/usr/bin/env bash
# Crea la release vX.Y.Z con el ZIP en GitHub y en GitLab.
# Requiere: gh autenticado, GITLAB_TOKEN con scope 'api', jq, curl, zip.
# Uso: ./scripts/release.sh 1.0.0
set -euo pipefail

VERSION="${1:-1.0.0}"
TAG="v${VERSION}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"
ZIP="$DIST/cyberlab-setup-${TAG}.zip"
SUMS="$DIST/SHA256SUMS"

GH_REPO="${GH_NAMESPACE:-BENDER35}/${REPO_NAME:-cyberlab-setup}"
GL_NS="${GITLAB_NAMESPACE:-BENDER_5000}"
GL_PROJECT="${GITLAB_PROJECT:-cyberlab-setup}"
GL_HOST="${GITLAB_HOST:-gitlab.com}"
API="https://${GL_HOST}/api/v4"
GL_ENC="${GL_NS}%2F${GL_PROJECT}"

NOTES=$(mktemp)
trap 'rm -f "$NOTES"' EXIT
cat > "$NOTES" <<EOF
CyberLab Setup ${TAG}

Instalador multiplataforma (Linux, macOS, Windows) de herramientas basicas de
ciberseguridad para laboratorio LOCAL y autorizado.

- Perfiles: core / extra / lab (acumulativos).
- Verificacion: python3 install.py --check
- Guia: docs/GUIA_DIDACTICA.es.md y docs/LEARNING_GUIDE.en.md

Uso responsable: solo en equipos propios o con autorizacion por escrito.
EOF

echo "== Construyendo artefacto =="
bash "$ROOT/scripts/build-release.sh" "$VERSION"

echo
echo "== GitHub release: $GH_REPO $TAG =="
if git -C "$ROOT" rev-parse "$TAG" >/dev/null 2>&1; then
    echo "La etiqueta local $TAG ya existe."
else
    git -C "$ROOT" tag -a "$TAG" -m "Release $TAG"
fi
git -C "$ROOT" push origin "$TAG" || echo "Aviso: no se pudo empujar la etiqueta a GitHub (gh la creara si falta)."

if gh release view "$TAG" --repo "$GH_REPO" >/dev/null 2>&1; then
    echo "La release ya existe; actualizando assets."
    gh release upload "$TAG" "$ZIP" "$SUMS" --repo "$GH_REPO" --clobber
else
    gh release create "$TAG" "$ZIP" "$SUMS" --repo "$GH_REPO" \
        --title "CyberLab Setup $TAG" --notes-file "$NOTES"
fi
echo "GitHub: https://github.com/$GH_REPO/releases/tag/$TAG"

echo
echo "== GitLab release: $GL_NS/$GL_PROJECT $TAG =="
if [[ -z "${GITLAB_TOKEN:-}" ]]; then
    echo "Error: define GITLAB_TOKEN (scope 'api') para publicar en GitLab." >&2
    exit 2
fi
TOKEN="${GITLAB_TOKEN}"

# La release de GitLab exige que la etiqueta exista en el remoto.
git -C "$ROOT" push --force "https://oauth2:${TOKEN}@${GL_HOST}/${GL_NS}/${GL_PROJECT}.git" "$TAG" >/dev/null 2>&1 || true

PROJECT_ID=$(curl -fsS -H "PRIVATE-TOKEN: ${TOKEN}" "$API/projects/${GL_ENC}" | jq -r '.id')
if [[ -z "$PROJECT_ID" || "$PROJECT_ID" == "null" ]]; then
    echo "Error: no se encontro el proyecto en GitLab." >&2
    exit 2
fi

if curl -fsS -o /dev/null -H "PRIVATE-TOKEN: ${TOKEN}" "$API/projects/${PROJECT_ID}/releases/${TAG}"; then
    echo "La release ya existe en GitLab; asegurando assets."
else
    BODY=$(jq -n --arg tag "$TAG" --arg name "CyberLab Setup $TAG" --arg desc "$(cat "$NOTES")" \
             '{tag_name:$tag, name:$name, description:$desc}')
    curl -fsS -H "PRIVATE-TOKEN: ${TOKEN}" -H 'Content-Type: application/json' \
         -X POST -d "$BODY" "$API/projects/${PROJECT_ID}/releases" >/dev/null
fi

upload_asset() {
    local file="$1" label="$2"
    local response url
    response=$(curl -fsS -H "PRIVATE-TOKEN: ${TOKEN}" \
                   -F "file=@${file}" "$API/projects/${PROJECT_ID}/uploads")
    url=$(echo "$response" | jq -r '.url')
    if [[ -z "$url" || "$url" == "null" ]]; then
        echo "Error: no se pudo subir $label a GitLab." >&2
        return 1
    fi
    local full_url="https://${GL_HOST}/${GL_NS}/${GL_PROJECT}${url}"
    local link_body
    link_body=$(jq -n --arg name "$label" --arg url "$full_url" \
                  '{name:$name, url:$url, link_type:"package"}')
    curl -fsS -H "PRIVATE-TOKEN: ${TOKEN}" -H 'Content-Type: application/json' \
         -X POST -d "$link_body" "$API/projects/${PROJECT_ID}/releases/${TAG}/assets/links" >/dev/null
    echo "  asset: $label -> $full_url"
}

upload_asset "$ZIP" "cyberlab-setup-${TAG}.zip"
upload_asset "$SUMS" "SHA256SUMS"

echo "GitLab: https://${GL_HOST}/${GL_NS}/${GL_PROJECT}/-/releases/${TAG}"
echo
echo "Release publicada en ambas plataformas."
