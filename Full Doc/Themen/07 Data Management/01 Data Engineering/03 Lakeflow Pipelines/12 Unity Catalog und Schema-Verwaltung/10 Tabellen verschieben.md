# Tabellen zwischen Pipelines verschieben

Dieses Dokument beschreibt, wie sich Streaming Tables und Materialized Views von einer Lakeflow-Pipeline in eine andere verschieben lassen — ohne Full Refresh und ohne Datenverlust. Jede Aussage wurde per `WebFetch` gegen `docs.databricks.com/aws/en/ldp/move-table` verifiziert.

## Abschnittsübersicht

1. [Anwendungsfälle](#anwendungsfaelle)
2. [Voraussetzungen](#voraussetzungen)
3. [Schritt-für-Schritt-Ablauf](#ablauf)
4. [Troubleshooting](#troubleshooting)
5. [Beispiel mit mehreren Tabellen](#beispiel)
6. [Einschränkungen](#einschraenkungen)
7. [Quellen](#quellen)

---

## <a id="anwendungsfaelle">1. Anwendungsfälle</a>

Die Doku nennt folgende praktische Szenarien für das Verschieben von Tabellen:

- Aufteilen großer Pipelines in besser handhabbare Einheiten.
- Konsolidierung separater Pipelines zu einer größeren Einheit.
- Anpassung von Refresh-Zeitplänen für einzelne Tabellen.
- Übergang von Tabellen aus älteren Publishing-Methoden zu aktuellen Standards.
- Verschieben von Tabellen über verschiedene Workspace-Umgebungen hinweg.

---

## <a id="voraussetzungen">2. Voraussetzungen</a>

**Mindest-Runtime-Versionen:**

- Databricks Runtime 16.3 oder höher für die Ausführung des `ALTER`-Befehls.
- Version 17.2 speziell für Verschiebungen über Workspace-Grenzen hinweg.

**Metastore-Anforderungen:** Beide beteiligten Pipelines müssen sich in Workspaces befinden, die sich einen Metastore teilen. Dies lässt sich mit der Funktion `current_metastore` prüfen.

**Berechtigungs- und Eigentümer-Anforderungen:**

- Der ausführende Nutzer bzw. das Service Principal muss der Run-As-User für beide Pipelines sein.
- Sowohl Quell- als auch Ziel-Pipeline müssen dem ausführenden Nutzer gehören.

**Publishing-Mode-Anforderungen:** Die Ziel-Pipeline sollte im Default Publishing Mode arbeiten (der es erlaubt, Tabellen in mehrere Kataloge und Schemas zu veröffentlichen). Alternativ können beide Pipelines im Legacy Publishing Mode arbeiten, sofern sie identische `catalog`- und `target`-Einstellungen teilen.

**Kritische Einschränkung:** Dieses Feature unterstützt **nicht** das Verschieben einer Pipeline im Default Publishing Mode zu einer Pipeline im Legacy Publishing Mode.

---

## <a id="ablauf">3. Schritt-für-Schritt-Ablauf</a>

### Schritt 1: Quell-Pipeline anhalten

Eine aktive Quell-Pipeline stoppen und vollständig beenden lassen.

### Schritt 2: Tabellendefinition entfernen

Den Definitionscode der Tabelle aus dem Notebook bzw. den Dateien der Quell-Pipeline entfernen. Abhängige Abfragen oder unterstützender Code, der für die Pipeline-Funktionalität nötig bleibt, werden dabei erhalten.

### Schritt 3: ALTER-Befehl ausführen

Folgender SQL-Befehl wird aus einem Notebook oder SQL-Editor im Workspace der Quell-Pipeline ausgeführt:

```sql
ALTER [MATERIALIZED VIEW | STREAMING TABLE | TABLE] <table-name>
SET TBLPROPERTIES("pipelines.pipelineId"="<destination-pipeline-id>");
```

- `ALTER MATERIALIZED VIEW` für Unity-Catalog-Materialized-Views.
- `ALTER STREAMING TABLE` für Unity-Catalog-Streaming-Tables.
- `ALTER TABLE` für Hive-Metastore-Tabellen.
- Die `pipelineId` muss gültig sein; der Wert `null` ist nicht erlaubt.

Beispiel:

```sql
ALTER STREAMING TABLE sales
SET TBLPROPERTIES("pipelines.pipelineId"="abcd1234-ef56-ab78-cd90-1234efab5678");
```

### Schritt 4: Tabelle zur Ziel-Pipeline hinzufügen

Die Tabellendefinition wird in den Code der Ziel-Pipeline eingefügt.

**Wichtige Hinweise:**

- Unterscheiden sich Katalog- oder Schema-Einstellungen, kann eine exakte Code-Übernahme fehlschlagen, da „partiell qualifizierte Tabellen in der Definition unterschiedlich aufgelöst werden können". Tabellennamen sollten bei Bedarf vollständig qualifiziert werden.
- Append-once-Flows sollten entfernt oder auskommentiert werden, um eine erneute Ausführung zu vermeiden.

---

## <a id="troubleshooting">4. Troubleshooting</a>

| Fehler | Erklärung |
|---|---|
| `DESTINATION_PIPELINE_NOT_IN_DIRECT_PUBLISHING_MODE` | Die Quelle nutzt den Default Mode, das Ziel den Legacy-LIVE-Schema-Modus. Diese Kombination wird nicht unterstützt. |
| `PIPELINE_TYPE_NOT_WORKSPACE_PIPELINE_TYPE` | Nur Workspace-Pipelines können verschoben werden; eigenständige Tabellen sind ausgeschlossen. |
| `DESTINATION_PIPELINE_NOT_FOUND` | Die `pipelineId` ist ungültig oder `null`. |
| Tabelle aktualisiert sich nach dem Verschieben nicht im Ziel | Schnelle Wiederherstellung durch Rückgängigmachen des Vorgangs (Rückverschiebung zur Quelle). |
| `PIPELINE_PERMISSION_DENIED_NOT_OWNER` | Beide Pipelines müssen dem ausführenden Nutzer gehören. |
| `TABLE_ALREADY_EXISTS` | Die Backing-Tabelle existiert bereits; die kollidierende Tabelle muss per `DROP` entfernt werden. |

---

## <a id="beispiel">5. Beispiel mit mehreren Tabellen</a>

Die Doku demonstriert das Verschieben einer einzelnen Tabelle (`table_b`) aus einer Pipeline mit drei Tabellen.

**Ursprünglicher Quell-Pipeline-Code:**

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col

@dp.table
def table_a():
    return spark.read.table("source_table")

@dp.table
def table_b():
    return (
        spark.read.table("table_a")
        .select(col("column1"), col("column2"))
    )

@dp.table
def table_c():
    return (
        spark.read.table("table_b")
        .groupBy(col("column1"))
        .agg(sum("column2").alias("sum_column2"))
    )
```

**Angepasster Quell-Pipeline-Code (table_b entfernt):**

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col

@dp.table
def table_a():
    return spark.read.table("source_table")

# Removed, to be in new pipeline:
# @dp.table
# def table_b():
#     return (
#         spark.read.table("table_a")
#         .select(col("column1"), col("column2"))
#     )

@dp.table
def table_c():
    return (
        spark.read.table("table_b")
        .groupBy(col("column1"))
        .agg(sum("column2").alias("sum_column2"))
    )
```

**ALTER-Befehl:**

```sql
ALTER MATERIALIZED VIEW table_b
SET TBLPROPERTIES("pipelines.pipelineId"="<new-pipeline-id>");
```

**Ziel-Pipeline-Code (einfache Variante):**

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col

@dp.table(name="table_b")
def table_b():
    return (
        spark.read.table("table_a")
        .select(col("column1"), col("column2"))
    )
```

**Ziel-Pipeline-Code (Variante mit vollständig qualifizierten Namen):**

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col

@dp.table(name="source_catalog.source_schema.table_b")
def table_b():
    return (
        spark.read.table("source_catalog.source_schema.table_a")
        .select(col("column1"), col("column2"))
    )
```

**Ergebnis:** Nach der Ausführung behandelt die Quell-Pipeline `table_b` als extern; die Ziel-Pipeline übernimmt die Aktualisierung.

---

## <a id="einschraenkungen">6. Einschränkungen</a>

- Eigenständige Materialized Views und Streaming Tables können nicht verschoben werden.
- Append-once-Flows (Python `append_flow(once=True)` und SQL `INSERT INTO ONCE`) werden nicht unterstützt — ihr Status bleibt nicht erhalten und sie können erneut ausgeführt werden.
- Private Tabellen oder Views sind ausgeschlossen.
- Beide Pipelines müssen Workspace-Pipelines sein; `null`-Pipelines sind nicht erlaubt.
- Pipelines müssen im selben Workspace liegen oder in verschiedenen Workspaces, die sich einen Metastore teilen.
- Die Eigentümer-Anforderung gilt für beide beteiligten Pipelines.
- Pipelines im Default Publishing Mode können nicht zu Pipelines im Legacy Mode verschoben werden.
- Bei Legacy-Mode-Pipelines müssen Quelle und Ziel übereinstimmende `catalog`- und `target`-Einstellungen haben.

---

## <a id="quellen">7. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/move-table

**Stand:** 2026-08-19
