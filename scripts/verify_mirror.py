#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compara las refs (ramas y etiquetas) de GitHub y GitLab.

Salida: 0 si coinciden todos los SHA, 1 si hay diferencias, 2 si no se puede consultar.
Uso:
    python3 scripts/verify_mirror.py
    python3 scripts/verify_mirror.py --json
    python3 scripts/verify_mirror.py --fix      # reenvia el espejo y vuelve a verificar
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

GH_NS = os.environ.get("GH_NAMESPACE", "BENDER35")
GH_REPO = os.environ.get("GH_PROJECT", "cyberlab-setup")
GL_NS = os.environ.get("GITLAB_NAMESPACE", "BENDER_5000")
GL_REPO = os.environ.get("GITLAB_PROJECT", "cyberlab-setup")
GH_HOST = os.environ.get("GITHUB_HOST", "github.com")
GL_HOST = os.environ.get("GITLAB_HOST", "gitlab.com")


def run(cmd, timeout=120):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return p.returncode == 0, p.stdout + p.stderr
    except Exception as exc:
        return False, str(exc)


def gh_token():
    if os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"):
        return None  # git/credential helper ya lo usa
    if shutil.which("gh"):
        ok, out = run(["gh", "auth", "token", "--hostname", GH_HOST], timeout=30)
        if ok and out.strip():
            return out.strip()
    return None


def github_url():
    token = gh_token()
    if token:
        return "https://x-access-token:%s@%s/%s/%s.git" % (token, GH_HOST, GH_NS, GH_REPO)
    return "https://%s/%s/%s.git" % (GH_HOST, GH_NS, GH_REPO)


def gitlab_url():
    token = os.environ.get("GITLAB_TOKEN")
    if token:
        return "https://oauth2:%s@%s/%s/%s.git" % (token, GL_HOST, GL_NS, GL_REPO)
    return "git@%s:%s/%s.git" % (GL_HOST, GL_NS, GL_REPO)


def remote_refs(url):
    ok, out = run(["git", "ls-remote", "--heads", "--tags", url])
    if not ok:
        return None, out.strip()
    refs = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        sha, ref = parts
        if ref.endswith("^{}"):   # etiqueta anotada: ignorar el objeto desreferenciado
            continue
        refs[ref] = sha
    return refs, ""


def compare(gh_refs, gl_refs):
    only_gh = sorted(set(gh_refs) - set(gl_refs))
    only_gl = sorted(set(gl_refs) - set(gh_refs))
    mismatch = sorted(k for k in set(gh_refs) & set(gl_refs) if gh_refs[k] != gl_refs[k])
    return {"only_github": only_gh, "only_gitlab": only_gl, "sha_mismatch": mismatch}


def main():
    p = argparse.ArgumentParser(description="Verifica que el espejo GitHub -> GitLab este sincronizado.")
    p.add_argument("--json", action="store_true", help="Salida en JSON.")
    p.add_argument("--fix", action="store_true", help="Reenviar el espejo antes de verificar.")
    p.add_argument("--verbose", "-v", action="store_true", help="Mostrar todas las refs coincideintes.")
    args = p.parse_args()

    root = Path(__file__).resolve().parent.parent
    if args.fix:
        script = root / "scripts" / "mirror-to-gitlab.sh"
        if not script.exists():
            print("No se encontró scripts/mirror-to-gitlab.sh", file=sys.stderr)
            return 2
        ok, out = run(["bash", str(script)], timeout=600)
        print(out.strip())
        if not ok:
            return 2

    gh_refs, gh_err = remote_refs(github_url())
    gl_refs, gl_err = remote_refs(gitlab_url())
    if gh_refs is None or gl_refs is None:
        msg = {"error": "No se pudieron leer las refs remotas", "github": gh_err, "gitlab": gl_err}
        print(json.dumps(msg, indent=2) if args.json else msg, file=sys.stderr)
        return 2

    diff = compare(gh_refs, gl_refs)
    equal = not any(diff.values())
    payload = {
        "github": "%s/%s" % (GH_NS, GH_REPO),
        "gitlab": "%s/%s" % (GL_NS, GL_REPO),
        "github_refs": len(gh_refs),
        "gitlab_refs": len(gl_refs),
        "in_sync": equal,
        "differences": diff,
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("GitHub : %s/%s (%d refs)" % (GH_NS, GH_REPO, len(gh_refs)))
        print("GitLab : %s/%s (%d refs)" % (GL_NS, GL_REPO, len(gl_refs)))
        for key, label in (("only_github", "Solo en GitHub"),
                           ("only_gitlab", "Solo en GitLab"),
                           ("sha_mismatch", "SHA diferente")):
            if diff[key]:
                print("%s:" % label)
                for ref in diff[key]:
                    print("  - %s  GH=%s GL=%s" % (
                        ref, gh_refs.get(ref, "-"), gl_refs.get(ref, "-")))
        if args.verbose and equal:
            for ref in sorted(gh_refs):
                print("  OK %s %s" % (gh_refs[ref], ref))
        print("RESULTADO: " + ("ESPEJO SINCRONIZADO" if equal else "ESPEJO DESINCRONIZADO"))
    return 0 if equal else 1


if __name__ == "__main__":
    sys.exit(main())
