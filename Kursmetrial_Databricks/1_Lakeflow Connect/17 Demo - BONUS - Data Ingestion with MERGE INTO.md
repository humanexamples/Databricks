```sql
MERGE INTO target t
USING source s
ON {merge_condition}
WHEN MATCHED THEN {matched_action}
WHEN NOT MATCHED THEN {not_matched_action}
```

```sql
MERGE INTO main_users_target target
USING update_users_source source
ON target.id = source.id
WHEN MATCHED AND source.status = 'update' THEN
  UPDATE SET 
    target.email = source.email,
    target.status = source.status
WHEN MATCHED AND source.status = 'delete' THEN
  DELETE
WHEN NOT MATCHED THEN
  INSERT (id, first_name, email, sign_up_date, status)
  VALUES (source.id, source.first_name, source.email, source.sign_up_date, source.status);
```

```sql
--------------------------------------------
-- Diese Abfrage gibt einen FEHLER zurück
--------------------------------------------

MERGE INTO main_users_target target
USING new_users_source source
ON target.id = source.id
WHEN MATCHED AND source.status = 'update' THEN
  UPDATE SET 
    target.email = source.email,
    target.status = source.status
WHEN MATCHED AND source.status = 'delete' THEN
  DELETE
WHEN NOT MATCHED AND source.status = 'new' THEN
  INSERT (id, first_name, email, sign_up_date, status, country)
  VALUES (source.id, source.first_name, source.email, source.sign_up_date, source.status, source.country);
```

Sie müssen Schema Evolution explizit aktivieren, um das Schema der Zieltabelle weiterzuentwickeln. Ab Databricks Runtime 15.2 können Sie Schema Evolution in einer Merge-Anweisung per SQL mit der Anweisung `MERGE WITH SCHEMA EVOLUTION INTO` angeben. Sie können auch die Spark-Konfiguration `spark.databricks.delta.schema.autoMerge.enabled` für die aktuelle SparkSession auf *true* setzen. Weitere Informationen finden Sie auf der Dokumentationsseite [Enable schema evolution](https://docs.databricks.com/en/delta/update-schema.html#enable-schema-evolution).

```sql
-- Die Anweisung MERGE WITH SCHEMA EVOLUTION INTO verwenden
MERGE WITH SCHEMA EVOLUTION INTO main_users_target target  
USING new_users_source source
ON target.id = source.id
WHEN MATCHED AND source.status = 'update' THEN
  UPDATE SET 
    target.email = source.email,
    target.status = source.status
WHEN MATCHED AND source.status = 'delete' THEN
  DELETE
WHEN NOT MATCHED AND source.status = 'new' THEN
  INSERT (id, first_name, email, sign_up_date, status, country)
  VALUES (source.id, source.first_name, source.email, source.sign_up_date, source.status, source.country);
```
