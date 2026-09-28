While this course focuses on LakeFlow Connect managed connectors, there are other ingestion features in Databricks that may be useful as your architecture evolves.

## Lakehouse Federation

Allows you to **query external data sources** without moving your data.

Especially useful for:
- **Ad hoc reporting**
- Proof-of-concept work
- The **exploratory phase** of new ETL pipelines or reports
- Supporting workloads during **incremental migration**

[What is Lakehouse Federation](https://docs.databricks.com/aws/en/query-federation/)
[Lakehouse Federation: Discover, query and govern your data — no matter where it lives](https://www.databricks.com/resources/demos/videos/governance/lakehouse-federation)

## Zerobus 

A LakeFlow Connect API that allows developers to write event data directly to their lakehouse at very high throughput (100 MB/s) with near real-time latency (<5 seconds).

Simplify ingestion for:
- IOT
- Clickstreams
- Telemetry, and more

[Eliminate Hops in Your Streaming Architecture with Zerobus, Part of LakeFlow Connect](https://www.databricks.com/dataaisummit)
[Announcing the General Availability of Databricks LakeFlow](https://www.databricks.com/blog/announcing-general-availability-databricks-lakeflow)

## Delta Sharing

Allows you to securely share data across platforms, clouds, and regions.

[Delta Sharing Demo](https://www.databricks.com/resources/demos/videos/data-sharing/delta-sharing)
[What is Delta Sharing documentation](https://docs.databricks.com/aws/en/opensharing)

## Databricks Marketplace

Databricks Marketplace ist ein offener Marktplatz für Data-, Analytics- und AI-Assets, technisch auf dem offenen Sharing-Protokoll von Databricks aufgesetzt (früher als „Delta Sharing" bezeichnet, in aktueller Doku auch „OpenSharing" genannt). Angeboten werden u. a.:

- Datasets
- Notebooks
- Dashboards
- ML Models
- Solution Accelerators

### Zugriff in 3 Schritten

1. **Marketplace öffnen** — über das Symbol in der linken Sidebar des Workspace (alternativ über die öffentliche Marketplace-Website ohne eigenen Workspace erreichbar).
2. **Asset suchen** — per Suchleiste nach Name, Kategorie oder Anbieter filtern; für den Einstieg eignen sich die von Databricks selbst bereitgestellten Assets, da sie gut dokumentiert sind.
3. **„Get instant access" klicken** — Nutzungsbedingungen akzeptieren, optional den Zielkatalog-Namen anpassen, erneut bestätigen. Bei kostenlosen Listings erfolgt der Zugriff sofort ohne Freigabeprozess; manche Anbieter-Listings erfordern dagegen eine Freigabe durch den Anbieter.

### Danach

- Das Asset erscheint automatisch als **schreibgeschützter Katalog in Unity Catalog** (sichtbar im Catalog Explorer) — keine manuelle Katalog-Anbindung nötig.
- Die Daten bleiben **live beim Anbieter** und werden nicht in den eigenen Workspace kopiert; Abfragen laufen direkt über das Sharing-Protokoll gegen die aktuellen Anbieterdaten.
- Zugriff erfolgt direkt über SQL, Notebooks oder Dashboards wie bei jeder anderen Unity-Catalog-Tabelle.

[What is Databricks Marketplace](https://docs.databricks.com/aws/en/marketplace/)
[OpenSharing / Delta Sharing Dokumentation](https://docs.databricks.com/aws/en/opensharing)
