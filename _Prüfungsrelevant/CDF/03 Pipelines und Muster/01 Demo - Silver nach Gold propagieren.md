[← Übersicht](../00%20Uebersicht.md)

# Demo: Änderungen von Silver nach Gold propagieren

> Quelle: offizielles Databricks-Notebook [Change data feed demo](https://docs.databricks.com/aws/en/notebooks/source/delta/cdf-demo.html) (Python/SQL, 23 Zellen; vollständig übernommen)

**Szenario:** Eine Silver-Tabelle zählt pro Land die geimpften Personen und verfügbaren Dosen. Eine Gold-Tabelle berechnet daraus die Impfquote. Wenn sich Silver ändert, sollen **nur die Änderungen** nach Gold übertragen werden.

**Kombination:** Legacy-CDF · `table_changes()` · Window-Funktion `rank()` · `MERGE INTO`

---

## 1. Silver-Tabelle anlegen

Tracks absolute number vaccinations and available doses by country:

```python
countries = [("USA", 10000, 20000), ("India", 1000, 1500), ("UK", 7000, 10000), ("Canada", 500, 700) ]
columns = ["Country","NumVaccinated","AvailableDoses"]
spark.createDataFrame(data=countries, schema = columns).write.format("delta").mode("overwrite").saveAsTable("silverTable")
```

```sql
%sql
SELECT * FROM silverTable
```

## 2. Gold-Tabelle mit der Impfquote erzeugen

```python
import pyspark.sql.functions as F
spark.read.format("delta").table("silverTable").withColumn("VaccinationRate", F.col("NumVaccinated") / F.col("AvailableDoses")) \
  .drop("NumVaccinated").drop("AvailableDoses") \
  .write.format("delta").mode("overwrite").saveAsTable("goldTable")
```

```sql
%sql
SELECT * FROM goldTable
```

## 3. CDF auf Silver einschalten

```sql
%sql
ALTER TABLE silverTable SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
```

> Erst **ab hier** zeichnet die Tabelle Änderungen auf. Die Anlage (Version 0) und das Setzen der Eigenschaft (Version 1) liegen vor bzw. auf dem Aktivierungspunkt, deshalb liest das Notebook später **ab Version 2**.

## 4. Silver täglich aktualisieren: Insert, Update, Delete

```python
# Insert new records
new_countries = [("Australia", 100, 3000)]
spark.createDataFrame(data=new_countries, schema = columns).write.format("delta").mode("append").saveAsTable("silverTable")
```

```sql
%sql
-- update a record
UPDATE silverTable SET NumVaccinated = '11000' WHERE Country = 'USA'
```

```sql
%sql
-- delete a record
DELETE from silverTable WHERE Country = 'UK'
```

```sql
%sql
SELECT * FROM silverTable
```

Die drei Operationen erzeugen die Versionen **2** (Insert), **3** (Update) und **4** (Delete).

## 5. Änderungen in SQL und PySpark ansehen

```sql
%sql
-- view the changes
SELECT * FROM table_changes('silverTable', 2, 5) order by _commit_timestamp
```

```python
changes_df = spark.read.format("delta").option("readChangeData", True).option("startingVersion", 2).table('silverTable')
display(changes_df)
```

> Das Notebook verwendet noch den Alias **`readChangeData`**. Aktuelle Doku-Beispiele nutzen `readChangeFeed`; beide Namen sind gültig.

## 6. Änderungen nach Gold übertragen

**Schritt 1:** Pro Land nur die neueste Änderung behalten, ohne `update_preimage`:

```sql
%sql
-- Collect only the latest version for each country
CREATE OR REPLACE TEMPORARY VIEW silverTable_latest_version as
SELECT *
    FROM
         (SELECT *, rank() over (partition by Country order by _commit_version desc) as rank
          FROM table_changes('silverTable', 2, 5)
          WHERE _change_type !='update_preimage')
    WHERE rank=1
```

**Schritt 2:** Mit `MERGE` in Gold übernehmen:

```sql
%sql
-- Merge the changes to gold
MERGE INTO goldTable t USING silverTable_latest_version s ON s.Country = t.Country
        WHEN MATCHED AND s._change_type='update_postimage' THEN UPDATE SET VaccinationRate = s.NumVaccinated/s.AvailableDoses
        WHEN NOT MATCHED THEN INSERT (Country, VaccinationRate) VALUES (s.Country, s.NumVaccinated/s.AvailableDoses)
```

```sql
%sql
SELECT * FROM goldTable
```

## 7. Aufräumen

```sql
%sql
DROP TABLE silverTable;
DROP TABLE goldTable;
```

---

## Einordnung und Grenzen des Demo-Musters

| Baustein | Aufgabe |
|---|---|
| `table_changes('silverTable', 2, 5)` | liest die Änderungen ab Version 2. Die Endversion 5 liegt hinter dem letzten Commit (4); zum Verhalten bei Versionen außerhalb des Bereichs siehe [02/01 Batch](../02%20Lesen/01%20Batch%20-%20table_changes%20und%20readChangeFeed.md) |
| `WHERE _change_type != 'update_preimage'` | alte Werte vor Updates werden nicht gebraucht |
| `rank() … ORDER BY _commit_version DESC` → `rank = 1` | nur die jüngste Änderung pro Land |
| `MERGE` | Update bei `update_postimage`, Insert bei neuen Ländern |

**Was die Demo nicht abdeckt:**

- **Deletes:** Die `MERGE`-Anweisung hat keinen `WHEN MATCHED … THEN DELETE`-Zweig. „UK“ wird in Silver gelöscht, bleibt aber in Gold stehen. Eine Variante mit Delete-Zweig steht in [../../CDC/04 Change Data Feed – Änderungen weiterreichen](../../CDC/04%20Change%20Data%20Feed%20-%20Aenderungen%20weiterreichen.md).
- **Feste Versionsgrenzen:** Die Versionen 2 bis 5 sind hartkodiert. In Produktion übernimmt ein **Stream mit Checkpoint** diese Buchführung → [02 Streaming](../02%20Lesen/02%20Streaming%20-%20readStream%20und%20Optionen.md).
- Deklarativ geht dasselbe mit **AUTO CDC** → [02 CDF und AUTO CDC](02%20CDF%20und%20AUTO%20CDC.md).

---
[← Übersicht](../00%20Uebersicht.md) · [Nächste Datei →](02%20CDF%20und%20AUTO%20CDC.md)
