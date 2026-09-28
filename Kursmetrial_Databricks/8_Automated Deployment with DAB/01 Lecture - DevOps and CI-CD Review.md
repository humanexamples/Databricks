

### Der DevOps-Lebenszyklus

DevOps ist ein Prozess zur kontinuierlichen Integration, zum Testen und Deployen Ihres Codes.

![Bild](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/Includes/images/lecture_devops_review/ci-cd_role.png)

Dieselben DevOps-Prinzipien erstrecken sich auf Datenpipelines als DataOps und auf Machine Learning als MLOps.

- **DevOps** – DevOps geht um die Automatisierung von Prozessen, verbesserte Zusammenarbeit, Testen und schnellere Auslieferung. 

  DataOps = DevOps für Data Engineering: DataOps wendet dieselben Prinzipien von Automatisierung, Zusammenarbeit und kontinuierlicher Verbesserung auf Ihre Daten-Workflows an.

- **DataOps** (Data Engineering) – eine Teilmenge von DevOps, die DevOps auf Data Engineering anwendet. Es automatisiert die Verwaltung von Datenpipelines und sichert reibungslose, zuverlässige Datenflüsse von der Erfassung bis zur Verarbeitung. Das bedeutet weniger Engpässe und schnellere Erkenntnisse.

- **MLOps** (Machine Learning) – die Anwendung von DevOps auf Machine Learning. Es strafft den Prozess des Deployens und Verwaltens von ML-Modellen und sichert, dass Modelle schnell von der Entwicklung in die Produktion gelangen und auf Leistung überwacht werden.

### CI/CD in DevOps

- **Continuous Integration (CI)** betont Planung, Entwicklung, Umgebungsverwaltung und das Testen der Pipelines.
- **Continuous Deployment/Delivery (CD)** konzentriert sich auf die Automatisierung von Release-Prozessen, Deployment, Betrieb und Monitoring dieser Pipelines.



Vier wesentliche Vorteile von Continuous Integration:

- **Frühe Erkennung** – durch häufige Integration werden Bugs und Konflikte früh erkannt, was sie leichter behebbar macht.
- **Schnellerer Zyklus** – häufige Integration beschleunigt die Auslieferung neuer Funktionen und Fixes.
- **Zusammenarbeit** – regelmäßige Integration führt zu saubererem, modularerem Code und besserer Teamarbeit.
- **Automatisiertes Testen** – automatisierte Tests laufen bei jeder Integration und sichern, dass der Code stabil ist und mit bestehenden Funktionen zusammenarbeitet.

### B3. Review der Testschritte auf hoher Ebene

Automatisiertes Testen folgt der **Testpyramide**: schnelle, günstige Tests an der Basis laufen ständig; langsamere, breitere Tests an der Spitze laufen seltener.

- **Systemtests** – testen die gesamte Anwendung und sichern, dass alle Teile in einem realen Szenario zusammen funktionieren.
  *Bsp.:* End-to-End-Datenpipeline in einem Workflow. (Am langsamsten und teuersten.)
- **Integrationstests** – testen die Interaktion zwischen verschiedenen Komponenten oder Systemen.
  *Bsp.:* Notebooks / Declarative Pipelines / Jobs.
- **Unit-Tests** – testen **einzelne** Funktionen oder Methoden isoliert. Schnell, kostengünstig, hohe Abdeckung und automatisiert.
  *Bsp.:* Benutzerdefinierte PySpark-Funktionen. (Die Basis der Pyramide.)

### B4. Continuous Delivery/Deployment (CD) – Überblick

Beide teilen dieselbe automatisierte Pipeline bis zum Staging. **Continuous Delivery** behält ein manuelles Tor vor der Produktion; **Continuous Deployment** automatisiert auch diesen letzten Schritt.

**Continuous Delivery (CD) – manueller Push in die Produktion**

Pusht Änderungen automatisch nach Staging/Pre-Production, **mit der Möglichkeit, jederzeit manuell in die Produktion zu deployen**.

`Develop → Version Control → [AUTO] Build → [AUTO] Test → [AUTO] Deploy to Stage → [MANUELL] Deploy to Production`

**Continuous Deployment (CD) – automatischer Push in die Produktion**

Ein **vollständig automatisierter Prozess**, bei dem jede Änderung, die Tests besteht, sofort in die **Produktion** deployed wird.

`Develop → Version Control → [AUTO] Build → [AUTO] Test → [AUTO] Deploy to Stage → [AUTO] Deploy to Production`

> Continuous Deployment erfordert gut gestaltete Tests, um zuverlässig entscheiden zu können, dass die Pipeline deployed werden soll.

### B5. Überblick über den CI/CD-Workflow auf hoher Ebene

Der vollständige Workflow kombiniert **Continuous Integration** (entwickeln, bauen, testen, Versionskontrolle) mit **Continuous Delivery/Deployment** (Deploy to Stage, Deploy to Production).

`Develop → Build → Test → Version Control` *(Continuous Integration)*
`→ Deploy to Stage → Deploy to Production` *(Continuous Delivery / Continuous Deployment)*

> CI/CD strafft die Entwicklung von Datenpipelines, indem Testen und Deployment automatisiert werden, was zu schnelleren, zuverlässigeren Releases führt. Dieser Ansatz minimiert manuelle Fehler, verbessert die Zusammenarbeit und sichert hochwertige Software, die schnell und konsistent ausgeliefert wird.

### B6. Umgebungen für CI/CD isolieren

Ein CI/CD-Workflow hält Entwicklung und Testen von der Live-Produktion fern. In Databricks isolieren Sie Umgebungen über mehrere **Workspaces**, mehrere **Catalogs** oder beides.

- **Workspaces** – mehrere Workspaces verwenden, einen für jede Umgebung (DEV, STAGE, PROD).
- **Catalogs** – mehrere Catalogs verwenden, einen für jede Umgebung (DEV, STAGE, PROD).

> Das minimale Setup sind zwei Umgebungen (Development & Stage, und Production), aber dies variiert je nach den Anforderungen Ihrer Organisation.

### B7. Ihre Daten für CI/CD einrichten

Jede Umgebung verwendet Daten, die für ihren Zweck geeignet sind – von kleinen, anonymisierten Sätzen in der Entwicklung bis zu echten, geschützten Daten in der Produktion.

**Dev-Daten**
- Oft eine kleine, statische Teilmenge der Produktionsdaten
- Anonymisierte oder synthetische Datensätze
- Unterstützt schnelle Entwicklung und Tests
- Sichert Datenschutz und Datenintegrität

**Stage-Daten**
- Spiegeln Produktionsstruktur und -volumen wider, typischerweise statisch
- Anonymisiert oder von sensiblen Informationen bereinigt
- Sichern realistisches Testen und Validieren

**Prod-Daten**
- Live und voll betriebsbereit
- Enthalten echte Benutzerdaten, kontinuierlich aktualisiert
- Erfordern hohe Sicherheit, Datenschutz und Compliance

### B8. Deployment-Werkzeuge in Databricks – Überblick

Databricks bietet drei Wege, das Deployment zu automatisieren: die **REST-API**, die **Databricks-SDKs** und die **Databricks CLI**. Dieser Kurs verwendet die CLI mit Declarative Automation Bundles (DABs).

**REST-API**
- Bietet direkten Zugriff auf Databricks-Funktionalität über HTTP-Anfragen
- Erfordert die **manuelle Konstruktion** von HTTP-Anfragen und die Behandlung von Antworten

**Databricks SDK**
- Beschleunigt die Entwicklung; deckt alle öffentlichen REST-API-Operationen ab
- SDKs für: Python, Java, Go, R

**Databricks CLI**
- Einfach zu bedienende Schnittstelle für Automatisierung aus Terminal, Eingabeaufforderung oder Bash-Skripten
- Verwenden Sie **Declarative Automation Bundles (DABs)** innerhalb der CLI, um Infrastruktur als Code zu schreiben
- *In diesem Kurs verwendete Methode*

### B9. Die Databricks CLI verwenden: Verbindung und Authentifizierung

Es gibt drei gängige Wege, sich mit der Databricks CLI zu verbinden und zu authentifizieren, je nach Ihren Bedürfnissen. Dieser Kurs verwendet primär den **Notebook**-Ansatz.

**Web-Terminal**
- CLI-Befehle aus dem Databricks-Web-Terminal ausführen
- Ermöglicht Shell-Befehle in Databricks
- Verwendet standardmäßig die neueste Version der CLI
- Authentifizierung basierend auf dem aktuellen Benutzer
- Muss aktiviert werden

**VS Code**
- Die CLI lokal installieren und verwenden
- Sie müssen sich bei Databricks authentifizieren
- Verwenden Sie die Databricks VS Code Extension für zusätzliche Funktionen

**Databricks-Notebook**
- Shell-Befehle mit `%sh` in einem Notebook ausführen
- Die Databricks CLI installieren und verwenden
- Mit einem Token authentifizieren, um die CLI zu verwenden
- *Hauptmethode in diesem Kurs*

- 

### Nächste Schritte

Bevor Sie fortfahren, müssen Sie das erforderliche Setup-Notebook ausführen: `./02 - REQUIRED - Course Setup and Authentication`. Es erstellt die isolierten Catalogs und konfiguriert die Databricks-CLI-Authentifizierung, die in jedem Demo und Lab verwendet wird. Wenn Sie es überspringen, funktioniert der Rest des Kurses nicht korrekt.

---

&copy; 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
