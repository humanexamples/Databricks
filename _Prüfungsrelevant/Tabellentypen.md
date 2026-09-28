# Tabellentypen in Databricks

Welche Tabellenarten gibt es, wofür setzt man sie ein, was können sie und wo sind ihre Grenzen? Alle Tabellen liegen in Unity Catalog im Namensraum **`catalog.schema.table`**.

> Gegenstück zu Views: [View-Typen.md](View-Typen.md)

---

## Überblick

| Typ | Wer verwaltet Daten und Speicherort? | Formate | `DROP TABLE` löscht Daten? | Typischer Einsatz |
|---|---|---|---|---|
| **Managed Table** (Standard) | Unity Catalog | Delta Lake, Apache Iceberg | ✅ ja (nach 7 Tagen Recovery-Frist) | Produktions-Workloads, häufig abgefragte Daten |
| **External Table** | Du selbst (`LOCATION`) | DELTA, CSV, JSON, AVRO, PARQUET, ORC, TEXT | ❌ nein, nur Metadaten weg | Legacy-Daten, inkompatible Formate, direkter Zugriff fremder Clients |
| **Foreign Table** | Externes System (Lakehouse Federation) | abhängig vom Quellsystem | ❌ nein | Lesezugriff auf externe DBs/Kataloge ohne Migration |
| **Temporary Table** | Databricks, sitzungsgebunden | Delta (fix) | verschwindet mit Session-Ende | Zwischenergebnisse in Analyse/SQL-Pipelines |
| **Streaming Table** | Unity Catalog, besessen von **einer** Pipeline | Delta | ✅ ja | Inkrementelle Ingestion (Append-only), Low-Latency |

**Merksatz:** *Managed = Unity Catalog besitzt Daten **und** Metadaten. External = Unity Catalog besitzt nur die Metadaten. Foreign = Unity Catalog regelt nur den Zugriff.*

---

## 1. Managed Table

Standard und von Databricks empfohlen. Wird ohne `LOCATION` angelegt. Die Daten liegen im Managed-Storage von Catalog oder Schema (weiterhin im eigenen Cloud-Account).

```sql
CREATE TABLE main.sales.orders (id INT, amount DOUBLE);
```

```python
df.write.saveAsTable("main.sales.orders")                       # Delta
df.write.format("iceberg").saveAsTable("main.sales.orders_ice")  # Iceberg
```

**Vorteile**
- **Predictive Optimization** führt `OPTIMIZE`, `VACUUM` und `ANALYZE` automatisch aus (Abrechnung über Serverless).
- **Automatic Liquid Clustering** wählt die Clustering-Keys selbst.
- **Automatische Upgrades** auf neue Features wie Checkpoint V2, Row Tracking, Catalog Commits und Parquet v2, ohne Code-Änderung.
- Niedrigere Storage- und Query-Kosten als External oder Foreign Tables, dazu Metadaten-Caching.
- Multi-Statement-ACID-Transaktionen über mehrere Tabellen.
- Offener Zugriff über Delta- und Iceberg-Clients, Credential Vending und OpenSharing.
- **`UNDROP TABLE`** stellt gelöschte Tabellen innerhalb der Recovery-Frist wieder her (Standard **7 Tage**, konfigurierbar 0 h bis 30 Tage).

```sql
ALTER CATALOG my_catalog RETAIN DROPPED TO 30 DAYS;
UNDROP TABLE main.sales.orders;
```

**Einschränkungen**
- Speicherort und Layout lassen sich nicht selbst bestimmen.
- `DROP` löscht die Daten: Nach der Recovery-Frist sind sie innerhalb von 48 h endgültig weg.
- Automatische Upgrades setzen voraus, dass Serverless in der Region verfügbar ist.

**Konvertierung External → Managed:** Voraussetzung sind Delta-Format und DBR 17.3 LTS+. Die Downtime liegt meist bei wenigen Minuten.
```sql
ALTER TABLE catalog.schema.my_external_table SET MANAGED;
```

---

## 2. External Table

Du gibst den Speicherort über `LOCATION` bzw. `option("path", ...)` an. Unity Catalog verwaltet nur die **Metadaten und die Governance**, nicht Lebenszyklus, Optimierung oder Layout.

```sql
CREATE TABLE main.raw.sec_filings
LOCATION 's3://depts/finance/sec_filings';
```

```python
df.write.option("path", "s3://bucket/dir").saveAsTable("main.raw.events")
```

**Einsatzgebiete** (laut Databricks nur diese zwei Hauptfälle):
1. Bestehende Daten in Formaten registrieren, die **nicht Managed-kompatibel** sind, z. B. JSON oder Avro.
2. **Nicht-Databricks-Clients** brauchen direkten Dateizugriff ohne Unity-Catalog-Berechtigungsprüfung.

**Vorteile**
- Volle Kontrolle über Speicherort und Dateien.
- `DROP TABLE` entfernt nur die Metadaten, die Dateien bleiben erhalten.
- Unterstützt viele Dateiformate.

**Einschränkungen**
- Keine automatische Optimierung, schlechtere Performance als Managed Tables.
- Rechte: `CREATE EXTERNAL TABLE` auf der **External Location**, dazu `USE CATALOG`, `USE SCHEMA` und `CREATE TABLE`.
- Bei Nicht-Delta-Tabellen mit Partitionen: Die Partition Discovery listet standardmäßig rekursiv alle Verzeichnisse, was bei großen Tabellen langsam ist. Die Alternative ist **Partition Metadata Logging** (DBR 13.3+). Schreiben fremde Systeme Dateien direkt in den Pfad, braucht es danach `MSCK REPAIR TABLE ... SYNC PARTITIONS`.

---

## 3. Foreign Table (Federated Table)

Tabelle aus einem **Foreign Catalog**, die über Lakehouse Federation in Unity Catalog registriert ist. Die Daten verwaltet das externe System.

| Registrierung | Funktionsweise | Beispiele |
|---|---|---|
| **Query Federation** | JDBC-Verbindung zur externen DB | PostgreSQL, MySQL |
| **Catalog Federation** | externer Katalog, direkter Dateizugriff | Hive Metastore, AWS Glue, Snowflake Horizon |

**Vorteile**
- Zugriff auf externe Daten **ohne Migration**, mit Unity-Catalog-Governance.
- Gut als Brücke während einer Migration.

**Einschränkungen**
- **Nur lesend**: kein `MODIFY`-Privileg bei Lakehouse Federation und extern föderierten Metastores. Ausnahme ist ein interner föderierter HMS.
- Keine automatischen Optimierungen und schwächere Transaktionsgarantien als Managed Tables.
- Für häufig genutzte oder produktive Daten empfiehlt Databricks eine Migration zu Managed Tables.

**Konvertierung Foreign → External** (DBR 17.3+). Historie und Berechtigungen bleiben erhalten:
```sql
ALTER TABLE source_table SET EXTERNAL DRY RUN;   -- nur prüfen
ALTER TABLE source_table SET EXTERNAL;
```

---

## 4. Temporary Table

Sitzungsgebundene Managed Delta-Tabelle für Zwischenergebnisse.

```sql
CREATE OR REPLACE TEMP TABLE temp_recent_orders AS
SELECT * FROM prod.sales.orders
WHERE order_date >= current_date() - INTERVAL 30 DAYS;

SELECT * FROM temp_recent_orders;   -- ohne catalog.schema
```

**Vorteile**
- Man braucht **kein** `CREATE TABLE`-Recht, jeder Nutzer kann Temporary Tables anlegen.
- Der Katalog-Namensraum bleibt sauber, und Databricks räumt automatisch auf.
- Unterstützt `INSERT`, `UPDATE` und `MERGE`.
- Namensauflösung: Die Temporary Table **überschattet** eine gleichnamige permanente Tabelle im aktuellen Schema.

**Einschränkungen**

| Einschränkung | Details |
|---|---|
| Lebensdauer | Ende der Session, **max. 7 Tage** |
| `DELETE FROM` | ❌ nicht unterstützt |
| `ALTER TABLE` | ❌ stattdessen Tabelle ersetzen |
| Time Travel / Clone | ❌ |
| Streaming (`foreachBatch`) | ❌ |
| APIs | **nur SQL**, keine DataFrame-API |
| `USING`-Klausel | nicht erlaubt (immer Delta) |
| Teilen | nur der erstellende Nutzer. Nicht auf Dedicated-Clustern (Single User) |
| Namensraum | geteilt mit Temporary Views, gleicher Name nicht möglich |

---

## 5. Streaming Table

Eine Delta-Tabelle mit Unterstützung für inkrementelle Verarbeitung. Sie ist Ziel von Flows in einer Lakeflow-Pipeline oder wird per Databricks SQL angelegt.

```sql
CREATE OR REFRESH STREAMING TABLE bronze_orders AS
SELECT * FROM STREAM read_files('/Volumes/main/raw/orders', format => 'json');
```

**Einsatzgebiete**
- **Ingestion** großer **Append-only**-Datenmengen über Auto Loader, Kafka, Event Hubs oder Pub/Sub.
- Low-Latency-Verarbeitung, auch im Real-Time Mode mit Latenz unter einer Sekunde.
- Für Quellen mit Updates und Deletes: **`AUTO CDC`** als Ziel-Flow verwenden.

**Vorteile**
- Jede Zeile wird **genau einmal** verarbeitet, der Fortschritt wird über Checkpoints gehalten.
- Mehrere Flows können in dieselbe Streaming Table schreiben (Fan-in).
- Hoher Durchsatz und niedrige Latenz.

**Einschränkungen**
- **Begrenzte Evolution:** Änderungen an der Query wirken nur auf **neue** Zeilen. Alte Zeilen werden erst bei einem **Full Refresh** neu verarbeitet.
- **Joins** werden nicht neu berechnet, wenn sich die Dimensionstabelle ändert („fast but wrong“). Für korrekte Joins ist eine Materialized View besser.
- Wird von **genau einer Pipeline** besessen, andere Pipelines können sie nicht ändern.
- Kein `CLONE` (weder Quelle noch Ziel).
- Zustandsbehaftete Low-Latency-Verarbeitung braucht begrenzte Streams oder **Watermarks**.
- Nicht-Admins brauchen das `REFRESH`-Privileg.

---

## Entscheidungshilfe

| Situation | Tabellentyp |
|---|---|
| Neue Lakehouse-Daten, Standardfall | **Managed Table** |
| Vorhandene JSON/CSV/Avro-Dateien registrieren oder fremde Tools lesen die Dateien direkt | **External Table** |
| Daten in PostgreSQL, Snowflake oder Glue nur abfragen, nicht migrieren | **Foreign Table** |
| Zwischenergebnis nur für diese Session | **Temporary Table** |
| Kontinuierlich wachsende Quelle inkrementell laden | **Streaming Table** |
| Aggregation oder Join, der immer zum aktuellen Quellstand passen muss | → **Materialized View**, siehe [View-Typen.md](View-Typen.md) |

## Typische Prüfungsfallen

- `DROP TABLE` auf einer **Managed** Table löscht die Daten (mit 7 Tagen `UNDROP`-Frist). Auf einer **External** Table bleiben die Dateien liegen.
- Eine External Table entsteht durch **`LOCATION`** bzw. `option("path")`. Ohne diese Angabe ist die Tabelle immer Managed.
- Foreign Tables sind **read-only**.
- Temporary Tables: kein `DELETE`, kein Time Travel, nur SQL.
- Streaming Table ändert sich nach einer Query-Änderung nur für neue Zeilen. Für alle Zeilen braucht es einen Full Refresh.

---

## Quellen im Projekt

- [01 Tabellenkonzepte und Tabellentypen.md](../Full%20Doc/Themen/01%20Platform/02%20Tables/01%20Tabellenkonzepte%20und%20Tabellentypen.md)
- [03 Managed Tables.md](../Full%20Doc/Themen/01%20Platform/02%20Tables/03%20Managed%20Tables.md)
- [04 External und Foreign Tables.md](../Full%20Doc/Themen/01%20Platform/02%20Tables/04%20External%20und%20Foreign%20Tables.md)
- [04 Table.md (Unity Catalog)](../Full%20Doc/Themen/02%20Unity%20Catalog/04%20Table.md)
- [07 Streaming Tables.md](../Full%20Doc/Themen/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/01%20Concepts/07%20Streaming%20Tables.md)
- [02 Prozedural vs Deklarativ, Batch vs Streaming, Tabellen vs Views.md](Data%20Transformation%20and%20Modeling/04%20DML%20und%20Kernkonzepte/02%20Prozedural%20vs%20Deklarativ%2C%20Batch%20vs%20Streaming%2C%20Tabellen%20vs%20Views.md)

Offizielle Doku: [Table types](https://docs.databricks.com/aws/en/tables/types) · [Managed tables](https://docs.databricks.com/aws/en/tables/managed) · [External tables](https://docs.databricks.com/aws/en/tables/external) · [Foreign tables](https://docs.databricks.com/aws/en/tables/foreign) · [Temporary tables](https://docs.databricks.com/aws/en/tables/temporary-tables) · [Streaming tables](https://docs.databricks.com/aws/en/ldp/concepts/streaming-tables)
