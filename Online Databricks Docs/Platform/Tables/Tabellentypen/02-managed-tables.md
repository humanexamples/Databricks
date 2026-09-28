# Unity Catalog Managed Tables für Delta Lake und Apache Iceberg

Managed Tables sind der Standard-Tabellentyp in Databricks für Delta Lake und Apache Iceberg. Databricks übernimmt Lesen, Schreiben, Speicherung und Optimierung vollständig.

## Vorteile von Managed Tables

- Geringere Speicher- und Rechenkosten
- Schnellere Abfrageleistung über alle Client-Typen hinweg
- Automatische Tabellenwartung und Optimierung
- Sicherer Zugriff für externe Clients über offene APIs
- Unterstützung für Delta Lake und Apache Iceberg
- Automatische Upgrades auf neue Plattform-Funktionen

## Besondere Funktionen von Managed Tables

| Funktion | Nutzen | Konfiguration |
| --- | --- | --- |
| Catalog Commits | Ermöglicht Multi-Statement-Transaktionen, schnellere Query-Planung, erzwingbare Schema-Änderungen, sichere Schreibvorgänge von externen Engines | Standardmäßig aus; wird über `delta.feature.catalogManaged` gesetzt |
| Predictive Optimization | Optimiert automatisch das Datenlayout mit KI; führt `OPTIMIZE`, `VACUUM`, `ANALYZE` aus | Für neue Konten seit 11. November 2024 standardmäßig aktiv |
| Multi-Statement-Transaktionen | Mehrere SQL-Anweisungen als atomaren Commit mit ACID-Garantien ausführen | Standardmäßig aus; Nutzung über `BEGIN ATOMIC...END;` oder `BEGIN TRANSACTION...COMMIT;` |
| Automatisches Liquid Clustering | Wählt Clustering-Schlüssel intelligent aus; passt sich an Abfragemuster an | Standardmäßig aus |
| Metadaten-Caching | Caching von Transaktions-Metadaten im Arbeitsspeicher | Standardmäßig aktiv; nicht konfigurierbar |
| Volltextsuche-Indizes | Beschleunigt Substring- und Schlüsselwort-Suchen über die Funktionen `search` und `isearch` | Beta; erfordert Runtime 18.2 oder höher; standardmäßig aus |
| Automatisches Löschen von Dateien nach DROP | Löscht Datendateien nach einer Wiederherstellungsfrist (Standard 7 Tage) | Standardmäßig aktiv; konfigurierbar auf Katalog- oder Schema-Ebene |

## Zugriff von externen Systemen

Managed Tables unterstützen Interoperabilität über zwei Wege:

- **Unity REST API**: Lese-, Schreib- und Erstellungszugriff für Delta-Lake-Clients
- **Iceberg REST Catalog (IRC)**: Lese- und Schreibzugriff für Apache-Iceberg-Clients

Beide Wege unterstützen Credential Vending. Dabei werden temporäre, eingeschränkte Zugangsdaten ausgestellt, die die Rechte des anfragenden Databricks-Prinzipals übernehmen. Unterstützte externe Engines sind zum Beispiel Trino, DuckDB, Apache Spark, Daft sowie weitere Iceberg-REST-Catalog-integrierte Engines wie Dremio.

## Eine Managed Table erstellen

Für das Erstellen einer Managed Table sind folgende Berechtigungen nötig:

- `USE SCHEMA` auf dem übergeordneten Schema
- `USE CATALOG` auf dem übergeordneten Katalog
- `CREATE TABLE` auf dem übergeordneten Schema

SQL: Managed Delta-Tabelle erstellen

```sql
%sql
CREATE TABLE <catalog-name>.<schema-name>.<table-name>(
  <column-specification>
);
```

SQL: Managed Iceberg-Tabelle erstellen

```sql
%sql
CREATE TABLE <catalog-name>.<schema-name>.<table-name>(
  <column-specification>
)
USING iceberg;
```

Python: mit `saveAsTable()`

```python
from pyspark.sql.types import StructType, StructField, StringType
schema = StructType([StructField("<column-name>", StringType())])
spark.createDataFrame([], schema).write \
  .saveAsTable("<catalog-name>.<schema-name>.<table-name>")
```

Python: mit der DeltaTableBuilder API

```python
from delta.tables import DeltaTable
DeltaTable.create(spark) \
  .tableName("<catalog-name>.<schema-name>.<table-name>") \
  .addColumn("<column-name>", "<data-type>") \
  .property("<key>", "<value>") \
  .execute()
```

Python: Managed Iceberg-Tabelle erstellen

```python
from pyspark.sql.types import StructType, StructField, StringType
schema = StructType([StructField("<column-name>", StringType())])
spark.createDataFrame([], schema).write \
  .format("iceberg") \
  .saveAsTable("<catalog-name>.<schema-name>.<table-name>")
```

Wichtiger Hinweis: Für eine Apache-Iceberg-Tabelle muss `USING iceberg` explizit angegeben werden. Sonst erstellt Databricks standardmäßig eine Delta-Lake-Tabelle.

## Eine Managed Table löschen

Für das Löschen einer Managed Table sind folgende Berechtigungen nötig:

- `MANAGE` auf der Tabelle oder Eigentümerschaft der Tabelle
- `USE SCHEMA` auf dem übergeordneten Schema
- `USE CATALOG` auf dem übergeordneten Katalog

SQL

```sql
%sql
DROP TABLE IF EXISTS catalog_name.schema_name.table_name;
```

Python

```python
spark.sql("DROP TABLE IF EXISTS catalog_name.schema_name.table_name")
```

Alternative ab Runtime 18.2

```python
spark.catalog.dropTable("catalog_name.schema_name.table_name", ifExists=True)
```

## Wiederherstellungsfrist konfigurieren (Public Preview)

Die Wiederherstellungsfrist reicht von 0 Stunden (deaktiviert) bis 7–30 Tage. Der Standard ist 7 Tage. Einstellungen auf Schema-Ebene überschreiben Einstellungen auf Katalog-Ebene.

SQL: Wiederherstellungsfrist setzen

```sql
%sql
ALTER CATALOG my_catalog RETAIN DROPPED TO 30 DAYS;
ALTER SCHEMA my_catalog.my_schema RETAIN DROPPED TO 7 DAYS;
```

Python-Äquivalent

```python
spark.sql("ALTER CATALOG my_catalog RETAIN DROPPED TO 30 DAYS")
spark.sql("ALTER SCHEMA my_catalog.my_schema RETAIN DROPPED TO 7 DAYS")
```

Mit Wiederherstellungsfrist neu anlegen

```sql
%sql
CREATE CATALOG my_catalog RETAIN DROPPED FOR 30 DAYS;
CREATE SCHEMA my_catalog.my_schema RETAIN DROPPED FOR 7 DAYS;
```

Wiederherstellungsfrist prüfen

```sql
%sql
DESCRIBE CATALOG EXTENDED my_catalog;
DESCRIBE SCHEMA EXTENDED my_catalog.my_schema;
```

```python
spark.sql("DESCRIBE CATALOG EXTENDED my_catalog").show()
spark.sql("DESCRIBE SCHEMA EXTENDED my_catalog.my_schema").show()
```

## Weitere Hinweise

- Pfadbasierter Zugriff auf Unity Catalog Managed Tables wird nicht unterstützt, außer im Compatibility Mode.
- Databricks führt regelmäßig Optimierungsvorgänge auf Iceberg-Tabellen mit Serverless Compute aus.

