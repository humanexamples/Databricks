# 15 - Ingestion von Unternehmensdaten mit LakeFlow Connect

In dieser Demonstration lernen Sie die **LakeFlow Connect** Managed Connectors für externe Unternehmensquellen kennen – ein einfach zu bedienendes Tool, um Daten aus verschiedenen Systemen wie Datenbanken (z. B. SQL Server), Anwendungen (z. B. Salesforce, Workday) und Dateispeicherdiensten (z. B. SharePoint) in das Lakehouse zu bringen.

Es ist darauf ausgelegt, Daten effizient zu verarbeiten und die Performance automatisch zu verbessern.

### Lernziele

Am Ende der Demonstration sollten Sie in der Lage sein:

- die verfügbaren Databricks Managed Connectors zu erkunden, um Daten über LakeFlow Connect zu ingestieren.
- zu sehen, wie Daten mit Partner Connect ingestiert werden.
- einen Datenbank-Connector hinzuzufügen und eine Demonstration einer Ingestion-Pipeline zu konfigurieren:
  - Auswählen, welche Daten Sie ingestieren und mit Databricks synchronisieren möchten
  - Die Daten-Pipeline mit Unity Catalog (Katalog und Schema) synchronisieren

1. Führen Sie die folgenden Schritte aus, um die Lakeflow-Connect-Dokumentation anzuzeigen:

   a. Rufen Sie die Seite der [Databricks-Dokumentation](https://docs.databricks.com/aws/en/) auf.

   b. Erweitern Sie in der linken Navigationsleiste **Data Engineering**.

   c. Erweitern Sie **Lakeflow Connect**, um die verfügbare Dokumentation zur Daten-Ingestion mit Lakeflow Connect anzuzeigen.

   d. Erweitern Sie **Managed Connectors**, um Informationen zu den von Databricks verwalteten Connectors aufzurufen.

**HINWEIS:** Bitte beachten Sie, dass sich die Navigationshinweise zur Dokumentation bei einem Update ändern können.

2. Führen Sie die folgenden Schritte aus, um die verfügbaren **Data Ingestion**-Funktionen in Databricks zu erkunden:

   a. Klicken Sie in der linken Hauptnavigationsleiste mit der rechten Maustaste auf **Data Ingestion** und wählen Sie **Open in a New Tab**.

   b. Unter **Databricks Connectors** sehen Sie verschiedene von Databricks verwaltete Connectors, die von LakeFlow Connect bereitgestellt werden.

   c. Im Abschnitt **Files** können Sie:

   - **Tabellen erstellen oder ändern** (Create or modify tables)

   - **Dateien in ein Volume hochladen** (Upload files to a volume)

   - Dateien per Drag-and-Drop hinzufügen, wenn Sie die Optionen zum Erstellen/Ändern von Tabellen oder zum Hochladen von Dateien in ein Volume verwenden.

   d. Unter **Fivetran Connectors** können Sie über einen Partner nach bestimmten Datenquellenverbindungen suchen.

   e. Klicken Sie auf einen beliebigen Connector, um Details anzuzeigen.

   f. Aus Gründen der Abwärtskompatibilität können Sie Dateien auch direkt in **DBFS** hochladen, Databricks empfiehlt jedoch künftig das Hochladen in Unity Catalog.

3. Führen Sie die folgende Point-and-Click-Demonstration durch, um zu lernen, wie Sie mit **LakeFlow Connect** einen Databricks Managed Connector zu einer externen Datenbank oder SaaS-Anwendung verwenden.

      **HINWEIS:** In diesem Kurs steht keine aktive Datenbank oder SaaS-Anwendung zur Verfügung. Die folgenden Demos sind ein einfacher Rundgang. Wählen Sie in einer Live-Schulung eine der folgenden Touren aus.

   - [LakeFlow Connect Managed Connector Demonstration](https://app.getreprise.com/launch/BXZY58n/) – Einfache Demonstration

   - [Databricks Lakeflow Connect for Workday Reports: Connect, Ingest, and Analyze Workday Data Without Complexity](https://www.databricks.com/resources/demos/tours/appdev/lakeflow-workday-connect?itm_data=demo_center)

   - [Databricks Lakeflow Connect for Salesforce: Powering Smarter Selling with AI and Analytics](https://www.databricks.com/resources/demos/tours/platform/discover-databricks-lakeflow-connect-demo?itm_data=demo_center)

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
