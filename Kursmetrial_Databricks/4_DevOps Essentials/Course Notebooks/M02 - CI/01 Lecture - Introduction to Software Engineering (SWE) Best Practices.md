

> - **Lesbarkeit des Codes.** Schreiben Sie Code, der leicht zu verstehen und zu warten ist. Klarer, lesbarer Code reduziert Verwirrung und minimiert die Fehlerwahrscheinlichkeit, wenn Aktualisierungen oder Änderungen nötig sind.
>- die Verwendung konsistenter **Namenskonventionen**. Beschreibende, konsistente Namen für Variablen, Funktionen und Klassen machen Ihren Code selbsterklärend und verbessern die Zusammenarbeit im Team.
> - die Einbindung von **modularem Design in Ihre Codebasis.** Das bedeutet, Ihr Projekt in kleinere, wiederverwendbare Komponenten (wie Funktionen) zu zerlegen. Das macht Ihren Code nicht nur leichter wartbar, sondern ermöglicht auch reibungsloseres Skalieren, während Ihr Projekt wächst.
> - Sie können auch **Code-Linting-Werkzeuge** einsetzen, um diese Praktiken durchzusetzen. Linting-Werkzeuge analysieren Ihren Code automatisch auf potenzielle Fehler, Inkonsistenzen und Stilverstöße. Linting-Werkzeuge liegen zwar außerhalb des Umfangs dieses Kurses, sind aber eine hervorragende Ressource zur Verbesserung der Codequalität und zur Wahrung der Lesbarkeit.
> 
> **Code dokumentieren**
> 
>- Gute Dokumentation verbessert Folgendes:
> - Klare Dokumentation hilft Entwicklern, Zweck und Funktionalität des Codes zu verstehen, wodurch Aktualisierungen und Fehlerbehebungen schneller und einfacher werden.
>- Gute Dokumentation verbessert die Zusammenarbeit. Gut dokumentierter Code lässt Teammitglieder sich schnell einarbeiten und reduziert Missverständnisse und Fehler.
> - Dokumentation verbessert den Wissenstransfer. Durch das Dokumentieren Ihres Codes bleiben Schlüsselinformationen über Codedesign und -struktur erhalten, was reibungslose Übergänge sicherstellt, wenn Teammitglieder wechseln.
> 
> **Automatisiertes Testen**
> 
> - Ein Unit-Test überprüft die Funktionalität einer einzelnen Einheit oder Codekomponente, typischerweise isoliert, um sicherzustellen, dass sie sich wie erwartet verhält.
>- Integrationstests hingegen prüfen, wie verschiedene Komponenten oder Systeme zusammenarbeiten, um sicherzustellen, dass sie als Ganzes korrekt funktionieren.
> 
>**Versionskontrolle und Code-Review**
> 
> - Bei der Versionskontrolle sind Werkzeuge wie Git unerlässlich, um Änderungen zu verfolgen, mit Ihrem Team zusammenzuarbeiten und eine Historie Ihrer Codebasis zu führen. Sie ermöglichen es Ihnen, Änderungen zurückzurollen, mehrere Versionen zu verwalten und Konflikte zu vermeiden – und dabei Ihre Arbeit organisiert und sicher zu halten.
> - Als Nächstes: Code-Reviews. In Kombination mit Versionskontrolle sind Code-Reviews ein wirksames Mittel, um Fehler früh zu erkennen, die Codequalität zu verbessern und Konsistenz bei den Coding-Standards sicherzustellen. Code-Reviews fördern die Zusammenarbeit, ermutigen zum Wissensaustausch im Team und führen letztlich zu wartbarerem und zuverlässigerem Code.
> - Kurz gesagt: Nutzen Sie Versionskontrolle, um Ihre Codebasis effektiv zu verwalten, und die Durchführung von Code-Reviews hilft, die Qualität Ihres Codes durch Zusammenarbeit zu verbessern.
> 
>**CI/CD**
> 
>- Als Nächstes CI/CD, also Continuous Integration und Continuous Deployment/Delivery.
> - Auf hoher Ebene: Continuous Integration (CI) liegt vor, wenn Entwickler regelmäßig Code in ein gemeinsames Repository committen, bauen, testen und freigeben. Ziel ist es, Probleme frühzeitig durch kontinuierliche Integration und Tests zu erkennen.
> - Als Nächstes: Continuous Deployment (CD). Dies automatisiert die Freigabe von Code in die Produktion, nachdem Ihre automatisierten Tests (Unit- und Integrationstests) bestanden wurden. Ziel ist es, Features und Fixes schnell und konsistent zu liefern und Fehler zu vermeiden.
> - Dieser Kurs konzentriert sich hauptsächlich auf Continuous Integration innerhalb der CI/CD-Pipeline, mit einem Überblick über Continuous Deployment und Delivery.
> 
>**Isolierte Umgebungen**
> 
>- Zuletzt: Sie möchten Code nicht direkt an der Produktions-Codebasis ändern.
> - Organisationen verwenden oft unterschiedliche Umgebungen für jede Phase. Ein typisches Setup umfasst „Development & Stage“ und „Production“, dies kann jedoch je nach den Prozessen Ihrer Organisation variieren.
> - Getrennte Umgebungen helfen, Änderungen zu isolieren und gründliches Testen vor der Bereitstellung sicherzustellen, wodurch Probleme durch das Vermischen von Entwicklung und Produktion verhindert werden.
> - In Databricks können Sie Umgebungen auf verschiedene Arten isolieren:
> - Sie können mehrere Workspaces verwenden, einen pro Umgebung.
>- Oder Sie verwenden einen einzelnen Workspace mit mehreren Katalogen.
> - Ein großer Vorteil von Databricks ist Unity Catalog, das integrierte Funktionen wie Lineage, Sicherheit und Monitoring bietet – ganz ohne Drittanbieter-Werkzeuge.
>
> Dies war ein kurzer Überblick über einige wichtige Best Practices der Softwareentwicklung. Es gibt noch viele weitere, die wir in diesem Überblick nicht behandeln.
> 
> Diese Praktiken zielen darauf ab, qualitativ hochwertige, wartbare Software zu schaffen, die sich im Laufe der Zeit weiterentwickeln kann. Der Fokus liegt darauf, effizienten, lesbaren und fehlerfreien Code zu schreiben.
> 
> Behalten Sie im weiteren Verlauf im Hinterkopf, wie Ihnen diese Best Practices helfen können, bessere, effizientere Datenpipelines zu bauen.

---

### Überblick über die Werkzeuge

- **Databricks Workspaces** – Entwickeln Sie Code und führen Sie Unit-Tests in Databricks Workspaces oder lokal aus, mit Notebooks oder Dateien (SQL, Python, Scala usw.).
- **Databricks Git Folders** – Nutzen Sie Databricks Git Folders, um Versionskontrolle bereitzustellen und den Workflow erheblich zu verbessern.
- **Unity Catalog** – Konzentrieren Sie sich auf die Nutzung von Unity Catalog innerhalb eines einzelnen Workspace oder mehrerer Workspaces, um Ihre Umgebungen sicher zu isolieren und den notwendigen Datenzugriff bereitzustellen.
- **Databricks-Deployment-Werkzeuge** – Lassen Sie Code über CI/CD-Pipelines mit Databricks-Deployment-Werkzeugen testen & bereitstellen, um automatisch in Ihre gewünschte Umgebung zu deployen.

