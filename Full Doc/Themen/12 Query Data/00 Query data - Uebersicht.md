# Query data – Übersicht

> Quelle: <https://docs.databricks.com/aws/en/query>

Das Abfragen von Daten ist der grundlegende Schritt für nahezu alle datengetriebenen Aufgaben in Databricks. Abfragen lassen sich **interaktiv** ausführen (Notebooks, SQL-Editor, Datei-Editor, Dashboards) oder als Teil von **Lakeflow-Pipelines** bzw. **Jobs** einplanen.

---

## Welche Daten kann man mit Databricks abfragen?

Databricks unterscheidet zwei große Kategorien.

### 1. Daten im Databricks-Lakehouse

Lakehouse-Tabellen, die mit einfachen `CREATE TABLE`-Anweisungen erstellt werden, haben folgende Eigenschaften:

- Gespeichert im **Delta-Lake-Format**
- Gespeichert im **Cloud-Objektspeicher**
- Verwaltet durch **Unity Catalog**

**Managed vs. Unmanaged:**

- **Managed Tables** sind für die meisten Anwendungsfälle empfohlen.
- **Unmanaged (External) Tables** verwenden eine `LOCATION`-Angabe.
- Legacy-Workloads greifen ggf. über Dateipfade auf Delta Lake zu, ohne eine Tabelle zu registrieren.

> Delta Lake ist Voraussetzung dafür, dass Daten als Teil des Lakehouse gelten, weil es die Transaktionsgarantien liefert.

### 2. Externe Daten

Beispiele:

- Foreign Tables, die über **Lakehouse Federation** registriert sind
- Hive-Metastore-Tabellen auf Parquet-Basis
- Externe Unity-Catalog-Tabellen auf JSON-Basis
- CSV-Daten im Cloud-Objektspeicher
- Streaming-Daten aus Kafka

---

## Tabellen über den Namen abfragen

**Namenskonvention:**

- Mit Unity Catalog: `<catalog-name>.<schema-name>.<table-name>`
- Ohne Unity Catalog: `<schema-name>.<table-name>`

```sql
SELECT * FROM catalog_name.schema_name.table_name
```

```python
spark.read.table("catalog_name.schema_name.table_name")
```

### Namensauflösung in Unity Catalog

| Bezeichnermuster | Verhalten |
|---|---|
| `catalog_name.schema_name.object_name` | Verweist auf das angegebene Datenbankobjekt |
| `schema_name.object_name` | Objekt im angegebenen Schema des aktuellen Katalogs |
| `object_name` | Objekt im aktuellen Katalog und Schema |

### Aktueller Katalog und aktuelles Schema

In interaktiven Umgebungen lässt sich der aktuelle Kontext mit `current_catalog()` und `current_schema()` prüfen.

| Anweisung | Ergebnis |
|---|---|
| `USE CATALOG catalog_name` | Setzt den aktuellen Katalog; Schema wird auf `default` zurückgesetzt |
| `USE SCHEMA schema_name` | Setzt das Schema im aktuellen Katalog |
| `USE SCHEMA catalog_name.schema_name` | Setzt Katalog und Schema |

---

## Daten über den Pfad abfragen

Databricks empfiehlt **Unity-Catalog-Volumes** für den Zugriff auf Cloud-Objektspeicher.

### Volume-Pfade

```sql
SELECT * FROM json.`/Volumes/catalog_name/schema_name/volume_name/path/to/data`
```

```python
spark.read.format("json").load("/Volumes/catalog_name/schema_name/volume_name/path/to/data")
```

### Direkte URIs (Legacy-Muster)

```sql
SELECT * FROM json.`abfss://container-name@storage-account-name.dfs.core.windows.net/path/to/data`
SELECT * FROM json.`gs://bucket_name/path/to/data`
SELECT * FROM json.`s3://bucket_name/path/to/data`
```

```python
spark.read.format("json").load("abfss://container-name@storage-account-name.dfs.core.windows.net/path/to/data")
spark.read.format("json").load("gs://bucket_name/path/to/data")
spark.read.format("json").load("s3://bucket_name/path/to/data")
```

---

## Daten über SQL-Warehouses abfragen

SQL-Warehouses werden verwendet für:

- SQL-Editor
- Databricks-SQL-Abfragen
- Dashboards
- SQL-Alerts

Optional nutzbar mit: Notebooks, Datei-Editor, Lakeflow Jobs.

**Wichtige Einschränkung:** Nur SQL-Syntax wird unterstützt; andere Sprachen und APIs sind nicht verfügbar.

> Abfragen auf Datendateien sollten Unity-Catalog-Volumes nutzen. URIs direkt in Abfragen auf SQL-Warehouses können zu unerwarteten Fehlern führen.

---

## Daten über All-Purpose- oder Jobs-Compute abfragen

Die meisten Abfragen aus Notebooks, Workflows und dem Datei-Editor laufen auf Databricks-Runtime-Clustern. Für nicht-interaktive Workloads wird **Jobs-Compute** empfohlen.

### Interaktive vs. nicht-interaktive Workloads

Apache Spark nutzt **Lazy Evaluation** – Ergebnisse werden nur bei Bedarf berechnet. Für Produktions-Workloads spart das Entfernen von `display()`-Abfragen Zeit und Kosten, da unnötige Berechnungen entfallen, die niemand manuell prüft.

---

## Verwandte Themen

- [CSV lesen und schreiben](01%20Dateiformate/01%20CSV%20lesen%20und%20schreiben.md)
- [JSON lesen und schreiben](01%20Dateiformate/02%20JSON%20lesen%20und%20schreiben.md)
- [Parquet lesen und schreiben](01%20Dateiformate/03%20Parquet%20lesen%20und%20schreiben.md)
- [JSON-Strings abfragen (semi-strukturiert)](02%20Semi-strukturierte%20Daten/01%20JSON-Strings%20abfragen.md)
