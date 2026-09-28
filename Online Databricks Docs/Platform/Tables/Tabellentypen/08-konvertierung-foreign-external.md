# Foreign Table zu einer External UnityCatalog-Table konvertieren

Diese Funktion unterstützt nur die Konvertierung von Foreign Tables, die über HMS Federation oder Glue Federation eingebunden sind.

## Übersicht: SET EXTERNAL

Der Befehl `SET EXTERNAL` konvertiert eine Foreign Table zu einer Unity Catalog External Table. Die wichtigsten Vorteile:

- Die Tabellenhistorie bleibt erhalten.
- Konfigurationen, Name, Einstellungen und Berechtigungen bleiben gleich.

## Voraussetzungen

- **Datenformat:** Delta, Parquet, ORC, Avro, JSON, CSV oder TEXT
- **Tabellentyp:** HMS-basierte externe Tabellen (keine verwalteten Tabellen)
- **Runtime:** Databricks Runtime 17.3 oder höher
- **Berechtigungen:** OWNER oder MANAGE auf der Tabelle, CREATE auf der EXTERNAL LOCATION

Warnung: Gleichzeitige Schreibvorgänge auf die Quelltabelle und aus Unity Catalog heraus werden nicht unterstützt.

## SQL-Syntax

```sql
%sql
ALTER TABLE source_table SET EXTERNAL [DRY RUN]
```

## Parameter

- **source_table:** die vorhandene Foreign Table in Unity Catalog. Nach der Konvertierung beeinflusst ein Löschen der Quelltabelle im externen Katalog die Unity-Catalog-Tabelle nicht mehr.
- **DRY RUN:** prüft die Konvertierbarkeit, ohne echte Änderungen vorzunehmen. Bei Erfolg lautet die Rückgabe `DRY_RUN_SUCCESS`.

## Rückgängig machen

```sql
%sql
DROP TABLE catalog.schema.my_external_table;
```

## Häufige Fragen

### Umgang mit dem SerDe-Format

Für Parquet-SerDe-Tabellen in AWS Glue ist folgender Python-Code nötig, um die Tabellendefinition anzupassen:

```python
import boto3
import json

glue_client = boto3.client('glue', region_name='<your-aws-region>')

DATABASE_NAME = '<your-database-name>'
TABLE_NAME = '<your-table-name>'
SPARK_PROVIDER = 'PARQUET'
SPARK_PARTITION_PROVIDER = 'filesystem'

print(f"Retrieving current table definition for {DATABASE_NAME}.{TABLE_NAME}...")
response = glue_client.get_table(DatabaseName=DATABASE_NAME, Name=TABLE_NAME)

table_definition = response['Table']

serde_library = table_definition['StorageDescriptor']['SerdeInfo'].get('SerializationLibrary', '')
is_parquet_serde = serde_library == "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"

if not is_parquet_serde:
    print(f"The table {TABLE_NAME} does not use a Parquet SerDe. Found: {serde_library}")
else:
    print(f"Table {TABLE_NAME} is using a Parquet SerDe.")
    s3_path = table_definition['StorageDescriptor']['Location']
    print(f"S3 Path found: {s3_path}")

    if 'SerdeInfo' in table_definition['StorageDescriptor']:
        if 'Parameters' not in table_definition['StorageDescriptor']['SerdeInfo']:
            table_definition['StorageDescriptor']['SerdeInfo']['Parameters'] = {}
        table_definition['StorageDescriptor']['SerdeInfo']['Parameters']['path'] = s3_path

    if 'Parameters' not in table_definition:
        table_definition['Parameters'] = {}

    table_definition['Parameters']['spark.sql.sources.provider'] = SPARK_PROVIDER
    table_definition['Parameters']['spark.sql.partitionProvider'] = SPARK_PARTITION_PROVIDER

    table_definition.pop('CreateTime', None)
    table_definition.pop('UpdateTime', None)
    table_definition.pop('LastAccessTime', None)
    table_definition.pop('Retention', None)
    table_definition.pop("DatabaseName", None)
    table_definition.pop('CreatedBy', None)
    table_definition.pop('IsRegisteredWithLakeFormation', None)
    table_definition.pop('CatalogId', None)
    table_definition.pop('VersionId', None)

    print(f"Updating the table {TABLE_NAME} in Glue...")
    response = glue_client.update_table(
        DatabaseName=DATABASE_NAME,
        TableInput=table_definition,
    )
    print(f"Table {TABLE_NAME} updated successfully!")
```

### Konvertierung auf Schema- oder Katalog-Ebene

Um mehrere Tabellen gleichzeitig zu konvertieren, lässt sich folgender Ansatz nutzen:

```python
df = (dx.from_tables("prod.*.*").with_sql("ALTER TABLE {full_table_name} SET EXTERNAL;").apply())
```

## Weiterführende Links

- Foreign Tables über SQL konvertieren
- External oder Foreign Delta-Lake-Tabellen zu Managed Tables konvertieren
- HMS- und Glue-Federation-Dokumentation

---
**Quelle:** https://docs.databricks.com/aws/en/tables/convert-foreign-external  
**Stand:** 2026-08-06
