# llm-note

**llm-note** ist ein lokaler Notizkern für LLM-Agenten. Das Modul verbindet ein kleines SQLite-Denkarium mit einfachen Text-Notizbüchern, ohne Cloudkonto, ohne Server und ohne externe Laufzeitabhängigkeiten.

## Funktionen

- Strukturierte Notizen, Logbuch-Einträge, Kategorien, Stimmung und Beförderungsmarker speichern.
- Schnelle Text-Notizbücher mit `#NB:`-Transfermarkierungen führen.
- Notizen per Python oder CLI durchsuchen.
- Brainstorm-Einträge anlegen und später in Aufgaben, Wiki-Seiten oder Issues überführen.
- Nutzertexte in sechs Sprachen bündeln: Deutsch, Englisch, Spanisch, vereinfachtes Chinesisch, Japanisch und Russisch.

## Schnellstart

```bash
pip install -e .
llm-note --locale de write "Öffentliche README prüfen" --cat release
llm-note --locale de search README
```

## Datenschutz

llm-note sendet selbst keine Daten ins Netz. Datenbanken und Notizordner bleiben lokale Dateien und sind in `.gitignore` ausgeschlossen.

## Lizenz

[MIT](LICENSE) - Copyright 2026 Lukas Geiger
