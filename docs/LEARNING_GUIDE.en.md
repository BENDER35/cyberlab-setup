# Learning guide — Basic cybersecurity lab (local, authorized)

**Version 1.0.0** · [Back to README](README.md) · [Versión en español](GUIA_DIDACTICA.es.md)

This guide accompanies `CyberLab Setup`. It is written for beginners who want
to practise **without leaving their own machine**. Every example uses
`127.0.0.1`, `localhost`, Docker containers, or virtual machines on an internal
network (`host-only`/`NAT`).

---

## 0. Golden rule (read before running anything)

> You may only scan, intercept, test or analyse **machines and networks you
> own**, or systems for which you have **written permission**.

- ✅ Your PC, your router, your VMs, your containers, your test files.
- ❌ Neighbours' networks, campus or corporate networks, third parties on the Internet.
- ❌ Real credentials, other people's personal data, malware on the host machine.

If you practise outside your home, get written authorization and define the
scope in writing: which systems, what time window, and which actions are allowed.

---

## 1. Learning objectives

By the end of this guide you will be able to:

1. Install and verify a baseline toolset on Linux, macOS or Windows.
2. Discover devices and open ports on **your** local network with Nmap.
3. Capture and read your own network traffic with Wireshark/TShark.
4. Run a deliberately vulnerable **local** app (DVWA or Juice Shop) with Docker.
5. Intercept your own HTTP requests with OWASP ZAP or Burp Suite.
6. Write a simple YARA rule and test it against a file you create.
7. Audit passwords **you generated** and explain what makes a password weak.
8. Produce a short report with findings and recommendations.

---

## 2. Preparing the environment

### 2.1 Requirements

| OS | Requirements |
|---|---|
| Linux | Python 3.8+, `sudo`, internet access to download packages. |
| macOS | Python 3.8+, Homebrew (<https://brew.sh>), macOS 12+. |
| Windows | Windows 10/11, Python 3.8+ with *Add Python to PATH*, PowerShell. |

### 2.2 Initial check

```bash
python3 --version
git --version
```

On Windows PowerShell:

```powershell
python --version
git --version
```

### 2.3 Install in phases

```bash
# Phase 1: see what would be installed (nothing is changed)
python3 install.py --dry-run --profile core

# Phase 2: install the baseline
python3 install.py --profile core --yes --report install-report.json

# Phase 3: verify
python3 install.py --check
```

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Profile core -Yes
.\install.ps1 -Check
```

**What to expect:** lines marked `[OK]`, `[MAN]`, or `[FAIL]`.
`[MAN]` means *manual installation*: open the official URL printed in the
output. It is not a script error.

### 2.4 Isolating the lab

- Create an internal network in VirtualBox (*Host-only Adapter*) or a Docker
  network: `docker network create labnet`.
- Disable Wi-Fi if your VMs expose vulnerable ports.
- Never forward lab ports from your router to the Internet.

---

## 3. Exercise 1 — Local discovery with Nmap

**Goal:** understand what "open port" means and identify services on your host.

**Setup:** use `localhost` or your VM's IP (e.g. `192.168.56.10`).

```bash
# Your own machine
nmap -sT 127.0.0.1

# Your VM on a host-only network (replace the IP)
nmap -sS -T3 192.168.56.10

# Most common ports with version detection
nmap -sV --top-ports 20 192.168.56.10
```

**Questions:**

1. Which ports are `open`, `closed` and `filtered`?
2. Which service is behind each open port?
3. Why can `-sS` require elevated privileges while `-sT` usually does not?

**Deliverable:** the command output plus a table with port, service and
potential risk:

| Port | Service | Observation |
|---|---|---|
| 22 | SSH | Restrict by IP and use keys |
| 80 | HTTP | No TLS: lab use only |

---

## 4. Exercise 2 — Capturing traffic with Wireshark

**Goal:** read a conversation your own machine generated.

1. Open Wireshark and choose `loopback` (Linux/macOS) or
   `Npcap Loopback Adapter` (Windows).
2. Start the capture.
3. Generate your own traffic:

```bash
ping -c 4 127.0.0.1      # Linux/macOS
ping -n 4 127.0.0.1      # Windows
curl -I http://127.0.0.1:8000
```

4. Stop and apply the display filter `icmp || http`.
5. Save the capture as `captura-local.pcapng`.

Command-line equivalent (TShark):

```bash
tshark -i lo -c 20 -w captura-local.pcapng     # Linux
tshark -i lo0 -c 20 -w captura-local.pcapng    # macOS
tshark -i "Npcap Loopback Adapter" -c 20 -w captura-local.pcapng   # Windows
```

**Questions:**

1. What are the source and destination IP addresses?
2. Which fields does an ICMP header contain?
3. Why must you not capture other users' traffic?

---

## 5. Exercise 3 — A local vulnerable app with Docker

**Goal:** have a legal target for web testing.

```bash
docker network create labnet

# DVWA
docker run -d --name dvwa --network labnet -p 127.0.0.1:8080:80 vulnerables/web-dvwa

# Or OWASP Juice Shop
docker run -d --name juice --network labnet -p 127.0.0.1:3000:3000 bkimminich/juice-shop
```

Open <http://127.0.0.1:8080> (DVWA) or <http://127.0.0.1:3000> (Juice Shop).

> The ports are bound to `127.0.0.1`: only your machine can reach them.
> Do not replace `-p 127.0.0.1:...` with `-p 80:` on a shared network.

Cleanup:

```bash
docker rm -f dvwa juice
docker network rm labnet
```

---

## 6. Exercise 4 — Intercepting proxy (ZAP / Burp)

**Goal:** view and modify an HTTP request before it reaches the server.

1. Install the `extra` profile with authorization:

```bash
python3 install.py --profile extra --yes --authorize-lab --only zap
```

2. Open ZAP → *Tools → Options → Proxy* (default `127.0.0.1:8080`).
3. Point your browser at that proxy for **localhost only**.
4. Visit `http://127.0.0.1:8080` (DVWA) and inspect the request history.
5. Run *Spider* against that same URL and review the findings.

**Questions:**

1. What is the difference between a `GET` and a `POST` request?
2. Which headers reveal information about the client?
3. What is a *spider* and why limit it to your own lab?

---

## 7. Exercise 5 — YARA rules

**Goal:** detect a pattern inside a file you created.

1. Create a harmless test file:

```bash
printf 'This is a YARA test file\nTEST-MARKER-1234\n' > sample.txt
```

2. Create `rule.yar`:

```yara
rule TestMarker
{
    meta:
        description = "Detects the lab test marker"
        author = "student"
    strings:
        $marker = "TEST-MARKER-1234"
    condition:
        $marker
}
```

3. Run:

```bash
yara rule.yar sample.txt
```

**Expected result:** `TestMarker sample.txt`.

**Questions:** what happens if you change one letter of the marker? How could
you make the rule more robust (for example with a regular expression)?

---

## 8. Exercise 6 — Auditing your own passwords

**Goal:** understand length and randomness.

Generate your own hashes (never use somebody else's hashes):

```bash
printf 'password123' | md5sum          # Linux
printf 'password123' | md5 -q          # macOS
```

Create a small wordlist `wordlist.txt` with your own test words and run:

```bash
john --format=raw-md5 --wordlist=wordlist.txt my-hashes.txt
```

**Questions:**

1. Which passwords were cracked in under a second, and why?
2. Compare `password123` with `Correct-Horse-Battery-Staple-42!`.
3. Why is MD5 unsuitable for password storage today?

In KeePassXC: create a database, store your lab credentials and set a long
master password.

---

## 9. Final report (template)

```markdown
# Lab report — Name / Date

## 1. Scope
Own machines: 127.0.0.1, VM 192.168.56.10, DVWA container.
Authorization: self. Network: host-only, no Internet egress.

## 2. Tools used
Nmap, TShark, ZAP, YARA, John.

## 3. Findings
| ID | Finding | Evidence | Risk | Recommendation |
|----|---------|----------|------|----------------|
| 1  | HTTP without TLS | captura-local.pcapng | Medium | Enable HTTPS |

## 4. Conclusion
What I learned, what was difficult, what I will practise next.

## 5. Cleanup
Containers removed, captures saved, VM powered off.
```

---

## 10. Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| `nmap: command not found` | Not in PATH | `python3 install.py --check`; reinstall with `--only nmap`. |
| Wireshark shows no interfaces | Npcap/permissions | Windows: reinstall Npcap. Linux: `wireshark` group + log out/in. |
| `brew: command not found` | Homebrew missing | Install from <https://brew.sh>. |
| Docker `permission denied` | User not in `docker` group | Log out and back in. |
| ZAP does not intercept HTTPS | Missing CA certificate | Install ZAP's CA only in the lab browser. |
| `--authorize-lab` required | Restricted profile | Re-read section 0 and add the flag if appropriate. |

---

## 11. Glossary

| Term | Meaning |
|---|---|
| **Port** | Logical endpoint of a service (80 = HTTP, 443 = HTTPS). |
| **Sniffing** | Passive capture of network traffic. |
| **MITM** | Man in the middle: intercepting communication between two parties. |
| **Fuzzing** | Sending unexpected input to find errors. |
| **Hardening** | Reducing a system's attack surface. |
| **IOC** | Indicator of compromise: a clue to an intrusion. |
| **Reverse shell** | Remote shell initiated from the target (only on your own VMs). |

---

## 12. Next steps

- Repeat exercise 1 with your VM powered off and compare the results.
- Write a new YARA rule for a marker of your own.
- Practise `ssh -L` to build a local tunnel to your VM.
- Read the official documentation linked from `catalog.py`.
- Publish your report (without sensitive data) to your personal repository.
