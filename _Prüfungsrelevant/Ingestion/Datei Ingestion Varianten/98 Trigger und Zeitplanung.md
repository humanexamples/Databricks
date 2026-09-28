[← Übersicht](00%20Uebersicht.md)

# Trigger und Zeitplanung

| Trigger | Code | Verhalten |
|---|---|---|
| So schnell wie möglich | `.writeStream` ohne `.trigger(...)` | Dauerbetrieb, minimale Latenz |
| Micro-Batch | `.trigger(processingTime="1 minute")` | fester Intervall, Dauerbetrieb |
| Einmal-Batch | `.trigger(availableNow=True)` | alle bis Startzeitpunkt vorhandenen Dateien, dann Stop – ideal für geplante Jobs |
| Streaming Table SQL | `SCHEDULE REFRESH EVERY 1 HOUR` / `SCHEDULE REFRESH CRON '...'` | verwalteter Refresh |
| Job-Zeitplan | `"schedule": { "quartz_cron_expression": "0 0 * * * ?" }` | zeitgesteuerter Joblauf |
| File-Arrival-Trigger | siehe unten | Joblauf bei **neuer** Datei (nicht bei Überschreiben) |

File-Arrival-Trigger (Jobs-Definition):

```json
{
  "trigger": {
    "file_arrival": {
      "url": "/Volumes/catalog/schema/landing/",
      "min_time_between_triggers_seconds": 60,
      "wait_after_last_change_seconds": 15
    }
  }
}
```

Grenzen ohne File-Events: max. 10.000 Dateien im überwachten Pfad, max. 50 Jobs/Workspace, keine Wildcards im Pfad; Prüfintervall ~1 Minute. Mit aktivierten File-Events keine Dateimengen-Grenze.

---
[← Übersicht](00%20Uebersicht.md)
