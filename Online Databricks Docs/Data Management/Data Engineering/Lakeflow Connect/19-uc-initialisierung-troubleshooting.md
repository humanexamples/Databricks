# Fehlerbehebung: UNITY_CATALOG_INITIALIZATION_FAILED

Der Fehler `UNITY_CATALOG_INITIALIZATION_FAILED` tritt auf, wenn Unity Catalog beim Cluster-Start den Speicher nicht initialisieren kann. Trotz des Namens liegt die Ursache meist an Infrastrukturproblemen – insbesondere Netzwerk- oder Cloud-Speicher-Berechtigungsproblemen – statt an einer Fehlkonfiguration von Unity Catalog.

## Allgemeine Fehlermeldung

Die angezeigte Meldung lautet sinngemäß: „Ensure that your Unity Catalog configuration is correct, and that required resources exist and are accessible.“ Die eigentliche Ursache liegt jedoch häufig im Netzwerk oder bei Berechtigungen, nicht in der Konfiguration.

## Ursache 1: Fehlkonfiguration von PrivateLink oder Customer-Managed-VPC-DNS

**Problem:** Unity Catalog verbindet sich mit regionalen Databricks-Hostnamen (z. B. `nvirginia.cloud.databricks.com`), die das Private-Link-Routing umgehen können, wenn Private DNS nicht aktiviert ist – das führt zu Verbindungsfehlern in abgeschotteten VPCs.

**Lösung:**

- In AWS unter VPC > Endpoints den Endpoint des Databricks-Workspace öffnen.
- Prüfen, ob „Private DNS names enabled“ auf **Yes** steht.
- Sicherstellen, dass in den VPC-Einstellungen `enableDnsSupport` und `enableDnsHostnames` beide auf `true` stehen.
- Private DNS Names aktivieren, falls deaktiviert, und anschließend prüfen, ob die regionalen Hostnamen zu privaten IPs aufgelöst werden.

## Ursache 2: Fehlende S3-Berechtigungen für den Unity-Catalog-Speicher

**Problem:** Die IAM-Rolle des Serverless-Compute-Clusters hat keine ausreichenden Berechtigungen für den S3-Bucket des Unity-Catalog-Metastores, insbesondere für den Pfad `__unitystorage`.

**Lösung:**

- Den Metastore-Bucket anhand der Fehlerprotokolle identifizieren (Format: `s3://[BUCKET]/__unitystorage/...`).
- Prüfen, ob die IAM-Rolle folgende S3-Berechtigungen besitzt: `GetObject`, `PutObject`, `DeleteObject`, `ListBucket`, `GetBucketLocation`.
- Bei Nutzung einer Network Connectivity Configuration (NCC) prüfen, ob deren Private-Endpoint-Regel den UC-Metastore-Bucket abdeckt.
- Die Pipeline nach den Änderungen neu starten.

## Ursache 3: Unity-Catalog-Ressourcen nicht korrekt konfiguriert

**Problem:** Referenzierte Kataloge, Schemata oder Verbindungen existieren nicht oder sind nicht zugänglich.

**Lösung:**

- Existenz und Zugänglichkeit von Katalog und Schema im Databricks-Catalog-Interface prüfen.
- Sicherstellen, dass die Berechtigungen `USE CATALOG` und `USE SCHEMA` vorhanden sind.
- Bei Lakeflow Connect die Verbindung über Catalog > External Data > Connections prüfen.
- Sicherstellen, dass Cluster/Pipeline über die nötigen Unity-Catalog-Berechtigungen verfügen.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/uc-initialization-troubleshoot  
**Stand:** 2026-08-07
