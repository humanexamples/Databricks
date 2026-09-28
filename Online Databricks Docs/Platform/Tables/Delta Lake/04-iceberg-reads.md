# Iceberg Reads für Delta-Lake-Tabellen

Mit Iceberg Reads generiert Databricks automatisch Iceberg-Metadaten für eine Delta-Lake-Tabelle. Iceberg-Clients können die Delta-Daten dann lesen, ohne dass Dateien neu geschrieben werden. Die Funktion benötigt Databricks Runtime 14.3 LTS oder höher.

## Funktionsweise

Das Universal Format (UniForm) erzeugt Iceberg-Metadaten asynchron neben den Delta-Lake-Metadaten. Die Parquet-Dateien selbst werden nicht neu geschrieben. Delta- und Iceberg-Clients greifen so auf dieselbe Datenkopie zu.

- Zstandard ersetzt Snappy als Kompressions-Codec.
- Die Metadaten-Generierung läuft asynchron. Das kann die Ressourcennutzung des Drivers erhöhen.

## Voraussetzungen

- Die Delta-Lake-Tabelle muss in Unity Catalog registriert sein (managed oder external).
- Column Mapping muss aktiviert sein.
- `minReaderVersion` muss mindestens 2 sein, `minWriterVersion` mindestens 7.
- Schreibvorgänge benötigen Databricks Runtime 14.3 LTS oder höher.
- Deletion Vectors dürfen nicht gleichzeitig aktiviert sein.

## Iceberg Reads aktivieren

### Bei der Tabellenerstellung

```sql
%sql
CREATE TABLE T(c1 INT) TBLPROPERTIES(
  'delta.columnMapping.mode' = 'id',
  'delta.enableIcebergCompatV2' = 'true',
  'delta.universalFormat.enabledFormats' = 'iceberg');
```

### Bei bestehenden Tabellen (Runtime 15.4 LTS oder höher)

```sql
%sql
ALTER TABLE table_name SET TBLPROPERTIES(
  'delta.columnMapping.mode' = 'name',
  'delta.enableIcebergCompatV2' = 'true',
  'delta.universalFormat.enabledFormats' = 'iceberg');
```

Mit REORG (für Deletion Vectors oder älteres UniForm):

```sql
%sql
REORG TABLE table_name APPLY (UPGRADE UNIFORM(ICEBERG_COMPAT_VERSION=2));
```

## Aktivierung überprüfen

```sql
%sql
DESCRIBE EXTENDED catalog_name.schema_name.table_name;
```

oder

```sql
%sql
SHOW TBLPROPERTIES catalog_name.schema_name.table_name;
```

Prüfen Sie, ob die Eigenschaften `delta.enableIcebergCompatV2 = true` und `delta.universalFormat.enabledFormats = iceberg` gesetzt sind.

## Iceberg Reads deaktivieren

```sql
%sql
ALTER TABLE table_name UNSET TBLPROPERTIES ('delta.universalFormat.enabledFormats');
```

## Status der Metadaten verfolgen

| Feld | Beschreibung |
|---|---|
| `converted_delta_version` | Neueste Delta-Version mit erfolgreich erzeugten Iceberg-Metadaten |
| `converted_delta_timestamp` | Zeitstempel der letzten erfolgreichen Konvertierung |

## Metadaten-Generierung manuell auslösen

```sql
%sql
MSCK REPAIR TABLE <table-name> SYNC METADATA
```

## Pfad der Metadaten-Datei

`<table-path>/metadata/<version-number>-<uuid>.metadata.json`

## VACUUM und Aufräumen

Ab Runtime 17.2 löscht `VACUUM` nicht nachverfolgte Dateien im Verzeichnis `metadata/`. Erreichbare Iceberg-Metadaten bleiben dabei erhalten. Nach Ablauf der Aufbewahrungsfrist entfernt `FULL VACUUM` nicht mehr erreichbare Metadaten physisch. Predictive Optimization übernimmt das normalerweise automatisch.

## Wichtige Einschränkungen

- Nur lesend für Iceberg-Clients. Schreibvorgänge werden nicht unterstützt.
- Deletion Vectors werden nicht unterstützt (Apache Iceberg v3 unterstützt sie).
- Nicht aktivierbar auf materialisierten Sichten oder Streaming-Tabellen mit `IcebergCompatV2`.
- Tabellen müssen über ihren Namen angesprochen werden, damit die Metadaten-Generierung ausgelöst wird.
- `VOID`-Typen werden nicht unterstützt.
- Manche OpenSharing-Clients haben Kompatibilitätseinschränkungen.
- Der Legacy Change Data Feed funktioniert für Delta, aber nicht für Iceberg.

---
**Quelle:** https://docs.databricks.com/aws/en/delta/iceberg-reads  
**Stand:** 2026-08-06
