# ALTER-SQL-Anweisungen mit Pipeline-Datasets nutzen

Dieses Dokument beschreibt, wie `ALTER`-SQL-Anweisungen mit von Lakeflow Declarative Pipelines erzeugten Datasets (Streaming Tables, Materialized Views) zusammenspielen — insbesondere den zentralen Konflikt zwischen manuellen `ALTER`-Änderungen und der erneuten Ausführung der Pipeline-Definition bei jedem Update. Jede Aussage wurde per `WebFetch` gegen `docs.databricks.com/aws/en/ldp/using-alter-sql` verifiziert.

## Abschnittsübersicht

1. [Einordnung](#einordnung)
2. [Unterstützte ALTER-Operationen](#unterstuetzte-operationen)
3. [Zentrale Einschränkung: Pipeline überschreibt ALTER-Änderungen](#zentrale-einschraenkung)
4. [Lösungsstrategie](#loesung)
5. [Nicht unterstützte Änderungen](#nicht-unterstuetzt)
6. [Quellen](#quellen)

---

## <a id="einordnung">1. Einordnung</a>

Lakeflow Pipelines erlauben, Pipelines mit SQL- oder Python-Code zu definieren, typischerweise im Lakeflow Pipelines Editor verfasst. Während Databricks SQL primär für die eigenständige Pipeline-Erstellung außerhalb von Lakeflow dient, unterstützt es das Ändern von Dataset-Eigenschaften über alle Pipeline-Typen hinweg mittels `ALTER`-Anweisungen.

---

## <a id="unterstuetzte-operationen">2. Unterstützte ALTER-Operationen</a>

Zwei zentrale `ALTER`-Anweisungen ändern von Pipelines erzeugte Datasets:

1. **Streaming Tables:** `ALTER STREAMING TABLE` ändert Eigenschaften einer Streaming Table.
2. **Materialized Views:** `ALTER MATERIALIZED VIEW` ändert Eigenschaften einer Materialized View.

Diese Befehle funktionieren über Datasets hinweg, die durch Lakeflow Pipelines, Lakeflow-Connect-Ingestion-Pipelines oder eigenständige Databricks-SQL-Pipelines erzeugt wurden.

Für Datasets eigenständiger Pipelines erlaubt zusätzlich die `SET OWNER TO`-Klausel einen Eigentümerwechsel.

---

## <a id="zentrale-einschraenkung">3. Zentrale Einschränkung: Pipeline überschreibt ALTER-Änderungen</a>

Eine grundlegende Einschränkung: Der SQL-Code, der eine Tabelle oder View in einer Pipeline definiert, wird bei jedem Update erneut ausgeführt. Das kann Änderungen, die per `ALTER`-Anweisung vorgenommen wurden, wieder rückgängig machen.

### Konkretes Beispiel

Enthält eine Materialized-View-Definition eine Maskierung:

```sql
CREATE OR REPLACE MATERIALIZED VIEW masked_view (
    id int,
    name string,
    region string,
    ssn string MASK catalog.schema.ssn_mask_fn
)
WITH ROW FILTER catalog.schema.us_filter_fn ON (region)
AS SELECT id, name, region, ssn
       FROM employees;
```

Wird die Maske per `ALTER` entfernt:

```sql
ALTER MATERIALIZED VIEW masked_view ALTER COLUMN ssn DROP MASK;
```

wird die Entfernung beim nächsten Refresh der Materialized View rückgängig gemacht, da die ursprüngliche Definition die Maskierungsfunktion erneut anwendet.

---

## <a id="loesung">4. Lösungsstrategie</a>

Änderungen erfordern zunächst eine Anpassung der SQL-Definition der Pipeline, erst danach die Ausführung der entsprechenden `ALTER`-Anweisung. Bei Lakeflow-Pipelines erfolgt die Anpassung des Quellcodes über den Pipeline-Editor; bei eigenständigen Pipelines wird der SQL-Code in einer beliebigen Databricks-SQL-Umgebung aktualisiert und ausgeführt.

---

## <a id="nicht-unterstuetzt">5. Nicht unterstützte Änderungen</a>

Zeitplan (Schedule) oder Trigger eines in Lakeflow Pipelines definierten Datasets können **nicht** per `ALTER`-Anweisung geändert werden.

---

## <a id="quellen">6. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/using-alter-sql

**Stand:** 2026-08-19
