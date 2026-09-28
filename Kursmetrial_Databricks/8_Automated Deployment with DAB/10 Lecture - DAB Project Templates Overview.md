In dieser kurzen Vorlesung lernen Sie, dass Sie ein Bundle nicht von Grund auf bauen müssen. Databricks stellt Standard-Bundle-Vorlagen bereit, um ein Projekt zu scaffolden, und Sie können auch Ihre eigenen benutzerdefinierten Vorlagen erstellen.

Verwenden Sie eine Databricks-Standard-Bundle-Vorlage, um Ihr Bundle mit `databricks bundle init` zu scaffolden.

Verfügbare Standardvorlagen: `default-python`, `default-sql`, `dbt-sql`, `mlops-stacks`.

```bash
databricks bundle init default-python
```

> **Zusätzliche Notizen (Sprechernotizen):**
>
> - Sie haben hier zwei Hauptoptionen: Sie können entweder die von Databricks bereitgestellten vorkonfigurierten Vorlagen verwenden oder Ihre eigenen benutzerdefinierten Vorlagen erstellen, um Ihre spezifischen Bedürfnisse zu erfüllen.
> - Databricks bietet mehrere Standard-Bundle-Vorlagen, darunter:
>   - `default-python` für Python-basierte Projekte
>   - `default-sql` für SQL-basierte Projekte
>   - `dbt-sql` für Projekte mit dbt-(Data-Build-Tool-)Workflows
>   - `mlops-stacks` für Machine-Learning-Operations-Stacks
> - Um mit einer dieser Vorlagen zu beginnen, verwenden Sie den Databricks-CLI-Befehl `databricks bundle init`. Dieser Befehl initialisiert Ihr Asset-Bundle automatisch basierend auf der ausgewählten Vorlage und erspart Ihnen Zeit beim Einrichten der Konfiguration von Grund auf.
> - Ein Hinweis: Wenn Sie eine Bundle-Vorlage innerhalb eines Databricks-Notebooks verwenden, erhalten Sie die gesamte Vorlage. Wenn Sie den CLI-Befehl außerhalb eines Notebooks ausführen, ermöglicht Ihnen eine Reihe von Eingabeaufforderungen, bestimmte Teile der Vorlage auszuwählen.

### A2. Benutzerdefinierte Bundle-Vorlagen

Sie können auch Ihre eigene Vorlage bauen und aus einem lokalen Pfad oder einer Remote-URL initialisieren.

- **Anforderungen** – benutzerdefinierte Vorlagen erfordern mindestens `databricks_template_schema.json` und `databricks.yml.tmpl`.
- **Anpassung** – Sie können Benutzer-Eingabeaufforderungen einbeziehen, Ordnerstrukturen definieren und Einstellungen anpassen.
- **Verwendung** – um eine benutzerdefinierte Vorlage zu verwenden, übergeben Sie einfach den lokalen Pfad oder die Remote-URL der Vorlage an den Databricks-CLI-Befehl `bundle init`.

```bash
databricks bundle init /projects/templates/test-template
```

> **Zusätzliche Notizen (Sprechernotizen):**
>
> - Zusätzlich zu den Standardvorlagen von Databricks können Sie benutzerdefinierte Bundle-Vorlagen erstellen, die spezifisch für Ihre Organisation sind.
> - Obwohl wir in diesem Kurs nicht auf die Details des Erstellens benutzerdefinierter Vorlagen eingehen, hier einige wichtige Punkte:
>   - Benutzerdefinierte Vorlagen erfordern mindestens `databricks_template_schema.json` und `databricks.yml.tmpl`.
>   - Sie können Benutzer-Eingabeaufforderungen einbeziehen, Ordnerstrukturen definieren und Einstellungen anpassen.
>   - Um eine benutzerdefinierte Vorlage zu verwenden, übergeben Sie einfach den lokalen Pfad oder die Remote-URL der Vorlage an den Databricks-CLI-Befehl `bundle init`.
> - Benutzerdefinierte Vorlagen helfen Organisationen, Bundles konsistent und wiederholbar zu erstellen und zu verwalten, indem Ordnerstrukturen, Tasks und DevOps-Infrastructure-as-Code (IaC) für Entwicklung und Deployment etabliert werden.

## B. Fazit

- Databricks stellt **Standard-Bundle-Vorlagen** (`default-python`, `default-sql`, `dbt-sql`, `mlops-stacks`) bereit, um ein Bundle mit `databricks bundle init` zu scaffolden.
- Sie können auch **benutzerdefinierte Vorlagen** bauen (Minimum: ein Schema-JSON und ein `databricks.yml.tmpl`) und aus einem lokalen Pfad oder einer URL initialisieren.
