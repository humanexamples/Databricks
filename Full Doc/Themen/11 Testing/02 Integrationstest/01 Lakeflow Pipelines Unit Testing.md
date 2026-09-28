# Lakeflow Pipelines Unit Testing

Das Beta-Testing-Framework für Lakeflow Declarative Pipelines: isolierte Test-Ausführung über eine Test-SparkSession mit Tabellen-Umleitung, Mock-Daten-Erstellung, Auto-CDC-Tests und vollständige Beispiele. Teil der [Testing](../Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Kernfähigkeiten](#kernfaehigkeiten)
3. [Wann Unit Testing einsetzen](#wann)
4. [Voraussetzungen](#voraussetzungen)
5. [Kritische Isolationsgrenzen](#isolation)
6. [Nicht unterstützte Governance-Operationen](#governance)
7. [Operative und Autoring-Einschränkungen](#einschraenkungen)
8. [Implementierungsschritte](#implementierung)
9. [Testing-APIs](#apis)
10. [Mock-Daten erstellen](#mock-daten)
11. [Ausführliches Beispiel: Aggregations-Testing](#aggregation-beispiel)
12. [Auto-CDC-Testing](#auto-cdc)
13. [Joins- und Expectations-Testing](#joins-expectations)
14. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick</a>

Databricks bietet ein Testing-Framework für Lakeflow Declarative Pipelines, das die Validierung von Transformationslogik mit Mock-Daten ermöglicht. Das Feature befindet sich in **Beta** und ist ausschließlich über den webbasierten Lakeflow Pipelines Editor verfügbar.

## <a id="kernfaehigkeiten">2. Kernfähigkeiten</a>

1. **Isolierte Test-Ausführung:** „Das Framework stellt eine SparkSession bereit, die Tabellenoperationen in ein temporäres Test-Schema umleitet" — verhindert Auswirkungen auf Produktionsdaten.
2. **Flexibler Test-Umfang:** einzelne Tabellen, abhängige Tabellenketten oder ganze Pipelines auf dem Pipeline-Compute über die Test-SparkSession ausführen.
3. **Ergebnisvalidierung:** Standard-pytest-Assertions verifizieren Ergebnisse aus isolierten Ausgabetabellen.

## <a id="wann">3. Wann Unit Testing einsetzen</a>

- Validierung neuer Transformationslogik vor dem Produktions-Deployment.
- Testen von Auto-CDC-Spezifikationen mit Mock-Change-Events.
- Verifikation von Expectations und Datenqualitätsregeln.
- Testen von Ketten abhängiger Transformationen (Bronze → Silver → Gold-Muster).

## <a id="voraussetzungen">4. Voraussetzungen</a>

**Berechtigungen und Konfiguration:**

- Pipeline-**Owner**-Berechtigung sowie `USE CATALOG`- und `CREATE SCHEMA`-Rechte auf dem Default-Catalog.
- **Triggered** (nicht kontinuierlicher) Pipeline-Modus.
- Pipeline muss auf dem **PREVIEW**-Channel laufen.
- Spark Connect wird nicht unterstützt.

**Berechtigungsprüfung:** Owner-Status im **Share**-Dialog der Pipeline bestätigen. Für Catalog-Rechte im Catalog Explorer den Tab **Permissions** prüfen. Fehlende Rechte gewähren mit:

```sql
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG <catalog_name> TO `<principal>`;
```

## <a id="isolation">5. Kritische Isolationsgrenzen</a>

### Nur Tabellennamen-Umleitung

Test-Isolation gilt ausschließlich für Operationen, die Tabellen namentlich referenzieren. Folgende Operationen umgehen die Isolation:

- **Pfad-basierte Reads/Writes:** `spark.read.load("/Volumes/...")`, `dbfs:/`-Pfade oder Cloud-Storage-Pfade (`s3://`, `abfss://`).
- **Connector-Operationen:** Kafka-Reads von Produktions-Brokern; Auto-Loader-Reads von tatsächlichem Cloud-Storage.
- **`event_log()`-Funktion:** „Die table-valued Function `event_log()` nicht in einem Pipeline-Unit-Test verwenden" — sie liefert Produktionsdaten statt Test-Event-Logs. Stattdessen den `event_log_table_name` aus dem Run-Status nutzen und über `test_spark` abfragen.

## <a id="governance">6. Nicht unterstützte Governance-Operationen</a>

Folgende Operationen erreichen Produktionssysteme und müssen vermieden werden: `GRANT`, `REVOKE`, `ALTER ... OWNER TO`; `SET`/`UNSET TAGS`; `CREATE`/`DROP POLICY`; `CREATE`/`DROP CATALOG` bzw. `CREATE`/`DROP SCHEMA`.

## <a id="einschraenkungen">7. Operative und Autoring-Einschränkungen</a>

**Operative Einschränkungen:**

- **Keine nebenläufige Ausführung:** Tests parallel zu laufenden Pipeline-Updates auszuführen wird nicht unterstützt.
- **Temporäre-Schema-Bereinigung:** abnormal beendete Runs können `redirecting_<id>`-Schemas hinterlassen, die manuell gelöscht werden müssen.
- **Compute-Abrechnung:** Testläufe verbrauchen Pipeline-Compute und werden standardmäßig abgerechnet.
- **Nur selektiver Refresh:** Full Refresh ist nicht verfügbar.

**Autoring-Einschränkungen:**

- Tests müssen in Python geschrieben werden (SQL-Pipelines lassen sich dennoch testen).
- Ausführung ist auf den webbasierten Editor beschränkt.
- Mock-Daten erben keine Row Filters oder Column Masks von Produktionstabellen.

## <a id="implementierung">8. Implementierungsschritte</a>

### Schritt 1 — Pipeline-Einstellungen konfigurieren

**UI:** Settings → Advanced settings → Channel → Preview, dann Pipeline-Modus auf Triggered setzen.

**JSON:**

```json
"continuous": false,
"channel": "PREVIEW"
```

### Schritt 2 — Testdatei erstellen

Im Lakeflow Pipelines Editor auf **+** klicken und **Test** wählen, um eine Testdatei im automatisch generierten `tests`-Ordner zu erstellen (nicht Teil der Pipeline-Quelle).

### Schritt 3 — Tests generieren oder schreiben

Genie Codes „Generate tests"-Button für Scaffolding nutzen, oder erforderliche Imports manuell hinzufügen:

```python
import pytest
from pyspark.pipelines.testing import TestPipeline, test_spark

test_pipeline = TestPipeline.active()
```

### Schritt 4 — Tests ausführen

Im Editor über das Play-Icon neben einzelnen Testfunktionen ausführen, oder „Run tests in file" für alle Tests einer Datei nutzen. Ergebnisse erscheinen im unteren Panel.

## <a id="apis">9. Testing-APIs</a>

| API | Beschreibung |
|---|---|
| `TestPipeline.active()` | gibt das `TestPipeline`-Objekt der aktuell bearbeiteten Pipeline zurück |
| `test_pipeline.run(test_spark, set([table_names]))` | führt selektiven Refresh der angegebenen Tabellen aus (bzw. aller, wenn leere Menge) |
| `test_spark`-Fixture | liefert eine SparkSession mit namensbasierter Tabellen-Umleitung in ein temporäres Test-Schema |

## <a id="mock-daten">10. Mock-Daten erstellen</a>

### SQL-basierte Mock-Daten

```python
test_spark.sql("""
    CREATE TABLE catalog.schema.table_name AS
    SELECT * FROM VALUES
        (1, 'value1'),
        (2, 'value2')
    AS t(id, name)
""")
```

### DataFrame-basierte Mock-Daten

```python
df = test_spark.createDataFrame(
    [(1, 'value1'), (2, 'value2')],
    schema=["id", "name"])
df.write.saveAsTable("catalog.schema.table_name")
```

### Synthetische Daten mit Faker

Zuerst `%pip install faker` in der Pipeline ausführen:

```python
from pyspark.sql import functions as F
from faker import Faker

fake = Faker()
fake_firstname = F.udf(fake.first_name)
fake_lastname = F.udf(fake.last_name)
fake_email = F.udf(fake.ascii_company_email)

df = (
    test_spark.range(0, 100)
    .withColumn("firstname", fake_firstname())
    .withColumn("lastname", fake_lastname())
    .withColumn("email", fake_email()))
df.write.saveAsTable("catalog.schema.table_name")
```

## <a id="aggregation-beispiel">11. Ausführliches Beispiel: Aggregations-Testing</a>

Zeilenanzahl-, Schema- und Null-Behandlungs-Validierung:

```python
import pytest
from pyspark.pipelines.testing import TestPipeline, test_spark
from pyspark.testing import assertDataFrameEqual

test_pipeline = TestPipeline.active()

def mock_users(session):
    session.sql("""
        CREATE TABLE catalog.schema.wanderbricks_users AS
        SELECT * FROM VALUES
            (1, 'alice@example.com', 'Alice', 'admin'),
            (2, NULL, 'Bob', 'user'),
            (3, 'charlie@example.com', 'Charlie', 'user'),
            (4, NULL, 'Dana', 'admin')
        AS t(user_id, email, name, user_type)
    """)

def test_users_row_count(test_spark):
    mock_users(test_spark)
    test_pipeline.run(test_spark, set(["catalog.schema.users"]))
    result = test_spark.table("catalog.schema.users")
    assert result.count() == 4

def test_users_schema(test_spark):
    mock_users(test_spark)
    test_pipeline.run(test_spark, set(["catalog.schema.users"]))
    result = test_spark.table("catalog.schema.users")
    expected_fields = {"user_id", "email", "name", "user_type"}
    actual_fields = set(f.name for f in result.schema.fields)
    assert expected_fields == actual_fields

def test_users_null_handling(test_spark):
    mock_users(test_spark)
    test_pipeline.run(test_spark, set(["catalog.schema.users"]))
    result = test_spark.table("catalog.schema.users")
    null_emails = result.filter("email IS NULL").count()
    assert null_emails == 2

def test_counts(test_spark):
    mock_users(test_spark)
    test_pipeline.run(test_spark, set(["catalog.schema.users", "catalog.schema.counts"]))
    result = test_spark.table("catalog.schema.counts")
    admin_row = result.filter("user_type = 'admin'").collect()[0]
    user_row = result.filter("user_type = 'user'").collect()[0]
    assert admin_row["total_count"] == 2
    assert admin_row["count_valid_emails"] == 1
    assert user_row["total_count"] == 2
    assert user_row["count_valid_emails"] == 1

def test_counts_full_dataframe(test_spark):
    mock_users(test_spark)
    test_pipeline.run(test_spark, set(["catalog.schema.users", "catalog.schema.counts"]))
    result = test_spark.table("catalog.schema.counts")
    expected = test_spark.createDataFrame(
        [("admin", 2, 1), ("user", 2, 1)],
        schema=["user_type", "total_count", "count_valid_emails"]
    )
    assertDataFrameEqual(result, expected)
```

## <a id="auto-cdc">12. Auto-CDC-Testing</a>

### Standard-CDC-Flow-Test

```python
def test_auto_cdc_flow(test_spark):
    test_spark.sql("""
        CREATE TABLE catalog.schema.change_feed AS
        SELECT * FROM VALUES
            (1, 'Alice', 1000),
            (2, 'Bob', 1001),
            (1, 'Alice Updated', 1002)
        AS t(userId, name, ts)
    """)
    test_pipeline.run(test_spark, set(["catalog.schema.target_autocdc"]))
    result = test_spark.table("catalog.schema.target_autocdc")
    user_ids = set(row["userId"] for row in result.collect())
    assert user_ids == {1, 2}
    latest_user1 = result.filter("userId = 1").collect()[0]
    assert latest_user1["ts"] == 1002
    assert latest_user1["name"] == "Alice Updated"
    user2 = result.filter("userId = 2").collect()[0]
    assert user2["ts"] == 1001
```

### Test für verspätet eintreffende Events

```python
def test_auto_cdc_late_arriving(test_spark):
    test_spark.sql("""
        CREATE TABLE catalog.schema.change_feed AS
        SELECT * FROM VALUES
            (1, 'Alice', 1000),
            (2, 'Bob', 1001)
        AS t(userId, name, ts)
    """)
    test_pipeline.run(test_spark, set(["catalog.schema.target_autocdc"]))
    test_spark.sql("""
        INSERT INTO catalog.schema.change_feed VALUES
            (1, 'Alice Updated', 1003),
            (2, 'Bob (stale)', 999)
    """)
    test_pipeline.run(test_spark, set(["catalog.schema.target_autocdc"]))
    result = test_spark.table("catalog.schema.target_autocdc")
    alice = result.filter("userId = 1").collect()[0]
    assert alice["ts"] == 1003
    assert alice["name"] == "Alice Updated"
    bob = result.filter("userId = 2").collect()[0]
    assert bob["ts"] == 1001
    assert bob["name"] == "Bob"
```

### CDC-aus-Snapshot-Test

```python
def test_auto_cdc_from_snapshot_flow(test_spark):
    test_spark.sql("""
        CREATE TABLE catalog.schema.snapshot AS
        SELECT * FROM VALUES
            (1, 'Alice', '2024-01-01'),
            (2, 'Bob', '2024-01-02')
        AS t(userId, name, created_at)
    """)
    test_pipeline.run(test_spark, set(["catalog.schema.target"]))
    test_spark.sql("TRUNCATE TABLE catalog.schema.snapshot")
    test_spark.sql("INSERT INTO catalog.schema.snapshot VALUES (2, 'Bob', '2024-01-03')")
    test_pipeline.run(test_spark, set(["catalog.schema.target"]))
    result = test_spark.table("catalog.schema.target")
    assert result.count() == 3
    user_ids = [row["userId"] for row in result.collect()]
    assert set(user_ids) == {1, 2}
```

## <a id="joins-expectations">13. Joins- und Expectations-Testing</a>

```python
def mock_properties(session):
    session.sql("""
        CREATE TABLE catalog.schema.property_images AS
        SELECT * FROM VALUES
            (101, 'img1.jpg', '2024-02-01'),
            (102, 'img2.jpg', '2024-01-15'),
            (103, 'img3.jpg', '2024-12-20')
        AS t(property_id, image_url, uploaded_at)
    """)
    session.sql("""
        CREATE TABLE catalog.schema.property_amenities AS
        SELECT * FROM VALUES
            (101, 'wifi'),
            (102, 'pool'),
            (103, 'parking')
        AS t(property_id, amenity)
    """)

def test_property_join(test_spark):
    mock_properties(test_spark)
    test_pipeline.run(test_spark, set(["catalog.schema.property_images_amenities_join"]))
    result = test_spark.table("catalog.schema.property_images_amenities_join")
    assert result.count() == 3
    property_ids = set(row["property_id"] for row in result.collect())
    assert property_ids == {101, 102, 103}

def test_property_expectation(test_spark):
    mock_properties(test_spark)
    test_spark.sql("""
        INSERT INTO catalog.schema.property_images VALUES (104, 'img4.jpg', '2023-12-31')
    """)
    test_spark.sql("""
        INSERT INTO catalog.schema.property_amenities VALUES (104, 'gym')
    """)
    test_pipeline.run(test_spark, set(["catalog.schema.property_images_amenities_join"]))
    result = test_spark.table("catalog.schema.property_images_amenities_join")
    valid_ids = set(row["property_id"] for row in result.collect())
    assert 104 not in valid_ids
    assert valid_ids == {101, 102, 103}
```

## <a id="quelle">14. Quelle</a>

- https://docs.databricks.com/aws/en/ldp/unit-testing

**Stand:** 2026-08-21.
