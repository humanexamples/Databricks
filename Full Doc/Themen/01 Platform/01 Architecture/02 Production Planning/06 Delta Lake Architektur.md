# Phase 6: Delta-Lake-Architektur gestalten

Teil der [Production Planning](Uebersicht.md)-Reihe. Behandelt Medallion-Architektur (Ingestion-Strategie, Table-Management-Strategie, Hub-and-Spoke-Medallion) und Data-Governance-Strategie aus Sicht der Deployment-Planung. Für die Grunddefinitionen von Bronze/Silver/Gold siehe [Medallion Architecture.md](../Medallion%20Architecture.md) — dieses Dokument ergänzt die dortigen Layer-Definitionen um konkrete Ingestion-, Table-Management- und Governance-Entscheidungen für die Produktionsplanung.

## Abschnittsübersicht

1. [Medallion-Architektur gestalten](#medallion)
2. [Landing Zone](#landing-zone)
3. [Data-Ingestion-Strategie gestalten](#ingestion)
4. [Table-Management-Strategie gestalten](#table-management)
5. [Hub-and-Spoke-Medallion-Design](#hub-spoke)
6. [Data-Governance-Strategie gestalten](#governance)
7. [Empfehlungen](#empfehlungen)
8. [Ergebnisse der Phase](#ergebnisse)
9. [Quelle](#quelle)

---

## <a id="medallion">1. Medallion-Architektur gestalten</a>

Die Medallion-Architektur organisiert Daten in drei Schichten: Bronze (Rohdaten), Silver (verfeinerte Daten), Gold (geschäftsfertige Daten) — vollständige Definitionen siehe [Medallion Architecture.md](../Medallion%20Architecture.md). Im Kontext der Produktionsplanung gelten zusätzlich folgende layer-spezifische Best Practices:

**Bronze:** alle Quelldatenfelder erhalten; Unity-Catalog-Volumes zum Landen von Rohdateien nutzen; inkrementelle Ingestion implementieren; nach Ingestion-Datum partitionieren; Datenquellen und Zeitpläne dokumentieren.

**Silver:** Datenqualitätsprüfungen implementieren; Unity-Catalog-Managed-Tables nutzen; nach Geschäftsdimensionen partitionieren; Transformationslogik dokumentieren; SLAs für Datenaktualität etablieren.

**Gold:** getrennte Gold-Tabellen für unterschiedliche Geschäftsbereiche anlegen; Dynamic Views für Sicherheit nutzen; Predictive Optimization implementieren; Daten-Lineage dokumentieren; Datenprodukte über Unity Catalog veröffentlichen.

## <a id="landing-zone">2. Landing Zone</a>

Größere Organisationen implementieren häufig eine zusätzliche Landing Zone — vor der eigentlichen Bronze-Schicht. Muster: Cloud-Object-Storage nutzen (S3, ADLS Gen2, GCS); Unity-Catalog-Volumes für sicheren Dateizugriff; Schreibzugriff für Drittsysteme erlauben; Event-Benachrichtigungen zum Auslösen von Ingestion-Pipelines nutzen.

## <a id="ingestion">3. Data-Ingestion-Strategie gestalten</a>

### Ingestion-Methoden

- **Lakeflow Connect:** „verwalteter Ingestion-Dienst von Databricks, der regelmäßig Daten aus externen Quellen synchronisieren kann."
- **Partner-Ingestion-Tools** wie Fivetran für nicht unterstützte Quellen.
- **Custom-Ingestion-Pipelines** über Lakeflow oder Notebooks.

### Ingestion-Muster

- **Batch Ingestion:** geplante regelmäßige Ladevorgänge, geeignet für große historische Volumen, geringere Kosten, akzeptable Latenz.
- **Streaming Ingestion:** kontinuierliche Ingestion mit niedriger Latenz über Lakeflow Auto Loader, am besten für Echtzeit-Analysen, höhere Compute-Kosten.
- **Change Data Capture (CDC):** erfasst inkrementelle Änderungen aus Quellsystemen, effizient für große Tabellen mit häufigen Updates, bewahrt Daten-Lineage.

**Best Practices:** Unity-Catalog-Volumes zum Landen von Rohdaten nutzen; idempotente Ingestion implementieren; Auto Loader für effiziente Datei-Ingestion nutzen; Retention-Policies konfigurieren; Pipelines auf Fehlschläge überwachen.

## <a id="table-management">4. Table-Management-Strategie gestalten</a>

### Managed vs. External Tables

Managed Tables werden „vollständig von Unity Catalog verwaltet und in einer Managed-Storage-Location gespeichert." External Tables erfordern „direkten Dateizugriff auf die Daten" und sollten nur genutzt werden, wenn „Daten aus regulatorischen oder Compliance-Gründen in bestimmten Cloud-Storage-Pfaden verbleiben müssen."

**Best Practices:** Managed Tables für alle neuen Lakehouse-Daten nutzen; Managed Volumes für Landing Zones nutzen; External Tables nur für Daten mit spezifischen Pfadanforderungen reservieren; Eigentümerschaft und Lifecycle-Policies dokumentieren; Predictive Optimization aktivieren.

## <a id="hub-spoke">5. Hub-and-Spoke-Medallion-Design</a>

Kombiniert die Medallion-Architektur mit Enterprise-Deployments: Ein zentraler Data Hub nimmt organisationsweite Assets auf, während Datendomänen domänenspezifische Daten aufnehmen. Publishing-Modelle können zentralisiert oder verteilt sein.

**Beispielstruktur:** ein Data Hub mit Bronze-, Silver- und Gold-Schichten speist Sales- und Engineering-Domänen, die jeweils eigene Medallion-Schichten besitzen.

**Best Practices:** den Hub für organisationsweit gemeinsam genutzte Daten nutzen; Domänen erlauben, domänenspezifische Daten selbst zu kuratieren; klare Publishing-Policies für Datenprodukte etablieren; Unity-Catalog-Catalogs zur Datentrennung nutzen; Databricks-managed OpenSharing für das Teilen von Datenprodukten nutzen.

## <a id="governance">6. Data-Governance-Strategie gestalten</a>

### Datenqualitätsstrategie

Datenqualität muss sich über die Schichten hinweg verbessern. Werkzeuge:

- Constraints zur Sicherstellung von Datenqualität und -integrität.
- Primary und Foreign Keys zur Kodierung von Beziehungen.
- Expectations, die Qualitätsprobleme am Weiterfließen nach unten hindern.
- Lakehouse Monitoring für statistische Eigenschaften.

**Best Practices:** Qualitätsprüfungen bereits bei der Bronze-Ingestion implementieren; striktere Regeln für Silver und Gold durchsetzen; Metriken über die Zeit überwachen; SLAs für kritische Datensätze definieren; Alerting bei Verstößen automatisieren.

### Daten-Silos vermeiden

Unterscheidung zwischen „Data Copy" und „Data Silo": „Eine eigenständige oder Wegwerf-Kopie von Daten ist für sich genommen nicht schädlich." Probleme entstehen, „wenn diese Kopien operativ werden und nachgelagerte Geschäfts-Datenprodukte von ihnen abhängen."

**Best Practices:** Unity-Catalog-Views und OpenSharing statt Kopieren nutzen; Single Sources of Truth etablieren; Kopien auf Abteilungsebene vermeiden; Unity-Catalog-Lineage zur Abhängigkeitsverfolgung nutzen; redundante Datensätze stilllegen.

### Data Catalog und Discovery

Unity Catalog bietet Data Discovery und Lineage. Ein Data Catalog sollte Suche ermöglichen, Metadaten und Beschreibungen liefern, Daten-Lineage zeigen sowie Qualitätsmetriken und Aktualitätsinformationen anzeigen.

Das System „erfasst automatisch Lineage für: Table-zu-Table-Abhängigkeiten, Notebook- und Job-Ausführungen, die Daten lesen oder schreiben, vorgelagerte Quellsysteme, nachgelagerte Konsumenten und Datenprodukte."

**Best Practices:** Beschreibungen und Tags zu allen Catalogs und Tabellen hinzufügen; Daten-Eigentümer dokumentieren; die Unity-Catalog-Suche nutzen; Metadaten regelmäßig überprüfen; Lineage vor Änderungen einsehen.

## <a id="empfehlungen">7. Empfehlungen</a>

**Empfohlene Praktiken:**

- Medallion-Architektur zur Strukturierung des Data Lake nutzen.
- Unity-Catalog-Managed-Tables für Lakehouse-Daten einsetzen.
- Unity-Catalog-Volumes für Landing Zones nutzen.
- Qualitätsprüfungen auf jeder Schicht implementieren.
- Predictive Optimization für häufig abgefragte Tabellen aktivieren.
- Klare Publishing-Policies für Datenprodukte etablieren.

**Zu vermeidende Praktiken:**

- Daten-Silos durch operative Datenduplizierung schaffen.
- External Tables unnötig verwenden.
- Die Bronze-Schicht überspringen (Bewahrung der Rohdaten).
- Qualitätsprüfungen wegen Zeitdrucks überspringen.
- Unverwalteter Daten-Sprawl ohne Governance zulassen.

## <a id="ergebnisse">8. Ergebnisse der Phase</a>

Nach Abschluss dieser Phase sollten vorliegen: entworfene Medallion-Architektur mit klaren Layer-Zwecken; definierte Data-Ingestion-Strategie; etablierte Table-Management-Strategie; bewertete Hub-and-Spoke-Architektur; Datenqualitätsstrategie mit layer-spezifischen Prüfungen; etablierte Data-Governance-Policies; entworfene Landing-Zone-Architektur; definiertes Publishing-Modell für Datenprodukte.

**Nächste Phase:** Phase 7 — Infrastructure-as-Code-Ansatz planen (siehe [07 Infrastructure as Code.md](07%20Infrastructure%20as%20Code.md)).

## <a id="quelle">9. Quelle</a>

- https://docs.databricks.com/aws/en/lakehouse-architecture/deployment-guide/delta-lake

**Stand:** 2026-08-21.
