# Delta Lake: Einschränkungen auf Amazon S3

Delta Lake auf Amazon S3 hat einige Besonderheiten. Diese Seite fasst die wichtigsten Einschränkungen zusammen.

## Bucket-Versionierung und Delta Lake

Databricks rät davon ab, die Bucket-Versionierung auf S3-Buckets zu aktivieren, die Delta-Lake-Daten speichern. Delta Lake hat eine eigene Versionierung. S3-Versionierung führt dazu, dass Dateien erhalten bleiben, die Delta Lake bereits als gelöscht betrachtet. Das betrifft auch Dateien, die durch `VACUUM`-Operationen entfernt wurden, sowie Transaktionsprotokolle.

Empfehlung: Wird Bucket-Versionierung dennoch genutzt, empfiehlt Databricks, nur drei Versionen vorzuhalten und eine Lifecycle-Management-Richtlinie einzurichten, die Versionen nach maximal 7 Tagen löscht.

## Einschränkungen bei Multi-Cluster-Schreibzugriffen

Wichtiger Hinweis: Databricks empfiehlt, dieselbe Delta-Lake-Tabelle auf S3 nicht aus unterschiedlichen Workspaces heraus zu verändern.

Das Eventual-Consistency-Modell von S3 birgt Risiken, wenn mehrere Cluster gleichzeitig dieselbe Tabelle ändern. Innerhalb eines einzelnen Workspace werden Multi-Cluster-Schreibzugriffe unterstützt. Nicht unterstützt werden sie jedoch bei:

- Server-seitiger Verschlüsselung mit vom Kunden bereitgestellten Schlüsseln (Server-Side Encryption with Customer-Provided Encryption Keys)
- S3-Pfaden mit eingebetteten Zugangsdaten in Clustern ohne Zugriff auf den AWS Security Token Service

Die zugehörige Konfigurationseinstellung lautet `spark.databricks.delta.multiClusterWrites.enabled`. Der Standardwert ist `true`.

## Risiken beim Löschen von Dateien

Delta-Lake-Tabellen sollten nicht mit `rm -rf` gelöscht werden. Das kann zu veralteten, inkonsistenten Daten führen.

---
**Quelle:** https://docs.databricks.com/aws/en/delta/s3-limitations  
**Stand:** 2026-08-06
