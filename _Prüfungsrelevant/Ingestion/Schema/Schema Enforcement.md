# Schema Enforcement

**Schema Enforcement** = Databricks setzt beim Schreiben das Tabellenschema durch und **weist Schreibvorgänge ab**, die nicht dazu passen — Datenqualitäts-Validierung „an der Tür".

- Gilt **nur für Delta-Lake-Tabellen**. *"Schema enforcement does not apply to tables with non-Delta formats, such as CSV or JSON files stored in cloud storage."*
- Gegenstück: **Schema Evolution** — kontrollierte Änderung des Schemas (siehe eigene Datei).

---

## `INSERT`-Operationen

Zwei Regeln:

1. **Alle eingefügten Spalten müssen in der Zieltabelle existieren.**
2. **Die Datentypen müssen zum Zieltabellen-Schema passen** — Databricks *"attempts to safely cast column data types to match the target table."*

```sql
-- Ablehnung: Spalte existiert nicht im Ziel
INSERT INTO catalog.schema.target_table (id, unknown_column) VALUES (1, 'value');
-- Fehler: UNRESOLVED_COLUMN.WITH_SUGGESTION (SQLSTATE 42703) — schlägt gültige Spaltennamen vor
```

```sql
-- Erfolg: sicherer automatischer Cast
INSERT INTO catalog.schema.target_table (id, bigint_column) VALUES (1, 42);
-- Integer 42 wird sicher zu BIGINT gecastet
```

---

## `MERGE`-Operationen

Durchgesetzte Regeln:

- *"If the data type in the source statement does not match the target column, `MERGE` tries to safely cast column data types to match the target table."*
- Die Ziel-Spalten von `UPDATE`- und `INSERT`-Aktionen **müssen in der Zieltabelle existieren**.
- Bei `INSERT *` / `UPDATE SET *`: die Quelle muss **alle** Zielspalten enthalten; zusätzliche Quellspalten werden **ignoriert**.

```sql
-- Ablehnung: nicht existierende Spalte referenziert
MERGE INTO catalog.schema.target_table AS t
USING catalog.schema.source_table AS s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.unknown_column = s.name
WHEN NOT MATCHED THEN INSERT (id, unknown_column) VALUES (s.id, s.name);
-- Fehler: DELTA_MERGE_UNRESOLVED_EXPRESSION — listet die auflösbaren Spalten auf
```

```sql
-- Erfolg: Quelle enthält alle Zielspalten; extra_col wird ignoriert
MERGE INTO catalog.schema.target_table AS t
USING catalog.schema.source_table AS s
ON t.id = s.id
WHEN NOT MATCHED THEN INSERT *;
```

---

## Safe Cast — was gilt als „sicher"?

Der Safe-Cast-Versuch castet den **eingehenden Wert verlustfrei auf den bestehenden Zieltyp** (z. B. `int` → `bigint`), **ohne** den deklarierten Zieltyp zu ändern.

- Ändert sich der **Zieltyp selbst** (echtes Type Widening, z. B. `int`-Spalte wird `bigint`), braucht es zusätzlich aktivierte Schema Evolution **und** `delta.enableTypeWidening = true` — siehe [Schema Evolution.md](Schema%20Evolution.md).
- **Ungeklärt in der Doku:** vollständige Liste erlaubter/verbotener Casts und der konkrete Fehlertext bei nicht sicher castbaren Abweichungen (z. B. `string` → `int`-Zielspalte). Kandidaten aus der Fehlerklassen-Referenz: `CANNOT_UP_CAST_DATATYPE`, `CANNOT_MERGE_INCOMPATIBLE_DATA_TYPE` — beide **nicht** explizit als `MERGE`-spezifisch bestätigt.

---

## Schema ändern (statt abweisen)

- **Explizit:** `ALTER TABLE catalog.schema.table_name ADD COLUMN new_column STRING;`
- **Automatisch:** `mergeSchema` / `INSERT WITH SCHEMA EVOLUTION` / `MERGE WITH SCHEMA EVOLUTION` / `spark.databricks.delta.schema.autoMerge.enabled` — siehe [Schema Evolution.md](Schema%20Evolution.md).

```sql
SET spark.databricks.delta.schema.autoMerge.enabled = true;
INSERT INTO catalog.schema.table_name SELECT * FROM source_table;
```

```python
df.write.option("mergeSchema", "true").mode("append").saveAsTable("catalog.schema.table_name")
```

---

## External Tables

Ändern externe Clients die Metadaten einer External Table **außerhalb** von Databricks, synchronisiert Unity Catalog die Schema-Updates nicht automatisch → Enforcement kann beeinträchtigt sein. Resynchronisierung:

```sql
MSCK REPAIR TABLE <table-name> SYNC METADATA;
```

---

## Verwandte Themen

- [Schema Definition (StructType).md](Schema%20Definition%20%28StructType%29.md) · [Schema Evolution.md](Schema%20Evolution.md) · [Schema Inference.md](Schema%20Inference.md) · [Rescued Data.md](Rescued%20Data.md)
- Deep-Dive im Projekt: [01 Platform/02 Tables/06 Schema und Tabellenhistorie.md](01%20Platform/02%20Tables/06%20Schema%20und%20Tabellenhistorie.md) (Abschnitt 3)
- [01 Platform/02 Tables/07 Table Features/13 Type Widening.md](01%20Platform/02%20Tables/07%20Table%20Features/13%20Type%20Widening.md)
