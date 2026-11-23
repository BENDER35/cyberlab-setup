#!/usr/bin/env bash
# Configura los secretos/variables de GitHub necesarios para el espejo a GitLab.
# Uso: GITLAB_TOKEN=glpat-xxx ./scripts/setup-mirror.sh
set -euo pipefail

GH_REPO="${GH_NAMESPACE:-BENDER35}/${REPO_NAME:-cyberlab-setup}"
GL_NS="${GITLAB_NAMESPACE:-BENDER_5000}"
GL_PROJECT="${GITLAB_PROJECT:-cyberlab-setup}"

if [[ -z "${GITLAB_TOKEN:-}" ]]; then
    echo "Error: define GITLAB_TOKEN (PAT de GitLab con scopes 'api' y 'write_repository')." >&2
    exit 2
fi

USER_JSON=$(curl -fsS -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" https://gitlab.com/api/v4/user)
GL_USER=$(echo "$USER_JSON" | jq -r '.username')
echo "Token GitLab valido para: $GL_USER"

if [[ "$GL_USER" != "$GL_NS" ]]; then
    echo "Aviso: el token pertenece a '$GL_USER' pero el namespace es '$GL_NS'." >&2
    echo "       Ajusta GITLAB_NAMESPACE si es necesario." >&2
fi

gh secret set GITLAB_TOKEN --repo "$GH_REPO" --body "$GITLAB_TOKEN"
gh variable set GITLAB_NAMESPACE --repo "$GH_REPO" --body "$GL_NS"
gh variable set GITLAB_PROJECT --repo "$GH_REPO" --body "$GL_PROJECT"

echo "Configurado en https://github.com/$GH_REPO/settings/secrets/actions:"
echo "  GITLAB_TOKEN      (secret)"
echo "  GITLAB_NAMESPACE  = $GL_NS"
echo "  GITLAB_PROJECT    = $GL_PROJECT"
echo
echo "El workflow .github/workflows/mirror-to-gitlab.yml hara el espejo automatico."
