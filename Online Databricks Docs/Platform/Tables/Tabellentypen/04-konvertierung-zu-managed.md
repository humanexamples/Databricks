# External oder Foreign Delta-Lake-Tabellen zu Unity Catalog Managed Tables konvertieren

Unity Catalog Managed Tables sind der empfohlene Tabellentyp in Databricks. Die Konvertierung behält Tabellenkonfigurationen, Namen, Einstellungen, Berechtigungen, Views und die Tabellenhistorie bei.

## Befehlsunterschied nach Quelltyp

| Quelltyp | Befehl | Anforderung |
| --- | --- | --- |
| External | `ALTER TABLE ... SET MANAGED` | Keine MOVE- oder COPY-Option |
| Foreign | `ALTER TABLE ... SET MANAGED {MOVE \| COPY}` | MOVE oder COPY muss angegeben werden |

## Voraussetzungen

### Für External Tables

- Delta-Lake-Format erforderlich
- Databricks Runtime 17.3 LTS oder höher, oder Serverless Compute
- Eigentümerschaft der Tabelle
- Lesende und schreibende Clients müssen Databricks Runtime 15.4 LTS oder höher nutzen
- Externe Clients müssen das Lesen von Unity Catalog Managed Tables unterstützen
- Die Tabelle darf nicht gleichzeitig `minReaderVersion=2`, `minWriterVersion=7` und Column Mapping verwenden

### Für Foreign Tables

- Delta-Lake-Format (Parquet muss vorher zu Delta konvertiert werden)
- Databricks Runtime 17.3 oder höher
- Muss eine externe HMS-Tabelle sein (keine verwaltete HMS-Tabelle)
- OWNER- oder MANAGE-Berechtigung auf der Tabelle; CREATE-Berechtigung auf der EXTERNAL LOCATION
- Nur Hive Metastore und Glue Federation werden unterstützt

## Konvertierung per SQL

External Tables ohne Iceberg-Lesezugriff:

```sql
%sql
ALTER TABLE catalog.schema.my_external_table SET MANAGED;
```

External Tables mit aktiviertem Iceberg-Lesezugriff:

```sql
%sql
ALTER TABLE catalog.schema.my_external_table SET MANAGED TRUNCATE UNIFORM HISTORY;
```

Foreign Tables:

```sql
%sql
ALTER TABLE source_table SET MANAGED {MOVE | COPY}
```

## Geschätzte Ausfallzeiten

| Tabellengröße | Cluster | Kopierzeit | Ausfallzeit |
| --- | --- | --- | --- |
| ≤ 100 GB | 32-Core X-Large SQL Warehouse | ca. 6 Min. | ca. 1–2 Min. |
| 1 TB | 64-Core 2X-Large SQL Warehouse | ca. 30 Min. | ca. 1–2 Min. |
| 10 TB | 256-Core 4X-Large SQL Warehouse | ca. 1,5 Std. | ca. 1–5 Min. |

## Konvertierung überprüfen

```sql
%sql
DESCRIBE EXTENDED catalog_name.schema_name.table_name
```

Alternativ über die Systemtabellen:

```sql
%sql
SELECT table_type FROM system.information_schema.tables
WHERE table_catalog = 'catalog_name'
AND table_schema = 'schema_name'
AND table_name = 'table_name';
```

## Rückgängig machen (innerhalb von 14 Tagen)

External Tables:

```sql
%sql
ALTER TABLE catalog.schema.my_managed_table UNSET MANAGED;
```

Foreign Tables (MOVE):

```sql
%sql
ALTER TABLE catalog.schema.my_managed_table UNSET MANAGED
DROP TABLE catalog.schema.my_managed_table
```

Foreign Tables (COPY):

Hier reicht es, die Managed Table zu löschen. Die Neuanbindung über Federation erfolgt automatisch nach dem Katalog-Sync.

## Pfadbasierte Weiterleitung

Nach der Konvertierung leiten ab Databricks Runtime 18.1 alte, pfadbasierte Lesezugriffe automatisch an den verwalteten Speicherort weiter. Empfohlen wird trotzdem die Migration zu namensbasiertem Zugriff, um den Performance-Overhead zu beseitigen: Pfadbasierte Referenzen sollten durch namensbasierte Referenzen ersetzt werden.

## Wichtige Einschränkungen

- Zeitstempel-basiertes Time Travel steht für Commits nach der Konvertierung nicht zur Verfügung, falls die Konvertierung rückgängig gemacht wird.
- Bei Open Sharing muss nach der Konvertierung manuell erneut geteilt werden.
- Die pfadbasierte Weiterleitung erfordert einen Neustart aller Streaming-Jobs.
- Für Foreign Tables werden nur Hive Metastore und Glue Federation unterstützt.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/convert-to-managed  
**Stand:** 2026-08-09
