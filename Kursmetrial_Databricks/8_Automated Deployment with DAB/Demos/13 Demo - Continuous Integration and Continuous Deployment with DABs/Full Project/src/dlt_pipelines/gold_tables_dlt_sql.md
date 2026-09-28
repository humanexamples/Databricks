# 13 Demo - Continuous Integration and Continuous Deployment with DABs/Full Project/src/dlt_pipelines/gold_tables_dlt.sql

```sql
-- DLT Gold Table(s)

CREATE OR REFRESH MATERIALIZED VIEW chol_age_agg
AS
SELECT 
    HighCholest_Group, 
    Age_Group, 
    count(*) as Total
FROM LIVE.health_silver
GROUP BY HighCholest_Group, Age_Group
```
