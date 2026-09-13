# Security Policy / Sicherheitsrichtlinie

[English](#english) · [Deutsch](#deutsch)

---

<a id="english"></a>
## English

### Supported Versions

| Version | Supported          | Security SLA        |
| :---    | :---:              | :---                |
| 1.0.x   | :white_check_mark: | 48h Response / 5-Day Triage |
| < 1.0.0 | :x:                | Unsupported         |

### Reporting a Vulnerability

Please do **not** disclose vulnerabilities via public GitHub issues, discussions, or pull requests.

1. **GitHub Private Vulnerability Reporting (Preferred):**
   Navigate to the repository on GitHub, open the **Security** tab, and click **Report a vulnerability**.
2. **Direct Security Contact (Encrypted / Urgent):**
   Send an advisory email to:
   - `security@open-bricks.org`
   - CC: `support@lukasgeiger.com`, `lukas@open-bricks.org`

### Response & Remediation SLA

- **Acknowledgment:** Within **48 hours** of receiving a report.
- **Triage & Severity Assessment:** Within **5 business days**.
- **Fix & Advisory Disclosure:** Coordinated release within 14 calendar days depending on severity.

### Scope & Threat Model

`llm-note` is intentionally designed local-first and zero-egress:
- **Zero Network Egress:** Core note operations do not communicate with external network services or cloud endpoints.
- **Loopback Interface Binding:** The optional Web GUI binds strictly to `127.0.0.1`.
- **Path Traversal Resistance:** Plain-text notebook storage paths are sanitized to stay within the designated notebook directory.
- **Unprivileged Execution:** Runs strictly in user space (`RunAsInvoker`) and never requires elevated or administrator privileges.

---

<a id="deutsch"></a>
## Deutsch

### Unterstützte Versionen

| Version | Unterstützt        | Sicherheits-SLA     |
| :---    | :---:              | :---                |
| 1.0.x   | :white_check_mark: | 48h Antwort / 5 Tage Triage |
| < 1.0.0 | :x:                | Nicht unterstützt   |

### Melden einer Schwachstelle

Bitte veröffentliche Sicherheitslücken **nicht** in öffentlichen Issues oder Foren.

1. **GitHub Private Vulnerability Reporting (Bevorzugt):**
   Öffne das Repository auf GitHub, wähle den Reiter **Security** und klicke auf **Report a vulnerability**.
2. **Direkter Sicherheitskontakt:**
   Sende eine E-Mail an:
   - `security@open-bricks.org`
   - CC: `support@lukasgeiger.com`, `lukas@open-bricks.org`

### Reaktions- und Behebungs-SLA

- **Eingangsbestätigung:** Innerhalb von **48 Stunden**.
- **Triage & Risikobewertung:** Innerhalb von **5 Werktagen**.
- **Patch & Veröffentlichung:** Koordinierter Release innerhalb von 14 Kalendertagen.

### Geltungsbereich & Sicherheitsmodell

`llm-note` arbeitet lokal und ohne ausgehenden Netzwerkverkehr:
- **Keine Netzwerk-Telemetrie:** Der Notizkern führt keine externen Netzwerkverbindungen aus.
- **Loopback-Bindung:** Die optionale Web-GUI lauscht ausschließlich auf `127.0.0.1`.
- **Schutz vor Pfad-Traversal:** Notizbuch-Pfade werden validiert und auf das Zielverzeichnis begrenzt.
- **Keine Rechteausweitung:** Führt Code ausschließlich mit Standard-Benutzerrechten aus (`RunAsInvoker`).
