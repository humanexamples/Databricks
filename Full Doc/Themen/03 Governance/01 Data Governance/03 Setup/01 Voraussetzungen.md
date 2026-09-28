# Voraussetzungen für Unity Catalog

## Regionale Verfügbarkeit

Alle Regionen unterstützen Unity Catalog.

## Compute-Anforderungen

- Cluster benötigen mindestens **Databricks Runtime 11.3 LTS**.
- SQL-Warehouses unterstützen Unity Catalog standardmäßig.
- Cluster müssen im **Standard- oder Dedicated Access Mode** laufen, um auf Unity-Catalog-Daten zuzugreifen.

## Unterstützte Dateiformate

| Tabellentyp | Unterstützte Formate |
|---|---|
| Managed Tables | nur Delta oder Iceberg |
| External Tables | Delta, CSV, JSON, Avro, Parquet, ORC, Text |

## Namensregeln

- Maximal 255 Zeichen pro Objektname.
- Verbotene Zeichen: Punkte, Leerzeichen, Schrägstriche, ASCII-Steuerzeichen (00–1F hex), DELETE-Zeichen (7F hex).
- Unity Catalog speichert alle Objektnamen **klein geschrieben**.
- Sonderzeichen wie Bindestriche müssen in SQL mit Backticks maskiert werden.

## Wichtige Einschränkungen

- Workspace-Gruppen können nicht in `GRANT`-Anweisungen verwendet werden — stattdessen Account-Gruppen nutzen.
- R-Workloads benötigen Runtime 15.4 LTS+ für dynamische View-Sicherheit.
- Managed Tables benötigen Runtime 13.3 LTS+; External Tables benötigen 14.2+ für Shallow Clone.
- Bucketing wird nicht unterstützt.
- Python-UDFs benötigen Runtime 13.3 LTS+.
- Standard-Scala-Thread-Pools sind untersagt — stattdessen `org.apache.spark.util.ThreadUtils` verwenden.

## Ressourcen-Kontingente

Unity Catalog erzwingt Kontingente (Quotas) für schützbare Objekte. Die Nutzung lässt sich über die Resource-Quotas-APIs überwachen.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/requirements
