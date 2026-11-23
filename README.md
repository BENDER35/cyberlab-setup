# CyberLab Setup

> Cross-platform installer for a **basic, authorized, local-only** cybersecurity lab.
> Soporte completo para **Linux · macOS · Windows**.
> [Español](README.es.md) · [Guía didáctica (ES)](docs/GUIA_DIDACTICA.es.md) · [Learning guide (EN)](docs/LEARNING_GUIDE.en.md)

`CyberLab Setup` installs a curated set of general-purpose security tools with a
single command, verifies them, and produces a JSON report. It is designed for
students and self-learners practising **only on their own equipment or on
systems they are explicitly authorized to test**.

> ⚠️ **Scope:** local lab only. The scripts do not scan, exploit or connect to
> third-party systems. See [SECURITY.md](SECURITY.md).

---

## Contents

- [Quick start](#quick-start)
- [Profiles and tools](#profiles-and-tools)
- [CLI reference](#cli-reference)
- [Verification and troubleshooting](#verification-and-troubleshooting)
- [Repository mirror and releases](#repository-mirror-and-releases)
- [Project layout](#project-layout)
- [License](#license)

---

## Quick start

### 1. Get the code

```bash
git clone https://github.com/BENDER35/cyberlab-setup.git
cd cyberlab-setup
```

Mirror (backup): <https://gitlab.com/BENDER_5000/cyberlab-setup.git>

### 2. Run the installer

| OS | Command |
|---|---|
| Linux | `chmod +x install.sh && ./install.sh --profile core --yes` |
| macOS | `chmod +x install.sh && ./install.sh --profile core --yes` |
| Windows (PowerShell) | `powershell -ExecutionPolicy Bypass -File .\install.ps1 -Profile core -Yes` |

Python 3.8+ is the only prerequisite. The wrapper detects it and delegates to
`install.py`, which can also be called directly:

```bash
python3 install.py --profile core --yes
```

Recommended first run (preview before installing):

```bash
python3 install.py --dry-run --profile core
python3 install.py --check                # verify what is already installed
```

### 3. Advanced profiles

```bash
# Web app testing + password auditing (requires your explicit authorization)
python3 install.py --profile extra --yes --authorize-lab

# Containers, VMs and exploitation framework on isolated machines only
python3 install.py --profile lab --yes --authorize-lab --only docker,virtualbox
```

On Windows PowerShell the flags also work in `-PascalCase` form
(`-Profile`, `-Only`, `-AuthorizeLab`, `-Yes`, …).

---

## Profiles and tools

Profiles are **cumulative**: `core` ⊂ `extra` ⊂ `lab`.

| Profile | Purpose |
|---|---|
| `core` | Safe baseline available on all three operating systems. |
| `extra` | Web/proxy, password auditing and optional CLI helpers. |
| `lab` | Docker, VirtualBox and Metasploit for isolated vulnerable machines. |

### Core (all three OS)

| ID | Tool | Category | What it is used for |
|---|---|---|---|
| `python` | Python 3 + pip | Fundamentals | Scripting and automation |
| `git` | Git | Fundamentals | Version control |
| `curl` | curl | Fundamentals | HTTP requests / downloads |
| `openssh` | OpenSSH client | Fundamentals | Encrypted remote access |
| `nmap` | Nmap + Ncat | Network | Host/port discovery on your LAN |
| `wireshark` | Wireshark + TShark | Network | Protocol capture and analysis |
| `gnupg` | GnuPG | System | Signing and encrypting evidence |
| `keepassxc` | KeePassXC | Passwords | Local password manager |
| `openssl` | OpenSSL CLI | System | Keys and certificates for local TLS |
| `yara` | YARA | Malware | Static rule-based file analysis |

### Extra (opt-in with `--authorize-lab`)

`gh`, `glab`, `zap`, `burp`, `sqlmap`, `gobuster`, `hashcat`, `john`, `lynis`
(Linux/macOS only), `clamav`.

### Lab (opt-in with `--authorize-lab`)

`docker`, `virtualbox`, `metasploit`. Metasploit is **not** auto-installed: the
official installer is a remote script, so the catalog links to the official
download for manual review.

Tools without a reliable winget/apt ID are reported as `MANUAL` with an official
download URL instead of failing silently. Nothing is downloaded from unofficial
mirrors.

---

## CLI reference

```
usage: install.py [-h] [--profile {core,extra,lab}] [--only ONLY] [--skip SKIP]
                  [--check] [--dry-run] [--yes] [--authorize-lab] [--no-sudo]
                  [--pm PM] [--log LOG] [--report REPORT] [--list] [-v] [--version]
```

| Flag | Description |
|---|---|
| `--profile` | `core` (default), `extra` or `lab`. |
| `--only a,b` | Install/verify only these tool IDs. |
| `--skip a,b` | Exclude these tool IDs. |
| `--check` | Verify only; no changes. Exits non-zero if a core tool is missing. |
| `--dry-run` | Print the commands without executing them. |
| `--yes`, `-y` | Skip the interactive confirmation (required without a TTY). |
| `--authorize-lab` | Acknowledge the responsible-use rule; unlocks restricted tools. |
| `--no-sudo` | Skip privileged steps (Linux/macOS). |
| `--pm apt,brew` | Force the package managers to use. |
| `--log FILE` | Append a log to `FILE` (default: `cyberlab-install-<timestamp>.log`). |
| `--report FILE` | Write a machine-readable JSON report. |
| `--list` | Print the full catalog and exit. |
| `-v` | Verbose output. |

Exit codes: `0` success, `1` at least one failed tool, `2` invalid arguments.

---

## Verification and troubleshooting

```bash
python3 install.py --check --report install-report.json
nmap --version && tshark --version && yara --version
```

| Problem | Fix |
|---|---|
| `brew: command not found` (macOS) | Install Homebrew from <https://brew.sh>, then re-run. |
| `sudo` password prompt | Expected on Linux/macOS; enter your own user password. |
| Wireshark cannot capture (Linux) | Log out and back in after the installer adds you to the `wireshark` group. |
| Docker permission denied (Linux) | Log out and back in after being added to the `docker` group. |
| `winget` asks for agreements | Re-run with `--yes`; the installer already passes acceptance flags. |
| A GUI tool shows `MANUAL` | Open the official URL from the output and install it by hand. |
| Python not found on Windows | Install from <https://www.python.org/downloads/> and tick **Add Python to PATH**. |

The installer never runs a remote shell script automatically and never echoes
tokens or passwords into the log.

---

## Repository mirror and releases

- **Primary (GitHub):** <https://github.com/BENDER35/cyberlab-setup>
- **Backup/mirror (GitLab):** <https://gitlab.com/BENDER_5000/cyberlab-setup>

Automatic mirroring is configured with GitHub Actions
(`.github/workflows/mirror-to-gitlab.yml`): every push to a branch or tag is
forwarded to GitLab via `git push --force --prune`. It requires two GitHub
secrets/variables:

| Name | Type | Value |
|---|---|---|
| `GITLAB_TOKEN` | Secret | GitLab PAT with `write_repository` (and `api` for project creation/releases) |
| `GITLAB_NAMESPACE` | Variable | `BENDER_5000` |
| `GITLAB_PROJECT` | Variable | `cyberlab-setup` |

Helper scripts:

```bash
scripts/create-repos.sh      # create both repositories (needs GH_TOKEN + GITLAB_TOKEN)
scripts/setup-mirror.sh      # upload the GitLab token/variables to GitHub using gh
python3 scripts/verify_mirror.py   # compare branch heads and tags on both hosts
scripts/build-release.sh 1.0.0     # build dist/cyberlab-setup-v1.0.0.zip
scripts/release.sh 1.0.0           # tag + publish the ZIP on GitHub and GitLab
```

`verify_mirror.py` exits `0` when all branch/tag SHAs match and `1` when they
do not; `--fix` re-pushes the mirror. The mirror workflow also runs a
verification step after each push.

---

## Project layout

```
.
├── install.py               # cross-platform installer (Linux/macOS/Windows)
├── catalog.py               # tool catalog (IDs, install steps, checks)
├── install.sh               # Linux/macOS wrapper
├── install.ps1              # Windows wrapper
├── docs/
│   ├── GUIA_DIDACTICA.es.md # guía didáctica en español
│   └── LEARNING_GUIDE.en.md # learning guide in English
├── scripts/                 # repo creation, mirror, verification, releases
├── .github/workflows/       # automatic mirror + mirror verification
├── .gitlab-ci.yml           # sanity checks + release helper on GitLab
├── README.md                # this file
└── README.es.md             # versión en español
```

---

## License

MIT — see [LICENSE](LICENSE). Tools installed by this script keep their own
licenses. Educational use only; you are responsible for complying with local
laws and with the owner's authorization.
