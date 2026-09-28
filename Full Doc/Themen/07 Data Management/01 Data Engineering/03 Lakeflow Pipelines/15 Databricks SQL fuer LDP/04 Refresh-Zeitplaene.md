# Refresh-Zeitpläne für Standalone Pipelines

Dieses Dokument beschreibt die verschiedenen Wege, Refreshes für Standalone Materialized Views und Streaming Tables zu planen: manuell, `TRIGGER ON UPDATE`, `SCHEDULE`, sowie über einen SQL-Task in einem Job. Der vollständige Seiteninhalt (Azure-Spiegelseite) konnte wörtlich abgerufen werden.

## Abschnittsübersicht

1. [Übersicht der Zeitplan-Methoden](#uebersicht)
2. [Manueller Refresh](#manuell)
3. [`TRIGGER ON UPDATE`](#trigger)
4. [`SCHEDULE` (zeitbasiert)](#schedule)
5. [SQL-Task in einem Job](#sql-task)
6. [Zeitplan zu bestehender Pipeline hinzufügen/ändern/entfernen](#alter)
7. [Refresh-Status verfolgen](#status)
8. [Aktiven Refresh stoppen](#stoppen)
9. [Lauf-Historie einsehen](#historie)
10. [Timeouts](#timeouts)
11. [Benachrichtigungen (Beta)](#benachrichtigungen)
12. [Performance-Modus (Beta)](#performance-modus)
13. [Quellen](#quellen)

---

## <a id="uebersicht">1. Übersicht der Zeitplan-Methoden</a>

| Methode | Beschreibung | Beispiel-Anwendungsfall |
|---|---|---|
| Manuell | On-Demand-Refresh per SQL-`REFRESH`-Anweisung oder über die Workspace-UI | Entwicklung, Tests, Ad-hoc-Updates |
| `TRIGGER ON UPDATE` | Automatischer Refresh der Pipeline, sobald sich Upstream-Daten ändern | Produktions-Workloads mit Frische-SLAs oder unvorhersehbaren Refresh-Zeiträumen |
| `SCHEDULE` | Refresh der Pipeline in festen Zeitintervallen | Vorhersehbare, zeitbasierte Refresh-Anforderungen |
| SQL-Task in einem Job | Orchestrierung über Lakeflow Jobs | Komplexe Pipelines mit systemübergreifenden Abhängigkeiten |

Auch bei bestehendem Zeitplan lässt sich jederzeit ein manueller Refresh ausführen, wenn aktuelle Daten benötigt werden.

## <a id="manuell">2. Manueller Refresh</a>

### Per `REFRESH`-Anweisung

```sql
REFRESH MATERIALIZED VIEW <table-name>;
```

Für Streaming Tables wird `REFRESH STREAMING TABLE` verwendet.

### Per Workspace-UI

Unter "Jobs & Pipelines" die gewünschte Pipeline auswählen und auf "Start" klicken.

## <a id="trigger">3. `TRIGGER ON UPDATE`</a>

Die `TRIGGER ON UPDATE`-Klausel refresht eine Pipeline automatisch, sobald sich die Upstream-Quelldaten ändern — dadurch entfällt die Notwendigkeit, Zeitpläne über mehrere Pipelines hinweg zu koordinieren. Dies ist der empfohlene Ansatz für Produktions-Workloads, insbesondere wenn Upstream-Abhängigkeiten nicht nach vorhersehbaren Zeitplänen laufen. Nach der Konfiguration überwacht die Pipeline ihre Quelltabellen und refresht automatisch, sobald Änderungen in einer der Upstream-Quellen erkannt werden.

**Einschränkungen (wörtlich bestätigt):**

- Abhängigkeits-Obergrenze: Eine Pipeline kann maximal **10 Upstream-Tabellen und 30 Upstream-Views** überwachen. Für mehr Abhängigkeiten muss die Logik auf mehrere Pipelines aufgeteilt werden.
- Workspace-Obergrenze: Maximal **1.000 Pipelines mit `TRIGGER ON UPDATE`** können pro Workspace existieren. Bei Bedarf für mehr ist der Databricks-Support zu kontaktieren.
- Minimales Intervall: Das minimale Trigger-Intervall beträgt **1 Minute**.

```sql
CREATE OR REFRESH STREAMING TABLE catalog.schema.customer_orders
  TRIGGER ON UPDATE
AS SELECT
    o.customer_id,
    o.name,
    o.order_id
FROM catalog.schema.orders o;
```

### Refresh-Frequenz drosseln mit `AT MOST EVERY`

Nützlich, wenn Quelldaten häufig aktualisiert werden, nachgelagerte Konsumenten aber keine Echtzeitdaten benötigen. Das Schlüsselwort `INTERVAL` ist vor dem Zeitwert erforderlich.

```sql
CREATE OR REFRESH STREAMING TABLE catalog.schema.customer_orders
  TRIGGER ON UPDATE AT MOST EVERY INTERVAL 5 MINUTES
AS SELECT
    o.customer_id,
    o.name,
    o.order_id
FROM catalog.schema.orders o;
```

## <a id="schedule">4. `SCHEDULE` (zeitbasiert)</a>

Refresh-Zeitpläne lassen sich direkt in der Pipeline-Definition festlegen, um die View in festen Zeitabständen zu aktualisieren — sinnvoll, wenn die Aktualisierungskadenz der Daten bekannt und vorhersehbar ist. Auch bei bestehendem Zeitplan lässt sich weiterhin manuell refreshen.

Databricks unterstützt zwei Syntaxformen: `SCHEDULE EVERY` für einfache Intervalle und `SCHEDULE CRON` für präzise Zeitplanung. Die Schlüsselwörter `SCHEDULE` und `SCHEDULE REFRESH` sind semantisch äquivalent. Beim Anlegen eines Zeitplans wird automatisch ein neuer Databricks-Job zur Verarbeitung des Updates eingerichtet.

### `SCHEDULE EVERY` (Stunden-, Tages-, Wochenintervalle)

```sql
CREATE OR REPLACE MATERIALIZED VIEW catalog.schema.hourly_metrics
  SCHEDULE EVERY 1 HOUR
AS SELECT
    date_trunc('hour', event_time) AS hour,
    count(*) AS events
FROM catalog.schema.raw_events
GROUP BY 1;
```

Für sub-stündliche Intervalle muss stattdessen `SCHEDULE CRON` verwendet werden.

### `SCHEDULE CRON`

```sql
CREATE OR REPLACE MATERIALIZED VIEW catalog.schema.regular_metrics
  SCHEDULE CRON '0 */15 * * * ?' AT TIME ZONE 'UTC'
AS SELECT
    date_trunc('minute', event_time) AS minute,
    count(*) AS events
FROM catalog.schema.raw_events
WHERE event_time > current_timestamp() - INTERVAL 1 HOUR
GROUP BY 1;
```

Dieses Beispiel plant einen Refresh alle 15 Minuten, jeweils zur Viertelstunde in der UTC-Zeitzone.

Den Zeitplan einsehen: per `DESCRIBE EXTENDED`-Anweisung im SQL-Editor, oder über den Catalog Explorer (Tab "Overview", Bereich "Refresh status").

## <a id="sql-task">5. SQL-Task in einem Job</a>

Pipeline-Refreshes lassen sich über Lakeflow Jobs orchestrieren, indem SQL-Tasks mit `REFRESH`-Befehlen erstellt werden. Zwei Wege:

- **Über den SQL-Editor:** `REFRESH`-Befehl schreiben und über den "Schedule"-Button direkt aus der Query heraus einen Job erstellen.
- **Über die Jobs-UI:** neuen Job anlegen, SQL-Task-Typ hinzufügen und eine SQL-Query oder ein Notebook mit dem `REFRESH`-Befehl anhängen.

```sql
REFRESH STREAMING TABLE catalog.schema.sales;
```

**Hinweis laut Doku:** Bei Standalone Materialized Views und Streaming Tables führt die Orchestrierung eines Refreshs über einen Job **nicht** zu kontinuierlicher Ausführung — jeder Job-Lauf führt einen einzelnen, getriggerten Refresh aus. Kontinuierliche Ausführung über einen Job gilt ausschließlich für vollständige Lakeflow-Pipelines.

Dieser Ansatz eignet sich, wenn komplexe mehrstufige Pipelines systemübergreifende Abhängigkeiten haben, eine Integration in bestehende Job-Orchestrierung benötigt wird, oder Job-Level-Alerting/Monitoring erforderlich ist. SQL-Tasks nutzen sowohl das dem Job zugeordnete SQL-Warehouse als auch die Serverless Compute, die den Refresh ausführt.

## <a id="alter">6. Zeitplan zu bestehender Pipeline hinzufügen/ändern/entfernen</a>

### Hinzufügen

```sql
-- Ändert den Zeitplan so, dass die Streaming Table refresht wird,
-- sobald ihre Upstream-Daten aktualisiert werden.
ALTER STREAMING TABLE sales
  ADD TRIGGER ON UPDATE;
```

### Ändern

Für sub-stündliche Zeitpläne muss eine `CRON`-Expression verwendet werden, da die `EVERY`-Klausel keine Minutenintervalle unterstützt:

```sql
ALTER STREAMING TABLE catalog.schema.my_table
  ALTER SCHEDULE CRON '0 */5 * * * ?';
```

### Entfernen

```sql
ALTER STREAMING TABLE catalog.schema.my_table
  DROP SCHEDULE;
```

Dieser system-verwaltete Job selbst lässt sich nicht direkt bearbeiten — Änderungen erfolgen ausschließlich über `CREATE OR REFRESH` oder `ALTER` an der Pipeline-Definition.

## <a id="status">7. Refresh-Status verfolgen</a>

Über die Pipelines-UI oder die per `DESCRIBE EXTENDED` zurückgegebenen "Refresh Information":

```sql
DESCRIBE TABLE EXTENDED <table-name>;
```

Alternativ über den Catalog Explorer, der u. a. Refresh-Status und -Historie, Tabellenschema, Beispieldaten (bei aktiver Compute), Berechtigungen, Lineage und Nutzungsstatistiken anzeigt.

## <a id="stoppen">8. Aktiven Refresh stoppen</a>

Über die "Pipeline details"-Seite in der UI (Button "Stop"), über die Databricks CLI, oder über den Endpunkt `POST /api/2.0/pipelines/{pipeline_id}/stop` der Pipelines-REST-API.

## <a id="historie">9. Lauf-Historie einsehen</a>

Im Catalog Explorer zeigt der Detailbereich den "Refresh schedule"; ein Klick darauf (z. B. auf "Every 1 hour") führt zur Job-Seite des system-verwalteten Jobs, der den Zeitplan ausführt — inklusive eines Graphen der letzten 48 Stunden an Läufen (Erfolg/Fehlschlag, Dauer).

## <a id="timeouts">10. Timeouts</a>

Pipeline-Refreshes laufen mit einem Timeout, der die maximale Laufzeit begrenzt. Für Standalone Pipelines, die am oder nach dem **14. August 2025** erstellt oder aktualisiert wurden, wird der Timeout beim Update per `CREATE OR REFRESH` festgehalten:

- Ist ein `STATEMENT_TIMEOUT` gesetzt, wird dieser Wert verwendet.
- Andernfalls wird der Timeout des SQL-Warehouses verwendet, das den Befehl ausführt.
- Hat das Warehouse keinen konfigurierten Timeout, gilt ein **Standard von 2 Tagen**.

Der Timeout wird sowohl beim initialen Create als auch bei nachfolgenden geplanten Refreshes verwendet. Für Streaming Tables, die zuletzt vor dem 14. August 2025 aktualisiert wurden, gilt der Timeout fest auf 2 Tage.

```sql
SET STATEMENT_TIMEOUT = '6h';

CREATE OR REFRESH MATERIALIZED VIEW my_catalog.my_schema.my_mv
  SCHEDULE EVERY 12 HOURS
AS SELECT * FROM large_source_table;
```

Dieses Beispiel richtet die Materialized View so ein, dass sie alle 12 Stunden refresht wird; dauert ein Refresh länger als 6 Stunden, läuft er in den Timeout und wartet auf den nächsten geplanten Refresh.

**Timeout-Synchronisation:** Timeouts werden ausschließlich synchronisiert, wenn explizit `CREATE OR REFRESH` ausgeführt wird. Geplante Refreshes verwenden weiterhin den beim letzten `CREATE OR REFRESH` festgehaltenen Timeout; eine alleinige Änderung des Warehouse-Timeouts wirkt sich nicht auf bestehende geplante Refreshes aus. **Wichtig:** Nach Änderung eines Warehouse-Timeouts muss `CREATE OR REFRESH` erneut ausgeführt werden, damit der neue Timeout auf künftige geplante Refreshes angewendet wird.

## <a id="benachrichtigungen">11. Benachrichtigungen (Beta)</a>

**Beta-Hinweis:** Das Feature "Notifications for DDL scheduled refreshes" befindet sich im Beta-Status. Workspace-Admins steuern den Zugriff über die "Previews"-Seite (Opt-in "System-Managed Job for Materialized Views & Streaming Tables").

Je nach Zeitplanungsmethode:

- **Über einen Job geplant:** Benachrichtigungen für den SQL-Task in Lakeflow Jobs werden direkt am Task konfiguriert.
- **Über eine `SCHEDULE`-Klausel geplant:** Bearbeitung im Catalog Explorer (Tab "Overview" → "Refresh schedule" → Bearbeiten-Symbol → "More options" → Benachrichtigungen hinzufügen/ändern).

Benachrichtigung per E-Mail ist bei Start, Erfolg oder Fehlschlag des geplanten Refreshs möglich. Standardmäßig wird der Owner nur bei Fehlschlag benachrichtigt.

## <a id="performance-modus">12. Performance-Modus (Beta)</a>

**Beta-Hinweis:** Das Feature zum Ändern des Performance-Modus für geplante Refreshes befindet sich im Beta-Status (gleicher Opt-in-Mechanismus wie Abschnitt 11).

Bei Ausführung über die UI läuft die Serverless Compute der Pipeline im **Performance-optimierten Modus**. Für über die SQL-Definition geplante Pipelines lässt sich der Performance-Modus über die Einstellung "Performance optimized" im Catalog Explorer wählen. Ist diese Einstellung deaktiviert (Standard), läuft die Pipeline im **Standard-Performance-Modus** — dieser reduziert Kosten für Workloads, bei denen eine etwas höhere Startlatenz akzeptabel ist; Serverless-Workloads im Standardmodus starten laut Doku typischerweise innerhalb von **4 bis 6 Minuten** nach Auslösung, abhängig von Compute-Verfügbarkeit und optimierter Terminplanung.

Ist "Performance optimized" aktiviert, ist die Pipeline auf schnelleren Start und schnellere Ausführung für zeitkritische Workloads optimiert. Beide Modi verwenden dieselbe SKU; der Standardmodus verbraucht jedoch weniger DBUs, entsprechend dem geringeren Compute-Verbrauch.

Standardmäßig verwenden Pipelines: den Performance-optimierten Modus bei interaktiver Ausführung in der UI, die "Performance optimized"-Einstellung des Jobs bei Planung über einen SQL-Task, und den Standardmodus bei Planung über eine `SCHEDULE`-Klausel.

---

## <a id="quellen">13. Quellen</a>

1. Schedule refreshes (AWS): https://docs.databricks.com/aws/en/ldp/dbsql/schedule-refreshes
2. Schedule refreshes (Azure-Spiegelseite, für vollständige wörtliche Wiedergabe inkl. aller Limits genutzt): https://learn.microsoft.com/en-us/azure/databricks/ldp/dbsql/schedule-refreshes
