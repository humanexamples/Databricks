# Iceberg Reads (Universal Format / UniForm)

Ab Databricks Runtime 14.3 LTS konfigurieren **Iceberg Reads** Delta-Lake-Tabellen so, dass sie automatisch Iceberg-Metadaten generieren — Iceberg-Clients können so Delta-Lake-Daten lesen, ohne Dateien neu schreiben zu müssen. Basierend auf der offiziellen Databricks-Doku-Seite.

## 1. Funktionsweise

Das **Universal Format (UniForm)** erzeugt automatisch Iceberg-Metadaten neben den Delta-Lake-Metadaten, ohne die Parquet-Datendateien neu zu schreiben. „Eine einzige Kopie der Datendateien unterstützt sowohl Delta- als auch Iceberg-Clients."

**Wichtige Überlegungen:**

- Delta-Tabellen nutzen Zstandard-Kompression statt Snappy für Parquet-Dateien.
- Die Iceberg-Metadaten-Generierung läuft asynchron und kann den Ressourcenverbrauch des Drivers erhöhen.

## 2. Voraussetzungen zur Aktivierung

1. Die Tabelle muss bei Unity Catalog registriert sein (Managed oder External).
2. Column Mapping muss aktiviert sein (siehe [05 Column Mapping.md](05%20Column%20Mapping.md)).
3. Mindest-Reader-Version ≥ 2 und Writer-Version ≥ 7.
4. Schreibvorgänge erfordern Databricks Runtime 14.3 LTS oder höher.
5. Deletion Vectors dürfen nicht gleichzeitig aktiviert sein (bei Iceberg v2 — v3 unterstützt sie, siehe [06 Deletion Vectors.md](06%20Deletion%20Vectors.md)). Mit [Iceberg v3](../05%20Apache%20Iceberg.md#iceberg-v3) (Private Preview, Stand 21.01.2026) müssen Deletion Vectors **nicht** deaktiviert werden.

**Wichtig:** Ist `IcebergCompatV2` einmal aktiviert, lässt sich das Column-Mapping-Feature **nicht** mehr entfernen. Das Aktivieren von Iceberg Reads fügt außerdem das Schreib-Protokoll-Feature `IcebergCompatV2` hinzu — nur Clients, die dieses Tabellen-Feature unterstützen, können danach noch in die Tabelle schreiben (das kann die Kompatibilität mit externen Delta-Lake-Clients einschränken).

## 3. Aktivierung

**Bei Tabellenerstellung:**

```sql
CREATE TABLE T(c1 INT) TBLPROPERTIES(
  'delta.columnMapping.mode' = 'id',
  'delta.enableIcebergCompatV2' = 'true',
  'delta.universalFormat.enabledFormats' = 'iceberg');
```

Databricks empfiehlt den `id`-Column-Mapping-Modus für Kompatibilität.

**Auf bestehenden Tabellen (ab Runtime 15.4 LTS):**

```sql
ALTER TABLE table_name SET TBLPROPERTIES(
  'delta.columnMapping.mode' = 'name',
  'delta.enableIcebergCompatV2' = 'true',
  'delta.universalFormat.enabledFormats' = 'iceberg');
```

**Über `REORG` bei komplexeren Fällen** — nötig, wenn Deletion Vectors bereits existieren, zuvor `IcebergCompatV1` aktiviert war, oder nicht-Hive-kompatible Engines (Athena, Redshift) benötigt werden:

```sql
REORG TABLE table_name APPLY (UPGRADE UNIFORM(ICEBERG_COMPAT_VERSION=2));
```

## 4. Verifikation

```sql
DESCRIBE EXTENDED catalog_name.schema_name.table_name;
```

Im Abschnitt **Delta Uniform Iceberg** prüfen.

**Alternative:**

```sql
SHOW TBLPROPERTIES catalog_name.schema_name.table_name;
```

Folgende Eigenschaften sollten vorhanden sein: `delta.enableIcebergCompatV2 = true`, `delta.universalFormat.enabledFormats = iceberg`.

## 5. Deaktivierung

```sql
ALTER TABLE table_name UNSET TBLPROPERTIES ('delta.universalFormat.enabledFormats');
```

**Hinweis:** Upgrades der Delta-Lake-Reader-/Writer-Protokollversionen lassen sich nicht rückgängig machen.

## 6. Asynchrone Metadaten-Generierung im Detail

Die Iceberg-Metadaten-Generierung wird automatisch ausgelöst, sobald eine Delta-Lake-Schreibtransaktion abgeschlossen ist, und läuft auf demselben Compute wie der Schreibvorgang selbst. Delta Lake stellt dabei sicher, dass **immer nur ein** Metadaten-Generierungsprozess gleichzeitig läuft — mehrere Delta-Commits können so zu einem einzigen Iceberg-Metadaten-Commit gebündelt werden, und ein zweiter, gleichzeitiger Generierungsversuch wird nicht ausgelöst (verhindert kaskadierende Latenz).

**Wichtig:** Delta-Lake-Tabellenversionen entsprechen **nicht garantiert** den Iceberg-Versionen — zur Überprüfung der Korrespondenz sollten die Tabelleneigenschaften herangezogen werden; Time-Travel-Queries nutzen weiterhin die Delta-Tabellenversionen/-Zeitstempel.

## 7. Status der Metadaten-Generierung

| Feld | Beschreibung |
|---|---|
| `converted_delta_version` | letzte Delta-Version mit erfolgreicher Iceberg-Metadaten-Generierung |
| `converted_delta_timestamp` | Zeitstempel des letzten konvertierten Delta-Commits |

Einsehbar über `DESCRIBE EXTENDED` oder Catalog Explorer.

## 8. Manuelle Metadaten-Konvertierung

Synchron auslösbar, wenn die automatische Generierung fehlschlägt (z. B. nach Cluster-Terminierung, Job-Fehlschlägen oder nicht-UniForm-konformen Schreibvorgängen):

```sql
MSCK REPAIR TABLE <table-name> SYNC METADATA;
```

## 9. Iceberg-Metadaten-JSON-Pfade

```
<table-path>/metadata/<version-number>-<uuid>.metadata.json
```

Manche Iceberg-Clients (z. B. BigQuery) benötigen explizite Pfadreferenzen — einsehbar über `DESCRIBE EXTENDED` oder Catalog Explorer.

## 10. VACUUM und Cleanup

Ab Databricks Runtime 17.2 löscht `VACUUM` nicht nachverfolgte Dateien im UniForm-Metadaten-Verzeichnis, während erreichbare Iceberg-Metadaten erhalten bleiben — UniForm nutzt dabei standardmäßig `cleanExpiredFiles(false)`. `OPTIMIZE` und die UniForm-Konvertierung machen alte Metadaten lediglich unerreichbar, löschen sie aber nicht sofort. Um nicht erreichbare Metadaten physisch zu entfernen, nach Ablauf der `delta.deletedFileRetentionDuration`-Aufbewahrungsfrist `FULL VACUUM` ausführen. Ist Predictive Optimization aktiviert, erfolgt die Bereinigung automatisch.

## 11. Wichtige Einschränkungen

- Iceberg-Client-Unterstützung ist **nur lesend** — Schreibvorgänge werden nicht unterstützt.
- Deletion Vectors inkompatibel mit Iceberg v2 (v3 unterstützt sie — mit Iceberg v3, Private Preview Stand 21.01.2026, ist ein vorheriges Deaktivieren der Deletion Vectors nicht nötig).
- Kann nicht auf Materialized Views oder Streaming Tables mit `IcebergCompatV2` aktiviert werden — über Lakeflow-Pipelines verwaltete Tabellen können jedoch `IcebergCompatV3` nutzen.
- Tabellen müssen für automatische Metadaten-Generierung über den Namen (nicht den Pfad) zugegriffen werden.
- Kein `VOID`-Typ unterstützt.
- **OpenSharing:** Empfänger können freigegebene Tabellen über die REST-Catalog-API als Iceberg-Tabellen lesen (Public Preview) — manche OpenSharing-Reader-Clients unterstützen dabei nicht alle Tabellen-Features.
- Legacy Change Data Feed funktioniert nur für Delta-Clients, nicht für Iceberg-Clients.

**Externer Iceberg-Catalog-Zugriff:** Über eine externe Connection-Konfiguration lässt sich Unity Catalog selbst als Iceberg-Catalog für externe Engines ansprechen (separat dokumentiert, siehe [18 Connection.md](../../../02%20Unity%20Catalog/18%20Connection.md) für Connection-Grundlagen).

## 12. Verwandte Themen

- Allgemeine Apache-Iceberg-Grundlagen, Iceberg v3, Cloning: siehe [Apache Iceberg.md](../05%20Apache%20Iceberg.md).
- Runtime-Anforderungen und Protokollversion im Gesamtüberblick: siehe [08 Feature Compatibility.md](08%20Feature%20Compatibility.md).
- Type Widening und Iceberg-Kompatibilität: siehe [13 Type Widening.md](13%20Type%20Widening.md), Abschnitt 9.

### Quelle

- https://docs.databricks.com/aws/en/delta/iceberg-reads
