# VARIANT-Datentyp

> **Gilt für:** Databricks SQL, Databricks Runtime 15.4 LTS und höher.

Der `VARIANT`-Datentyp **speichert semi-strukturierte Daten** innerhalb von Databricks-Tabellen — er ermöglicht flexible Speicherung JSON-artiger Informationen neben strukturierten Daten, ohne dass vorab ein Schema festgelegt werden muss.

---

## 1. Aktivierung

**Bei neuen Tabellen:**

```sql
CREATE TABLE table_name (variant_column VARIANT)
```

**Bei bestehenden Delta-Lake-Tabellen:**

```sql
ALTER TABLE table_name SET TBLPROPERTIES('delta.feature.variantType' = 'supported')
```

- **Apache-Iceberg-v3-Tabellen** enthalten `VARIANT`-Unterstützung automatisch.
- **Delta-Lake-Tabellen** erfordern die explizite Aktivierung wie oben.
- Zum Lesen und Schreiben von Tabellen mit aktivierter Variant-Unterstützung ist **Databricks Runtime 15.4 LTS oder höher** erforderlich.

> **Hinweis:** *"Enabling variant upgrades the table writer protocol. This might affect compatibility with external Delta Lake clients."* — die Aktivierung hebt das **Writer-Protokoll** der Tabelle an und kann damit die Kompatibilität mit externen Delta-Lake-Clients beeinträchtigen.

---

## 2. Wichtige Einschränkungen

- Variant-Spalten können **nicht** zum Partitionieren einer Tabelle verwendet werden.
- Eine Variant-Spalte kann **kein Clustering-Key** sein.
- Variant-Spalten können **nicht** mit `GROUP BY` oder `ORDER BY` verwendet werden.
- `DISTINCT` kann **nicht** auf einer Variant-Spalte aufgerufen werden.
- SQL-Set-Operatoren (`INTERSECT`, `UNION`, `EXCEPT`) sind mit Variant-Spalten **nicht** nutzbar.
- Column Generation kann **nicht** zum Erzeugen einer Variant-Spalte verwendet werden.
- Variant-Spalten unterstützen **keine** `minValues`/`maxValues`-Statistiken.
- Eine Variant-Spalte darf **keinen Wert größer als 128 MiB** enthalten (16 MiB in Databricks Runtime 17.1 und früher).

---

## 3. Hintergrund & Motivation

> Quellen: Databricks-Blog *„Introducing the Open Variant Data Type in Delta Lake and Apache Spark"* (Kent Marten, Gene Pang, Chenhao Li, Han Xiao; veröffentlicht 2024-06-03, aktualisiert 2025-05-06) sowie die Data-+-AI-Summit-2024-Session *„Variant Data Type – Making Semi-Structured Data Fast and Simple"* und das Video *„Say goodbye to messy JSON headaches with VARIANT"* (2024-06-24).

**Das Problem:** *"Without Variant, customers had to choose between flexibility and performance."* Semi-strukturierte Daten wurden entweder als `STRING`/JSON (flexibel, aber langsam zu parsen) oder in feste `STRUCT`-Schemata (schnell, aber unflexibel bei sich änderndem Schema) gespeichert.

**Die Lösung:** `VARIANT` speichert die Daten in einem **offenen binären Encoding** statt als Text. Das Parsen entfällt bei der Abfrage — Pfadzugriffe lesen direkt aus der Binärstruktur.

**Performance:** *"For both nested and flat schemas, performance with Variant improved 8x over String columns."* (Benchmark auf Databricks Runtime 15.0 mit Photon.) Die DAIS-Session formuliert es als *"an order of magnitude performance improvements compared with storing data as JSON strings, while maintaining the flexibility for supporting highly nested and evolving schema."*

**Typische Anwendungsfälle laut Blog:**

- Endpoint Detection & Response (EDR) mit variierenden JSON-Schemata
- Ad-Click-Analyse
- IoT-Telemetriedaten
- Anwendungslogs mit unbekanntem oder sich entwickelndem Schema

**Offene Implementierung:**

- Der `VARIANT`-Datentyp und die Binär-Ausdrücke sind in **Apache Spark** gemerged.
- Die Bibliothek für das binäre Encoding ist als **Open Source** verfügbar.
- Delta-Lake-Protokollunterstützung erfolgt über einen **RFC**.
- Enthalten ab **Apache Spark 4.0** und **Delta Lake 4.0**.
- Auf Databricks standardmäßig aktiviert ab **Databricks Runtime 15.3** (zum Zeitpunkt der Blog-Veröffentlichung Public Preview; inzwischen GA — siehe Blog *„Ingest semi-structured data faster and more efficiently with Variant – Now Generally Available"*).

**Daten laden (laut Blog):** über Tabellenspalten vom Typ `VARIANT`, die Funktion `PARSE_JSON()` zum Konvertieren von JSON-Strings, `CTAS`-Abfragen sowie `COPY INTO` für JSON-Ingestion. Pfadnavigation über intuitive **Dot-Notation**.

**Erweiterung *Shredding / Sub-Columnarization*** — im Blog von 2024 noch als geplant beschrieben, inzwischen ausgeliefert (Databricks Runtime 17.3): häufig genutzte Pfade innerhalb der Variant-Daten werden separat spaltenweise in den Parquet-Dateien gespeichert, um Abfragen auf diese Pfade zu beschleunigen (siehe [16 Variant Shredding.md](16%20Variant%20Shredding.md)).

---

## 4. Verwandte Themen

- **SQL-Datentyp-Referenz** (`VARIANT`-Syntax, `to_variant_object`, Literale, Beispiele): [05 SQL Language/04 Datentypen/01 VARIANT.md](../../../05%20SQL%20Language/04%20Datentypen/01%20VARIANT.md).
- **Variant abfragen** (`parse_json`, `:`-Operator, `variant_get`, `try_variant_get`, `is_variant_null`, `schema_of_variant`, `variant_explode`/`variant_explode_outer`, Casting): Doku *Query variant data* (`/aws/en/semi-structured/variant`); im Projekt siehe [12 Query Data/02 Semi-strukturierte Daten/01 JSON-Strings abfragen.md](../../../12%20Query%20Data/02%20Semi-strukturierte%20Daten/01%20JSON-Strings%20abfragen.md).
- **Variant vs. JSON-Strings:** Doku *How is variant different than JSON strings?* (`/aws/en/semi-structured/variant-json-diff`).
- **Variant als Ingestion-Ziel:** Doku *Ingest data as semi-structured variant type* (`/aws/en/ingestion/variant`).
- **Performance-Optimierung für häufig genutzte Felder:** [16 Variant Shredding.md](16%20Variant%20Shredding.md).
- **Runtime-Anforderungen und Protokollversion im Gesamtüberblick:** [08 Feature Compatibility.md](08%20Feature%20Compatibility.md).

---

## Quellen

- Variant type support for Apache Iceberg and Delta Lake (Feature-Doku): https://docs.databricks.com/aws/en/tables/features/variant
- Introducing the Open Variant Data Type in Delta Lake and Apache Spark (Blog): https://www.databricks.com/blog/introducing-open-variant-data-type-delta-lake-and-apache-spark
- Say goodbye to messy JSON headaches with VARIANT (Video, 2024-06-24): https://www.youtube.com/watch?v=fWdxF7nL3YI
- Variant Data Type – Making Semi-Structured Data Fast and Simple (Data + AI Summit 2024, Video): https://www.youtube.com/watch?v=jtjOfggD4YY · Session: https://www.databricks.com/dataaisummit/session/variant-data-type-making-semi-structured-data-fast-and-simple

**Stand:** 2026-09-02.
