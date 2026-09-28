# Row Tracking

Row Tracking „weist jeder Zeile stabile Row-IDs und Row-Commit-Versionen zu, was zeilenweises Lineage-Tracking ermöglicht." Verfügbar ab Databricks Runtime 14.0. Alle Apache-Iceberg-v3-Tabellen enthalten diese Fähigkeit automatisch, Delta-Lake-Tabellen erfordern explizite Aktivierung. Basierend auf der offiziellen Databricks-Doku-Seite.

## 1. Was es ermöglicht

- Zeilenweises Lineage-Tracking.
- Unterstützung für bestimmte inkrementelle Materialized-View-Updates.
- Eindeutige Identifikation von Zeilen über Änderungen hinweg.

## 2. Voraussetzungen

Databricks Runtime 14.0 oder höher. Die Aktivierung erhöht das Tabellen-Writer-Protokoll und „kann die Kompatibilität mit externen Delta-Lake-Clients beeinträchtigen."

## 3. Aktivierung auf Delta-Lake-Tabellen

**Bei Tabellenerstellung:**

```sql
CREATE TABLE table_name TBLPROPERTIES (delta.enableRowTracking = true) AS SELECT * FROM source_table;
```

**Auf bestehenden Tabellen:**

```sql
ALTER TABLE table_name SET TBLPROPERTIES (delta.enableRowTracking = true);
```

**Wichtiger Hinweis:** Die Aktivierung von Row Tracking auf bestehenden Tabellen weist automatisch allen bestehenden Zeilen Row-IDs und Row-Commit-Versionen zu — dieser Prozess kann mehrere neue Tabellenversionen erzeugen und erheblich Zeit in Anspruch nehmen. Nebenläufige Schreibvorgänge vor der Aktivierung auf aktiv beschriebenen Tabellen pausieren.

## 4. Hinzugefügte Metadaten-Felder

| Feld | Typ | Zweck |
|---|---|---|
| `_metadata.row_id` | Long | eindeutiger Zeilen-Identifier — bleibt über `MERGE`/`UPDATE` stabil |
| `_metadata.row_commit_version` | Long | Delta-Log-Version, in der die Zeile zuletzt eingefügt/aktualisiert wurde |

## 5. Deaktivierung

```sql
ALTER TABLE table_name SET TBLPROPERTIES (delta.enableRowTracking = false);
```

**Wichtig:** Das Deaktivieren entfernt das Tabellen-Feature **nicht**, stuft das Protokoll **nicht** herab und löscht die Metadaten-Felder **nicht** — für eine vollständige Entfernung ist `DROP FEATURE` nötig (siehe [07 Drop Feature.md](07%20Drop%20Feature.md)).

## 6. Klon-Verhalten und Storage

Geklonte Tabellen behalten eine **unabhängige Historie** — Row-IDs und -Commit-Versionen des Klons unterscheiden sich von denen der Quelltabelle.

Row-Tracking-Metadaten werden zunächst im Transaktionslog gespeichert; `OPTIMIZE`- und `REORG`-Operationen schreiben Dateien neu, um die Metadaten-Felder direkt darin abzulegen.

## 7. Einschränkung bei Change Data Feed

Row-ID- und Row-Commit-Version-Metadaten sind beim Lesen des Change Data Feed **nicht zugänglich** (siehe [02 Change Data Feed.md](02%20Change%20Data%20Feed.md)).

## 8. Verwandte Themen

- Automatic Change Data Feed baut auf Row Tracking auf: siehe [02 Change Data Feed.md](02%20Change%20Data%20Feed.md).
- Runtime-Anforderungen und Protokollversion im Gesamtüberblick: siehe [08 Feature Compatibility.md](08%20Feature%20Compatibility.md).

### Quelle

- https://docs.databricks.com/aws/en/tables/features/row-tracking
