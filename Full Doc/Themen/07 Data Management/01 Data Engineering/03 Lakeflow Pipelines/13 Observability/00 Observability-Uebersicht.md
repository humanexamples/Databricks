# Pipelines überwachen — Übersicht

Dieses Dokument gibt einen Überblick über die Monitoring-Möglichkeiten von Lakeflow Declarative Pipelines: die eingebaute Pipeline-UI, das Event Log, Query History und benutzerdefinierte Event Hooks. Es dient als Einstiegspunkt für die übrigen Dokumente dieses Themenblocks. Jede Aussage wurde per `WebFetch` gegen `docs.databricks.com/aws/en/ldp/observability` verifiziert.

## Abschnittsübersicht

1. [Die drei Monitoring-Ebenen](#drei-ebenen)
2. [Benachrichtigungen](#benachrichtigungen)
3. [Themenübersicht](#themenuebersicht)
4. [Troubleshooting-Themen](#troubleshooting-themen)
5. [Quellen](#quellen)

---

## <a id="drei-ebenen">1. Die drei Monitoring-Ebenen</a>

Pipeline-Monitoring funktioniert in drei Ebenen — vom schnellen Blick bis zur tiefen programmatischen Abfrage:

- **Die Jobs-&-Pipelines-Liste** ist die schnellste Prüfmöglichkeit. Sie zeigt das Ergebnis der letzten fünf Läufe als Statusanzeigen neben jeder Pipeline, sodass auf einen Blick erkennbar ist, ob aktuelle Läufe erfolgreich waren, fehlgeschlagen sind oder noch laufen.
- **Die Pipeline-Monitoring-UI** zeigt den nach Status eingefärbten Pipeline-Graph, Zeilenanzahlen und Datenqualitätsmetriken je Tabelle, die Update-Historie sowie Streaming-Backlog-Metriken für das ausgewählte Update (siehe `Monitoring-UI.md`).
- **Das Event Log** ist die zugrunde liegende Wahrheitsquelle für beide vorherigen Ebenen. Es handelt sich um eine strukturierte Delta-Tabelle, die für programmatische oder historische Zwecke abgefragt werden kann — etwa Update-Ergebnisse, Datenqualitäts-Trends und Ressourcennutzung (siehe `Event Logs ueberwachen.md`).

---

## <a id="benachrichtigungen">2. Benachrichtigungen</a>

Um auf Pipeline-Ereignisse zu reagieren, lassen sich Benachrichtigungen konfigurieren — entweder direkt an der Pipeline, wenn sie nach eigenem Zeitplan läuft, oder als Job-Benachrichtigungen, wenn die Pipeline innerhalb eines Lakeflow Jobs läuft (siehe `Monitoring-UI.md`, Abschnitt E-Mail-Benachrichtigungen).

---

## <a id="themenuebersicht">3. Themenübersicht</a>

| Thema | Beschreibung |
|---|---|
| Monitoring über die UI | Fortschritt und Status von Pipeline-Updates beobachten und bei Erfolg/Fehlschlag alarmieren. Metriken für Streaming-Quellen wie Apache Kafka und Auto Loader anzeigen. |
| Event Log | Detaillierte Informationen zu Pipeline-Updates extrahieren, z. B. Data Lineage, Datenqualitätsmetriken und Ressourcennutzung, über das Pipeline-Event-Log. Siehe zusätzlich das Schema des Event Logs. |
| Query History | Abfrageperformance über die Query History inspizieren und diagnostizieren. |
| Custom Monitoring | Benutzerdefinierte Aktionen bei bestimmten Ereignissen mittels Event Hooks definieren. |

---

## <a id="troubleshooting-themen">4. Troubleshooting-Themen</a>

Zusätzlich gibt es Troubleshooting-Themen für spezifische Szenarien:

| Thema | Beschreibung |
|---|---|
| Wiederherstellung nach Streaming-Checkpoint-Fehlschlag | Eine Pipeline mit ungültigem oder beschädigtem Streaming-Checkpoint wiederherstellen. |
| Hohe Initialisierungszeiten beheben | Hohe Initialisierungszeiten einer Pipeline durch Aufteilen und Lastverteilung von Flows über mehrere Pipelines beheben. |

---

## <a id="quellen">5. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/observability

**Stand:** 2026-08-19
