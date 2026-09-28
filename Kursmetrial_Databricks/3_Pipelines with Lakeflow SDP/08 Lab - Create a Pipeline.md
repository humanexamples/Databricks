Migrieren Sie einen klassischen ETL-Workflow in eine Pipeline für inkrementelle Datenverarbeitung. Sie üben den Aufbau von Streaming 

Ihr Data-Engineering-Team hat die Möglichkeit erkannt, eine bestehende ETL-Pipeline zu modernisieren, die ursprünglich in einem Databricks-Notebook entwickelt wurde. Die aktuelle Pipeline erfüllt zwar ihren Zweck, es fehlen ihr aber die Skalierbarkeit, Observability, Effizienz und automatisierten Datenqualitätsfunktionen, die bei wachsendem Datenvolumen und steigender Komplexität erforderlich sind.



```sql
CREATE OR REPLACE TABLE tblBonze
-- CREATE OR REFRESH STREAMING TABLE tblBronze (SDP-Lösung)
AS SELECT 
  *,
  current_timestamp() AS ingestion_time,
  _metadata.file_name AS raw_file_name
FROM read_files(
-- FROM STREAM read_files(..) (SDP-Lösung)
  '/Volumes/' || my_catalog || '/sdp_lab_1_bronze/lab_files',
  format => 'CSV',
  -- Explizites Schema
  schema => '
    EmployeeID STRING,
    FirstName STRING,
    Country STRING,
    Department STRING,
    Salary DOUBLE,
    HireDate DATE,
    Operation STRING,
    ProcessDate DATE
  ',
  -- CSV-Parsing-Optionen
  header => 'true',
  inferSchema => 'false'
);


CREATE OR REPLACE TABLE tblSilver 
-- CREATE OR REFRESH STREAMING TABLE tblSilver (SDP-Lösung)
-- (
-- CONSTRAINT check_country EXPECT (Country IN ('US','GR')),
-- CONSTRAINT check_salary EXPECT (Salary > 0),
-- CONSTRAINT check_null_id EXPECT (EmployeeID IS NOT NULL) ON VIOLATION DROP ROW
-- )
AS
SELECT
  EmployeeID,
  FirstName,
  upper(Country) AS Country,
  Department,
  Salary,
  HireDate,
  date_format(HireDate, 'MMMM') AS HireMonthName,
  year(HireDate) AS HireYear, 
  Operation
FROM tblBronze;  


CREATE OR REPLACE VIEW tblGold1 
-- CREATE OR REFRESH MATERIALIZED VIEW tblGold1 (SDP-Lösung)
AS
SELECT 
  Country,
  count(*) AS TotalEmployees,
  sum(Salary) AS TotalSalary
FROM tblSilver
GROUP BY Country;


CREATE OR REPLACE VIEW tblGold2
-- CREATE OR REFRESH MATERIALIZED VIEW tblGold2 (SDP-Lösung)
AS
SELECT
  Department,
  sum(Salary) AS TotalSalary
FROM tblSilver
GROUP BY Department;
```

### Die Pipeline-Einstellungen für SDP anpassen

- Ihre Spark Declarative Pipeline sollte **Serverless**-Compute verwenden.  



