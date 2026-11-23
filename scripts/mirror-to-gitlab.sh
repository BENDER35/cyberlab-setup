#!/usr/bin/env bash
# Empuja todas las ramas y etiquetas de este checkout a GitLab (espejo).
# Se usa desde GitHub Actions y tambien puede ejecutarse manualmente.
# Variables: GITLAB_TOKEN (obligatoria), GITLAB_NAMESPACE, GITLAB_PROJECT, GITLAB_HOST.
set -euo pipefail

if [[ -z "${GITLAB_TOKEN:-}" ]]; then
    echo "Error: define GITLAB_TOKEN con un PAT de GitLab." >&2
    exit 2
fi

NS="${GITLAB_NAMESPACE:-BENDER_5000}"
PROJECT="${GITLAB_PROJECT:-cyberlab-setup}"
HOST="${GITLAB_HOST:-gitlab.com}"
REMOTE="gitlab-mirror"
URL="https://oauth2:${GITLAB_TOKEN}@${HOST}/${NS}/${PROJECT}.git"

# Evita que el token aparezca en trazas.
trap 'URL=""' EXIT

if git remote get-url "$REMOTE" >/dev/null 2>&1; then
    git remote set-url "$REMOTE" "$URL"
else
    git remote add "$REMOTE" "$URL"
fi

echo "Mirror -> ${HOST}/${NS}/${PROJECT} (ramas y etiquetas)"
# Asegura que tenemos todo el historico y las refs de GitHub.
git fetch --prune origin '+refs/heads/*:refs/remotes/origin/*' >/dev/null 2>&1 || true
git push --force --prune "$REMOTE" \
    'refs/heads/*:refs/heads/*' \
    'refs/tags/*:refs/tags/*'

echo "Mirror completado."
