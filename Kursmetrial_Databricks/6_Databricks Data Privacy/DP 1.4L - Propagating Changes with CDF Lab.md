

In dieser Übung arbeiten wir mit den Fitness-Tracker-Datensätzen, um Änderungen mithilfe von Delta Lake Change Data Feed (CDF) durch ein Lakehouse zu propagieren.

Da die Tabelle **user_lookup** Identifikationsinformationen zwischen verschiedenen Pipelines verknüpft, machen wir sie zum Ausgangspunkt, von dem aus die Änderungen weitergegeben werden.

```sql
-- Aktivieren Sie Change Data Feed für die Tabelle **user_lookup**
ALTER TABLE user_lookup                              -- Tabellenname
SET TBLPROPERTIES (delta.enableChangeDataFeed=True)  -- Eigenschaft = True
```

```sql
-- Bestätigen Sie, dass für diese Tabelle `delta.enableChangeDataFeed` aktiviert ist.
DESCRIBE TABLE EXTENDED user_lookup;
```

```sql
-- Bestätigen Sie, dass der Eintrag als Version `1` im Verlauf der 
-- Tabelle **user_lookup** erscheint und dass die Spalte **operation** 
-- 'SET TBLPROPERTIES' enthält.

DESCRIBE HISTORY user_lookup;
```

```sql
-- Variable für die zu löschende user_id definieren
DECLARE OR REPLACE VARIABLE user_id INT DEFAULT 11745;

-- Die Variable in der DELETE-Anweisung verwenden
DELETE FROM user_lookup 
WHERE user_id = session.user_id;
```

## I. CDF-Ausgabe von user_lookup lesen (ab Version 1)

```sql
-- So lesen Sie die CDF-Daten:
-- 1. Verwenden Sie die Funktion 'table_changes'
-- 2. Wählen Sie alle Änderungen ab Version **1** der Tabelle **user_lookup** aus
SELECT * 
FROM table_changes("user_lookup", 1);
```

```python
## So lesen Sie die CDF Daten mit Python
user_lookup_df = (spark
                  .read
                  .format("delta")
                  .option("readChangeData", True) # Änderungsdaten lesen
                  .option("startingVersion", 1)  # Startversion für das Lesen
                  .table("user_lookup")
)
```

## J. Löschvorgänge an mehrere Tabellen weitergeben

```sql
-- Eine temporäre View der CDF-Änderungen der Tabelle user_lookup erstellen
CREATE OR REPLACE TEMPORARY VIEW user_lookup_deletes_vw AS
SELECT * 
FROM table_changes('user_lookup',2)
WHERE _change_type ='delete';
```

- Verwenden Sie die [MERGE INTO](https://docs.databricks.com/en/sql/language-manual/delta-merge-into.html)-Syntax:
```sql
MERGE [ WITH SCHEMA EVOLUTION ] INTO target_table_name [target_alias]
   USING source_table_reference [source_alias]
   ON merge_condition
   { WHEN MATCHED [ AND matched_condition ] THEN matched_action |
     WHEN NOT MATCHED [BY TARGET] [ AND not_matched_condition ] THEN not_matched_action |
     WHEN NOT MATCHED BY SOURCE [ AND not_matched_by_source_condition ] THEN not_matched_by_source_action } [...]

matched_action
 { DELETE |
   UPDATE SET * |
   UPDATE SET { column = { expr | DEFAULT } } [, ...] }

not_matched_action
 { INSERT * |
   INSERT (column1 [, ...] ) VALUES ( expr | DEFAULT ] [, ...] )

not_matched_by_source_action
 { DELETE |
   UPDATE SET { column = { expr | DEFAULT } } [, ...] }


```

```sql
-- Führen Sie einen Merge mit 'user_lookup_deletes_vw' als Quelle in 
-- die Tabelle 'users' durch und 'DELETE' Sie, wenn **alt_id** übereinstimmt.
MERGE INTO users u
USING user_lookup_deletes_vw ul
ON u.alt_id = ul.alt_id
WHEN MATCHED THEN DELETE;

-- Führen Sie einen Merge mit 'user_lookup_deletes_vw' als Quelle in 
-- die Tabelle 'users_bin' durch und 'DELETE' Sie, wenn 'alt_id' übereinstimmt.
MERGE INTO users_bin ub
USING user_lookup_deletes_vw ul
ON ub.user_id = ul.user_id
WHEN MATCHED THEN DELETE;
```
