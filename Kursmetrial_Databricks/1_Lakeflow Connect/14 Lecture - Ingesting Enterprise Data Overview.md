## B. LakeFlow Connect Managed Connectors

Die erste Methode zum Ingestieren von Unternehmensdaten ist die Verwendung von LakeFlow Connect Managed Connectors.

LakeFlow Connect Managed Connectors sind in Databricks integriert und darauf ausgelegt, das Ingestieren von Daten aus einer Vielzahl von Unternehmensdatenbanken und -anwendungen zu vereinfachen.

Sie bieten eine vollständig verwaltete Low-Code-Erfahrung und verringern den Bedarf an manueller Konfiguration oder individuellem Integrationscode.

LakeFlow Connect **Managed Connectors**

![](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/icons/manager_connectors.png)

![](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/icons/databricks_logo.png)

VORTEILE

- **Vereinfachen** das Ingestieren von Daten aus einer Vielzahl von Unternehmensdatenbanken und -anwendungen
- Bieten eine einfach zu bedienende **Benutzeroberfläche (UI)** (alternativ können Sie die API verwenden)
- **Vollständig von Databricks verwaltet**, wodurch der Bedarf an manueller Konfiguration oder individuellem Code sinkt

## C. Daten-Ingestion mit Lakeflow Connect Managed Connectors

Mit Lakeflow Connect Managed Connectors können Sie ganz einfach mit dem Ingestieren von Unternehmensdaten aus Quellen wie Workday, Salesforce, PostgreSQL, SQL Server und weiteren beginnen.

![LakeFlow Connect Managed Connectors Data Sources](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/lecture_enterprise_data/managed-connectors-data-sources.png)

##### Dokumentation
Managed Connectors in LakeFlow Connect befinden sich in unterschiedlichen Release-Stadien.
Einige sind in der Public Preview, andere GA. Prüfen Sie die offizielle [Dokumentation](https://docs.databricks.com/aws/en/release-notes/release-types) auf die neuesten Details.

##### FÜR ZUSÄTZLICHE HINWEISE AUFKLAPPEN

- Dies sind hocheffiziente, von Databricks verwaltete Connectors, die speziell für eine schnelle und zuverlässige Ingestion in Ihr Lakehouse entwickelt wurden
- Die Einrichtung kann über eine **„Point-and-Click“-UI** oder über die **API** erfolgen
- Managed Connectors befinden sich in **unterschiedlichen Release-Stadien** (einige in Public Preview, andere GA)

## D. Lakeflow Connect Managed Connectors: SaaS-Ingestion

Beginnen wir mit einem Überblick über die Architektur der Lakeflow Connect Managed Connectors für SaaS-Anwendungen.

Lakeflow Connect ermöglicht die Daten-Ingestion aus externen, öffentlich zugänglichen Quellen wie APIs oder OLAP-Endpunkten in Streaming-UC-Tabellen mithilfe serverloser, deklarativer Pipelines. Sie können diese Pipelines über die Benutzeroberfläche (UI) oder die API einrichten. Managed Connectors nutzen effiziente inkrementelle Lese- und Schreibvorgänge, um die Daten-Ingestion schneller, skalierbarer und kosteneffizienter zu machen, während Ihre Daten für die nachgelagerte Nutzung aktuell bleiben

![Saas Ingestion](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/lecture_enterprise_data/database_ SaaS_Ingestion.png)

Lakeflow Connect sammelt Daten aus externen Quellen in Streaming-UC-Tabellen mithilfe einer Declarative Pipeline auf Serverless Compute:
- Ein Lakeflow-Serverless-Declarative-Pipelines-Job **holt Anmeldeinformationen** aus Unity Catalog.
- Der Job **greift** auf die öffentlich zugängliche Datenquelle **zu** (z. B. API, offener OLAP-Port usw.).
- Der Dienst transformiert die Daten und speichert sie in einer **Streaming-UC-Tabelle**.

##### Dokumentation
Siehe die [Dokumentation](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/#saas-connector-components) zu den Komponenten der SaaS Managed Connectors.

##### FÜR ZUSÄTZLICHE HINWEISE AUFKLAPPEN

Zur Unterstützung dieses Ablaufs haben wir einen neuen Pipeline-Typ eingeführt: die Managed Ingestion Pipeline. Ihre Hauptaufgabe besteht darin, sich mit öffentlichen SaaS-Quellen (wie Salesforce oder Workday) zu verbinden, die Daten zu extrahieren und direkt in eine Streaming Table zu ingestieren. Diese Pipelines sind weitgehend vordefiniert und werden von Databricks verwaltet, sodass quellenspezifische Komplexitäten nahtlos behandelt werden.
Schließlich findet bei SaaS-Connectors die gesamte Datenbewegung in der Data Plane statt. Die Control Plane wird nur für die Einrichtung der Pipeline, das Monitoring (z. B. Lesen von Event Logs) und die Verwaltung verwendet.

## E. Architektur der Datenbank-Ingestion

Sehen wir uns nun an, wie sich die Architektur bei Verwendung eines LakeFlow Connect Managed Database Connectors ändert.

Wie bei SaaS-Connectors ist diese Architektur darauf ausgelegt, Daten in Streaming-UC-Tabellen zu übertragen – diesmal jedoch aus externen Datenbanken statt aus öffentlichen APIs.

![Database Ingestion Architecture](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/lecture_enterprise_data/database-ingestion-architecture.png)

LakeFlow Connect sammelt Daten aus **externen Datenbanken** in Streaming-UC-Tabellen:

1. Der Declarative-Pipelines-Job auf Classic Compute **holt Anmeldeinformationen** aus UC
2. Er verwendet die Anmeldeinformationen, um **sich mit Ihren Datenbankquellen zu verbinden und Daten zu sammeln**
3. Der aktuelle **Zustand und die Staging-Daten werden** in Ihrem Unity-Catalog-Volume **gespeichert**
4. Ein Serverless-Declarative-Pipelines-Job **verarbeitet die gesammelten Daten** in Ihre Streaming-UC-Tabellen

##### Dokumentation
Siehe die [Dokumentation](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/#database-connector-components) zu den Komponenten der Managed Database Connectors.

##### FÜR ZUSÄTZLICHE HINWEISE AUFKLAPPEN

Die Architektur der Datenbank-Ingestion ist aufwendiger als die für SaaS, da sie sich mit Datenbanken verbinden muss, die sich möglicherweise On-Premises oder in einer Private Cloud befinden.
**Neu eingeführte Schlüsselkomponenten**
Hier führen wir zwei neue Architekturelemente ein:

1. **Ingestion Gateway:**
   - Eine dedizierte Pipeline, die sich mit der Datenbank verbindet, um Folgendes zu extrahieren:
     - Metadaten
     - Snapshots
     - Change Logs – all dies wird im Unity-Catalog-(UC-)Volume zwischengespeichert.
2. **Unity Catalog Volume:**
   - Dient als zwischengeschaltete Staging-Schicht, aus der die nächste Pipeline die Daten abholen und streamen kann.
   - Es ist mit den Standardmechanismen von UC abgesichert, und standardmäßig ist der Zugriff auf den Benutzer beschränkt, der die Pipeline ausführt.

Warum haben wir diesen Gateway-Schritt überhaupt hinzugefügt?
Zunächst hilft er beim Networking. Viele Kunden haben Datenbanken, die (1) hinter einer Firewall liegen, (2) nicht öffentlich über das Internet erreichbar sind und so weiter. Wenn Sie keine Option wie Private Link haben, können wir das Gateway innerhalb Ihres Netzwerks bereitstellen.
Das Gateway hilft uns außerdem, die Last auf der Datenbank zu begrenzen. Schließlich möchten Sie wahrscheinlich die Anzahl direkter Verbindungen zu Ihrer Datenquelle begrenzen. Indem wir das Gateway von der Pipeline trennen, kann ein einzelnes Gateway mit der Datenbank kommunizieren – und dann für die Skalierbarkeit auf N Pipelines verteilen. (Zum Vergleich: Bei einem SaaS-Connector ist das kein Problem, da die Last in der Regel durch API-Limits gesteuert wird. Aber selbst dort nutzen wir diese Limits so effizient wie möglich.)

## F. Daten-Ingestion mit Partner Connect

Wenn für Ihre spezifische Datenquelle kein Managed Connector verfügbar ist, können Sie auch Partner Connect verwenden.

### F1. Partner Connect im Überblick

Mit Partner Connect können Sie Testkonten bei ausgewählten Databricks-Technologiepartnern erstellen und Ihren Databricks-Workspace über die Databricks-UI mit Partnerlösungen verbinden. So können Sie Partnerlösungen mit Ihren Daten im Databricks Lakehouse ausprobieren und anschließend die Lösungen übernehmen, die Ihre geschäftlichen Anforderungen am besten erfüllen.

![Left image](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/lecture_enterprise_data/managed_connectors_left.png)

- Mit Partner Connect können Sie Testkonten bei ausgewählten Databricks-Technologiepartnern erstellen.- Sie können Ihren Databricks-Workspace direkt über die Databricks-UI mit Partnerlösungen verbinden.- So können Sie Partnerlösungen mit Ihren Daten im Databricks Lakehouse testen.- Anschließend können Sie die Lösungen bewerten und übernehmen, die Ihre geschäftlichen Anforderungen am besten erfüllen.

![Right image](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/lecture_enterprise_data/partner_connect_right.png)

### F2. Das Partner-Connect-Ökosystem

Unsere Ingestion-Partner bleiben von zentraler Bedeutung. Sie bieten eine sehr breite Palette an Connectors, und diese Connectors verfügen oft über umfangreiche Funktionen, die von spezialisierten Teams erfahrener Engineers gepflegt werden.

![Partner Connect Ecosystem](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/lecture_enterprise_data/partner-connect-ecosystem.png)

##### Dokumentation
Weitere Informationen finden Sie unter den folgenden Links:

- [What is Databricks Partner Connect documentation](https://docs.databricks.com/aws/en/partner-connect/)
- [Partner Connect](https://www.databricks.com/partnerconnect#partner-demos)

##### FÜR ZUSÄTZLICHE HINWEISE AUFKLAPPEN

Wir möchten, dass Sie diese Wahlmöglichkeit weiterhin haben, daher werden wir auch künftig mit diesen Partnern zusammenarbeiten, um so viele hochwertige Connectors wie möglich anzubieten. Selbst wenn es für eine bestimmte Quelle einen nativen Connector gibt, werden wir diese Wahlfreiheit weiterhin unterstützen.
Wir fügen gerade erst die wichtigsten Connectors hinzu, die Kunden angefragt haben. Es geht um die Wahlfreiheit der Kunden.

## G. Fazit

In dieser Lektion haben Sie gelernt, wie Sie Unternehmensdaten über Cloud Object Storage hinaus in Databricks ingestieren:

- **LakeFlow Connect Managed Connectors** vereinfachen die Ingestion aus Unternehmensdatenbanken und SaaS-Anwendungen mit einer vollständig verwalteten, UI- oder API-gesteuerten Erfahrung.
- **Architektur der SaaS-Ingestion**: Ein serverloser Declarative-Pipelines-Job holt Anmeldeinformationen aus Unity Catalog, greift auf die öffentliche Datenquelle zu und schreibt in Streaming-UC-Tabellen.
- **Architektur der Datenbank-Ingestion**: Verwendet zusätzlich ein Ingestion Gateway (Classic Compute), um sich mit privaten Datenbanken zu verbinden, mit Staging und Zustandsverwaltung in Unity-Catalog-Volumes, bevor eine serverlose Pipeline in Streaming-UC-Tabellen schreibt.
- **Partner Connect** bietet eine Alternative, wenn kein nativer Managed Connector verfügbar ist, und stellt ein umfangreiches Ökosystem an Partnerlösungen bereit (Informatica, Qlik, Rivery, Alteryx, Prophecy, Fivetran und weitere).

### Nächste Schritte

Im nächsten Abschnitt arbeiten Sie praktisch mit LakeFlow Connect Managed Connectors, um Pipelines für die Ingestion von Unternehmensdaten einzurichten.

© 2026 Databricks, Inc. Alle Rechte vorbehalten.
Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) |
[Nutzungsbedingungen](https://databricks.com/terms-of-use) |
[Support](https://help.databricks.com/)
