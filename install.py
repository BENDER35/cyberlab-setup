#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Instalador multiplataforma de un laboratorio LOCAL de ciberseguridad.

Soporta Linux, macOS y Windows. Solo instala herramientas de uso general en
equipos propios o con autorizacion explicita. Ejecuta con --help para ver opciones.

Ejemplos:
    python3 install.py --profile core --yes
    python3 install.py --profile extra --yes --authorize-lab
    python3 install.py --profile lab --yes --authorize-lab --only docker,virtualbox
    python3 install.py --check
    python3 install.py --dry-run --profile core
    python3 install.py --list
"""

from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog import AUTH_NOTICE, PROFILES, TOOLS, by_id, selected_tools, summary  # noqa: E402

APP = "CyberLab Setup"
VERSION = "1.0.0"
EXIT_OK = 0
EXIT_FAIL = 1
EXIT_USAGE = 2


class Logger:
    """Escribe en stdout y, opcionalmente, en un archivo de log."""

    def __init__(self, log_path=None, verbose=False):
        self.verbose = verbose
        self._fh = None
        if log_path:
            path = Path(log_path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            self._fh = path.open("a", encoding="utf-8")
            self.log_file = str(path.resolve())
        else:
            self.log_file = None

    def line(self, msg="", stream="out", force=True):
        if not force and not self.verbose:
            return
        target = sys.stdout if stream == "out" else sys.stderr
        try:
            print(msg, file=target, flush=True)
        except BrokenPipeError:
            # Ej. '--list | head': se corta el pipe, no es un error real.
            pass
        if self._fh:
            self._fh.write(str(msg) + "\n")
            self._fh.flush()

    def command(self, cmd, env=None):
        suffix = ""
        if env:
            suffix = "  [env: " + ", ".join("%s=%s" % kv for kv in env.items()) + "]"
        self.line("    $ " + " ".join(_quote(c) for c in cmd) + suffix, force=False)

    def close(self):
        if self._fh:
            self._fh.close()


def _quote(value):
    value = str(value)
    return value if all(c.isalnum() or c in "-_./:=@~+" for c in value) else '"%s"' % value


def os_name():
    system = platform.system()
    return system if system in ("Linux", "Darwin", "Windows") else "Linux"


def is_root_or_admin():
    if os_name() == "Windows":
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    return hasattr(os, "geteuid") and os.geteuid() == 0


def package_managers(system, override=None):
    """Gestores disponibles en el equipo, ordenados por preferencia."""
    if override:
        wanted = [p.strip() for p in override.split(",") if p.strip()]
        return {p: (shutil.which(p) is not None or p in ("pip",)) for p in wanted}

    found = {}
    if system == "Linux":
        for pm in ("apt-get", "dnf", "pacman", "zypper"):
            if shutil.which(pm):
                found["apt" if pm == "apt-get" else pm] = True
        if shutil.which("brew"):
            found["brew"] = True
    elif system == "Darwin":
        if shutil.which("brew"):
            found["brew"] = True
    else:
        for pm in ("winget", "choco", "scoop"):
            if shutil.which(pm):
                found[pm] = True

    if shutil.which("go"):
        found["go"] = True
    if shutil.which("snap"):
        found["snap"] = True
    # pip se invoca siempre como 'python -m pip', no depende de un ejecutable.
    found["pip"] = True
    return found


def run(cmd, env=None, timeout=900):
    """Ejuta un comando sin shell. Devuelve (ok, salida, codigo)."""
    full_env = os.environ.copy()
    if env:
        full_env.update({str(k): str(v) for k, v in env.items()})
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=full_env,
            timeout=timeout,
            check=False,
        )
        return proc.returncode == 0, (proc.stdout or "").strip(), proc.returncode
    except FileNotFoundError:
        return False, "comando no encontrado: %s" % cmd[0], 127
    except subprocess.TimeoutExpired:
        return False, "timeout tras %ss: %s" % (timeout, cmd[0]), 124
    except Exception as exc:  # pragma: no cover - defensivo
        return False, "error inesperado: %s" % exc, 125


def first_line(text, limit=160):
    for line in (text or "").splitlines():
        line = line.strip()
        if line:
            return line[:limit]
    return ""


class Installer:
    def __init__(self, args, log):
        self.args = args
        self.log = log
        self.system = os_name()
        self.pm = package_managers(self.system, args.pm)
        self.privileged_ok = is_root_or_admin()
        self.apt_updated = False
        self.results = []

    # ---------------------------------------------------------------- utils
    def _with_sudo(self, cmd):
        if self.system == "Windows" or self.privileged_ok or self.args.no_sudo:
            return cmd
        if shutil.which("sudo"):
            return ["sudo"] + cmd
        return cmd

    def install_cmd(self, step):
        cmd = list(step["cmd"])
        if step["privileged"]:
            if self.system == "Windows" and not self.privileged_ok:
                return None, "requiere permisos de Administrador"
            if self.args.no_sudo and not self.privileged_ok:
                return None, "requiere sudo (usa --no-sudo para omitirlo)"
            cmd = self._with_sudo(cmd)
        return cmd, None

    def eligible_steps(self, tool):
        steps = tool["install"].get(self.system, [])
        eligible = []
        for s in steps:
            pm = s["pm"]
            if pm is None or pm in self.pm:
                eligible.append(s)
        return eligible

    def _maybe_apt_update(self, step):
        if step["pm"] != "apt" or self.apt_updated:
            return True
        if self.args.dry_run:
            self.log.line("    $ sudo apt-get update", force=False)
            self.apt_updated = True
            return True
        cmd, reason = self.install_cmd({"cmd": ["apt-get", "update"], "privileged": True})
        if cmd is None:
            self.log.line("    ! No se pudo actualizar el indice de apt: %s" % reason)
            return False
        self.log.command(cmd)
        ok, out, _ = run(cmd, timeout=600)
        self.log.line("    " + first_line(out), force=False)
        self.apt_updated = ok
        if not ok:
            self.log.line("    ! apt-get update fallo; se continuara con el indice actual.")
        return True

    # ------------------------------------------------------------ verificacion
    def verify(self, tool):
        candidates = tool["check"].get(self.system, [])
        if not candidates:
            return "manual", "verificacion manual (GUI)"
        for cmd in candidates:
            if shutil.which(cmd[0]) is None and self.system != "Windows":
                continue
            ok, out, _ = run(cmd, timeout=30)
            if ok:
                return "ok", first_line(out)
        return "missing", "no encontrado en PATH"

    # -------------------------------------------------------------- instalacion
    def install_tool(self, tool):
        entry = {
            "id": tool["id"],
            "name": tool["name"],
            "profile": tool["profile"],
            "status": "pending",
            "detail": "",
        }
        self.results.append(entry)

        state, detail = self.verify(tool)
        if state == "ok":
            entry.update(status="ok", detail="ya instalado: " + detail)
            self.log.line("  [OK]   %-24s %s" % (tool["name"], detail))
            return True

        steps = self.eligible_steps(tool)
        if not steps:
            url = tool.get("manual", {}).get(self.system)
            detail = "sin gestor de paquetes compatible"
            if url:
                detail += " | instalar manualmente: " + url
            if tool.get("notes"):
                detail += " | " + tool["notes"]
            entry.update(status="manual", detail=detail)
            self.log.line("  [MAN]  %-24s %s" % (tool["name"], detail))
            return True  # no es un fallo del script

        installed = False
        errors = []
        for step in steps:
            if step.get("note"):
                self.log.line("    i  " + step["note"])
            cmd, reason = self.install_cmd(step)
            if cmd is None:
                errors.append(reason)
                continue
            self._maybe_apt_update(step)
            self.log.command(cmd, step.get("env"))
            if self.args.dry_run:
                continue
            ok, out, code = run(cmd, step.get("env"), timeout=1800)
            self.log.line("    " + first_line(out), force=False)
            if ok:
                installed = True
                break
            errors.append("exit %s: %s" % (code, first_line(out)))

        if self.args.dry_run:
            entry.update(status="dry-run", detail="comandos mostrados, no ejecutados")
            self.log.line("  [DRY]  %-24s comandos mostrados" % tool["name"])
            return True

        state, detail = self.verify(tool)
        if state == "ok":
            entry.update(status="ok", detail="instalado: " + detail)
            self.log.line("  [OK]   %-24s %s" % (tool["name"], detail))
            return True

        if installed or state == "manual":
            url = tool.get("manual", {}).get(self.system)
            msg = "instalado pero no detectable en PATH"
            if url:
                msg += " | " + url
            entry.update(status="manual", detail=msg)
            self.log.line("  [MAN]  %-24s %s" % (tool["name"], msg))
            return True

        msg = "; ".join(errors) if errors else "sin pasos ejecutables"
        entry.update(status="failed", detail=msg)
        self.log.line("  [FAIL] %-24s %s" % (tool["name"], msg), stream="err")
        return False

    def post_install(self, installed_ids):
        """Ajustes de grupo en Linux para captura/contenedores sin root."""
        if self.system != "Linux" or self.privileged_ok or self.args.dry_run:
            return
        mapping = {"wireshark": "wireshark", "docker": "docker"}
        for tool_id, group in mapping.items():
            if tool_id not in installed_ids:
                continue
            if not run(["getent", "group", group])[0]:
                continue
            cmd = self._with_sudo(["usermod", "-aG", group, os.environ.get("USER", "")])
            self.log.line("  [POST] Anadiendo el usuario al grupo %s (reinicie sesion)." % group)
            self.log.command(cmd)
            ok, out, _ = run(cmd, timeout=60)
            if not ok:
                self.log.line("    ! " + first_line(out))

    # ------------------------------------------------------------------ run
    def run_checks(self, tools):
        self.log.line("Modo verificacion (--check):")
        missing_core = []
        for tool in tools:
            state, detail = self.verify(tool)
            self.results.append({
                "id": tool["id"], "name": tool["name"], "profile": tool["profile"],
                "status": state, "detail": detail,
            })
            self.log.line("  [%-7s] %-24s %s" % (state.upper(), tool["name"], detail))
            if state == "missing" and tool["profile"] == "core":
                missing_core.append(tool["name"])
        if missing_core:
            self.log.line("\nFaltan herramientas CORE: " + ", ".join(missing_core))
            return EXIT_FAIL
        return EXIT_OK

    def install_all(self, tools):
        self.log.line("Perfil: %s | OS: %s | Gestores: %s" % (
            self.args.profile, self.system, ", ".join(sorted(self.pm)) or "ninguno"))
        ok_count = 0
        for tool in tools:
            if self.install_tool(tool):
                ok_count += 1
        self.post_install({t["id"] for t in tools})
        failed = [r for r in self.results if r["status"] == "failed"]
        self.log.line("")
        self.log.line("Resumen: %d/%d herramientas satisfactorias (ok o manuales), %d fallos." % (
            ok_count, len(tools), len(failed)))
        return EXIT_FAIL if failed else EXIT_OK

    def write_report(self):
        if not self.args.report:
            return
        path = Path(self.args.report).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "app": APP,
            "version": VERSION,
            "date": dt.datetime.now().isoformat(timespec="seconds"),
            "os": self.system,
            "profile": self.args.profile,
            "package_managers": sorted(self.pm),
            "results": self.results,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self.log.line("Informe JSON: %s" % path.resolve())


def print_catalog(log):
    log.line("Catalogo de herramientas (perfil: core < extra < lab)\n")
    log.line("%-22s %-8s %-9s %-14s %s" % ("ID", "PERFIL", "AUTORIZ.", "CATEGORIA", "NOMBRE"))
    log.line("-" * 78)
    for tool in TOOLS:
        log.line("%-22s %-8s %-9s %-14s %s" % (
            tool["id"], tool["profile"],
            "si" if tool.get("authorization") else "no",
            tool["category"], tool["name"]))
    counts = summary()
    log.line("\nTotales: core=%d, extra=%d, lab=%d" % (counts["core"], counts["extra"], counts["lab"]))


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="install.py",
        description="Instala herramientas basicas de ciberseguridad para un laboratorio LOCAL autorizado.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=AUTH_NOTICE,
    )
    p.add_argument("--profile", choices=PROFILES, default="core", help="core (default), extra o lab (acumulativos).")
    p.add_argument("--only", help="Lista separada por comas de IDs a instalar/verificar.")
    p.add_argument("--skip", help="Lista separada por comas de IDs a excluir.")
    p.add_argument("--check", action="store_true", help="Solo verifica que este instalado; no instala nada.")
    p.add_argument("--dry-run", action="store_true", help="Muestra los comandos sin ejecutarlos.")
    p.add_argument("--yes", "-y", action="store_true", help="No pedir confirmacion interactiva.")
    p.add_argument("--authorize-lab", action="store_true",
                   help="Declara que usas las herramientas solo en equipos propios/autorizados.")
    p.add_argument("--no-sudo", action="store_true", help="Omitir pasos que requieren sudo (Linux/macOS).")
    p.add_argument("--pm", help="Forzar gestores de paquetes (ej. apt,brew o winget,choco).")
    p.add_argument("--log", default=None, help="Ruta del archivo de log.")
    p.add_argument("--report", default=None, help="Ruta de un informe JSON con el resultado.")
    p.add_argument("--list", action="store_true", help="Listar el catalogo y salir.")
    p.add_argument("--verbose", "-v", action="store_true", help="Mostrar comandos y salida detallada.")
    p.add_argument("--version", action="version", version="%s %s" % (APP, VERSION))
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    log = Logger(args.log or "cyberlab-install-%s.log" % stamp, args.verbose)
    log.line("%s v%s  |  %s" % (APP, VERSION, dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    log.line("Aviso: " + AUTH_NOTICE)

    if args.list:
        print_catalog(log)
        log.close()
        return EXIT_OK

    only = {x.strip() for x in (args.only or "").split(",") if x.strip()}
    skip = {x.strip() for x in (args.skip or "").split(",") if x.strip()}
    unknown = (only | skip) - {t["id"] for t in TOOLS}
    if unknown:
        log.line("IDs desconocidos: " + ", ".join(sorted(unknown)), stream="err")
        log.close()
        return EXIT_USAGE

    if args.profile == "lab" and not args.authorize-lab:
        log.line("El perfil 'lab' requiere --authorize-lab. Lee el aviso de uso responsable.", stream="err")
        log.close()
        return EXIT_USAGE

    tools = selected_tools(args.profile, only, skip)
    restricted = [t for t in tools if t.get("authorization")]
    if restricted and not args.authorize-lab:
        log.line("Se omiten herramientas restringidas (requieren --authorize-lab): " +
                 ", ".join(t["name"] for t in restricted))
        tools = [t for t in tools if not t.get("authorization")]

    if not tools:
        log.line("No hay herramientas que instalar con esos filtros.", stream="err")
        log.close()
        return EXIT_USAGE

    if not args.check and not args.dry_run and not args.yes:
        if not sys.stdin.isatty():
            log.line("Sin TTY: use --yes para confirmar la instalacion.", stream="err")
            log.close()
            return EXIT_USAGE
        log.line("Se instalaran %d herramientas. Continuar? [y/N] " % len(tools), force=True)
        if sys.stdin.readline().strip().lower() not in ("y", "yes", "s", "si"):
            log.line("Cancelado por el usuario.")
            log.close()
            return EXIT_OK

    installer = Installer(args, log)
    if args.check:
        code = installer.run_checks(tools)
    else:
        code = installer.install_all(tools)
    installer.write_report()
    if log.log_file:
        log.line("Log: %s" % log.log_file)
    log.close()
    return code


if __name__ == "__main__":
    sys.exit(main())
