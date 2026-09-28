## Continuous Integration (CI) und Continuous Deployment (CD)

![CI/CD-Workflow auf hoher Ebene](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_role_ci-cd_devops/high_level_ci-cd_overview.png)

![Rolle von CI/CD](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_role_ci-cd_devops/ci-cd_role.png)

---

CI umfasst das regelmäßige Zusammenführen von Codeänderungen mehrerer Beitragender in ein zentrales Repository und das Ausführen automatisierter Tests, um die Codequalität sicherzustellen.

## Testschritte auf hoher Ebene

![Testübersicht auf hoher Ebene](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_role_ci-cd_devops/high_level_testing_strip.png)

- **Systemtests** – Testen die gesamte Anwendung und stellen sicher, dass alle Teile in einem realitätsnahen / produktionsähnlichen Szenario zusammen funktionieren. Bsp.: End-to-End-Datenpipeline in einem Job.
- **Integrationstests** – Testen die Interaktion zwischen verschiedenen Komponenten oder Systemen. Bsp.: Interaktionen von Notebooks / SDP / Jobs.
- **Unit-Tests** – Testen einzelne Funktionen oder Methoden isoliert. Schnell, kostengünstig, hohe Abdeckung und automatisiert. Bsp.: Eigene PySpark-Funktionen.

---

## Continuous Delivery/Deployment (CD) – Überblick

**Continuous Delivery (CD):** Automatisches Übertragen von Änderungen in Staging-/Pre-Produktions-Umgebungen mit der Möglichkeit, jederzeit **manuell** in die Produktion zu deployen.

![CD-Überblick auf hoher Ebene](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_role_ci-cd_devops/cd_overview.png)



**Continuous Deployment (CD)** – Vollständig automatisierter Prozess, bei dem jede Änderung, die die Tests besteht, sofort in die Produktion bereitgestellt wird.

![CD-Überblick](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_role_ci-cd_devops/cd_overview_auto.png)

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> Continuous Deployment treibt die Automatisierung einen Schritt weiter. Sobald eine Änderung alle Tests besteht, wird sie automatisch in die Produktion bereitgestellt, wodurch sichergestellt wird, dass neue Features oder Fixes schnell und nahtlos ohne manuellen Eingriff geliefert werden.
>
> Wenn Ihre Continuous-Integration-Prozesse zum Beispiel aufeinander abgestimmt und gut umgesetzt sind, können wir unsere Datenpipeline automatisch von der Entwicklung über Staging bis in die Produktion deployen und manuelle Bereitstellungsschritte vermeiden. Die Umsetzung dieser Technik erfordert gut durchdachte Tests, um sicherzustellen, dass die Pipeline bereitgestellt werden sollte.




