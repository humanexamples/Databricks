![DBAcademy](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/icons/databricks_academy.png)

# Vorlesung – Zusätzliche Funktionen und Ingestion in bestehende UC-Tabellen

## Überblick

Databricks bietet zusätzliche Funktionen wie Lakehouse Federation, Zerobus, Open Sharing und Databricks Marketplace, um die Möglichkeiten zur Datenintegration, zum Teilen von Daten und zur Zusammenarbeit im Lakehouse zu erweitern.

Diese Lektion zeigt außerdem, wie `MERGE INTO` die Ingestion in bestehende UC-Tabellen vereinfacht, indem Updates, Inserts und Deletes aus einer Quelle in einer einzigen atomaren Operation angewendet werden.

## Lernziele

Am Ende dieser Lektion können Sie:

1. **Zusätzliche Databricks-Funktionen beschreiben**, die Datenintegration, Datenfreigabe und Zusammenarbeit erweitern
2. **Die wichtigsten Komponenten des Databricks Marketplace identifizieren** und geteilte Daten-Assets erkunden
3. **Den Zweck von MERGE INTO erklären**, um Updates, Inserts und Deletes auf bestehende UC-Tabellen anzuwenden
4. **MERGE-INTO-Klauseln beschreiben**, einschließlich Matched Updates, Matched Deletes und Not Matched Inserts
5. **Eine MERGE-INTO-Anweisung schreiben**, um Quelldaten in eine Ziel-UC-Tabelle zu mergen

## A. Ausblick: Funktionen außerhalb dieses Kurses
Obwohl sich dieser Kurs auf LakeFlow Connect Managed Connectors konzentriert, gibt es weitere Ingestion-Funktionen in Databricks, die nützlich sein können, wenn sich Ihre Architektur weiterentwickelt.
##### Klicken Sie auf die Tabs, um zwischen den Funktionen zu wechseln.

Lakehouse Federation

![Lakehouse Federation diagram](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/lecture_additional_features/lakehouse_federation.png)

Ermöglicht es Ihnen, **externe Datenquellen abzufragen**, ohne Ihre Daten zu verschieben.

Besonders nützlich für:

- **Ad-hoc-Reporting**
- **Proof-of-Concept**-Arbeiten
- Die **explorative Phase** neuer ETL-Pipelines oder Reports
- Die Unterstützung von Workloads während einer **schrittweisen Migration**

Zerobus *(demnächst verfügbar)*

![Zerobus diagram](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/lecture_additional_features/Zerobus.png)

Eine **LakeFlow Connect API**, mit der Entwickler **Event-Daten direkt in ihr Lakehouse schreiben** können – mit sehr hohem Durchsatz (100 MB/s) und einer Latenz nahezu in Echtzeit (<5 Sekunden).

**Vereinfacht die Ingestion** für:

- IoT
- Clickstreams
- Telemetrie und mehr

Open Sharing

![Open Sharing diagram](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/lecture_additional_features/Delta_sharing.png)

Ermöglicht das **sichere Teilen von Daten** über Plattformen, Clouds und Regionen hinweg.

##### Dokumentation

1. **Lakehouse Federation**
   - Dokumentation [What is Lakehouse Federation](https://docs.databricks.com/aws/en/query-federation/)
   - [Lakehouse Federation: Discover, query and govern your data — no matter where it lives](https://www.databricks.com/resources/demos/videos/governance/lakehouse-federation)

2. **Zerobus**
   - [Eliminate Hops in Your Streaming Architecture with Zerobus, Part of LakeFlow Connect](https://www.databricks.com/dataaisummit/session/eliminate-hops-your-streaming-architecture-zerobus-part-lakeflow)
   - [Announcing the General Availability of Databricks LakeFlow](https://www.databricks.com/blog/announcing-general-availability-databricks-lakeflow)

3. **Open Sharing**
   - [Open Sharing Demo](https://www.databricks.com/resources/demos/videos/data-sharing/delta-sharing)
   - Dokumentation [What is Open Sharing](https://docs.databricks.com/aws/en/delta-sharing/)

## B. Daten mit dem Databricks Marketplace ingestieren

Der Databricks Marketplace ist ein offener Marktplatz für all Ihre Daten, Analytics und KI, basierend auf dem Open-Source-Standard Open Sharing. Der Databricks Marketplace erweitert Ihre Möglichkeiten, Innovationen bereitzustellen und all Ihre Analytics- und KI-Initiativen voranzubringen.

![Databricks Marketplace](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/lecture_additional_features/databricks_marketplace.png)

## Databricks Marketplace

Er ist ein offener Austauschplatz für alle Datenprodukte:

- Datensätze
- Notebooks
- Dashboards
- ML-Modelle
- Solution Accelerators

**Basierend auf Open Sharing**

##### Dokumentation
- Dokumentation [What is Databricks Marketplace](https://docs.databricks.com/aws/en/marketplace)
- [Databricks Marketplace](https://www.databricks.com/product/marketplace)

## C. Open Sharing mit dem Databricks Marketplace
Der Einstieg in Daten-Assets aus dem Databricks Marketplace ist schnell und einfach – in nur drei Schritten.
##### Klicken Sie links auf einen Schritt, um hier detaillierte Anweisungen und Abbildungen zu sehen.

← IN 3 SCHRITTEN STARTEN

1. Den Marketplace öffnen

Navigieren Sie in Ihrem Databricks-Workspace über die linke Seitenleiste zum **Databricks Marketplace**

2. Nach Assets suchen

Verwenden Sie die Suchleiste, um verfügbare Daten-Assets zu durchsuchen – beginnen Sie mit Assets, die direkt von **Databricks** bereitgestellt werden

3. Sofortigen Zugriff erhalten

Wählen Sie das Asset aus und klicken Sie auf **"Get instant access"** – schon können Sie geteilte, kuratierte Daten-Assets nutzen!

Wählen Sie einen Schritt zum Erkunden

Klicken Sie links auf einen Schritt, um hier detaillierte Anweisungen und Abbildungen zu sehen.

> Wo Sie ihn finden
> - Melden Sie sich bei Ihrem **Databricks-Workspace** an
> - Suchen Sie in der linken Navigationsleiste nach **Marketplace**
> - Standardmäßig für alle Workspace-Benutzer verfügbar
> ![](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/lecture_additional_features/step1_marketplace.png)
> Marketplace in der linken Seitenleiste

> Worauf Sie achten sollten
> - Suchen Sie nach **Name, Kategorie oder Anbieter**
> - Filtern Sie nach **Free**, um kostenlose Datensätze zu finden
> - Beginnen Sie mit **von Databricks bereitgestellten** Assets – sie sind gut dokumentiert und sofort einsatzbereit
> - Prüfen Sie die Tabs **Tables, Files** und **Notebooks** für unterschiedliche Asset-Typen

> Was als Nächstes passiert
> - Das Asset wird automatisch zu Ihrem **Unity Catalog** hinzugefügt
> - Der Zugriff erfolgt **sofort** – für kostenlose Assets ist kein Genehmigungsworkflow erforderlich
> - Fragen Sie die Daten direkt mit **SQL, Notebooks oder Dashboards** ab
> - Die Daten bleiben über Open Sharing **live und aktuell** – kein Kopieren erforderlich
> ![Get instant access button on Databricks Marketplace asset page](https://files.training.databricks.com/binder/prod_main/data-ingestion-with-lakeflow-connect-en_us-3.1.2/images/20260828T081727Z/Data Ingestion with LakeFlow Connect/Includes/images/lecture_additional_features/step2_get_access.png)
> Klicken Sie auf "Get instant access", um das Asset freizuschalten

## D. Updates, Inserts und Deletes auf UC-Tabellen mit MERGE INTO

Mit dem Befehl MERGE INTO können Sie Updates, Inserts und Deletes aus einer Quelltabelle in einer einzigen atomaren Operation auf eine bestehende UC-Tabelle anwenden.

### D1. MERGE INTO im Überblick

MERGE INTO

Führt eine Menge von Updates, Inserts und Deletes aus einer Quelltabelle in eine Ziel-UC-Tabelle zusammen.
MERGE INTO unterstützt Schema Enforcement oder Schema Evolution und ermöglicht unterschiedliche Aktionen, je nachdem, ob eine Zeile zwischen Quell- und Zieltabelle übereinstimmt:

Übereinstimmende Zeilen (Matched)

UPDATE oder DELETE

Nicht übereinstimmende Zeilen laut Ziel (Unmatched by target)

INSERT

Nicht übereinstimmende Zeilen laut Quelle (Unmatched by source)

UPDATE oder DELETE

Diese Funktionalität macht MERGE INTO ideal für die Behandlung von Slowly Changing Dimensions (SCDs), inkrementellen Ladevorgängen und komplexen Change-Data-Capture-(CDC-)Szenarien.

### D2. MERGE INTO – Beispiel Schritt für Schritt

Es gibt Situationen, in denen Sie Datensätze in einer Zieltabelle auf Basis von Informationen aus einer anderen Tabelle aktualisieren, einfügen oder löschen müssen.

In diesem Szenario haben wir:

- Eine **target_table** mit den Benutzern peter und zebi, beide mit dem Status "current"

- Eine **source_table** mit drei Zeilen, die Änderungen angeben:
  - **peter**: status = "delete" (aus dem Ziel entfernen)
  - **zebi**: status = "update" (E-Mail auf zebi@other.com aktualisieren)
  - **samarth**: status = "new" (als neue Zeile einfügen)

Ziel ist es, die **target_table** zu aktualisieren, indem alle drei Arten von Änderungen in einer einzigen **MERGE INTO**-Operation angewendet werden.

target_table

| users | email | status |
| --- | --- | --- |
| peter | peter@email.com | current |
| zebi | zebi@email.com | current |
| ... | ... | ... |

**target_table** aktualisieren
mit der **source_table**

source_table

| users | email | status |
| --- | --- | --- |
| peter | peter@email.com | delete |
| zebi | zebi@other.com | update |
| samarth | samarth@other.com | new |

target_table

| users | email | status |
| --- | --- | --- |
| zebi | zebi@other.com | update |
| samarth | samarth@other.com | new |
| ... | ... | ... |

## E. MERGE-INTO-SQL-Syntax

Schritte

1. Ziel- und Quelltabelle deklarieren — MERGE INTO target_table target USING source_table source

2. Die Bedingung für das Mergen angeben — ON target.id = source.id

3. Erste WHEN-Klausel für den Merge — WHEN MATCHED AND source.status = 'update'

4. Zweite WHEN-Klausel für den Merge — WHEN MATCHED AND source.status = 'delete'

5. WHEN-NOT-MATCHED-Klausel für den Merge — Zeilen einfügen, die im Ziel nicht vorhanden sind

6. Endergebnis — Vollständig aktualisierte target_table

Tabellen

source_table

| id | users | email | status |
| --- | --- | --- | --- |
| 1 | peter | peter@email | delete |
| 2 | zebi | zebi@email | update |
| 3 | samarth | samarth@email | new |

Ursprüngliche target_table

| id | users | email | status |
| --- | --- | --- | --- |
| 1 | peter | peter@email | current |
| 2 | zebi | zebi@email | current |
| 4 | matt | matt@email | current |

source_table

| id | users | email | status |
| --- | --- | --- | --- |
| 1 | peter | peter@email | delete |
| 2 | zebi | zebi@email | update |
| 3 | samarth | samarth@email | new |

Aktualisierte target_table

| id | users | email | status |
| --- | --- | --- | --- |
| 1 | peter | peter@email | current |
| 2 | zebi | zebi@email | current |
| 4 | matt | matt@email | current |

source_table

| id | users | email | status |
| --- | --- | --- | --- |
| 1 | peter | peter@email | delete |
| 2 | zebi | zebi@email | update |
| 3 | samarth | samarth@email | new |

Aktualisierte target_table

| id | users | email | status |
| --- | --- | --- | --- |
| 1 | peter | peter@email | current |
| 2 | zebi | zebi@email | update |
| 4 | matt | matt@email | current |

source_table

| id | users | email | status |
| --- | --- | --- | --- |
| 1 | peter | peter@email | delete |
| 2 | zebi | zebi@email | update |
| 3 | samarth | samarth@email | new |

Aktualisierte target_table

| id | users | email | status |
| --- | --- | --- | --- |
| 1 | peter | peter@email | current |
| 2 | zebi | zebi@email | update |
| 4 | matt | matt@email | current |

source_table

| id | users | email | status |
| --- | --- | --- | --- |
| 1 | peter | peter@email | delete |
| 2 | zebi | zebi@email | update |
| 3 | samarth | samarth@email | new |

Aktualisierte target_table

| id | users | email | status |
| --- | --- | --- | --- |
| 2 | zebi | zebi@email | update |
| 4 | matt | matt@email | current |
| 3 | samarth | samarth@email | new |

source_table

| id | users | email | status |
| --- | --- | --- | --- |
| 1 | peter | peter@email | delete |
| 2 | zebi | zebi@email | update |
| 3 | samarth | samarth@email | new |

Vollständig aktualisierte target_table

| id | users | email | status |
| --- | --- | --- | --- |
| 2 | zebi | zebi@email | current |
| 4 | matt | matt@email | current |
| 3 | samarth | samarth@email | new |

SQL

|  |  |
| --- | --- |
| MERGE INTO |  |

##### FÜR ZUSÄTZLICHE HINWEISE AUFKLAPPEN

1. **Schritt 1: Ziel- und Quelltabelle deklarieren**
   - MERGE INTO `target_table` target – Damit wird die Zieltabelle deklariert, also die Tabelle, die Sie aktualisieren, in die Sie einfügen oder aus der Sie löschen möchten. Sie erhält den Alias target, um später in der Abfrage darauf zu verweisen.
   - USING `source_table` source – Damit wird die Quelltabelle definiert, also die Tabelle mit den neuen Daten oder Änderungen, die Sie auf das Ziel anwenden möchten. Sie erhält den Alias source.

2. **Schritt 2: Die Merge-Bedingung angeben**
   `ON target.id = source.id` definiert die Abgleichsbedingung zwischen Quell- und Zieltabelle, typischerweise über einen eindeutigen Schlüssel wie `id`.

3. **Schritt 3: WHEN MATCHED – UPDATE**
   WHEN MATCHED AND source.status = 'update' THEN
   Wenn eine Zeile in beiden Tabellen existiert und die Quelle angibt, dass es sich um ein Update handelt.
   UPDATE SET – Aktualisiert die Zieltabelle mit neuen Werten aus der Quelle:
   - email
   - status

4. **Schritt 4: WHEN MATCHED – DELETE**
   WHEN MATCHED AND source.status = 'delete' THEN DELETE
   Wenn die Zeile in beiden Tabellen existiert und die Quelle angibt, dass sie gelöscht werden soll, wird sie aus dem Ziel entfernt.

   - **Schritt 5: WHEN NOT MATCHED – INSERT**
     Wenn die Zeile in der Quelle, aber nicht im Ziel existiert …
     INSERT (...) VALUES (...) – Eine neue Zeile mit Werten aus der Quelle wird in die Zieltabelle eingefügt.

     - **Schritt 6: Endergebnis**
       Dieser einzelne MERGE-INTO-Befehl:
       - Aktualisiert Zeilen, wenn status = 'update'
       - Löscht Zeilen, wenn status = 'delete'
       - Fügt neue Zeilen ein, die im Ziel nicht vorhanden sind
       Dieses Muster eignet sich perfekt für inkrementelle Datenladevorgänge, CDC oder SCD-Type-1-Muster. Matts Zeile (id=4) war nicht in der Quelltabelle enthalten und bleibt daher im Ziel unverändert.

## F. Fazit

- Databricks unterstützt eine umfassendere Integration und Zusammenarbeit durch Lakehouse Federation, Zerobus, Open Sharing und Databricks Marketplace.
- Databricks Marketplace und Open Sharing ermöglichen das sichere Entdecken, Abrufen und Austauschen von Daten- und KI-Assets ohne unnötiges Kopieren von Daten.
- `MERGE INTO` führt atomare Updates, Inserts und Deletes in UC-Tabellen durch und unterstützt inkrementelle Ingestion-Muster wie SCD, CDC und Datensynchronisation.

© 2026 Databricks, Inc. Alle Rechte vorbehalten.
Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) |
[Nutzungsbedingungen](https://databricks.com/terms-of-use) |
[Support](https://help.databricks.com/)
