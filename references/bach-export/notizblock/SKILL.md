---
name: notizblock
description: >
  Freie Notizen und Themen-Notizbücher in BACH.
---

# Notizblock-Service v1.1

**Freie Notizen und Themen-Notizbücher in BACH**

---

## Überblick

Der Notizblock-Service stellt eine einfache, dateisystembasierte Notiz-Infrastruktur bereit:

- **Standard-Notizblock:** `user/notizen/Notizblock.txt` — universale Inbox, alles landet hier solange kein anderer Notizblock angegeben wird
- **Weitere Notizblöcke:** Benannte `.txt`-Dateien auf gleicher Ebene
- **Themen-Ordner:** Für thematisch gruppierte Notizbücher
- **Format:** Plain-Text (`.txt`) — maximal portabel, kein Lock-in

---

## Datei-Struktur

```
user/notizen/
├── Notizblock.txt          ← Standard-Inbox (immer vorhanden)
├── Einkaufsliste.txt       ← Weiterer Notizblock (gleiche Ebene)
├── Thema A/
│   └── Formeln.txt         ← Notizblock im Themenordner
├── Thema B/
│   ├── Ideen.txt
│   └── Quellen.txt
└── Archiv/
    └── Notizblock_2026-01.txt
```

---

## Anlegen-Regeln

| Benutzer sagt | Ergebnis |
|---|---|
| "Lege neuen Notizblock an namens Einkaufsliste" | `user/notizen/Einkaufsliste.txt` |
| "Lege Thema an namens Physik" | Ordner `user/notizen/Physik/` |
| "Lege Notizblock in Thema Physik namens Formeln an" | `user/notizen/Physik/Formeln.txt` |
| Ohne Angabe | → immer in `Notizblock.txt` |

**Namenskonvention:** Datei-/Ordnernamen exakt wie vom User angegeben (Groß-/Kleinschreibung erhalten). Leerzeichen werden zu Unterstrichen: `Einkaufs Liste` → `Einkaufs_Liste.txt`.

---

## Standard-Notizblock (Inbox)

`user/notizen/Notizblock.txt` ist der universelle Sammelpunkt:
- Alles landet hier, solange kein anderer Notizblock aktiv ist
- Chronologisch, neueste Einträge unten
- Unstrukturiert — kein Zwang zu Kategorien

### Eintrag-Format

```
---
[2026-02-18 14:30]
Schnelle Notiz ohne Zuweisung.

---
[2026-02-18 15:00]
Interviewidee mit Prof. Wagner.
#NB: interviews

---
[2026-02-18 16:15]
Einkauf: Milch, Butter, Mehl
#NB: Einkaufsliste

```

### Transfer-Markierung `#NB: <ziel>`

Einträge mit `#NB:` werden auf Anfrage in das Zielnotizbuch verschoben:
- `#NB: Einkaufsliste` → nach `Einkaufsliste.txt`
- `#NB: Physik/Formeln` → nach `Physik/Formeln.txt`

Claude führt auf Befehl "Transfers ausführen" alle offenen `#NB:`-Markierungen durch und entfernt die Markierung im Quell-Notizblock.

---

## Wann Notizblock nutzen?

- Schnelle Gedanken ohne passenden Kontext
- Dinge die nicht in Kalender, Aufgaben oder Datenbank gehören
- Zwischen-Speicher für Transkript-Passagen
- Spontane Einfälle, Links, Zitate

**Nicht für:**
- Terminierte Aufgaben → AUFGABEN.md im persönlichen Assistenten
- Gesundheitsdaten → Gesundheitsassistent
- Steuer/Belege → Büroassistent

---

## CLI-Befehle

```bash
# In Standard-Notizblock schreiben
bach notiz "Meine Notiz"

# In bestimmten Notizblock schreiben
bach notiz "Milch kaufen" --in Einkaufsliste
bach notiz "E=mc²" --in "Physik/Formeln"

# Neuen Notizblock anlegen
bach notiz neu Einkaufsliste               # → user/notizen/Einkaufsliste.txt
bach notiz neu "Physik"                    # → Ordner user/notizen/Physik/
bach notiz neu "Physik/Formeln"            # → user/notizen/Physik/Formeln.txt

# Inhalt anzeigen
bach notiz show                            # Standard-Notizblock
bach notiz show Einkaufsliste
bach notiz show "Physik/Formeln"
bach notiz show --alle                     # Alle Notizbücher

# Transfers ausführen
bach notiz transfer                        # Alle #NB: Markierungen abarbeiten
bach notiz transfer --preview              # Vorschau ohne Ausführung

# Archivieren
bach notiz archiv                          # Notizblock.txt archivieren, neu starten

# Suche
bach notiz suche "Wagner"                  # Volltextsuche in allen Notizbüchern
```

---

## Integration mit anderen BACH-Komponenten

| Komponente | Integration |
|---|---|
| **Transkriptions-Service** | `bach transkript to-notizblock` → überträgt in Notizblock |
| **Persönlicher Assistent** | Schnellnotizen im laufenden Gespräch |
| **Research-Agent** | Recherche-Fragmente und Zitate |
| **Production-Agent** | Content-Ideen, Inspirationen |
| **Decision-Briefing** | Entscheidungs-Kontext und Notizen |

---

## Datenbank

Kein DB-Eintrag nötig — reiner dateibasierter Service ohne Agent-Hierarchie.
Optional: Volltextsuche via FTS5 (`document_fts` Tabelle in `bach.db`).

---

## Status

**Typ:** Service (dateibasiert)
**Version:** 1.1.0
**Erstellt:** 2026-02-18
**Abhängigkeiten:** Keine
