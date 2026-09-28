# Auto Loader — Unity-Catalog-Integration

Quelle: [Using Auto Loader with Unity Catalog](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/unity-catalog).

Auto Loader kann Daten sicher aus External Locations laden, die über Unity Catalog konfiguriert sind. Ab **Databricks Runtime 11.3 LTS** kann Auto Loader sowohl mit Standard- als auch mit Dedicated-Access-Modi verwendet werden (früher "shared" und "single-user"). Directory-Listing-Modus wird standardmäßig unterstützt.

---

## Speicherorte für Auto-Loader-Ressourcen

Das Unity-Catalog-Sicherheitsmodell geht davon aus, dass alle in einem Workload referenzierten Speicherorte von Unity Catalog verwaltet werden. Databricks empfiehlt, Checkpoint- und Schema-Evolution-Informationen stets an von Unity Catalog verwalteten Speicherorten abzulegen.

**Wichtige Einschränkung:** Unity Catalog erlaubt es **nicht**, Checkpoint- oder Schema-Inferenz-/-Evolution-Dateien innerhalb des Tabellenverzeichnisses zu verschachteln. Checkpoint- und Schema-Dateien müssen an einem eigenen, von Unity Catalog verwalteten Speicherort liegen — nicht innerhalb des Tabellenverzeichnisses selbst.

---

## Erforderliche Berechtigungen

Am Beispiel eines Quellpfads `s3://autoloader-source/json-data` und eines Zielbuckets `s3://dev-bucket`:

| Speicherort | Erforderliche Berechtigung |
|---|---|
| Quell-External-Location (z. B. `s3://autoloader-source/json-data`) | `READ FILES` |
| Ziel-Bucket / External Location für Checkpoint (z. B. `s3://dev-bucket`) | `READ FILES`, `WRITE FILES`, `CREATE TABLE` |

Zusätzlich zu diesen Speicherort-Berechtigungen benötigt der ausführende Nutzer **Owner-Rechte auf den Zieltabellen**.

---

## Laden in eine Unity-Catalog-Managed-Table

```python
checkpoint_path = "s3://dev-bucket/_checkpoint/dev_table"
(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", checkpoint_path)
  .load("s3://autoloader-source/json-data")
  .writeStream
  .option("checkpointLocation", checkpoint_path)
  .trigger(availableNow=True)
  .toTable("dev_catalog.dev_database.dev_table"))
```

```sql
CREATE OR REFRESH STREAMING TABLE dev_catalog.dev_database.dev_table
AS SELECT * FROM STREAM read_files(
  's3://autoloader-source/json-data',
  format => 'json');
```

Wird `read_files` innerhalb einer `CREATE STREAMING TABLE`-Anweisung in Lakeflow-Pipelines verwendet, werden Checkpoint- und Schema-Speicherorte automatisch verwaltet.

---

## Laden in eine Unity-Catalog-External-Table

Um Daten an einem bestimmten Speicherort zu belassen, wird statt einer Managed Table eine Unity-Catalog-External-Table verwendet. Der Tabellen-Speicherort muss innerhalb einer External Location liegen, für die `CREATE EXTERNAL TABLE`-Berechtigungen bestehen; der Checkpoint-Speicherort muss ebenfalls in einer von Unity Catalog verwalteten External Location liegen.

```python
checkpoint_path = "s3://dev-bucket/_checkpoint/dev_table"
table_path = "s3://dev-bucket/external/dev_table"

# Einmalig: die External Table in UC registrieren
spark.sql(f"""
  CREATE TABLE IF NOT EXISTS dev_catalog.dev_database.dev_table
  USING DELTA
  LOCATION '{table_path}'
""")

(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", checkpoint_path)
  .load("s3://autoloader-source/json-data")
  .writeStream
  .option("checkpointLocation", checkpoint_path)
  .trigger(availableNow=True)
  .toTable("dev_catalog.dev_database.dev_table"))
```

---

## File Notification Mode mit Unity Catalog

Sind File Events auf der External Location aktiviert, die die betreffenden Dateien enthält, müssen beim Einrichten des Auto-Loader-Streams keine zusätzlichen Berechtigungen angegeben werden. Migriert man von einer External Location oder einem DBFS-Mount zu einem Unity-Catalog-Volume, bleiben die Exactly-once-Garantien von Auto Loader erhalten. Details in [06 File Notification Mode.md](06%20File%20Notification%20Mode.md) und [07 Wie File Events funktionieren.md](07%20Wie%20File%20Events%20funktionieren.md).
