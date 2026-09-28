# Serverless Compute für Notebooks

> Quelle: <https://docs.databricks.com/aws/en/compute/serverless/notebooks>

## Voraussetzungen

- Der Workspace muss für **Unity Catalog** aktiviert sein.
- Keine zusätzlichen Berechtigungen nötig, sofern Serverless Interactive Compute im Workspace aktiviert ist (Zugriff steuerbar — siehe [11 Serverless Compute verwalten.md](11%20Serverless%20Compute%20verwalten.md)).

## Notebook an Serverless Compute anhängen

- Im Notebook das **Compute-Dropdown** öffnen und **Serverless** auswählen.
- Neue Notebooks verwenden beim ersten Ausführen von Code **standardmäßig Serverless**, wenn keine andere Ressource gewählt ist.

## Query Insights / „See performance"

- Nach der Ausführung einer Zelle liefert der Link **„See performance"** SQL- und Python-Query-Metriken.
- Alle Abfragen werden in der **Query History** des Workspace erfasst.
- **Nicht** verfügbar: Spark UI, Download des Query-Profils, Verbose-Metriken (nutze stattdessen Query Profile / Query History — siehe [09 Einschraenkungen.md](09%20Einschraenkungen.md)).

## Execution Timeout

- Serverless Notebooks haben einen **Standard-Execution-Timeout von 2,5 Stunden (9.000 Sekunden)**, um „durchgehende" Abfragen zu verhindern.
- Konfigurierbar auf **Workspace-Ebene** (Admin-Einstellungen → Compute → *Serverless interactive execution timeout*) und auf **Notebook-Ebene** über die Spark-Property **`spark.databricks.execution.timeout`**.

> Vgl. Jobs: dort gibt es standardmäßig **keinen** Query-Execution-Timeout (ebenfalls über `spark.databricks.execution.timeout` konfigurierbar); maximale Laufzeit einer Serverless-Ausführung: **7 Tage** (siehe [09 Einschraenkungen.md](09%20Einschraenkungen.md)).

## Umgebung / Sprachen

- Serverless verwendet **Environment-Versionen** statt klassischer Databricks-Runtime-Versionen; Konfiguration der Umgebung (Base Environment, Abhängigkeiten, Memory, GPU) über das **Environment-Seitenpanel** — siehe [04 Umgebung und Abhaengigkeiten.md](04%20Umgebung%20und%20Abhaengigkeiten.md).
- Unterstützte Sprachen in Serverless Notebooks: **Python** und **SQL**. **Scala und R werden nicht unterstützt** (siehe [09 Einschraenkungen.md](09%20Einschraenkungen.md)).
- Neue Notebooks verwenden standardmäßig das `.ipynb`-Format.

## Verwandte Themen

- [03 Git-Ordner (Git Folder Serverless).md](03%20Git-Ordner%20(Git%20Folder%20Serverless).md)
- [04 Umgebung und Abhaengigkeiten.md](04%20Umgebung%20und%20Abhaengigkeiten.md)
