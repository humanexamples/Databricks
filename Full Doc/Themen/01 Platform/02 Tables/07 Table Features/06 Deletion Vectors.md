# Deletion Vectors

Deletion Vectors beschleunigen Datenmodifikationsoperationen, indem sie „Zeilen stattdessen als modifiziert in Metadaten markieren" — statt ganze Dateien neu zu schreiben. „Lesevorgänge wenden die Deletion-Vector-Einträge zur Query-Zeit an, um den aktuellen Tabellenzustand aufzulösen." Ohne dieses Feature erfordert das Aktualisieren einer einzelnen Zeile das Neuschreiben der gesamten Parquet-Datei. Basierend auf der offiziellen Databricks-Doku-Seite.

## 1. Wie sie funktionieren

- Zeichnen Zeilenmodifikationen in Metadaten auf, statt Datendateien neu zu schreiben.
- Wenden Deletion-Vector-Einträge während der Query-Ausführung an, um den aktuellen Tabellenzustand zu zeigen.
- Unterstützen `DELETE`, `UPDATE` und `MERGE` sowohl auf Delta-Lake- als auch auf Apache-Iceberg-Tabellen.

## 2. Voraussetzungen

| Aspekt | Voraussetzung |
|---|---|
| Apache Iceberg v3 | Deletion Vectors standardmäßig enthalten |
| Delta Lake | muss explizit aktiviert werden |
| Schreiben | Databricks Runtime 14.3 LTS oder neuer (mit Optimierungen) |
| Lesen | Databricks Runtime 12.2 LTS oder neuer |

## 3. Code-Beispiele

**Delta Lake:**

```sql
CREATE TABLE <table-name> TBLPROPERTIES ('delta.enableDeletionVectors' = true);
ALTER TABLE <table-name> SET TBLPROPERTIES ('delta.enableDeletionVectors' = true);
```

**Apache Iceberg:**

```sql
CREATE TABLE <table-name> TBLPROPERTIES ('iceberg.enableDeletionVectors' = true);
ALTER TABLE <table-name> SET TBLPROPERTIES ('iceberg.enableDeletionVectors' = true);
```

Workspace-Einstellungen können Deletion Vectors bei SQL-Warehouses oder Runtime 14.3 LTS+ automatisch für neue Tabellen aktivieren.

**Wichtige Warnung:** Die Aktivierung von Deletion Vectors hebt das Tabellenprotokoll an — Clients ohne Deletion-Vector-Unterstützung können die Tabelle danach **nicht mehr lesen**. Ab Databricks Runtime 14.1+ lässt sich das Deletion-Vectors-Feature per `DROP FEATURE` entfernen, um die Kompatibilität wiederherzustellen (siehe [07 Drop Feature.md](07%20Drop%20Feature.md)).

## 4. Client-Kompatibilitätsmatrix

| Client | Schreibunterstützung | Leseunterstützung |
|---|---|---|
| Databricks Runtime mit Photon | `MERGE`, `UPDATE`, `DELETE` ab Runtime 12.2+ | Runtime 12.2+ |
| Databricks Runtime ohne Photon | `DELETE` (12.2+), `UPDATE` (14.1+), `MERGE` (14.3+) | Runtime 12.2+ |
| OSS Apache Spark mit Delta Lake | `DELETE` (Delta 2.4.0+), `UPDATE` (3.0.0+) | Delta 2.3.0+ |
| OpenSharing-Empfänger | nicht unterstützt | Runtime 14.1+ / delta-sharing-spark 3.1+ |

## 5. Physische Dateibereinigung

Um Parquet-Dateien mit Soft-Deleted-Zeilen physisch neu zu schreiben:

1. `OPTIMIZE` auf der Tabelle ausführen.
2. `REORG TABLE ... APPLY (PURGE)` ausführen — schreibt alle Dateien mit Deletion-Vector-Änderungen neu.
3. Auto-Compaction während Schreiboperationen nutzen.

**Für vollständige Datenentfernung und Compliance:**

1. `REORG TABLE ... APPLY (PURGE)` ausführen.
2. `VACUUM` mit auf den Purge-Abschlusszeitpunkt gesetzter Retention-Schwelle ausführen.

**Performance-Optimierung:** `spark.databricks.delta.reorg.purgeMode` auf `rows` setzen für große Tabellen — Standard `all` scannt alle Parquet-Footer, `rows` beschränkt die Operation auf Dateien mit Soft-Deleted-Zeilen.

## 6. Bezug zu Row-Level Concurrency

Databricks Runtime 14.2+ unterstützt Row-Level Concurrency auf Tabellen mit aktivierten Deletion Vectors, was nebenläufige Modifikationen unterschiedlicher Zeilen erlaubt (ausführlich in [Liquid Clustering.md](../../../09%20Performance%20Optimization/01%20Foundation%20Design/05%20Liquid%20Clustering.md), Abschnitt 9.2).

## 7. Iceberg-Integration

- **Iceberg v3:** vollständige Unterstützung, Deletion Vectors standardmäßig aktiviert.
- **Iceberg v2:** unterstützt Deletion Vectors beim Lesen nicht.
- **Iceberg v3 mit aktivierten Reads:** unterstützt Deletion Vectors — mit [Iceberg v3](../05%20Apache%20Iceberg.md#iceberg-v3) (Private Preview, Stand 21.01.2026) müssen Deletion Vectors dafür **nicht** deaktiviert werden, anders als bei Iceberg v2 (siehe [14 Iceberg Reads (UniForm).md](14%20Iceberg%20Reads%20%28UniForm%29.md)).

## 8. Bekannte Einschränkungen

- Manifest-Dateien können für Tabellen mit Deletion Vectors nicht generiert werden, ohne vorher `REORG TABLE` auszuführen.
- Manifest-Dateien können mit aktivierten Deletion Vectors nicht inkrementell generiert werden.
- Das Tabellenprotokoll lässt sich nach Aktivierung von Deletion Vectors auf Materialized Views/Streaming Tables nicht mehr herabstufen.
- Bestehende Deletion Vectors bleiben auch nach Entfernung bestehen, neue Schreibvorgänge erzeugen jedoch keine mehr.
- **File-Compaction-Hinweis:** Kompaktierungs-Vorgänge garantieren nicht strikt, dass in Deletion Vectors erfasste Änderungen aufgelöst werden — manche Änderungen werden physisch nicht angewendet, wenn die betroffenen Datendateien keine Kandidaten für die Kompaktierung sind.

## 9. Photon-Optimierung

Photon nutzt Deletion Vectors, um `DELETE`-, `MERGE`- und `UPDATE`-Operationen über Predictive-I/O-Updates zu beschleunigen (siehe [Data Skipping und Tabellenstatistiken.md](../../../09%20Performance%20Optimization/01%20Foundation%20Design/04%20Data%20Skipping%20und%20Tabellenstatistiken.md), Abschnitt 8).

### Quelle

- https://docs.databricks.com/aws/en/tables/features/deletion-vectors
