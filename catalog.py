#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catalogo de herramientas de ciberseguridad para un laboratorio LOCAL y autorizado.

Cada entrada describe como instalar y verificar una herramienta en Linux, macOS y
Windows. No se descarga ni se ejecuta nada automaticamente desde este archivo:
es solo el inventario que consume ``install.py``.

Uso responsable: todas las herramientas estan pensadas para equipos y redes
propias, o para las que tengas autorizacion por escrito.
"""

from __future__ import annotations

# Perfiles: core -> extra -> lab (acumulativos).
PROFILES = ("core", "extra", "lab")

CATEGORIES = {
    "fundamentos": "Fundamentos / Herramientas base",
    "red": "Analisis de red",
    "web": "Seguridad web",
    "sistema": "Auditoria y sistema",
    "password": "Contrasenas y credenciales",
    "malware": "Analisis de malware",
    "laboratorio": "Laboratorio aislado",
}

AUTH_NOTICE = (
    "Estas herramientas solo deben usarse en equipos/redes propios o con "
    "autorizacion explicita por escrito. El espejo y el uso de estas herramientas "
    "fuera de ese ambito es responsabilidad exclusiva del usuario."
)


def step(cmd, pm=None, privileged=False, env=None, note=None):
    """Construye un paso de instalacion.

    cmd       : lista de argumentos (sin shell, sin inyeccion).
    pm        : gestor de paquetes requerido (apt, dnf, brew, winget, ...).
                None = paso universal.
    privileged: si requiere sudo/root.
    env       : variables de entorno adicionales.
    note      : aviso que se muestra al ejecutarlo.
    """
    return {
        "cmd": list(cmd),
        "pm": pm,
        "privileged": bool(privileged),
        "env": env or {},
        "note": note,
    }


TOOLS = [
    # ------------------------------------------------------------------ CORE
    {
        "id": "python",
        "name": "Python 3 + pip",
        "category": "fundamentos",
        "description": "Lenguaje base para scripts, automatizacion y muchas herramientas del ecosistema.",
        "homepage": "https://www.python.org/downloads/",
        "profile": "core",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "python3", "python3-pip", "python3-venv"], "apt", True),
                step(["dnf", "install", "-y", "python3", "python3-pip"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "python", "python-pip"], "pacman", True),
                step(["zypper", "install", "-y", "python3", "python3-pip"], "zypper", True),
            ],
            "Darwin": [
                step(["xcode-select", "--install"], "brew", False,
                     note="Instala las Command Line Tools de Xcode si aun no estan presentes."),
                step(["brew", "install", "python@3.12"], "brew", False),
            ],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "Python.Python.3.12",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "python3", "--no-progress"], "choco", True),
            ],
        },
        "check": {
            "Linux": [["python3", "--version"]],
            "Darwin": [["python3", "--version"]],
            "Windows": [["python", "--version"], ["py", "-3", "--version"]],
        },
        "manual": {"Windows": "https://www.python.org/downloads/"},
    },
    {
        "id": "git",
        "name": "Git",
        "category": "fundamentos",
        "description": "Control de versiones para gestionar scripts, evidencias y laboratorios.",
        "homepage": "https://git-scm.com/",
        "profile": "core",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "git"], "apt", True),
                step(["dnf", "install", "-y", "git"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "git"], "pacman", True),
                step(["zypper", "install", "-y", "git"], "zypper", True),
            ],
            "Darwin": [step(["brew", "install", "git"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "Git.Git",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "git", "--no-progress"], "choco", True),
            ],
        },
        "check": {"Linux": [["git", "--version"]], "Darwin": [["git", "--version"]], "Windows": [["git", "--version"]]},
    },
    {
        "id": "curl",
        "name": "curl",
        "category": "fundamentos",
        "description": "Cliente HTTP/HTTPS para descargas y pruebas basicas de endpoints propios.",
        "homepage": "https://curl.se/",
        "profile": "core",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "curl"], "apt", True),
                step(["dnf", "install", "-y", "curl"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "curl"], "pacman", True),
                step(["zypper", "install", "-y", "curl"], "zypper", True),
            ],
            "Darwin": [step(["brew", "install", "curl"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "curl.curl",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "curl", "--no-progress"], "choco", True),
            ],
        },
        "check": {"Linux": [["curl", "--version"]], "Darwin": [["curl", "--version"]], "Windows": [["curl", "--version"]]},
        "notes": "Windows 10/11 ya incluye curl; el paso anterior solo es necesario si falta.",
    },
    {
        "id": "openssh",
        "name": "OpenSSH (cliente)",
        "category": "fundamentos",
        "description": "Acceso remoto cifrado y tuneles SSH en el laboratorio local.",
        "homepage": "https://www.openssh.com/",
        "profile": "core",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "openssh-client"], "apt", True),
                step(["dnf", "install", "-y", "openssh-clients"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "openssh"], "pacman", True),
                step(["zypper", "install", "-y", "openssh-clients"], "zypper", True),
            ],
            "Darwin": [],
            "Windows": [],
        },
        "check": {"Linux": [["ssh", "-V"]], "Darwin": [["ssh", "-V"]], "Windows": [["ssh", "-V"]]},
        "manual": {
            "Darwin": "Ya incluido en macOS; no requiere instalacion.",
            "Windows": ('Windows 10/11 lo incluye. Si falta, ejecuta como Administrador: '
                        'Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0'),
        },
    },
    {
        "id": "nmap",
        "name": "Nmap + Ncat",
        "category": "red",
        "description": "Descubrimiento de hosts y puertos en la red local; Ncat sustituye a netcat.",
        "homepage": "https://nmap.org/",
        "profile": "core",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "nmap"], "apt", True),
                step(["dnf", "install", "-y", "nmap", "ncat"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "nmap"], "pacman", True),
                step(["zypper", "install", "-y", "nmap", "ncat"], "zypper", True),
            ],
            "Darwin": [step(["brew", "install", "nmap"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "Nmap.Nmap",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "nmap", "--no-progress"], "choco", True),
            ],
        },
        "check": {"Linux": [["nmap", "--version"]], "Darwin": [["nmap", "--version"]], "Windows": [["nmap", "--version"]]},
        "notes": "Ncat se instala junto con Nmap. Escanea solo tu propia red/laboratorio.",
    },
    {
        "id": "wireshark",
        "name": "Wireshark + TShark",
        "category": "red",
        "description": "Analizador de protocolos con interfaz grafica y version CLI (tshark).",
        "homepage": "https://www.wireshark.org/",
        "profile": "core",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "wireshark", "tshark"], "apt", True,
                     env={"DEBIAN_FRONTEND": "noninteractive"},
                     note="Si se pregunta por captura por no-root, responde 'No'; el instalador anadira tu usuario al grupo wireshark."),
                step(["dnf", "install", "-y", "wireshark", "wireshark-cli"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "wireshark-cli", "wireshark-qt"], "pacman", True),
                step(["zypper", "install", "-y", "wireshark", "tshark"], "zypper", True),
            ],
            "Darwin": [step(["brew", "install", "--cask", "wireshark"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "Wireshark.Wireshark",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "wireshark", "--no-progress"], "choco", True),
            ],
        },
        "check": {"Linux": [["tshark", "--version"]], "Darwin": [["tshark", "--version"]], "Windows": [["tshark", "--version"]]},
        "notes": "Windows instala Npcap automaticamente. En Linux puede ser necesario reinciar sesion para capturar sin root.",
    },
    {
        "id": "gnupg",
        "name": "GnuPG",
        "category": "sistema",
        "description": "Cifrado y firmas digitales; util para proteger evidencias y configuraciones.",
        "homepage": "https://gnupg.org/",
        "profile": "core",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "gnupg"], "apt", True),
                step(["dnf", "install", "-y", "gnupg2"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "gnupg"], "pacman", True),
                step(["zypper", "install", "-y", "gnupg2"], "zypper", True),
            ],
            "Darwin": [step(["brew", "install", "gnupg"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "GnuPG.GnuPG",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "gnupg", "--no-progress"], "choco", True),
            ],
        },
        "check": {"Linux": [["gpg", "--version"]], "Darwin": [["gpg", "--version"]], "Windows": [["gpg", "--version"]]},
    },
    {
        "id": "keepassxc",
        "name": "KeePassXC",
        "category": "password",
        "description": "Gestor de contrasenas local y de codigo abierto para credenciales del laboratorio.",
        "homepage": "https://keepassxc.org/",
        "profile": "core",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "keepassxc"], "apt", True),
                step(["dnf", "install", "-y", "keepassxc"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "keepassxc"], "pacman", True),
                step(["zypper", "install", "-y", "keepassxc"], "zypper", True),
            ],
            "Darwin": [step(["brew", "install", "--cask", "keepassxc"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "KeePassXC.KeePassXC",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "keepassxc", "--no-progress"], "choco", True),
            ],
        },
        "check": {"Linux": [["keepassxc", "--version"]], "Darwin": [["keepassxc", "--version"]], "Windows": [["keepassxc", "--version"]]},
    },
    {
        "id": "openssl",
        "name": "OpenSSL CLI",
        "category": "sistema",
        "description": "Certificados, claves y cifrado; util para montar TLS en el laboratorio.",
        "homepage": "https://www.openssl.org/",
        "profile": "core",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "openssl"], "apt", True),
                step(["dnf", "install", "-y", "openssl"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "openssl"], "pacman", True),
                step(["zypper", "install", "-y", "openssl"], "zypper", True),
            ],
            "Darwin": [step(["brew", "install", "openssl@3"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "OpenSSL.Light",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "openssl.light", "--no-progress"], "choco", True),
            ],
        },
        "check": {"Linux": [["openssl", "version"]], "Darwin": [["openssl", "version"]], "Windows": [["openssl", "version"]]},
        "manual": {"Windows": "https://slproweb.com/products/Win32OpenSSL.html"},
    },
    {
        "id": "yara",
        "name": "YARA",
        "category": "malware",
        "description": "Reglas para identificar y clasificar archivos por patrones (analisis estatico basico).",
        "homepage": "https://virustotal.github.io/yara/",
        "profile": "core",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "yara"], "apt", True),
                step(["dnf", "install", "-y", "yara"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "yara"], "pacman", True),
                step(["zypper", "install", "-y", "yara"], "zypper", True),
            ],
            "Darwin": [step(["brew", "install", "yara"], "brew")],
            "Windows": [step(["choco", "install", "-y", "yara", "--no-progress"], "choco", True)],
        },
        "check": {"Linux": [["yara", "--version"]], "Darwin": [["yara", "--version"]], "Windows": [["yara", "--version"]]},
        "manual": {"Windows": "https://github.com/VirusTotal/yara/releases"},
    },

    # ----------------------------------------------------------------- EXTRA
    {
        "id": "gh",
        "name": "GitHub CLI (gh)",
        "category": "fundamentos",
        "description": "Gestiona repositorios, issues y releases desde la terminal.",
        "homepage": "https://cli.github.com/",
        "profile": "extra",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "gh"], "apt", True),
                step(["dnf", "install", "-y", "gh"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "github-cli"], "pacman", True),
                step(["zypper", "install", "-y", "gh"], "zypper", True),
            ],
            "Darwin": [step(["brew", "install", "gh"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "GitHub.CLI",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "gh", "--no-progress"], "choco", True),
            ],
        },
        "check": {"Linux": [["gh", "--version"]], "Darwin": [["gh", "--version"]], "Windows": [["gh", "--version"]]},
    },
    {
        "id": "glab",
        "name": "GitLab CLI (glab)",
        "category": "fundamentos",
        "description": "Gestiona proyectos y releases de GitLab desde la terminal (copia de seguridad del repo).",
        "homepage": "https://gitlab.com/gitlab-org/cli",
        "profile": "extra",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["dnf", "install", "-y", "glab"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "glab"], "pacman", True),
                step(["brew", "install", "glab"], "brew"),
            ],
            "Darwin": [step(["brew", "install", "glab"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "GitLab.Glab",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "glab", "--no-progress"], "choco", True),
            ],
        },
        "check": {"Linux": [["glab", "--version"]], "Darwin": [["glab", "--version"]], "Windows": [["glab", "--version"]]},
        "manual": {"Linux": "https://gitlab.com/gitlab-org/cli/-/releases", "Windows": "https://gitlab.com/gitlab-org/cli/-/releases"},
    },
    {
        "id": "zap",
        "name": "OWASP ZAP",
        "category": "web",
        "description": "Proxy interceptador y scanner de aplicaciones web para DVWA/Juice Shop locales.",
        "homepage": "https://www.zaproxy.org/",
        "profile": "extra",
        "authorization": True,
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["snap", "install", "zap", "--classic"], "snap", True),
            ],
            "Darwin": [step(["brew", "install", "--cask", "owasp-zap"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "OWASP.ZedAttackProxy",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "owasp-zap", "--no-progress"], "choco", True),
            ],
        },
        "check": {},
        "manual": {"Linux": "https://www.zaproxy.org/download/", "Darwin": "https://www.zaproxy.org/download/", "Windows": "https://www.zaproxy.org/download/"},
        "notes": "Verificacion manual: abrir la aplicacion y comprobar su numero de version.",
    },
    {
        "id": "burp",
        "name": "Burp Suite Community",
        "category": "web",
        "description": "Proxy interceptador alternativo para practicar trafico HTTP/HTTPS propio.",
        "homepage": "https://portswigger.net/burp/communitydownload",
        "profile": "extra",
        "authorization": True,
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [step(["snap", "install", "burpsuite", "--classic"], "snap", True)],
            "Darwin": [step(["brew", "install", "--cask", "burp-suite-community"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "PortSwigger.BurpSuiteCommunity",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
            ],
        },
        "check": {},
        "manual": {"Linux": "https://portswigger.net/burp/communitydownload", "Darwin": "https://portswigger.net/burp/communitydownload", "Windows": "https://portswigger.net/burp/communitydownload"},
        "notes": "Requiere Java (JRE) en algunas plataformas. Verificacion manual.",
    },
    {
        "id": "sqlmap",
        "name": "sqlmap",
        "category": "web",
        "description": "Pruebas de inyeccion SQL contra aplicaciones vulnerables desplegadas localmente.",
        "homepage": "https://sqlmap.org/",
        "profile": "extra",
        "authorization": True,
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["python3", "-m", "pip", "install", "--user", "sqlmap"], "pip"),
                step(["apt-get", "install", "-y", "sqlmap"], "apt", True),
            ],
            "Darwin": [step(["python3", "-m", "pip", "install", "--user", "sqlmap"], "pip")],
            "Windows": [step(["python", "-m", "pip", "install", "--user", "sqlmap"], "pip")],
        },
        "check": {"Linux": [["sqlmap", "--version"]], "Darwin": [["sqlmap", "--version"]], "Windows": [["sqlmap", "--version"]]},
        "notes": "Si sqlmap no esta en PATH, usa 'python -m sqlmap'. Solo contra tus propias aplicaciones.",
    },
    {
        "id": "gobuster",
        "name": "Gobuster",
        "category": "web",
        "description": "Descubrimiento de rutas y subdominios en objetivos propios (fuerza bruta controlada).",
        "homepage": "https://github.com/OJ/gobuster",
        "profile": "extra",
        "authorization": True,
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "gobuster"], "apt", True),
                step(["go", "install", "github.com/OJ/gobuster/v3@latest"], "go"),
            ],
            "Darwin": [step(["brew", "install", "gobuster"], "brew")],
            "Windows": [step(["choco", "install", "-y", "gobuster", "--no-progress"], "choco", True)],
        },
        "check": {"Linux": [["gobuster", "version"]], "Darwin": [["gobuster", "version"]], "Windows": [["gobuster", "version"]]},
        "manual": {"Windows": "https://github.com/OJ/gobuster/releases"},
    },
    {
        "id": "hashcat",
        "name": "Hashcat",
        "category": "password",
        "description": "Auditoria de hashes propios; util para entender politicas de contrasenas.",
        "homepage": "https://hashcat.net/hashcat/",
        "profile": "extra",
        "authorization": True,
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "hashcat"], "apt", True),
                step(["dnf", "install", "-y", "hashcat"], "dnf", True),
                step(["brew", "install", "hashcat"], "brew"),
            ],
            "Darwin": [step(["brew", "install", "hashcat"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "hashcat.hashcat",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "hashcat", "--no-progress"], "choco", True),
            ],
        },
        "check": {"Linux": [["hashcat", "--version"]], "Darwin": [["hashcat", "--version"]], "Windows": [["hashcat", "--version"]]},
        "notes": "Usa unicamente hashes generados por ti en el laboratorio.",
    },
    {
        "id": "john",
        "name": "John the Ripper",
        "category": "password",
        "description": "Comprobacion de debilidad de contrasenas en archivos propios del laboratorio.",
        "homepage": "https://www.openwall.com/john/",
        "profile": "extra",
        "authorization": True,
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "john"], "apt", True),
                step(["dnf", "install", "-y", "john"], "dnf", True),
                step(["brew", "install", "john"], "brew"),
            ],
            "Darwin": [step(["brew", "install", "john"], "brew")],
            "Windows": [step(["choco", "install", "-y", "johntheripper", "--no-progress"], "choco", True)],
        },
        "check": {"Linux": [["john", "--version"]], "Darwin": [["john", "--version"]], "Windows": [["john", "--version"]]},
        "manual": {"Windows": "https://www.openwall.com/john/"},
    },
    {
        "id": "lynis",
        "name": "Lynis",
        "category": "sistema",
        "description": "Auditoria de endurecimiento (hardening) de sistemas Linux/macOS.",
        "homepage": "https://cisofy.com/lynis/",
        "profile": "extra",
        "platforms": ["Linux", "Darwin"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "lynis"], "apt", True),
                step(["brew", "install", "lynis"], "brew"),
            ],
            "Darwin": [step(["brew", "install", "lynis"], "brew")],
        },
        "check": {"Linux": [["lynis", "show", "version"]], "Darwin": [["lynis", "show", "version"]]},
        "manual": {"Windows": "No nativo en Windows; ejecutalo dentro de una VM Linux o WSL."},
    },
    {
        "id": "clamav",
        "name": "ClamAV",
        "category": "malware",
        "description": "Antivirus de codigo abierto para analizar archivos descargados en el laboratorio.",
        "homepage": "https://www.clamav.net/",
        "profile": "extra",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "clamav", "clamav-daemon"], "apt", True),
                step(["dnf", "install", "-y", "clamav"], "dnf", True),
                step(["brew", "install", "clamav"], "brew"),
            ],
            "Darwin": [step(["brew", "install", "clamav"], "brew")],
            "Windows": [step(["choco", "install", "-y", "clamav", "--no-progress"], "choco", True)],
        },
        "check": {"Linux": [["clamscan", "--version"]], "Darwin": [["clamscan", "--version"]], "Windows": [["clamscan", "--version"]]},
        "manual": {"Windows": "https://www.clamav.net/downloads"},
    },

    # ------------------------------------------------------------------- LAB
    {
        "id": "docker",
        "name": "Docker / Docker Desktop",
        "category": "laboratorio",
        "description": "Contenedores para levantar DVWA, Juice Shop y otros objetivos vulnerables locales.",
        "homepage": "https://www.docker.com/",
        "profile": "lab",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "docker.io", "docker-compose-v2"], "apt", True),
                step(["dnf", "install", "-y", "docker"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "docker", "docker-compose"], "pacman", True),
            ],
            "Darwin": [step(["brew", "install", "--cask", "docker"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "Docker.DockerDesktop",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "docker-desktop", "--no-progress"], "choco", True),
            ],
        },
        "check": {"Linux": [["docker", "--version"]], "Darwin": [["docker", "--version"]], "Windows": [["docker", "--version"]]},
        "notes": "En Linux anade tu usuario al grupo docker y reinicia sesion. Windows/macOS requieren reinicio tras instalar.",
    },
    {
        "id": "virtualbox",
        "name": "VirtualBox",
        "category": "laboratorio",
        "description": "VM aisladas para practicar sin afectar al equipo anfitrion.",
        "homepage": "https://www.virtualbox.org/",
        "profile": "lab",
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {
            "Linux": [
                step(["apt-get", "install", "-y", "virtualbox"], "apt", True),
                step(["dnf", "install", "-y", "VirtualBox"], "dnf", True),
                step(["pacman", "-S", "--noconfirm", "virtualbox"], "pacman", True),
            ],
            "Darwin": [step(["brew", "install", "--cask", "virtualbox"], "brew")],
            "Windows": [
                step(["winget", "install", "--exact", "--id", "Oracle.VirtualBox",
                      "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"], "winget"),
                step(["choco", "install", "-y", "virtualbox", "--no-progress"], "choco", True),
            ],
        },
        "check": {"Linux": [["VBoxManage", "--version"]], "Darwin": [["VBoxManage", "--version"]], "Windows": [["VBoxManage", "--version"]]},
        "notes": "En Windows puede requerir activar virtualizacion (VT-x/AMD-V) en la BIOS/UEFI.",
    },
    {
        "id": "metasploit",
        "name": "Metasploit Framework",
        "category": "laboratorio",
        "description": "Framework de explotacion para practicar unicamente contra VMs propias y aisladas.",
        "homepage": "https://www.rapid7.com/products/metasploit/download/",
        "profile": "lab",
        "authorization": True,
        "platforms": ["Linux", "Darwin", "Windows"],
        "install": {},
        "check": {"Linux": [["msfconsole", "--version"]], "Darwin": [["msfconsole", "--version"]], "Windows": [["msfconsole.bat", "--version"]]},
        "manual": {
            "Linux": "https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html",
            "Darwin": "https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html",
            "Windows": "https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html",
        },
        "notes": ("No se instala automaticamente: el instalador oficial es un script remoto. "
                  "Descargalo y revisalo desde la URL oficial antes de ejecutarlo."),
    },
]


def by_id(tool_id):
    for tool in TOOLS:
        if tool["id"] == tool_id:
            return tool
    return None


def selected_tools(profile, only=None, skip=None):
    """Devuelve las herramientas del profile (acumulativo) aplicando only/skip."""
    if profile not in PROFILES:
        raise ValueError("Perfil desconocido: %s" % profile)
    level = PROFILES.index(profile)
    result = [
        t for t in TOOLS
        if PROFILES.index(t["profile"]) <= level
        and (not only or t["id"] in only)
        and (not skip or t["id"] not in skip)
    ]
    return result


def summary():
    counts = {p: 0 for p in PROFILES}
    for tool in TOOLS:
        counts[tool["profile"]] += 1
    return counts
