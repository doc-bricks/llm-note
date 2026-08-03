<img src="assets/banner.svg" width="100%" alt="llm-note banner">

# llm-note

[![CI](https://github.com/doc-bricks/llm-note/actions/workflows/ci.yml/badge.svg)](https://github.com/doc-bricks/llm-note/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/Lizenz-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](pyproject.toml)
[![Tests: 19 Passed](https://img.shields.io/badge/Tests-19%20Bestanden-brightgreen.svg)](tests/)
[![Ecosystem: doc-bricks](https://img.shields.io/badge/Ecosystem-doc--bricks-0055ff.svg)](https://github.com/doc-bricks)
[![Umbrella: open-bricks](https://img.shields.io/badge/Umbrella-open--bricks-blueviolet.svg)](https://github.com/open-bricks)

[Deutsch](README_de.md) · [English](README.md) · [Español](README_es.md) · [简体中文](README_zh-Hans.md) · [日本語](README_ja.md) · [Русский](README_ru.md)

> [!NOTE]
> **Datenschutz & Lokal-Zuerst**: `llm-note` arbeitet vollständig auf lokalen SQLite-Datenbanken und einfachen Textdateien. Es benötigt keine API-Schlüssel, keine Cloud-Server, keinen Vektordatenbank-Overhead und stellt keine ausgehenden Netzwerkverbindungen her. Ideal für datenschutzkonforme KI-Agenten-Workflows.

**llm-note** ist ein lokaler Notizkern für LLM-Agenten. Das Modul verbindet ein kleines SQLite-Denkarium mit einfachen Text-Notizbüchern, ohne Cloudkonto, ohne externen Server und ohne externe Laufzeitabhängigkeiten.

## Systemarchitektur

```mermaid
graph TD
    subgraph Clients["Schnittstellen & Clients"]
        CLI["llm-note CLI"]
        GUI["Lokale Weboberfläche"]
        PyAPI["Python API"]
        Skill["Agenten-Skill (SKILL.md)"]
    end

    subgraph CoreEngine["llm-note Notizkern"]
        NoteStore["NoteStore (SQLite)"]
        FileStore["FileNotebookStore (Text-Datei)"]
        HTTP["http.server (127.0.0.1)"]
        I18N["Lokalisierung (EN/DE/ES/ZH/JA/RU)"]
    end

    subgraph LocalStorage["Lokale Speicher-Ebene"]
        DB[("data/notes.db<br/>(SQLite Denkarium)")]
        Notebooks["notebooks/*.txt<br/>(Text-Notizbücher)"]
        LockFile[".llm-note.lock"]
    end

    CLI --> NoteStore
    GUI --> HTTP
    HTTP --> NoteStore
    CLI --> FileStore
    PyAPI --> NoteStore
    PyAPI --> FileStore
    Skill --> CLI
    Skill --> PyAPI

    NoteStore --> DB
    NoteStore --> I18N
    FileStore --> Notebooks
    FileStore --> LockFile
```

## Einstieg

Nutze llm-note, wenn ein Agent, Coding-Assistent oder lokaler Forschungsworkflow eine kleine, prüfbare Notizschicht braucht:

| Bedarf | llm-note hilft bei |
| --- | --- |
| Agenten-Gedächtnis | Entscheidungen, Beobachtungen und Folge-Marker lokal in SQLite speichern. |
| Notizbuch-Inbox | Textnotizen später prüfen, übertragen oder archivieren. |
| Datenschutz | Ohne gehostete Dienste, Konten, Embeddings oder Hintergrund-Netzwerkzugriffe arbeiten. |
| Skill-Paket | Einen wiederverwendbaren Notiz-Skill neben dem Python-Paket ausliefern. |

## Funktionen

- Strukturierte Notizen, Logbuch-Einträge, Kategorien, Stimmung und Beförderungsmarker speichern.
- Schnelle Text-Notizbücher mit `#NB:`-Transfermarkierungen führen.
- Notizen per Python oder CLI durchsuchen.
- Notizen in einer lokalen Browseroberfläche schreiben, filtern, suchen und lesen.
- Brainstorm-Einträge anlegen und später in Aufgaben, Wiki-Seiten oder Issues überführen.
- Nutzertexte in sechs Sprachen bündeln: Deutsch, Englisch, Spanisch, vereinfachtes Chinesisch, Japanisch und Russisch.

## Schnellstart

```bash
pip install -e .
llm-note --locale de write "Öffentliche README prüfen" --cat release
llm-note --locale de search README
```

## Lokale Weboberfläche

Die Oberfläche verwendet denselben Standard-Datenbankpfad wie die CLI:

```bash
llm-note --locale de gui
```

Der Befehl öffnet `http://127.0.0.1:8000/` im Standardbrowser. Eine andere
Datenbank oder einen anderen Port wählst du so:

```bash
llm-note --db data/notes.db --locale de gui --port 8765
```

Mit `--no-browser` startet nur der Server. Er ist ausschließlich über die
lokale Loopback-Adresse erreichbar und basiert auf `http.server`, gebündeltem
HTML und Systemschriften. Dadurch bleiben die Laufzeitabhängigkeiten auf die
Python-Standardbibliothek beschränkt; es gibt keine ausgehenden Anfragen.

Suchbegriffe werden wörtlich behandelt; `%` und `_` sind keine SQL-Wildcards.
Abfragelimits dürfen zwischen `0` und `1000` liegen. Text-Notizbücher behalten
Unicode-Namen und koordinieren parallele lokale Prozesse über die Datei
`.llm-note.lock` im Notizbuchordner. Offene Transfers erhalten eine
`#LLM-NOTE-ID`, damit ein Retry nach einem Dateifehler den Eintrag nicht
verdoppelt.

## Datenschutz

llm-note sendet selbst keine Daten an externe Dienste. Die optionale Oberfläche
lauscht nur auf `127.0.0.1` und stellt keine ausgehenden Anfragen. Datenbanken
und Notizordner bleiben lokale Dateien und sind in `.gitignore` ausgeschlossen.

## Einordnung

llm-note ist bewusst kleiner als vollständige Wissensdatenbanken wie Obsidian, Joplin, NotebookLM, Vektordatenbanken oder MCP-Notebook-Server. Es ist ein lokales Python-Paket für Agenten-Notizen, CLI-Notizbücher und reproduzierbare Logbücher, die in Git lesbar bleiben und leicht in andere Tools eingebettet werden können.

Passende Suchphrasen sind `local-first LLM notes`, `SQLite note store for agents`, `agent notebook CLI`, `private AI notebook`, `LLM memory logbook` und `BACH Notizblock extraction`.

## Lizenz

[MIT](LICENSE) - Copyright 2026 Lukas Geiger
