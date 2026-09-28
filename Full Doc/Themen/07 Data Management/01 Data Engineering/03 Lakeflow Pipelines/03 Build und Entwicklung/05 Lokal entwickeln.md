# Pipeline-Code in der lokalen Entwicklungsumgebung entwickeln — Referenz

Dieses Dokument fasst zusammen, wie sich Lakeflow-Declarative-Pipeline-Code (LDP) in einer lokalen IDE entwickeln, lokal testen und anschließend vom lokalen Rechner aus in einem Databricks-Workspace validieren, deployen und ausführen lässt. Jede faktische Aussage wurde per `WebFetch` gegen die offizielle Databricks-Online-Dokumentation verifiziert; die Azure/Microsoft-Learn-Spiegelseite lieferte den vollständigen, wörtlich zitierbaren Seiteninhalt und wurde als Hauptquelle für die Zitate verwendet, inhaltlich deckungsgleich mit der AWS-Fassung.

## Abschnittsübersicht

1. [Übersicht und Verhältnis zu Apache Spark Declarative Pipelines](#uebersicht)
2. [Pipeline-Code mit IDE-Unterstützung schreiben](#ide-support)
3. [Transformationslogik für lokale Tests trennen](#transformationslogik)
4. [Pipelines lokal zum Testen ausführen](#lokal-ausfuehren)
5. [Pipelines von der lokalen Umgebung aus in Databricks ausführen](#in-databricks-ausfuehren)
6. [Pipeline-Code von der IDE in einen Workspace synchronisieren](#sync-optionen)
7. [Quellen](#quellen)

---

## <a id="uebersicht">1. Übersicht und Verhältnis zu Apache Spark Declarative Pipelines</a>

Python-Pipeline-Quellcode lässt sich in der bevorzugten integrierten Entwicklungsumgebung (IDE) verfassen, lokal zum Testen ausführen und anschließend validieren, deployen und als Update im Databricks-Workspace ausführen, ohne die lokale Umgebung zu verlassen.

Lakeflow-Pipelines sind eine Obermenge von Apache Spark™ Declarative Pipelines. Code, der ausschließlich Apache-Spark-Declarative-Pipelines-APIs verwendet, läuft sowohl lokal als auch auf Databricks. Code, der Funktionen nutzt, die spezifisch für Lakeflow-Pipelines sind — etwa `AUTO CDC` und Expectations —, läuft dagegen nur auf Databricks. Für die genauen Funktionsunterschiede verweist die Doku auf die Seite "Lakeflow pipelines Python language reference".

Für interaktive Entwicklung und Tests direkt im Databricks-Workspace verweist die Doku auf den Lakeflow Pipelines Editor ("Develop and debug ETL pipelines with the Lakeflow Pipelines Editor").

---

## <a id="ide-support">2. Pipeline-Code mit IDE-Unterstützung schreiben</a>

Pipeline-Code wird mit dem Modul `pyspark.pipelines` geschrieben, importiert als `dp`:

```python
from pyspark import pipelines as dp
```

Da das Modul Teil von Apache Spark ist, bietet die IDE dabei Syntaxprüfung, Autovervollständigung und Typprüfung. Apache-Spark-Declarative-Pipelines-Code läuft dabei typischerweise unverändert auf Databricks. Derselbe Import-Befehl importiert innerhalb einer Lakeflow-Pipeline die Databricks-eigene Version von `pipelines`.

---

## <a id="transformationslogik">3. Transformationslogik für lokale Tests trennen</a>

Der wirksamste Weg, Pipeline-Code lokal testbar zu machen, besteht darin, die Transformationslogik in einfachen PySpark-Funktionen zu halten, getrennt von den `dp`-Decorators. Eine Funktion, die einen DataFrame entgegennimmt und einen DataFrame zurückgibt, hat keine Abhängigkeit zur Lakeflow-Pipelines-Runtime und lässt sich daher mit `pytest` lokal testen, genau wie jeder andere Apache-Spark-Code. Die dekorierten Funktionen sollten dünn gehalten werden, sodass sie die Logik nur importieren und aufrufen:

```python
# transformations/clean.py — pure PySpark, unit-testable on its own
def clean_orders(df):
    return df.filter("quantity > 0").withColumn("amount_usd", df.amount.cast("double"))

# pipeline file — a thin dp wrapper that imports and calls the logic
from pyspark import pipelines as dp
from transformations.clean import clean_orders

@dp.table(name="orders_silver")
def orders_silver():
    return clean_orders(spark.readStream.table("orders_bronze"))
```

Die geteilte Logik lässt sich als Wheel verpacken, um sie über mehrere Pipelines hinweg wiederzuverwenden. Für eine vollständige Anleitung zum Schreiben und Ausführen von Unit-Tests verweist die Doku auf die Seite "Unit testing for pipelines" (siehe `Unit Testing.md` in diesem Themenblock).

---

## <a id="lokal-ausfuehren">4. Pipelines lokal zum Testen ausführen</a>

Pipelines können auch lokal ausgeführt werden, um Code zu entwickeln und zu testen, bevor er auf Databricks läuft. Dazu dient das Kommandozeilen-Interface `spark-pipelines`, mit dem sich eine Pipeline mit lokalem Apache Spark initialisieren, validieren und ausführen lässt. Für Details verweist die Doku auf den "Spark Declarative Pipelines Programming Guide" in der Apache-Spark-Dokumentation.

Eine vollständige Pipeline nutzt laut Doku drei komplementäre Testebenen, von denen sich zwei lokal ausführen lassen:

- **Unit-Tests** für die Transformationslogik, ausgeführt mit `pytest` gegen die oben beschriebenen einfachen PySpark-Funktionen. Diese benötigen keine Pipeline-Runtime.
- **Validierung (Dry Run)** des Pipeline-Graphen, des Quellcodes und der Dataset-Referenzen, entweder lokal mit `spark-pipelines` oder mit `databricks pipelines dry-run` gegen den Workspace — jeweils ohne Daten zu schreiben.
- **Expectations**, die Datenqualitätsregeln bei jeder Zeile jedes Laufs auswerten. Da sie eine Runtime-Funktion von Lakeflow-Pipelines sind, laufen sie **nur auf Databricks, nicht lokal**.

Funktionalität, die spezifisch für Lakeflow-Pipelines ist, lässt sich lokal nicht ausführen oder testen. Dazu zählen laut Doku explizit Expectations und `AUTO CDC`-Funktionen.

**Ungeklärt:** Die genauen Kommandozeilen-Flags und die vollständige Optionsreferenz von `spark-pipelines init`, `spark-pipelines validate`/`dry-run` und `spark-pipelines run` werden auf dieser Seite nicht aufgeführt — die Doku verweist dafür ausdrücklich auf den externen "Spark Declarative Pipelines Programming Guide" der Apache-Spark-Dokumentation, der hier nicht mit abgerufen wurde.

---

## <a id="in-databricks-ausfuehren">5. Pipelines von der lokalen Umgebung aus in Databricks ausführen</a>

Mit der Befehlsgruppe `databricks pipelines` lassen sich Pipeline-Updates im Workspace direkt vom Terminal aus validieren, deployen und ausführen:

```bash
databricks pipelines init      # scaffold a pipeline project
databricks pipelines dry-run   # validate the pipeline graph without publishing data
databricks pipelines deploy    # deploy the project to your workspace
databricks pipelines run       # run an update
```

Pipeline-Updates laufen im Databricks-Workspace, nicht auf dem lokalen Rechner, unter Verwendung der für die Pipeline konfigurierten Compute-Ressourcen. Diese Befehle sind mit den `bundle`-Befehlen der Declarative Automation Bundles interoperabel, sodass sich mit einem einfachen Projekt beginnen lässt, das später um Bundle-Konfiguration und CI/CD-Praktiken erweitert wird.

Für Installation und Konfiguration der CLI verweist die Doku auf "Install or update the Databricks CLI", für die vollständige Befehlsreferenz auf die "`pipelines` command group", und für eine schrittweise Anleitung auf "Develop pipelines with Declarative Automation Bundles".

**Ungeklärt:** Konkrete YAML-Konfigurationsdateien (z. B. `databricks.yml` bzw. `pipeline.yml`) sind auf dieser Seite selbst nicht enthalten — sie werden nur über Verweise auf die separate Bundle-Tutorial-Seite referenziert, die hier nicht mit abgerufen wurde.

---

## <a id="sync-optionen">6. Pipeline-Code von der IDE in einen Workspace synchronisieren</a>

Die folgende Tabelle fasst die Optionen zum Synchronisieren von Pipeline-Quellcode zwischen lokaler IDE und Databricks-Workspace zusammen:

| Werkzeug/Muster | Details |
|---|---|
| Databricks CLI (`pipelines`-Befehlsgruppe) | Mit den `databricks pipelines`-Befehlen lässt sich ein Pipeline-Projekt aus der lokalen Umgebung deployen und ausführen. |
| Declarative Automation Bundles | Damit lassen sich Pipeline-Assets unterschiedlicher Komplexität deployen — von einer einzelnen Quellcode-Datei bis zu Konfigurationen für mehrere Pipelines, Jobs und Quellcode-Dateien. |
| Databricks-IDE-Erweiterung | Databricks bietet eine Integration für Visual Studio Code mit einfacher Synchronisierung zwischen lokaler IDE und Workspace-Dateien; die Erweiterung stellt außerdem Werkzeuge bereit, um Pipeline-Assets über Declarative Automation Bundles zu deployen. |
| Workspace-Dateien | Über Databricks-Workspace-Dateien lässt sich Pipeline-Quellcode in den Workspace hochladen und anschließend in eine Pipeline importieren. |
| Git-Ordner | Git-Ordner ermöglichen die Synchronisierung von Code zwischen lokaler Umgebung und Databricks-Workspace über ein Git-Repository als Vermittler. |

---

## <a id="quellen">Quellen</a>

- [Develop pipeline code in your local development environment (AWS)](https://docs.databricks.com/aws/en/ldp/develop-locally) — abgerufen 2026-08-19
- [Develop pipeline code in your local development environment (Azure/Microsoft Learn, vollständiger Wortlaut)](https://learn.microsoft.com/en-us/azure/databricks/ldp/develop-locally) — abgerufen 2026-08-19
