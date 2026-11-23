# CyberLab Setup

> Instalador multiplataforma para un laboratorio de ciberseguridad **básico,
> autorizado y de ámbito local**. Soporte completo para **Linux · macOS · Windows**.
> [English](README.md) · [Guía didáctica](docs/GUIA_DIDACTICA.es.md) · [Learning guide](docs/LEARNING_GUIDE.en.md)

`CyberLab Setup` instala con un solo comando un conjunto seleccionado de
herramientas genéricas de seguridad, las verifica y genera un informe JSON.
Está pensado para estudiantes y autodidactas que practican **únicamente en sus
propios equipos o en sistemas con autorización explícita**.

> ⚠️ **Ámbito:** laboratorio local. Los scripts no escanean, explotan ni se
> conectan a sistemas de terceros. Consulta [SECURITY.md](SECURITY.md).

---

## Contenido

- [Inicio rápido](#inicio-rápido)
- [Perfiles y herramientas](#perfiles-y-herramientas)
- [Referencia de la CLI](#referencia-de-la-cli)
- [Verificación y solución de problemas](#verificación-y-solución-de-problemas)
- [Espejo del repositorio y releases](#espejo-del-repositorio-y-releases)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Licencia](#licencia)

---

## Inicio rápido

### 1. Obtener el código

```bash
git clone https://github.com/BENDER35/cyberlab-setup.git
cd cyberlab-setup
```

Espejo (copia de seguridad): <https://gitlab.com/BENDER_5000/cyberlab-setup.git>

### 2. Ejecutar el instalador

| Sistema | Comando |
|---|---|
| Linux | `chmod +x install.sh && ./install.sh --profile core --yes` |
| macOS | `chmod +x install.sh && ./install.sh --profile core --yes` |
| Windows (PowerShell) | `powershell -ExecutionPolicy Bypass -File .\install.ps1 -Profile core -Yes` |

El único requisito previo es Python 3.8+. El script contenedor lo detecta y
delega en `install.py`, que también puede llamarse directamente:

```bash
python3 install.py --profile core --yes
```

Primera ejecución recomendada (previsualizar antes de instalar):

```bash
python3 install.py --dry-run --profile core
python3 install.py --check                # verificar lo que ya hay instalado
```

### 3. Perfiles avanzados

```bash
# Pruebas web y auditoría de contraseñas (requiere tu autorización explícita)
python3 install.py --profile extra --yes --authorize-lab

# Contenedores, VM y framework de explotación solo en máquinas aisladas
python3 install.py --profile lab --yes --authorize-lab --only docker,virtualbox
```

En PowerShell de Windows las opciones también funcionan en formato
`-PascalCase` (`-Profile`, `-Only`, `-AuthorizeLab`, `-Yes`, …).

---

## Perfiles y herramientas

Los perfiles son **acumulativos**: `core` ⊂ `extra` ⊂ `lab`.

| Perfil | Finalidad |
|---|---|
| `core` | Base segura disponible en los tres sistemas operativos. |
| `extra` | Proxy/web, auditoría de contraseñas y utilidades CLI opcionales. |
| `lab` | Docker, VirtualBox y Metasploit para máquinas vulnerables aisladas. |

### Core (los tres sistemas)

| ID | Herramienta | Categoría | Para qué sirve |
|---|---|---|---|
| `python` | Python 3 + pip | Fundamentos | Scripts y automatización |
| `git` | Git | Fundamentos | Control de versiones |
| `curl` | curl | Fundamentos | Peticiones HTTP / descargas |
| `openssh` | Cliente OpenSSH | Fundamentos | Acceso remoto cifrado |
| `nmap` | Nmap + Ncat | Red | Descubrimiento de hosts y puertos en tu LAN |
| `wireshark` | Wireshark + TShark | Red | Captura y análisis de protocolos |
| `gnupg` | GnuPG | Sistema | Firmar y cifrar evidencias |
| `keepassxc` | KeePassXC | Contraseñas | Gestor local de contraseñas |
| `openssl` | OpenSSL CLI | Sistema | Claves y certificados para TLS local |
| `yara` | YARA | Malware | Análisis estático de archivos por reglas |

### Extra (requiere `--authorize-lab`)

`gh`, `glab`, `zap`, `burp`, `sqlmap`, `gobuster`, `hashcat`, `john`, `lynis`
(solo Linux/macOS), `clamav`.

### Lab (requiere `--authorize-lab`)

`docker`, `virtualbox`, `metasploit`. Metasploit **no** se instala
automáticamente: el instalador oficial es un script remoto, por lo que el
catálogo enlaza la descarga oficial para que la revises manualmente.

Las herramientas sin un ID fiable en winget/apt se informan como `MANUAL` con
su URL oficial en lugar de fallar silenciosamente. No se descarga nada de
espejos no oficiales.

---

## Referencia de la CLI

```
usage: install.py [-h] [--profile {core,extra,lab}] [--only ONLY] [--skip SKIP]
                  [--check] [--dry-run] [--yes] [--authorize-lab] [--no-sudo]
                  [--pm PM] [--log LOG] [--report REPORT] [--list] [-v] [--version]
```

| Opción | Descripción |
|---|---|
| `--profile` | `core` (por defecto), `extra` o `lab`. |
| `--only a,b` | Instalar/verificar solo esos IDs. |
| `--skip a,b` | Excluir esos IDs. |
| `--check` | Solo verificar; no modifica nada. Falla si falta una herramienta core. |
| `--dry-run` | Muestra los comandos sin ejecutarlos. |
| `--yes`, `-y` | Omite la confirmación interactiva (obligatorio sin TTY). |
| `--authorize-lab` | Aceptas la regla de uso responsable; desbloquea herramientas restringidas. |
| `--no-sudo` | Omite los pasos que requieren sudo (Linux/macOS). |
| `--pm apt,brew` | Fuerza los gestores de paquetes a utilizar. |
| `--log ARCHIVO` | Añade el registro a `ARCHIVO` (por defecto `cyberlab-install-<fecha>.log`). |
| `--report ARCHIVO` | Escribe un informe JSON legible por máquina. |
| `--list` | Muestra el catálogo completo y sale. |
| `-v` | Salida detallada. |

Códigos de salida: `0` correcto, `1` algún fallo, `2` argumentos inválidos.

---

## Verificación y solución de problemas

```bash
python3 install.py --check --report install-report.json
nmap --version && tshark --version && yara --version
```

| Problema | Solución |
|---|---|
| `brew: command not found` (macOS) | Instala Homebrew desde <https://brew.sh> y vuelve a ejecutar. |
| Contraseña de `sudo` | Es normal en Linux/macOS; introduce la contraseña de tu usuario. |
| Wireshark no captura (Linux) | Cierra sesión y vuelve a entrar tras añadirte al grupo `wireshark`. |
| Docker: permiso denegado (Linux) | Cierra sesión y vuelve a entrar tras añadirte al grupo `docker`. |
| `winget` pide aceptar acuerdos | Vuelve a ejecutar con `--yes`; el script ya pasa los flags de aceptación. |
| Una herramienta GUI aparece como `MANUAL` | Abre la URL oficial indicada e instálala a mano. |
| Python no encontrado en Windows | Instálalo desde <https://www.python.org/downloads/> y marca **Add Python to PATH**. |

El instalador nunca ejecuta automáticamente scripts remotos ni escribe tokens
o contraseñas en el log.

---

## Espejo del repositorio y releases

- **Principal (GitHub):** <https://github.com/BENDER35/cyberlab-setup>
- **Espejo/copia (GitLab):** <https://gitlab.com/BENDER_5000/cyberlab-setup>

El espejo automático se configura con GitHub Actions
(`.github/workflows/mirror-to-gitlab.yml`): cada push a una rama o etiqueta se
reenvía a GitLab mediante `git push --force --prune`. Necesita dos
secret/variables de GitHub:

| Nombre | Tipo | Valor |
|---|---|---|
| `GITLAB_TOKEN` | Secreto | PAT de GitLab con `write_repository` (y `api` para crear proyectos/releases) |
| `GITLAB_NAMESPACE` | Variable | `BENDER_5000` |
| `GITLAB_PROJECT` | Variable | `cyberlab-setup` |

Scripts auxiliares:

```bash
scripts/create-repos.sh      # crear ambos repositorios (necesita GH_TOKEN + GITLAB_TOKEN)
scripts/setup-mirror.sh      # subir el token y las variables a GitHub con gh
python3 scripts/verify_mirror.py   # comparar commits y etiquetas en ambos hosts
scripts/build-release.sh 1.0.0     # generar dist/cyberlab-setup-v1.0.0.zip
scripts/release.sh 1.0.0           # etiquetar y publicar el ZIP en GitHub y GitLab
```

`verify_mirror.py` devuelve `0` si coinciden todos los SHA de ramas y etiquetas
y `1` si no; `--fix` vuelve a enviar el espejo. El workflow de espejo también
verifica automáticamente después de cada push.

---

## Estructura del proyecto

```
.
├── install.py               # instalador multiplataforma (Linux/macOS/Windows)
├── catalog.py               # catálogo de herramientas (IDs, pasos, verificaciones)
├── install.sh               # contenedor para Linux/macOS
├── install.ps1              # contenedor para Windows
├── docs/
│   ├── GUIA_DIDACTICA.es.md # guía didáctica en español
│   └── LEARNING_GUIDE.en.md # guía didáctica en inglés
├── scripts/                 # creación de repos, espejo, verificación y releases
├── .github/workflows/       # espejo automático + verificación
├── .gitlab-ci.yml           # comprobaciones y apoyo a releases en GitLab
├── README.md                # este archivo en inglés
└── README.es.md             # versión en español
```

---

## Licencia

MIT — consulta [LICENSE](LICENSE). Las herramientas instaladas conservan su
propia licencia. Uso exclusivamente didáctico; eres responsable de cumplir la
ley aplicable y la autorización del propietario.
