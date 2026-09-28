# 14L Bonus - Adding ML to Engineering Workflows with DABs/Solution - Lab DABs Workflow/src/dlt_pipelines/silver_sample_dlt.sql

```sql
-- Sample Silver Table for ML Task
CREATE OR REFRESH MATERIALIZED VIEW silver_sample_ml
AS
SELECT 
    *
FROM health_silver
LIMIT 2;
```
