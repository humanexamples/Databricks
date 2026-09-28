# Catalog Commits

## 1. Was es ist

Catalog Commits verlagern die Transaktionskoordination von der Tabellen- auf die Catalog-Ebene, sodass Unity Catalog Lese- und Schreibvorgänge über Tabellen hinweg koordiniert.  „Einzige Quelle der Wahrheit für den Zustand von Delta-Lake- und Apache-Iceberg-Tabellen"

## 2. Kernfähigkeiten

- **Multi-Table-Transaktionen:** „mehrere SQL-Statements über mehrere Tabellen hinweg als einen einzigen atomaren Commit ausführen. Alle Änderungen gelingen gemeinsam oder scheitern gemeinsam."
- **Governte Zugriffe:** Lese- und Schreibvorgänge koordinieren sich über Unity Catalog.
- **Schnellere Query-Planung:** direkte Metadaten-Auslieferung von Unity Catalog an Delta-Clients, reduziert Latenz.
- **Constraint-Durchsetzung:** Unity Catalog validiert Schema- und Constraint-Änderungen.
- **Schreibvorgänge externer Engines:** „sicheres Schreiben in Unity-Catalog-Managed-Tables von externen Engines aus. Unity Catalog koordiniert Commits, um Korruption und Nebenläufigkeitskonflikte zu verhindern."

## 3. Voraussetzungen

| Fähigkeit | Mindest-Runtime |
|---|---|
| Managed Tables lesen/schreiben/erstellen | 16.4+ |
| Aktivieren/Deaktivieren auf bestehenden Managed Tables | 18.0+ |
| Streaming Tables und Materialized Views | 17.3+ |
| Deaktivieren auf Streaming-Objekten | 18 LTS+ |

Tabellen müssen Unity-Catalog-Managed-Tables (Delta oder Iceberg), Streaming Tables oder Materialized Views sein. Für Iceberg befindet sich die Catalog-Commits-Unterstützung in **Private Preview** (Anmeldung über Formular erforderlich).

## 4. Code-Beispiele

**Für neue Tabellen aktivieren:**

```sql
CREATE TABLE sales_data (
  sale_id BIGINT,
  amount DECIMAL(10,2),
  sale_date DATE)
TBLPROPERTIES ('delta.feature.catalogManaged' = 'supported');
```

**Für bestehende Tabellen aktivieren:**

```sql
ALTER TABLE sales_data SET TBLPROPERTIES
  ('delta.feature.catalogManaged' = 'supported');
```

**Für Streaming Tables:**

```sql
CREATE OR REFRESH STREAMING TABLE streaming_sales_data
TBLPROPERTIES ('delta.feature.catalogManaged' = 'supported')
AS SELECT * FROM STREAM sales_data;
```

**Aktivierung verifizieren:**

```sql
DESCRIBE DETAIL sales_data;
```

Ist Catalog Commits aktiviert, erscheint `catalogManaged` in der Spalte `tableFeatures`.

## 5. Wichtige Einschränkungen

- Lässt sich nicht über `CREATE OR REPLACE TABLE` oder `REPLACE TABLE` umschalten.
- Inkompatibel mit externem Datenzugriff auf Streaming Tables und Materialized Views.
- Managed Tables nutzen für OpenSharing vor-signierte URLs statt Cloud-Tokens.
- Single-User-Cluster können nicht auf Streaming Tables mit aktiviertem Catalog Commits zugreifen.
- Die Aktivierung auf bestehenden Tabellen erfordert eine Synchronisierung, die bei Tabellen mit hohem Volumen mehrere Minuten dauern kann.
- Ein Abbruch laufender Upgrade-/Downgrade-Operationen riskiert einen inkonsistenten Zwischenzustand und Tabellensperrung.

## 6. Verwandte Themen

- Multi-Statement-, Multi-Table-Transaktionen bauen direkt auf Catalog Commits auf (siehe [08 Transactions.md](../08%20Transactions.md)).
- `DROP FEATURE` zum vollständigen Entfernen des `catalogManaged`-Features: siehe [07 Drop Feature.md](07%20Drop%20Feature.md).
- Runtime-Anforderungen und Protokollversion im Gesamtüberblick: siehe [08 Feature Compatibility.md](08%20Feature%20Compatibility.md).

### Quelle

- https://docs.databricks.com/aws/en/tables/features/catalog-commits

