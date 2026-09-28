# Das Projekt planen

In dieser Vorlesung lernen Sie, wie Sie ein Datenvisualisierungsprojekt planen, indem Sie Umgebungen strukturieren, Daten über Dev, Stage und Prod verwalten und eine CI/CD-Pipeline in Databricks für reibungslose, sichere Bereitstellungen einrichten.

---

## A. Das Projekt planen

Dieses Projekt konzentriert sich auf die Visualisierung von Gesundheitsdaten, indem es einer strukturierten Datenpipeline folgt. Wir beginnen damit, tägliche inkrementelle CSV-Dateien in eine Bronze-Tabelle zu ingestieren, und verfeinern diese Rohdaten dann zu einer bereinigten Silber-Tabelle. Von dort erstellen wir eine zusammengefasste Gold-Tabelle, die mit Konsumenten geteilt und zum Erstellen der finalen Visualisierung verwendet wird. Während des gesamten Prozesses nutzen wir verschiedene Datenbank-Assets, darunter Notebooks, Spark Declarative Pipeline, Lakeflow Jobs und Compute-Ressourcen, um eine reibungslose und effiziente Ausführung sicherzustellen.

- **Ergebnis (Deliverable)** – Gesundheitsdaten visualisieren.
- **Aufgaben**
  - Tägliche inkrementelle CSV-Dateien in eine Bronze-Tabelle ingestieren
  - Eine bereinigte Silber-Tabelle erstellen
  - Gold-Tabellen erstellen, um sie mit Konsumenten zu teilen
- **Databricks-Assets:** Workspace (Notebooks, SDP, Lakeflow Jobs, Compute)

---

## B. Ihre Datenumgebungen einrichten

### Dev-Daten

- Oft eine kleine, statische Teilmenge der Produktionsdaten
- Können anonymisierte oder synthetische Datensätze sein
- Unterstützt schnelle Entwicklung und schnelles Testen
- Stellt Datenschutz und Datenintegrität sicher

### Stage-Daten

- Staging-Daten spiegeln Struktur & Volumen der Produktion wider, typischerweise statisch
- Können anonymisierte oder bereinigte sensible Informationen enthalten
- Stellt realistisches Testen und Validieren sicher

### Prod-Daten

- Produktionsdaten: live & voll betriebsbereit
- Enthalten echte Nutzerdaten
- Werden kontinuierlich aktualisiert
- Erfordern hohe Standards für Sicherheit, Datenschutz & Compliance

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> Innerhalb einer CI/CD-Pipeline
>
> In der Entwicklung werden Daten oft anonymisiert oder mit synthetischen Datensätzen erzeugt, um schnelle Entwicklung und schnelles Testen zu ermöglichen, ohne Datenschutz oder Integrität der Produktionsdaten zu gefährden.
>
> Wenn Sie eine Staging-Umgebung haben, sollten Staging-Daten die Produktion in Struktur und Volumen eng widerspiegeln, mit anonymisierten oder bereinigten sensiblen Informationen, um realistisches Testen und Validieren sicherzustellen.
>
> Produktionsdaten sind live, voll betriebsbereit und werden kontinuierlich aktualisiert, enthalten echte Nutzerdaten und müssen mit hohen Standards für Sicherheit, Datenschutz und Compliance behandelt werden.
>
> Jede Umgebung sollte Daten haben, die ihrem spezifischen Zweck entsprechen, und in jeder Phase Realismus, Sicherheit und Compliance ausbalancieren. Wie dies umgesetzt wird, hängt von Ihrer Organisation und der Sensibilität Ihrer Daten ab.

---

## C. Umgebungen isolieren

Mann kann die DEV/STG/PRD Umgebungen entweder auf Workspace- oder Katalog-Ebene isolieren.

- **Workspace-Ebene:** Databricks definiert Workspaces als primäre organisatorische Bereitstellungseinheit. Ein eigener Workspace bedeutet ein eigenes virtuelles Netzwerk (VNet/VPC), eigene Compute-Ressourcen (Cluster) und getrennte Web-UIs.

- **Catalog-Ebene:** Databricks nutzt mit dem Unity Catalog einen dreistufigen Namensraum (`catalog.schema.table`). Ein Catalog isoliert Daten logisch. Er teilt sich jedoch dieselbe Steuerungsebene (Control Plane) und dasselbe übergeordnete Metastore-Verzeichnis in einer Region

Hier ist der direkte Vergleich:

| Kriterium              | Isolierung auf Workspace-Ebene                               | Isolierung auf Catalog-Ebene                                 |
| ---------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Art der Trennung**   | **Infrastrukturell & Physisch** (separate Compute-Ressourcen, Netzwerke, Web-Oberflächen). | **Logisch** (gemeinsame Infrastruktur, Trennung rein über Daten-Metadaten). |
| **Sicherheitsgrenze**  | Maximal. Benutzer in Workspace A haben standardmäßig keinen Zugriff auf Workspace B. | Hoch. Der Zugriff wird zentral über Berechtigungen (Access Control Lists) gesteuert. |
| **Verwaltungsaufwand** | **Hoch**. Jede Umgebung (z. B. Dev, Test, Prod) benötigt eigene Cluster, Richtlinien und Konfigurationen. | **Gering**. Eine einzige Steuerungsebene (Control Plane) für alle Umgebungen. |
| **Datenfreigabe**      | Aufwendig. Daten müssen oft repliziert oder über externe Tools geteilt werden. | **Sehr einfach**. Daten können per Mausklick sicher zwischen Katalogen freigegeben werden. |
| **Kosten**             | Höher, da oft redundante Cloud-Ressourcen und Leerlaufzeiten entstehen. | Niedriger, da Ressourcen (wie SQL-Warehouses) effizient geteilt werden können. |

---

## F. Architektur des Kursprojekts

Die Architektur des Kursprojekts verbindet Kataloge, Workflow-Tests, Spark Declarative Pipeline und Datenvisualisierung.

![Architektur des Kursprojekts](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_planning_the_project/course_project_architecture.png)

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> Nachdem wir nun ein Verständnis unseres Projekts, unserer Daten und der Isolierung von Umgebungen haben, tauchen wir in das Projekt-Setup ein.
>
> In diesem Projekt erstellen wir einen Katalog für jede Umgebung: Dev, Stage und Prod.
>
> Der Dev-Katalog enthält eine kleine, statische Teilmenge unserer Produktionsdaten, die für Entwicklung und erste Tests verwendet wird.
>
> Der Stage-Katalog enthält eine größere Teilmenge der Produktionsdaten und ermöglicht umfassenderes Testen, während wir durch unseren CI/CD-Prozess voranschreiten.
>
> Schließlich enthält der Prod-Katalog die Live-Produktionsdaten, auf die wir uns für den finalen Betrieb verlassen.
>
> Unser Workflow beginnt mit der Entwicklung anhand der Dev-Daten, wobei wir Unit- und Integrationstests ausführen, während wir durch die Pipeline voranschreiten. Die Pipeline ist mit Databricks Lakeflow Jobs eingerichtet, die die Unit-Tests, die Spark Declarative Pipeline und die finalen Visualisierungen ausführen.
>
> Während wir die Pipeline durch jede Phase testen, stellen wir sicher, dass alles korrekt funktioniert, bevor wir in die Produktion deployen.

---

## Fazit

- Die Projektplanung beginnt mit dem Ergebnis: die Visualisierung von Gesundheitsdaten aus täglichen CSV-Dateien über Bronze-, Silber- und Gold-Tabellen.
- Entwicklungs-, Staging- und Produktionsumgebungen können mit Workspaces, Storage und Unity-Catalog-Zugriffssteuerungen isoliert werden.
- 

---

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
