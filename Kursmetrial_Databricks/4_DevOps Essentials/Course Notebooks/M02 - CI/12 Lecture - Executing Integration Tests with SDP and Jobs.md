# Integrationstests mit SDP und Jobs ausführen

## B. Methoden für Integrationstests

### SDP – Methode 1 – Expectations

- **Gemeinsamer SDP-Code** – Derselbe SDP-Code (Notebooks), der die Transformationslogik definiert (mit eigenen Funktionen). Wird in Dev, Stage und Prod verwendet.
- **Beispiele für Validierungen**
  - Anzahl der Zeilen validieren
  - Eindeutige Werte in den neuen Spalten validieren
- **Expectations in Umgebungen** – Testtabellen nutzen **Expectations** in **Dev** und **Stage**.

![Diagramm der SDP-Expectations](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_executing_integration_test/SDP_method1_expectations.png)

### Jobs – Methode 2 – Aufgaben

- **Unit-Tests** – Testen einzelner Codeeinheiten isoliert. Wenn die Unit-Tests bestehen, geht es im Job weiter.
- **Pipeline-Aufgabe** – Ausführen einer Spark Declarative Pipeline, um die notwendigen Tabellen zu erstellen, ohne Expectations zu verwenden.
- **Tests können umfassen**
  - Anzahl der Zeilen validieren
  - Tabellen wurden erfolgreich erstellt
  - Spalten enthalten korrekte eindeutige Werte
  - Spalten enthalten Werte innerhalb eines bestimmten Bereichs
  - Spalten enthalten keine Duplikate

![Diagramm der Integrationstests mit Jobs-Aufgaben](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_executing_integration_test/jobs_method2_tasks.png)

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> **SDP – Methode 1 – Expectations:**
>
> Betrachten wir den Integrationstest mit SDP.
>
> In diesem Beispiel verwenden wir SDP, um CSV-Dateien aus jedem Katalog (Dev, Stage und Prod) basierend auf der Pipeline-Konfigurationsvariablen zu ingestieren; es liest einfach die Daten aus der entsprechenden Zielumgebung.
>
> Unabhängig von der Zielumgebung (Dev, Stage oder Prod) wird dieselbe SDP ausgeführt. Konzentrieren Sie sich auf die schwarzen Kästchen unter „Gemeinsamer SDP-Code“ im Bild. Dieselbe SDP-Transformationslogik, die eigene Funktionen enthält, wird in jeder Umgebung angewendet.
>
> In diesem Beispiel werden Daten aus dem Zielkatalog in die Tabelle „health_bronze“ ingestiert, dann in der Tabelle „health_silver“ bereinigt und schließlich in einer materialisierten Ansicht in der Gold-Tabelle „chol_age_agg“ für jede Umgebung aggregiert.
>
> Die violetten Kästchen unterhalb der gemeinsamen SDP stellen materialisierte Testansichten dar, die während der Dev- und Stage-Läufe mit SDP-Expectations erstellt werden. Da wir für Dev und Stage statische Daten verwenden, kennen wir die erwartete Ausgabe, was uns ermöglicht, unseren gemeinsamen SDP-Code zu testen. In diesem Fall führen wir zu Demonstrationszwecken einfache Expectations aus, etwa das Zählen der Zeilenanzahl in den Tabellen, um die korrekte Ingestion zu bestätigen. Normalerweise würden Sie deutlich fokussiertere Tests erstellen.
>
> **Jobs – Methode 2 – Aufgaben:**
>
> Anstatt SDP und Expectations für Integrationstests zu verwenden, können Sie auch Databricks Lakeflow Jobs mit Aufgaben verwenden.
>
> Betrachtet man den gesamten Job für dieses einfache Projekt, beginnen wir damit, Unit-Tests auszuführen, um einzelne Funktionen isoliert zu testen. Wenn ein Unit-Test fehlschlägt, schlägt der Job fehl.
>
> Als Nächstes führen wir die SDP aus, um die Daten zu ingestieren. In diesem Beispiel führen wir dieselbe SDP wie zuvor aus, jedoch ohne die Expectations.
>
> Danach führen wir Integrationstests mit Notebooks durch, die als Aufgaben innerhalb des Lakeflow Jobs festgelegt sind. Für diesen Job müssen Sie die korrekten Parameter für Ihre Zielumgebung (Dev, Stage oder Produktion) konfigurieren. Sie können eine Reihe von Integrationstests ausführen, etwa das Zählen von Zeilen in einer Tabelle, das Überprüfen, ob Tabellen erfolgreich erstellt wurden, das Prüfen, ob Tabellen die angegebenen Spalten oder eindeutigen Werte enthalten, das Sicherstellen, dass Spaltenwerte in einem bestimmten Bereich liegen, das Bestätigen, dass keine Duplikate vorhanden sind, und mehr.
>
> Sobald schließlich die Unit-Tests, die Datenpipeline und die Integrationstests erfolgreich ausgeführt wurden, wird die finale Visualisierung erstellt.

---

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
