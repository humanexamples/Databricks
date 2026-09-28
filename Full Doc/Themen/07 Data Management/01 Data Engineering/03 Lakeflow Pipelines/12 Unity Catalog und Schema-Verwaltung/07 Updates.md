# Pipeline-Updates ausführen

Ein Pipeline-Update startet einen Cluster, validiert den Quellcode und aktualisiert die in der Pipeline definierten Tabellen und Views. Dieses Dokument beschreibt Auslöser, Refresh-Semantik, selektive Updates, Dry Runs sowie das Ausführungsverhalten je nach Auslöser. Jede Aussage wurde per `WebFetch` gegen `docs.databricks.com/aws/en/ldp/updates` verifiziert; spezifische Zahlenwerte (Retention, Cluster-Wiederverwendungsdauer) wurden zusätzlich über die Azure-Spiegelseite `learn.microsoft.com/en-us/azure/databricks/ldp/updates` wörtlich gegengeprüft.

## Abschnittsübersicht

1. [Was ist ein Pipeline-Update?](#was-ist-ein-update)
2. [Wie werden Updates ausgelöst?](#ausloeser)
3. [Manuelles Auslösen](#manuell)
4. [Refresh-Semantik](#refresh-semantik)
5. [Update für ausgewählte Tabellen](#selektiv)
6. [Update für fehlgeschlagene Tabellen](#fehlgeschlagen)
7. [Selektiver Checkpoint-Reset](#checkpoint-reset)
8. [Fehlerprüfung ohne Tabellen-Update (Dry Run)](#dry-run)
9. [Verfügbarkeit von Update-Ergebnissen](#verfuegbarkeit)
10. [Ausführungsverhalten je nach Auslöser](#ausfuehrungsverhalten)
11. [Quellen](#quellen)

---

## <a id="was-ist-ein-update">1. Was ist ein Pipeline-Update?</a>

Ein Update führt folgende Schritte aus:

- Startet einen Cluster mit der korrekten Konfiguration.
- Ermittelt alle definierten Tabellen und Views und prüft auf Analysefehler wie ungültige Spaltennamen, fehlende Abhängigkeiten und Syntaxfehler.
- Erstellt oder aktualisiert Tabellen und Views mit den aktuellsten verfügbaren Daten.

Ein **Dry Run** erlaubt, Probleme im Pipeline-Quellcode zu prüfen, ohne auf das Erstellen/Aktualisieren von Tabellen zu warten (siehe Abschnitt 8).

---

## <a id="ausloeser">2. Wie werden Updates ausgelöst?</a>

| Auslöser | Details |
|---|---|
| Manuell | Über den Lakeflow Pipelines Editor oder die Pipelines-Liste. |
| Geplant (Scheduled) | Über Jobs, mittels Pipeline-Task. |
| Programmatisch | Über Drittanbieter-Tools, APIs und CLIs. |

---

## <a id="manuell">3. Manuelles Auslösen</a>

Möglichkeiten:

- Die gesamte Pipeline oder einen Teil (eine einzelne Quelldatei oder eine einzelne Tabelle) aus dem Lakeflow Pipelines Editor ausführen.
- Die gesamte Pipeline aus der **Jobs & Pipelines**-Liste über den Play-Button ausführen.
- Über die Pipeline-Monitoring-Seite den Start-Button klicken.

**Standardverhalten:** Ein manuell ausgelöstes Update aktualisiert standardmäßig alle in der Pipeline definierten Datasets.

---

## <a id="refresh-semantik">4. Refresh-Semantik</a>

| Update-Typ | Materialized View | Streaming Table |
|---|---|---|
| Refresh (Standard) | Aktualisiert Ergebnisse, um die aktuellen Ergebnisse der definierenden Abfrage widerzuspiegeln. Databricks prüft die Kosten und führt ein inkrementelles Refresh durch, wenn dies effizienter ist. | Verarbeitet neue Datensätze durch die in Streaming Tables und Flows definierte Logik. |
| Full Refresh | Berechnet Ergebnisse vollständig neu, um die aktuellen Ergebnisse der definierenden Abfrage widerzuspiegeln. | Löscht Daten aus Streaming Tables, löscht Checkpoints aus Flows und verarbeitet alle Datensätze aus der Datenquelle neu. |
| Reset Streaming Flow Checkpoints | Nicht anwendbar auf Materialized Views. | Löscht Checkpoints aus Flows, aber nicht die Daten aus Streaming Tables, und verarbeitet dann alle Datensätze aus der Datenquelle neu. |

Standardmäßig werden bei jedem Update alle Materialized Views und Streaming Tables einer Pipeline aktualisiert. Über zwei Funktionen lassen sich Tabellen optional von Updates ausschließen: **Select tables for refresh** und **Refresh failed tables** (siehe Abschnitte 5 und 6). Beide unterstützen sowohl Standard-Refresh-Semantik als auch Full Refresh.

### Wann ein Full Refresh sinnvoll ist

Databricks empfiehlt, Full Refreshes nur bei Bedarf durchzuführen. Ein Full Refresh verarbeitet stets alle Datensätze der angegebenen Datenquellen neu; Dauer und Ressourcenbedarf korrelieren mit der Größe der Quelldaten. Materialized Views liefern unabhängig von Standard- oder Full-Refresh dieselben Ergebnisse. Ein Full Refresh von Streaming Tables setzt die gesamte State- und Checkpoint-Verarbeitung zurück und kann zu verlorenen Datensätzen führen, falls Eingabedaten nicht mehr verfügbar sind.

Databricks empfiehlt Full Refresh nur, wenn die Eingabe-Datenquellen die Daten enthalten, die zur Wiederherstellung des gewünschten Zustands der Tabelle/View nötig sind:

| Datenquelle | Grund für fehlende Eingabedaten | Ergebnis eines Full Refresh |
|---|---|---|
| Kafka | Kurze Retention-Frist | Nicht mehr in Kafka vorhandene Datensätze werden aus der Zieltabelle entfernt. |
| Dateien im Objektspeicher | Lifecycle-Richtlinie | Nicht mehr im Quellverzeichnis vorhandene Dateien werden aus der Zieltabelle entfernt. |
| Datensätze in einer Tabelle | Aus Compliance-Gründen gelöscht | Nur noch in der Quelltabelle vorhandene Datensätze werden verarbeitet. |

Um Full Refreshes für eine Tabelle/View zu verhindern, kann die Tabellen-Property `pipelines.reset.allowed` auf `false` gesetzt werden (siehe `Properties.md`). Alternativ lässt sich ein Append Flow nutzen, um Daten an eine bestehende Streaming Table anzuhängen, ohne einen Full Refresh zu benötigen.

---

## <a id="selektiv">5. Update für ausgewählte Tabellen</a>

Daten lassen sich optional nur für ausgewählte Tabellen einer Pipeline neu verarbeiten — etwa während der Entwicklung, wenn nur eine einzelne Tabelle geändert wurde. Der Lakeflow Pipelines Editor bietet Optionen zum erneuten Verarbeiten einer Quelldatei, ausgewählter Tabellen oder einer einzelnen Tabelle.

---

## <a id="fehlgeschlagen">6. Update für fehlgeschlagene Tabellen</a>

Schlägt ein Pipeline-Update wegen Fehlern in einer oder mehreren Tabellen fehl, lässt sich ein Update ausschließlich für die fehlgeschlagenen Tabellen und alle nachgelagerten Abhängigkeiten starten. Nicht ausgewählte Tabellen werden dabei nicht aktualisiert, selbst wenn sie von einer fehlgeschlagenen Tabelle abhängen.

Auf der Pipeline-Monitoring-Seite lässt sich dazu **Refresh failed tables** klicken. Für eine feinere Auswahl: Über den Pfeil neben diesem Button **Select tables for refresh** öffnen, gewünschte Tabellen auswählen (Klick markiert/entfernt sie) und **Refresh selection** klicken. Über den Pfeil neben **Refresh selection** lässt sich zusätzlich **Full Refresh selection** wählen, um die Daten der ausgewählten Tabellen erneut zu verarbeiten.

---

## <a id="checkpoint-reset">7. Selektiver Checkpoint-Reset</a>

Für ausgewählte Streaming Flows lässt sich ein Update starten, das Daten erneut verarbeitet, ohne bereits eingelesene Daten zu löschen. Nicht ausgewählte Flows laufen dabei mit einem regulären REFRESH-Update.

Der Reset erfolgt über den `updates`-Request der Lakeflow-Pipelines-REST-API mit dem Parameter `reset_checkpoint_selection`, der eine Liste von Flow-Namen entgegennimmt. Jeder Flow-Name muss vollständig qualifiziert im Format `catalog.schema.flow_name` übergeben werden — die Verwendung nur des einfachen Namens (z. B. `my_flow` statt `my_catalog.my_schema.my_flow`) führt zum Fehlschlagen des Updates mit einer `IllegalArgumentException`.

- Wurde ein Flow mit explizitem Namen definiert (z. B. über den `flow_name`-Parameter bei `create_auto_cdc_flow`), lautet der vollständig qualifizierte Flow-Name `<catalog>.<schema>.<flow_name>`.
- Wurde kein expliziter Flow-Name gesetzt, ist der Standard-Flow-Name der vollständig qualifizierte Zieltabellenname im Format `catalog.schema.table`.

Flow-Namen finden sich in der Pipeline-UI oder in den Pipeline-Event-Logs.

```bash
curl -X POST \
-H "Authorization: Bearer <your-token>" \
-H "Content-Type: application/json" \
-d '{
"reset_checkpoint_selection": ["my_catalog.my_schema.my_streaming_table"]
}' \
https://<your-databricks-instance>/api/2.0/pipelines/<your-pipeline-id>/updates
```

Beispiel für einen Flow mit explizit vergebenem Namen:

```bash
curl -X POST \
-H "Authorization: Bearer <your-token>" \
-H "Content-Type: application/json" \
-d '{
"reset_checkpoint_selection": ["my_catalog.my_schema.my_custom_flow_name"]
}' \
https://<your-databricks-instance>/api/2.0/pipelines/<your-pipeline-id>/updates
```

---

## <a id="dry-run">8. Fehlerprüfung ohne Tabellen-Update (Dry Run)</a>

**Wichtig:** Die Dry-Run-Funktion befindet sich in der Public Preview.

Ein Dry Run löst die Definitionen der in der Pipeline definierten Datasets und Flows auf, materialisiert oder veröffentlicht dabei aber keine Datasets. Während des Dry Runs gefundene Fehler (z. B. falsche Tabellen- oder Spaltennamen) werden in der UI gemeldet.

Gestartet wird ein Dry Run über den Pfeil neben **Start** auf der Pipeline-Detailseite, dann **Dry run**. Nach Abschluss werden Fehler und Incrementalization Insights im Event-Tray im unteren Bereich angezeigt; das Event Log zeigt dabei ausschließlich Ereignisse, die sich auf den Dry Run beziehen, und im Pipeline-Graph werden keine Metriken angezeigt. Dry-Run-Ergebnisse sind in der UI nur sichtbar, solange der Dry Run das jüngste Update der Pipeline ist.

---

## <a id="verfuegbarkeit">9. Verfügbarkeit von Update-Ergebnissen</a>

Ob die Ergebnisse eines Updates in der UI erscheinen, hängt vom Update-Typ und zwei Bedingungen ab:

- **Retention-Fenster:** Wie lange abgeschlossene Updates aufbewahrt werden — Pipelines behalten **60 Tage** vergangener Updates.
- **Jüngstes Update:** Ob es sich um das zuletzt gestartete Update der Pipeline handelt.

| Update-Typ | Verfügbar in der UI solange | Wird aus der UI entfernt, wenn |
|---|---|---|
| Reguläres Update | Es innerhalb des Retention-Fensters liegt oder noch aktiv ist (nicht abgeschlossen). Ein aktives Update bleibt verfügbar, auch wenn es vor dem Retention-Fenster gestartet wurde. | Es abgeschlossen und älter als das Retention-Fenster ist. |
| Dry Run | Es das jüngste Update der Pipeline ist. | Ein späteres Update startet — egal ob ein weiterer Dry Run oder ein reguläres Update. |

In allen Fällen bleiben die Ereignisse eines Updates im Event Log erhalten, auch nachdem die Ergebnisse nicht mehr in der UI angezeigt werden.

---

## <a id="ausfuehrungsverhalten">10. Ausführungsverhalten je nach Auslöser</a>

Das Verhalten eines Pipeline-Updates hängt davon ab, wie es ausgelöst wurde:

- Über die Pipeline-Monitoring-UI mit **Run now** ausgelöste Updates nutzen ein auf schnellen Start und Debugging ausgerichtetes Verhalten (**Fast-start, debugging-focused behavior**).
- Über Jobs, die Pipelines-API oder kontinuierliche Pipelines ausgelöste Updates nutzen ein Verhalten mit automatischen Retries und Neustarts (**Automatic retry and restart behavior**).

Bei getriggerten Pipelines lässt sich das Standardverhalten für einen einzelnen Lauf über **Run now with different settings** im Dropdown überschreiben.

### Fast-Start, Debugging-fokussiertes Verhalten

Gilt für UI-„Run now" und Ad-hoc-Updates. Diese Läufe optimieren auf schnelle Iteration:

- Ein Cluster wird wiederverwendet, um den Overhead von Neustarts zu vermeiden. Standardmäßig laufen Cluster **zwei Stunden**; änderbar über die Einstellung `pipelines.clusterShutdown.delay`.
- Pipeline-Retries werden deaktiviert, damit Fehler sofort erkannt und behoben werden können.

### Automatische Retry- und Restart-Verhalten

Gilt für Jobs, API-ausgelöste Updates und kontinuierliche Pipelines. Diese Läufe priorisieren Zuverlässigkeit und Kosteneffizienz:

- Der Cluster wird bei bestimmten behebbaren Fehlern neu gestartet, u. a. Memory Leaks und abgelaufene Credentials.
- Bei bestimmten Fehlern (z. B. fehlgeschlagener Cluster-Start) wird die Ausführung erneut versucht.
- Der Cluster wird unmittelbar nach Abschluss des Laufs heruntergefahren.

**Hinweis:** Das Ausführungsverhalten steuert ausschließlich Cluster- und Pipeline-Ausführung. Speicherorte und Zielschemas im Katalog für die Veröffentlichung von Tabellen werden als Teil der Pipeline-Einstellungen konfiguriert und sind vom Ausführungsverhalten nicht betroffen.

---

## <a id="quellen">11. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/updates
- https://learn.microsoft.com/en-us/azure/databricks/ldp/updates (Gegenprüfung: 60-Tage-Retention, 2-Stunden-Cluster-Wiederverwendung)

**Stand:** 2026-08-19
