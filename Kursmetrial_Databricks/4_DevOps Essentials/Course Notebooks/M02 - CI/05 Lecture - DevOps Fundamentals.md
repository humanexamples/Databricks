In dieser Vorlesung untersuchen wir das Konzept von DevOps und besprechen, wie es Lakeflow Jobs in Data Engineering und Machine Learning unterstützt und verbessert.

## Der DevOps-Lebenszyklus

**PLANEN → CODEN → BUILDEN → TESTEN → RELEASE → DEPLOYEN → BETREIBEN → MONITOREN**

- **Planen** – Features und Anforderungen des Projekts planen.
- **Coden** – Das Projekt coden.
- **Builden** – Den Code in ausführbare Dateien builden.
- **Testen** – Den Code durch automatisierte Tests testen.
- **Release** – Die paketierte Anwendung freigeben.
- **Deployen** – Das Projekt in Produktionsumgebungen bereitstellen.
- **Betreiben** – Die freigegebene Anwendung betreiben.
- **Monitoren** – Leistung überwachen und Feedback sammeln.

---

## D. DevOps für Data Engineering und Machine Learning

![DevOps für Data Engineering und Machine Learning](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_devops_fundamentals/devops_data_engg_machine_learning.png)



Wir können DevOps-Prinzipien auf Data Engineering und Machine Learning anwenden. Denken Sie daran: Bei DevOps geht es um das Automatisieren von Prozessen, das Verbessern der Zusammenarbeit, das Testen und das Beschleunigen der Lieferung.

DataOps ist eine Teilmenge von DevOps und wendet DevOps auf Data Engineering an. Es automatisiert die Verwaltung von Datenpipelines und stellt reibungslose, zuverlässige Datenflüsse von der Erhebung bis zur Verarbeitung sicher. Das bedeutet weniger Engpässe und schnellere Erkenntnisse.

Bei MLOps geht es darum, DevOps auf Machine Learning anzuwenden. Es strafft den Prozess des Bereitstellens und Verwaltens von ML-Modellen und stellt sicher, dass Modelle schnell von der Entwicklung in die Produktion gelangen und auf Leistung überwacht werden.

---

## E. DevOps, DataOps und MLOps

### DevOps

*Softwareentwicklung und IT-Betrieb*

- CI/CD automatisieren
- Kontinuierliches Testen von Code ermöglichen
- Versionskontrolle
- Produktionsreife Lakeflow Jobs etablieren
- Orchestrierung & Automatisierung
- Systemleistung überwachen

### DataOps

*Aufbau qualitativ hochwertiger Datenpipeline-Prozesse*

- Eine Reihe von Praktiken, Prozessen und Technologien
- Datenverarbeitung optimieren
- Datenerkennung, -verwaltung und -governance zentralisieren
- Nachvollziehbare Data Lineage und Monitoring etablieren
- Teamübergreifende Zusammenarbeit verbessern
- Datenqualität überwachen

### MLOps

*Entwicklung und Bereitstellung von ML-Modellen*

- Modellcode als Software behandeln
- Modelle als Daten behandeln
- Den Modell-Lebenszyklus verwalten
- Modellleistung überwachen

> Außerhalb des Umfangs dieses Kurses.

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> DevOps, DataOps und ModelOps sind eine Reihe von Praktiken, Prozessen und Technologien. Vergleichen wir die drei Ansätze, die Lakeflow Jobs in unterschiedlichen Technologiebereichen straffen.
>
> Schlüsseln wir sie auf.
>
> Bei DevOps geht es darum, die Lücke zwischen Softwareentwicklung und IT-Betrieb zu schließen. Das Hauptziel ist die Automatisierung von CI/CD, also Continuous Integration und Deployment, um Softwarebereitstellung schneller und zuverlässiger zu machen.
>
> Bei DevOps konzentrieren wir uns außerdem auf automatisiertes Testen und Versionskontrolle, um die Codequalität sicherzustellen. Ziel ist es, reibungslose, produktionsreife Lakeflow Jobs zu etablieren und die Orchestrierung zu automatisieren, um manuelle Arbeit zu reduzieren.
>
> Schließlich hilft das Monitoring der Systemleistung, Probleme frühzeitig zu erkennen, damit alles reibungslos läuft.
>
> Als Nächstes DataOps, bei dem es um den Aufbau qualitativ hochwertiger Datenpipeline-Prozesse geht. Es optimiert die Datenverarbeitung und zentralisiert Datenerkennung, -verwaltung und -governance mit Unity Catalog.
>
> DataOps betont außerdem nachvollziehbare Data Lineage, sodass Sie Daten in jeder Phase verfolgen können. Das Monitoring von Daten entlang der Pipeline stellt sicher, dass sie korrekt und zugänglich bleiben, und fördert gleichzeitig die Teamzusammenarbeit, um Datenfluss und -qualität zu verbessern.
>
> Schließlich haben wir ModelOps, das sich auf den Lebenszyklus von Machine-Learning-Modellen konzentriert. Es behandelt Modellcode wie Software und stellt sicher, dass er versioniert, getestet und effizient bereitgestellt wird.
>
> ModelOps konzentriert sich außerdem auf das Verwalten des Modell-Lebenszyklus und das Überwachen der Modellleistung nach der Bereitstellung, um sicherzustellen, dass Modelle im Laufe der Zeit korrekt und effektiv bleiben. MLOps liegt außerhalb des Umfangs dieses Kurses.

---

## F. DataOps = DevOps für Data Engineering

![DataOps DevOps für Data Engineering](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_devops_fundamentals/dataops_devops.png)

> Sie sollten darüber nachdenken, wie **DevOps**-Prinzipien und -Kultur auf Ihre **Data-Engineering-Pipelines** angewendet werden können.

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> DataOps ist im Wesentlichen DevOps für Data Engineering – es wendet dieselben Prinzipien von Automatisierung, Zusammenarbeit und kontinuierlicher Verbesserung auf Daten-Lakeflow-Jobs an. So wie DevOps die Softwarelieferung strafft, konzentriert sich DataOps darauf, Fluss, Qualität und Verwaltung von Datenpipelines zu optimieren.
>
> Letztlich sollten Sie darüber nachdenken, wie DevOps-Prinzipien und -Kultur auf Ihre Data-Engineering-Pipelines angewendet werden können.

