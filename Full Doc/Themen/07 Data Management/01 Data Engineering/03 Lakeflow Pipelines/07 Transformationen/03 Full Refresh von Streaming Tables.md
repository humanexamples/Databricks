# Full Refresh für Streaming Tables — Referenz

Dieses Dokument beschreibt, was ein Full Refresh einer Streaming Table in Lakeflow-Declarative-Pipelines (LDP) bewirkt, wann er nötig ist, welche Auswirkungen er auf Datenquellen hat, und welche Best Practices dabei gelten. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/full-refresh-st`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte.

## Abschnittsübersicht

1. [Grundprinzip](#grundprinzip)
2. [Auswirkung auf Datenquellen](#auswirkung-quellen)
3. [Wann ein Full Refresh nötig ist](#wann-noetig)
4. [Limitierungen](#limitierungen)
5. [Best Practices](#best-practices)
6. [Quellen](#quellen)

---

## <a id="grundprinzip">1. Grundprinzip</a>

Ein Full Refresh einer Streaming Table verwirft alle bestehenden Daten und Metadaten und startet den Stream von vorne. Konkret: Die Streaming Table wird geleert, alle Checkpoint-Daten werden entfernt, und der Streaming-Prozess wird mit neuen Checkpoints für jeden in die Tabelle schreibenden Flow neu gestartet.

## <a id="auswirkung-quellen">2. Auswirkung auf Datenquellen</a>

Ein Full Refresh entfernt alle bestehenden Daten aus der Streaming Table. Hat die Datenquelle Retention-Limits (etwa Kafka-Topics mit kurzer Retention-Periode), können manche historischen Daten nach einem Full Refresh unwiederbringlich verloren sein.

Beispiel: Ist die Quelle Kafka mit 24-Stunden-Retention und wird nach diesem Zeitfenster ein Full Refresh durchgeführt, sind ältere Nachrichten nicht mehr verfügbar und können nicht erneut verarbeitet werden.

**Hinweis:** Full Refreshes werden nicht empfohlen für hochvolumige Streaming-Workloads oder wenn die Upstream-Retention das Replaying historischer Daten verhindert.

Hat die Streaming Table nachgelagerte abhängige Tabellen, schlägt die Pipeline fehl, bis auch diese Tabellen vollständig refresht wurden — sofern die Streaming Table nicht `skipChangeCommits` aktiviert hat. Nachgelagerte Materialized Views müssen ebenfalls vollständig refresht werden.

## <a id="wann-noetig">3. Wann ein Full Refresh nötig ist</a>

Full Refreshes müssen explizit ausgelöst werden — über **Full Refresh** in der Pipeline-UI oder durch Aktivierung von Auto Full Refresh in Lakeflow Connect.

Ein Full Refresh wird empfohlen, wenn Änderungen ein sicheres Fortsetzen einer Streaming Query vom bestehenden Checkpoint verhindern, oder wenn zuvor verarbeitete Daten mit aktualisierter Logik, Schema oder Quellkonfiguration inkonsistent würden.

### Schema-Änderungen

Folgende Schema-Änderungen an der Zieltabelle sind **nicht** rückwärtskompatibel und erfordern einen Full Refresh:

- Umbenennen von Spalten ohne aktivierten Column-Mapping-Modus.
- Ändern von Deduplizierungsspalten.
- Ändern von Spaltendatentypen, einschließlich:
  - Typverengung (z. B. `BIGINT → INT` oder `DOUBLE → FLOAT`).
  - Inkompatible Typänderungen (z. B. `STRING → INT`).
- Hartes Löschen von Spalten aus dem Tabellenschema.

Für solche Schema-Änderungen empfiehlt Databricks, eine neue Spalte mit dem gewünschten Schema bzw. Namen anzulegen und eine View über der Streaming Table zu erstellen, die alte und neue Werte per `UNION` zusammenführt.

### Änderungen am physischen Daten-Layout

Folgende Änderungen am physischen Daten-Layout erfordern einen Full Refresh:

- Migration von Legacy-Partitionierung zu einem neuen Clustering-Schema.

### Upstream-Quelländerungen

Folgende Upstream-Quelländerungen erfordern einen Full Refresh:

- Ändern der von der Streaming Query gelesenen Quelltabellen.
- Wechsel zwischen Quelltypen (z. B. Kafka zu Delta oder Auto Loader zu Kafka).
- Ändern von Quellspeicherorten, etwa Tabellenpfaden oder Kafka-Topic-Subscriptions.
- Droppen und Neuanlegen einer Quell-Delta-Tabelle, selbst wenn das Schema unverändert bleibt.

### Änderungen an zustandsbehafteter Verarbeitung

Folgende Änderungen an zustandsbehafteter Verarbeitung erfordern einen Full Refresh:

- Ändern von Aggregations-Gruppierungsschlüsseln oder Aggregatfunktionen.
- Hinzufügen oder Entfernen von Aggregationen.
- Ändern von Join-Keys oder Join-Typen.
- Hinzufügen oder Entfernen von Joins.
- Ändern von Deduplizierungsspalten oder -logik.

### Datenkontinuitätsprobleme

Ein Full Refresh kann nötig sein, wenn die Datenkontinuität beeinträchtigt ist:

- CDC-Logs sind wegen abgelaufener Retention nicht mehr verfügbar.
- Beschädigung oder Löschung des Streaming-Checkpoint-Verzeichnisses.
- Beschädigung oder Verlust von Schema-Tracking- oder Schema-Speicherort-Dateien.

## <a id="limitierungen">4. Limitierungen</a>

- Ein Full Refresh verarbeitet keine Daten erneut, sofern die Quelle nicht den vollständigen historischen Datensatz vorhält.
- Große Datasets können Full Refreshes kostenintensiv und zeitaufwändig machen.
- Nachgelagerte Konsumenten, die von der Tabelle abhängen, können fehlschlagen oder unvollständige Ergebnisse liefern, bis der Refresh abgeschlossen ist.

## <a id="best-practices">5. Best Practices</a>

| Situation | Best Practice |
|---|---|
| Auf Stabilität hin designen | Das Schema so planen, dass Änderungen vermieden werden, die einen Full Refresh erfordern. Spalten hinzufügen ist im Allgemeinen sicher, während das Ändern bestehender Spalten oder Partitionierungsschemata typischerweise eine Neuberechnung der Tabelle erfordert. |
| Aus Quellen mit kurzer Retention-Periode streamen | Streaming aus Quellen wie einem Kafka-Topic ohne lange Retention-Periode bedeutet, dass ein Full Refresh Daten verliert, die nicht mehr in der Quelle vorhanden sind. Um historischen Datenverlust zu vermeiden: Rohdaten in eine Streaming Table streamen (eine Bronze-Tabelle in der Medallion-Architektur). Flexible Spaltentypen (z. B. `variant` oder `string`) verwenden, damit diese Tabelle bei Änderungen an Upstream-Daten keinen Full Refresh benötigt. Diese Tabelle kann historische Daten speichern und von nachgelagerten Streaming Tables genutzt werden (die strengere Typen oder andere strukturelle Änderungen haben können) — benötigen die nachgelagerten Tabellen einen Full Refresh, verfügt diese Tabelle weiterhin über die historischen Daten, ohne selbst einen Full Refresh zu benötigen. |
| Alternativen vor einem Full Refresh erwägen | Alternativen: Bei Änderung der Quelle eines Flows eher einen neuen Flow anlegen statt den bestehenden Flow einer Streaming Table zu aktualisieren — das bewahrt die bestehenden Daten in der Tabelle, kann aber doppelte Daten schreiben, da der neue Flow einen neuen Checkpoint hat. Alternativ lässt sich der Checkpoint zurücksetzen, was aber ebenfalls zu doppelt geschriebenen Daten in der Zieltabelle führen kann. Ist keine der beiden Optionen akzeptabel, kann eine neue Streaming Table angelegt und über eine View mit der alten Streaming Table per `UNION` zusammengeführt werden. |
| Wenn ein Full Refresh nötig ist | Folgende Best Practices befolgen, wenn ein Full Refresh *tatsächlich* nötig ist: die Operation in einer Entwicklungs- oder Staging-Umgebung testen; betroffene nachgelagerte Abhängigkeiten dokumentieren; den Refresh während eines Wartungsfensters planen, um Auswirkungen auf Produktions-Workloads zu minimieren; sicherstellen, dass das Quellsystem genug historische Daten für das Replaying des Streams vorhält. |

Um Daten nach einem Full Refresh nachträglich einzuspielen, lässt sich ein `append once`-Flow anlegen (siehe `Backfill mit Flows.md` in `06 Flows`) — dieser führt einen einmaligen Backfill durch, ohne nach dem ersten Backfill weiterzulaufen. Der Code bleibt in der Pipeline; wird die Pipeline jemals erneut vollständig refresht, läuft der Backfill erneut.

---

## <a id="quellen">6. Quellen</a>

- Full refresh for streaming tables (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/ldp/full-refresh-st
- Full refresh for streaming tables (AWS): https://docs.databricks.com/aws/en/ldp/full-refresh-st

**Stand:** 2026-08-19.
