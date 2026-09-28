[← Übersicht](00%20Uebersicht.md)

# SCD Type 2 manuell mit `MERGE`

**Kombination:** Delta `MERGE` · Merge-Key-Trick (`UNION ALL`) · Identity-Spalte als Surrogate Key · Liquid Clustering · `foreachBatch` · Timestamp-CDC

Der klassische Weg ohne Pipeline. Er zeigt, was AUTO CDC intern alles abnimmt, und kommt in Bestandsprojekten sehr häufig vor.

**Das Problem:** Ein geänderter Kunde braucht **zwei** Aktionen in einem `MERGE`: die alte Version schließen (`UPDATE`) **und** eine neue Version einfügen (`INSERT`). Ein `MERGE` führt pro Quellzeile aber nur **eine** Aktion aus.

**Der Trick:** Jeder geänderte Kunde steht zweimal in der Quelle, einmal mit seinem Key (→ trifft die alte Version → `UPDATE`) und einmal mit `merge_key = NULL` (→ trifft nichts → `INSERT`).

---

## Zieltabelle

```sql
CREATE TABLE IF NOT EXISTS catalog.schema.dim_customer_history (
  customer_sk BIGINT GENERATED ALWAYS AS IDENTITY,   -- Surrogate Key je Version
  customer_id BIGINT,                                -- natürlicher Key
  name        STRING,
  city        STRING,
  valid_from  TIMESTAMP,
  valid_to    TIMESTAMP,
  is_current  BOOLEAN
)
CLUSTER BY (customer_id, is_current);
```

## Quelle vorbereiten (ein Event pro Kunde)

```sql
CREATE OR REPLACE TEMP VIEW updates AS
SELECT customer_id, name, city, op, updated_at
FROM catalog.schema.customer_changes_batch
QUALIFY row_number() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) = 1;
```

## Das SCD-2-`MERGE`

```sql
MERGE INTO catalog.schema.dim_customer_history t
USING (
  -- a) jedes Event mit seinem Key:
  --    schließt die aktuelle Version (Änderung/Delete) oder fügt einen Neukunden ein
  SELECT u.customer_id AS merge_key, u.*
  FROM updates u

  UNION ALL

  -- b) geänderte Bestandskunden ein zweites Mal mit NULL-Key:
  --    trifft keine Zielzeile → erzeugt die neue Version
  SELECT NULL AS merge_key, u.*
  FROM updates u
  JOIN catalog.schema.dim_customer_history t
    ON u.customer_id = t.customer_id AND t.is_current
  WHERE u.op <> 'd'
    AND (NOT (u.name <=> t.name) OR NOT (u.city <=> t.city))
) s
ON t.customer_id = s.merge_key

-- Delete in der Quelle: aktuelle Version schließen, keine neue anlegen
WHEN MATCHED AND t.is_current AND s.op = 'd' THEN
  UPDATE SET is_current = false, valid_to = s.updated_at

-- Änderung: aktuelle Version schließen (die neue kommt über Zweig b)
WHEN MATCHED AND t.is_current
             AND (NOT (t.name <=> s.name) OR NOT (t.city <=> s.city)) THEN
  UPDATE SET is_current = false, valid_to = s.updated_at

-- Neukunde (Zweig a) oder neue Version (Zweig b)
WHEN NOT MATCHED AND s.op <> 'd' THEN
  INSERT (customer_id, name, city, valid_from, valid_to, is_current)
  VALUES (s.customer_id, s.name, s.city, s.updated_at, NULL, true);
```

## Was mit welchem Kunden passiert

| Fall | Zweig a (`merge_key = id`) | Zweig b (`merge_key = NULL`) | Ergebnis |
|---|---|---|---|
| Neukunde | trifft nichts → `INSERT` | – (kein Treffer im Join) | 1 neue aktive Zeile |
| geändert | trifft aktuelle Version → `UPDATE` (schließen) | trifft nichts → `INSERT` | alte Version geschlossen, neue aktiv |
| unverändert | trifft, aber Bedingung falsch → nichts | – (durch `WHERE` gefiltert) | keine Änderung |
| gelöscht | trifft → `UPDATE` (schließen) | – (`op <> 'd'`) | keine aktive Version mehr |

---

## Dasselbe im Stream (`foreachBatch`)

Das `MERGE` läuft pro Micro-Batch. Der Batch wird als Temp View registriert und das SQL wiederverwendet.

```python
SCD2_MERGE = """ ...das MERGE von oben, mit USING-Quelle `updates`... """

def apply_scd2(batch_df, batch_id):
    (batch_df
        .selectExpr("*", "row_number() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) AS _rn")
        .filter("_rn = 1").drop("_rn")
        .createOrReplaceTempView("updates"))
    batch_df.sparkSession.sql(SCD2_MERGE)

(spark.readStream.table("catalog.schema.customer_changes")
    .writeStream
    .foreachBatch(apply_scd2)
    .option("checkpointLocation", "/Volumes/catalog/schema/_checkpoints/dim_customer_history")
    .trigger(availableNow=True)
    .start())
```

Wichtig: `batch_df.sparkSession.sql(...)` statt `spark.sql(...)`, damit die Temp View des Batches sichtbar ist.

**Mit Timestamp-CDC kombinieren:** Im Job aus [../CDC/05](../CDC/05%20Timestamp-basiertes%20CDC%20mit%20Lakeflow%20Jobs.md) das SCD-1-`MERGE` durch dieses `MERGE` ersetzen. `op` ist dann `'d'` bei `is_deleted = true`, sonst `'u'`.

---

## Grenzen gegenüber AUTO CDC

| Aspekt | manuelles `MERGE` | AUTO CDC `STORED AS SCD TYPE 2` |
|---|---|---|
| Verspätete Events (älter als die aktuelle Version) | werden falsch als neueste Version eingefügt | werden korrekt in die Historie einsortiert |
| Mehrere Änderungen desselben Keys pro Batch | nur die letzte wird historisiert (Zwischenstände gehen verloren) | alle werden als Versionen angelegt |
| Nur bestimmte Spalten versionieren | Bedingungen selbst pflegen | `TRACK HISTORY ON …` |
| Code-Umfang | ~40 Zeilen, fehleranfällig | ~8 Zeilen |
| Laufzeitumgebung | beliebig (Notebook, Job, SQL Warehouse) | Lakeflow Pipeline |

Wenn Zwischenstände innerhalb eines Batches erhalten bleiben sollen, reicht der `row_number()`-Filter nicht. Dann müssen die Events pro Key nacheinander angewendet werden, was schnell komplex wird. Das ist der stärkste Grund für AUTO CDC.

---
[← Vorherige Datei](02%20SCD%20Type%202%20mit%20AUTO%20CDC.md) · [Übersicht](00%20Uebersicht.md) · [Nächste Datei →](04%20SCD%20im%20Star-Schema.md)

## Quellen

- [Upsert into a Delta Lake table using merge (SCD Type 2)](https://docs.databricks.com/aws/en/delta/merge)
- [Use foreachBatch to write to arbitrary data sinks](https://docs.databricks.com/aws/en/structured-streaming/foreach)
