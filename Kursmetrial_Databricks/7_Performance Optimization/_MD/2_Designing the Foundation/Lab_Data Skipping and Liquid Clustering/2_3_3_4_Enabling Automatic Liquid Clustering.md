#### Enabling Automatic Liquid Clustering

Verwenden Sie **`CLUSTER BY AUTO`** beim Erstellen einer neuen Tabelle oder beim Ändern einer bestehenden Tabelle. Führen Sie **`DESCRIBE TABLE EXTENDED`** aus, um zu bestätigen, dass es aktiviert ist — achten Sie in den Tabelleneigenschaften auf **`clusterByAuto = true`**.

```python
## my_catalog verwenden
spark.sql(f"USE CATALOG {my_catalog}")

## Schema verwenden
spark.sql(f"USE SCHEMA {schema}")
```

```sql
-- Bei einer neuen Tabelle aktivieren
CREATE OR REPLACE TABLE auto_clustered_example (
  id BIGINT,
  transaction_date DATE,
  customer_id STRING,
  amount DOUBLE,
  region STRING
) CLUSTER BY AUTO;

-- Oder bei einer bestehenden unpartitionierten / liquid clustered Tabelle aktivieren
-- ALTER TABLE my_existing_table CLUSTER BY AUTO;
```

```sql
-- Überprüfen: nach "clusterByAuto = true" suchen und clusteringColumns auf ausgewählte Keys prüfen
DESCRIBE TABLE EXTENDED auto_clustered_example;
```

**Output:**

- **Table Properties:** [**clusterByAuto=true**,clusteringColumns=[],delta.checkpointPolicy=v2,delta.enableDeletionVectors=true,delta.enableRowTracking=true,delta.feature.clustering=supported,delta.feature.deletionVectors=supported,delta.feature.domainMetadata=supported,delta.feature.rowTracking=supported,delta.feature.v2Checkpoint=supported,delta.minReaderVersion=3,delta.minWriterVersion=7,delta.rowTracking.materializedRowCommitVersionColumnName=_row-commit-version-col-b5e731e7-bd5e-4f0d-b12c-fd72e9f402fd,delta.rowTracking.materializedRowIdColumnName=_row-id-col-0a5a6e87-5d12-4f47-89a6-ca0b5b3b49c3]

------

**Warum Sie möglicherweise nicht sofort ausgewählte Clustering-Keys sehen**

Nachdem Sie `CLUSTER BY AUTO` aktiviert haben, werden **nicht** sofort Clustering-Keys angezeigt. Predictive Optimization muss zunächst eine **ausreichende Query-History** für die Tabelle sammeln — es analysiert historische Query-Scan-Statistiken, um zu bestimmen, welche Spalten sich für das Clustering eignen. Die Auswahl der Keys erfolgt als Hintergrund-Wartungsoperation nach einem eigenen Zeitplan, nicht zum Zeitpunkt des Queries.

Es kann sein, dass keine Keys ausgewählt werden, wenn die Tabelle zu klein ist, zu wenige Queries vorliegen, wiederkehrende Filtermuster fehlen oder die Kosten-Nutzen-Analyse ergibt, dass Clustering keinen nennenswerten Vorteil bringen würde. In einer Live-Kursumgebung bedeutet dies, dass das Feld `clusteringColumns` in `DESCRIBE TABLE EXTENDED` während der Demo wahrscheinlich leer bleibt. Dies ist das erwartete Verhalten — Automatic Liquid Clustering ist für Produktions-Workloads konzipiert, die über Tage und Wochen laufen, nicht für kurzlebige Demo-Tabellen.

```sql
DROP TABLE IF EXISTS auto_clustered_example;
```

