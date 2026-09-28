Diese Lektion zeigt außerdem, wie `MERGE INTO` die Ingestion in bestehende Delta-Tabellen vereinfacht, indem Updates, Inserts und Deletes aus einer Quelle in einer einzigen atomaren Operation angewendet werden.

MERGE INTO unterstützt **Schema Enforcement** oder **Schema Evolution** und ermöglicht unterschiedliche Aktionen, je nachdem, ob eine Zeile zwischen Quell- und Zieltabelle übereinstimmt:

**Übereinstimmende Zeilen (Matched)**
UPDATE oder DELETE

**Nicht übereinstimmende Zeilen laut Ziel (Unmatched by target)**
INSERT

**Nicht übereinstimmende Zeilen laut Quelle (Unmatched by source)**
UPDATE oder DELETE

```sql
MERGE INTO target_table target
USING source_table source
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
