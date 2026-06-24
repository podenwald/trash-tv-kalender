# Trash TV Kalender

Automatisch erzeugter iCal-Kalender für deutsche Trash-TV- und Reality-TV-Termine.

Quelle in Version 1:

- TVMovie Trash-TV-Kalender

## Kalender abonnieren

Sobald GitHub Pages aktiv ist, kannst du diese URL in Google Kalender abonnieren:

```text
https://podenwald.github.io/trash-tv-kalender/calendar.ics
```

Google Kalender:

1. Google Kalender öffnen
2. Links bei „Weitere Kalender“ auf `+` klicken
3. „Per URL“ auswählen
4. URL einfügen
5. Kalender hinzufügen

## GitHub Pages aktivieren

1. Repository öffnen
2. `Settings` öffnen
3. Links `Pages` auswählen
4. Source: `Deploy from a branch`
5. Branch: `main`
6. Folder: `/root`
7. Speichern

## Manuell aktualisieren

1. Repository öffnen
2. Tab `Actions`
3. Workflow `Update Trash TV Calendar` öffnen
4. `Run workflow` klicken

## Technischer Hinweis

TVMovie veröffentlicht die Termine als redaktionellen Artikel. Der Parser ist daher tolerant gebaut:

- konkrete Daten wie `25. Juni 2026` werden als Kalendereinträge übernommen
- wiederkehrende Formulierungen wie `immer dienstags` werden nicht blind als Serie erzeugt
- Dopplungen werden entfernt

So vermeiden wir falsche Termine im Kalender.


## Version 2: Laufende Sendungen

Der Parser erkennt zusätzlich wöchentliche Hinweise wie `immer montags`, `wöchentlich dienstags` oder `ab dem ... immer mittwochs`.
Wenn kein Finale genannt wird, werden standardmäßig die nächsten 12 Wochen erzeugt. Bereits laufende Sendungen werden ab dem heutigen Datum fortgeführt, nicht rückwirkend komplett eingetragen.
