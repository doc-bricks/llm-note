# Security Policy / Sicherheitsrichtlinie

[English](#english) · [Deutsch](#deutsch)

---

<a id="english"></a>
## English

### Supported versions

| Version | Supported | Maintainer response target |
| :--- | :---: | :--- |
| 1.0.x | Yes | Acknowledgement target: 48 hours; initial triage target: 5 business days |
| < 1.0.0 | No | Not supported |

### Reporting a vulnerability

Please do **not** disclose vulnerabilities through public GitHub issues, discussions, or pull requests.

1. **GitHub Private Vulnerability Reporting (preferred):** Open the repository's **Security** tab and choose **Report a vulnerability**.
2. **Direct security contact:** Email:
   - `security@open-bricks.org`
   - CC: `support@lukasgeiger.com`, `lukas@open-bricks.org`

### Maintainer response targets

The maintainer aims to acknowledge a report within 48 hours and begin triage within 5 business days. These are response targets, not a service-level agreement or a guarantee of investigation, a fix, or disclosure by a particular date. There is no fixed remediation deadline.

### Scope and current implementation

`llm-note` is a local-first notes application. Its core uses local SQLite and plain-text notebook files, and the project declares no additional Python runtime packages.

- The optional web interface binds to loopback at `127.0.0.1`. This is not authentication against other processes running as the same user.
- Notebook paths are validated and kept within the configured notebook root by the application.
- The process does not request administrative or root elevation and inherits the permissions of the process that launches it.
- The application does not provide an operating-system egress block, sandbox, or privilege drop. Network access depends on the host environment; no zero-egress guarantee is made.

<a id="deutsch"></a>
## Deutsch

### Unterstützte Versionen

| Version | Unterstützt | Reaktionsziel des Maintainers |
| :--- | :---: | :--- |
| 1.0.x | Ja | Eingangsbestätigung: 48 Stunden; Beginn der Triage: 5 Werktage |
| < 1.0.0 | Nein | Nicht unterstützt |

### Schwachstellen melden

Veröffentliche Sicherheitslücken **nicht** in öffentlichen GitHub-Issues, Diskussionen oder Pull Requests.

1. **GitHub Private Vulnerability Reporting (bevorzugt):** Öffne im Repository den Reiter **Security** und wähle **Report a vulnerability**.
2. **Direkter Sicherheitskontakt:** Schreibe an:
   - `security@open-bricks.org`
   - CC: `support@lukasgeiger.com`, `lukas@open-bricks.org`

### Reaktionsziele des Maintainers

Der Maintainer strebt an, innerhalb von 48 Stunden den Eingang zu bestätigen und innerhalb von 5 Werktagen mit der Triage zu beginnen. Das sind Reaktionsziele, keine Service-Level-Vereinbarung und keine Garantie für Untersuchung, Korrektur oder Veröffentlichung bis zu einem bestimmten Datum. Eine feste Frist für Korrekturen gibt es nicht.

### Geltungsbereich und aktueller Implementierungsstand

`llm-note` ist eine lokal ausgerichtete Notizanwendung. Der Kern verwendet lokale SQLite-Datenbanken und Klartext-Notizbücher; das Projekt deklariert keine zusätzlichen Python-Laufzeitpakete.

- Die optionale Weboberfläche bindet an die Loopback-Adresse `127.0.0.1`. Das ist keine Authentifizierung gegenüber anderen Prozessen desselben Benutzers.
- Die Anwendung validiert Notizbuchpfade und hält sie innerhalb des konfigurierten Notizbuch-Stammverzeichnisses.
- Der Prozess fordert keine Administrator- oder Root-Erhöhung an und übernimmt die Berechtigungen des aufrufenden Prozesses.
- Die Anwendung stellt keine Egress-Sperre des Betriebssystems, keine Sandbox und keinen Rechteentzug bereit. Der Netzwerkzugriff hängt von der Hostumgebung ab; eine Zero-Egress-Garantie wird nicht gegeben.
