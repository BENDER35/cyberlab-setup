#!/usr/bin/env bash
# Crea (si no existen) el repositorio en GitHub y el proyecto espejo en GitLab.
# Requiere: gh autenticado y GITLAB_TOKEN con permiso 'api'.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GH_NS="${GH_NAMESPACE:-BENDER35}"
GL_NS="${GITLAB_NAMESPACE:-BENDER_5000}"
REPO="${REPO_NAME:-cyberlab-setup}"
VISIBILITY="${REPO_VISIBILITY:-public}"   # public | private | internal
DESC="Cross-platform installer for a basic, authorized, local Cybersecurity lab / Instalador multiplataforma de ciberseguridad basica para laboratorio local autorizado"

echo "== GitHub: $GH_NS/$REPO =="
if ! command -v gh >/dev/null 2>&1; then
    echo "Error: GitHub CLI (gh) no disponible." >&2
    exit 2
fi
if gh repo view "$GH_NS/$REPO" >/dev/null 2>&1; then
    echo "Ya existe: https://github.com/$GH_NS/$REPO"
else
    gh repo create "$GH_NS/$REPO" "--$VISIBILITY" --description "$DESC"
    echo "Creado: https://github.com/$GH_NS/$REPO"
fi

echo
echo "== GitLab: $GL_NS/$REPO =="
if [[ -z "${GITLAB_TOKEN:-}" ]]; then
    echo "Error: define GITLAB_TOKEN (PAT de GitLab con scope 'api')." >&2
    exit 2
fi
ENC="${GL_NS}%2F${REPO}"
if curl -fsS -o /dev/null -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
    "https://gitlab.com/api/v4/projects/${ENC}"; then
    echo "Ya existe: https://gitlab.com/$GL_NS/$REPO"
else
    PAYLOAD=$(jq -n --arg name "$REPO" --arg path "$REPO" --arg ns "$GL_NS" \
                   --arg desc "$DESC" --arg vis "$VISIBILITY" \
                   '{name:$name, path:$path, namespace:$ns, description:$desc, visibility:$vis,
                     initialize_with_readme:false, shared_runners_enabled:true}')
    curl -fsS -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" -H 'Content-Type: application/json' \
         -X POST -d "$PAYLOAD" "https://gitlab.com/api/v4/projects" \
         | jq -r '"Creado: \(.web_url) (id=\(.id))"'
fi

echo
echo "== Conectar el checkout local =="
git -C "$ROOT" remote remove origin 2>/dev/null || true
git -C "$ROOT" remote add origin "https://github.com/${GH_NS}/${REPO}.git"
if git -C "$ROOT" rev-parse --verify HEAD >/dev/null 2>&1; then
    git -C "$ROOT" branch -M main
    git -C "$ROOT" push -u origin main
fi
echo "Listo. Continua con scripts/setup-mirror.sh"
