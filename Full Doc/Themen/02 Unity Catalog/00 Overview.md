# Unity Catalog — Objektübersicht

Dieser Ordner ist die **Objekt-für-Objekt-Referenz** von Unity Catalog: eine Datei pro sicherbarem Objekttyp (01–23). Für die allgemeine Einordnung „Was ist Unity Catalog?" (Governance-Scope, Aktivierungsdatum, Kernfähigkeiten wie ABAC, Lineage, Audit-Logging, Data Sharing) siehe [03 Governance/01 Data Governance/01 Uebersicht/03 Was ist Unity Catalog.md](../03%20Governance/01%20Data%20Governance/01%20Uebersicht/03%20Was%20ist%20Unity%20Catalog.md). Für dieselben Objekte aus Zugriffskontroll-/Privilegien-Sicht (kompakte Tabelle statt Einzeldateien) siehe [03 Governance/01 Data Governance/02 Objektmodell/01 Securable Objects.md](../03%20Governance/01%20Data%20Governance/02%20Objektmodell/01%20Securable%20Objects.md).

## Objektmodell

Unity Catalog organisiert Daten- und KI-Assets in einem **dreistufigen Namespace** (`catalog.schema.objekt`). Assets können sein:

- **Managed:** Unity Catalog steuert sowohl die Governance als auch den zugrunde liegenden Datei-Speicher.
- **External:** Unity Catalog übernimmt nur die Governance, der Speicher bleibt extern verwaltet.

Weitere Objekte wie Storage Credentials und Connections existieren auf Metastore-Ebene, oberhalb der Katalog-Hierarchie.

![Objekt-Hierarchie in Unity Catalog](images/object-hierarchy.png)

Das vorangehende Diagramm zeigt Folgendes:

- [**Catalogs**](02%20Catalog.md) sind die oberste Ebene für deine Daten-Assets. Kataloge existieren direkt unterhalb des Metastores. Sie dienen dazu, deine Daten- und KI-Assets zu organisieren, typischerweise nach organisatorischen Einheiten oder Software-Entwicklungslebenszyklus-Bereichen.
  - [**Schemas**](03%20Schema.md) existieren innerhalb von Katalogen. Sie organisieren Daten- und KI-Assets in Kategorien, die feingranularer als Kataloge sind. Ein Schema kann einen einzelnen Anwendungsfall, ein Projekt oder eine Team-Sandbox repräsentieren.
    - [**Tables**](04%20Table.md) sind Sammlungen strukturierter Daten, organisiert in Zeilen und Spalten.
    - [**Views**](05%20View.md) sind gespeicherte Abfragen über andere Tabellen oder Views.
    - [**Volumes**](08%20Volume.md) repräsentieren Sammlungen unstrukturierter Daten im Cloud-Objektspeicher.
    - [**Functions**](09%20Function.md) sind Einheiten wiederverwendbarer Logik, die einen skalaren Wert oder eine Menge von Zeilen zurückgeben.
    - [**Models**](10%20Model.md) sind versionierte oder unversionierte, in Unity Catalog registrierte KI-Modelle.
    - [**Services**](11%20Service.md) sind governance-unterworfene, aufrufbare KI-Assets, etwa Model Services und MCP Services.
    - [**Secrets**](12%20Secret.md) speichern sensible Werte wie Zugangsdaten und Tokens, die sich in Unity Catalog regeln und referenzieren lassen, ohne den Wert offenzulegen.

Es gibt außerdem viele weitere sicherbare Objekte in Unity Catalog. All diese Objekte existieren direkt unterhalb des Metastores. Das folgende Diagramm hebt diese sicherbaren Objekte hervor.

Diese sicherbaren Objekte lassen sich grob in zwei Gruppen einteilen. Die erste Gruppe umfasst Objekte, die den Zugriff auf Cloud-Speicher und andere externe Datenquellen und -dienste verwalten:

- [**Storage Credentials**](14%20Storage%20credential.md) sind Objekte, die die zum Zugriff auf einen bestimmten Cloud-Speicherpfad benötigten Authentifizierungsinformationen repräsentieren.
- [**External Locations**](15%20External%20location.md) sind Objekte, die einen bestimmten Pfad im Cloud-Speicher repräsentieren. Sie enthalten außerdem einen Verweis auf das zum Zugriff auf diesen Pfad benötigte Storage Credential.
- Ein [**External-Metadata**](16%20External%20metadata.md)-Objekt dient dazu, benutzerdefinierte Data-Lineage-Beziehungen für Systeme festzulegen, die außerhalb von Unity Catalog operieren.
- [**Service Credentials**](17%20Service%20credential.md) sind Objekte, die die zum Zugriff auf externe Cloud-Dienste benötigten Authentifizierungsinformationen repräsentieren.
- [**Connections**](18%20Connection.md) sind Objekte, die eine Verbindung zu einem externen Datenbanksystem repräsentieren.

Die zweite Gruppe umfasst Objekte, die den Zugriff auf das Teilen von Daten- und KI-Assets über Metastore- oder Organisationsgrenzen hinweg verwalten:

- [**Shares**](19%20Share.md) sind Objekte, die eine logische Gruppierung von Daten-Assets repräsentieren, die mit externen [Recipients](21%20Recipient.md) geteilt werden sollen.
- [**Providers**](20%20Provider.md) sind Objekte, die eine externe Organisation oder Nutzergruppe repräsentieren, die Daten mit deiner Organisation geteilt hat.
- [**Recipients**](21%20Recipient.md) sind Objekte, die eine externe Organisation oder Nutzergruppe repräsentieren, mit der ein [Provider](20%20Provider.md) Daten teilt.
- [**Clean Rooms**](22%20Clean%20room.md) sind Objekte, die eine sichere Umgebung für die Zusammenarbeit mit anderen Organisationen repräsentieren, ohne zugrunde liegende Daten offenzulegen.

Nicht im Diagramm enthalten, aber ebenfalls mit eigener Datei in diesem Ordner: [Metastore](01%20Meta%20Store.md), [Materialized View](06%20Materialized%20View.md), [Metric View](07%20Metric%20View.md), [Feature](13%20Feature.md), [Tags](23%20Tags.md).

### Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects
