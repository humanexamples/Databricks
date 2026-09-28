# Was ist Unity Catalog?

Unity Catalog ist die **einheitliche Governance-Schicht für Daten und KI**, die fest in Databricks integriert ist. Sie erzwingt automatisch Zugriffskontrolle, verfolgt Lineage und protokolliert Aktivitäten über Daten- und KI-Interaktionen hinweg — workspaceübergreifend.

- **Automatisch aktiv:** Alle nach dem 8. November 2023 erstellten Workspaces haben Unity Catalog standardmäßig aktiviert.
- **Governance-Umfang:** Tabellen, Views, Volumes, Funktionen, Modelle und Services.
- **Zugriffswege:** Catalog Explorer, SQL, Databricks CLI und REST-APIs.

## Objektmodell

Unity Catalog organisiert Daten- und KI-Assets in einem **dreistufigen Namespace** (`catalog.schema.objekt`). Assets können sein:

- **Managed:** Unity Catalog steuert sowohl die Governance als auch den zugrunde liegenden Datei-Speicher.
- **External:** Unity Catalog übernimmt nur die Governance, der Speicher bleibt extern verwaltet.

Weitere Objekte wie Storage Credentials und Connections existieren auf Metastore-Ebene, oberhalb der Katalog-Hierarchie.

![Objekt-Hierarchie in Unity Catalog](images/object-hierarchy.png)

## Kernfähigkeiten

- Zugriffskontrolle über Privilegien und attributbasierte Policies (ABAC)
- Automatische Lineage-Verfolgung für Daten- und KI-Assets
- Audit-Logging für Compliance
- Datenklassifizierung und Qualitätsüberwachung
- Data Sharing über das OpenSharing-Protokoll
- Integration von KI-Governance

Objekt-für-Objekt-Referenz (eine Datei pro Objekttyp: Metastore, Catalog, Table, View, Volume, …) siehe [02 Unity Catalog/](../../../02%20Unity%20Catalog/00%20Overview.md).

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/
