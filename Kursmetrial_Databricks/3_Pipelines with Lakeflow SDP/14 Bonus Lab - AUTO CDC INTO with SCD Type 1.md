

In diesem Lab verwenden Sie Change Data Capture (CDC), um Änderungen zu erkennen und sie mit SCD-Type-1-Logik anzuwenden (Überschreiben, keine historischen Datensätze).

##### 

```sql
-- Die leere Streaming Table erstellen
CREATE OR REFRESH STREAMING TABLE tblSilver;

-- CDC SCD Type 1 durchführen
CREATE FLOW scd_type_1_flow AS
AUTO CDC INTO tblSilver  -- Zieltabelle, die mit SCD Type 1 (oder 2) aktualisiert wird
FROM STREAM tblBronze      -- Quell-Streaming-Table
KEYS (EmployeeID)
APPLY AS DELETE WHEN Operation = 'delete'
SEQUENCE BY ProcessDate
COLUMNS * EXCEPT (Operation)
STORED AS SCD TYPE 1;
```

