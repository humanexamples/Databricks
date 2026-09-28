# Shallow Clone für Unity-Catalog-Tabellen

Mit Shallow Clone erstellen Sie Unity-Catalog-Tabellen mit eigenen Zugriffsrechten, ohne die zugrunde liegenden Daten zu duplizieren. Diese Funktion befindet sich in Public Preview und unterstützt nur Delta-Lake-Tabellen.

## Voraussetzungen für die Runtime

Die Unterstützung unterscheidet sich zwischen Managed und External Tables. Für Managed Tables benötigen Sie Databricks Runtime 13.3 LTS oder höher. Für External Tables benötigen Sie Databricks Runtime 14.3 LTS oder höher.

## Managed Shallow Clones erstellen

```sql
%sql
CREATE TABLE <catalog-name>.<schema-name>.<target-table-name>
SHALLOW CLONE <catalog-name>.<schema-name>.<source-table-name>
```

Benötigte Rechte: `USE SCHEMA` und `USE CATALOG` auf der Quelle, sowie `USE SCHEMA` und `CREATE TABLE` auf dem Ziel.

## External Shallow Clones erstellen

```sql
%sql
CREATE TABLE <catalog-name>.<schema-name>.<target-table-name>
SHALLOW CLONE <catalog-name>.<schema-name>.<source-table-name>
LOCATION 's3://<bucket-name>/<path-name>/<target-table-name>'
```

External Clones benötigen dieselben Rechte wie Managed Clones, zusätzlich `CREATE EXTERNAL TABLE` auf dem Ziel-External-Location.

## Anforderungen an den Access Mode

Im Standard Access Mode benötigen Sie `USE CATALOG`, `USE SCHEMA` und `SELECT`. Änderungsoperationen (`INSERT`, `DELETE`, `UPDATE`, `MERGE`, `CREATE TABLE`, `DROP TABLE`) benötigen `MODIFY`-Rechte auf dem Klon-Ziel.

Im Dedicated Access Mode benötigen Sie Rechte sowohl auf der Quelle als auch auf dem Ziel für alle Operationen.

## Verhalten von VACUUM

Bei Managed Tables können `VACUUM`-Operationen auf der Quelle oder auf dem Ziel eines Shallow Clone Datendateien aus der Quelltabelle löschen.

Bei External Tables entfernt `VACUUM` Datendateien nur aus der Quelltabelle, wenn es direkt gegen die Quelltabelle ausgeführt wird.

Datendateien bleiben erhalten, solange sie von einem Shallow Clone innerhalb der Aufbewahrungsschwelle benötigt werden.

## Wichtige Einschränkungen

- Nur Delta-Lake-Tabellen werden unterstützt. Iceberg-Tabellen können nicht geklont werden.
- `CREATE OR REPLACE` kann bei Shallow Clones nicht verwendet werden.
- Shallow Clones können nicht verschachtelt werden.
- OpenSharing wird nicht unterstützt.
- Wird die Quelle einer Managed Table gelöscht, brechen abhängige Klone. Bei External Tables bleiben die Klone funktionsfähig.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/operations/clone-unity-catalog  
**Stand:** 2026-08-06
