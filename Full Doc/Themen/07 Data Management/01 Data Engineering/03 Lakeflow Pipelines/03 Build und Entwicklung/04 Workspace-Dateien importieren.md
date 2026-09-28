# Python-Module aus Git-Ordnern oder Workspace-Dateien importieren — Referenz

Dieses Dokument fasst zusammen, wie sich Python-Code aus Databricks-Git-Ordnern oder Workspace-Dateien in eine Lakeflow-Declarative-Pipeline (LDP) importieren lässt. Jede faktische Aussage wurde per `WebFetch` gegen die offizielle Databricks-Online-Dokumentation verifiziert; die Azure/Microsoft-Learn-Spiegelseite lieferte den vollständigen, wörtlich zitierbaren Seiteninhalt und wurde als Hauptquelle für die Zitate verwendet, inhaltlich deckungsgleich mit der AWS-Fassung.

## Abschnittsübersicht

1. [Übersicht: Drei Wege, ein Python-Modul zu importieren](#uebersicht)
2. [Ein Python-Modul in eine Pipeline einbinden (Utility-Datei)](#utility-datei)
3. [Ein Python-Modul zur Pipeline-Umgebung hinzufügen (geteilte Module)](#pipeline-umgebung)
4. [Ein Python-Modul per `import`-Anweisung importieren](#import-anweisung)
5. [Praxisbeispiel: Dataset-Queries als Python-Module importieren](#praxisbeispiel)
6. [Quellen](#quellen)

---

## <a id="uebersicht">1. Übersicht: Drei Wege, ein Python-Modul zu importieren</a>

Python-Code kann in Databricks-Git-Ordnern oder in Workspace-Dateien gespeichert und anschließend in eine Pipeline importiert werden. Für allgemeine Informationen zur Arbeit mit Modulen in Git-Ordnern oder Workspace-Dateien verweist die Doku auf die Seite "Work with Python and R modules".

Um eine Python-Datei zu importieren, gibt es laut Doku mehrere Optionen:

- Das Python-Modul als Utility-Datei in die Pipeline einbinden. Das eignet sich am besten, wenn das Modul spezifisch für diese eine Pipeline ist.
- Ein geteiltes Modul der Pipeline-Umgebung hinzufügen, in jeder Pipeline, die es benötigt.
- Ein Modul im Workspace direkt über eine `import`-Anweisung in den Python-Quellcode importieren.

---

## <a id="utility-datei">2. Ein Python-Modul in eine Pipeline einbinden (Utility-Datei)</a>

Ein Python-Modul kann als Teil der Pipeline selbst erstellt werden. Der Pipeline-Root-Ordner wird automatisch an den `sys.path` angehängt. Dadurch lässt sich das Modul direkt aus dem Python-Quellcode der Pipeline referenzieren.

Vorgehen laut Doku:

1. Die Pipeline im Pipeline-Editor öffnen.
2. Im Pipeline-Asset-Browser links auf **Add** (Plus-Symbol) klicken, dann **Utility** aus dem Menü wählen.
3. `my_utils.py` als **Name** eingeben.
4. Den Standardpfad belassen und auf **Create** klicken.

   Dadurch wird die Datei `my_utils.py` im Ordner `utilities` der Pipeline angelegt; existiert der Ordner `utilities` noch nicht, wird er ebenfalls erstellt. Die Dateien in diesem Ordner werden standardmäßig nicht zum Pipeline-Source hinzugefügt, sind aber aus den `.py`-Dateien aufrufbar, die Teil des Pipeline-Quellcodes sind.

   Die Utility-Datei enthält standardmäßig eine Beispielfunktion namens `distance_km()`, die eine Distanz in Meilen umrechnet.
5. In einer Python-Quelldatei im Transformations-Ordner (erstellbar über **Add** → **Transformation**) folgenden Code hinzufügen:

   ```python
   from utilities import my_utils
   ```

Funktionen aus `my_utils` können nun aufgerufen werden. Die `import`-Anweisung muss in jeder Python-Datei ergänzt werden, die Funktionen des Moduls aufrufen möchte.

---

## <a id="pipeline-umgebung">3. Ein Python-Modul zur Pipeline-Umgebung hinzufügen (geteilte Module)</a>

Soll ein Python-Modul über mehrere Pipelines hinweg geteilt werden, kann es an beliebiger Stelle in den Workspace-Dateien gespeichert und aus der Umgebung ("Environment") jeder Pipeline referenziert werden, die es benötigt. Referenzierbar sind laut Doku:

- Einzelne Python-Dateien (`.py`).
- Ein als Python-Wheel (`.whl`-Datei) verpacktes Python-Projekt.
- Ein unverpacktes Python-Projekt mit einer `pyproject.toml`-Datei (zur Definition von Projektname und -version).

Vorgehen zum Hinzufügen einer Abhängigkeit laut Doku:

1. Die Pipeline im Pipeline-Editor öffnen.
2. Oben in der Leiste auf **Settings** (Zahnrad-Symbol) klicken.
3. Im Ausklapp-Panel **Pipeline settings** unter **Pipeline environment** auf **Edit environment** (Stift-Symbol) klicken.
4. Eine Abhängigkeit hinzufügen. Beispiel für eine Datei im Workspace: `/Volumes/libraries/path/to/python_files/file.py`. Für ein in Git-Ordnern gespeichertes Python-Wheel: `/Workspace/libraries/path/to/wheel_files/file.whl`.

   Liegt die Datei im Root-Ordner der Pipeline, kann auch ganz ohne Pfad oder mit relativem Pfad referenziert werden.

**Hinweis aus der Doku:** Es lässt sich auch ein Pfad zu einem geteilten Ordner als Abhängigkeit hinzufügen, damit `import`-Anweisungen im Code die gewünschten Module finden — zum Beispiel `-e /Workspace/Users/<user_name>/path/to/add/`.

---

## <a id="import-anweisung">4. Ein Python-Modul per `import`-Anweisung importieren</a>

Eine Workspace-Datei lässt sich auch direkt im Python-Quellcode referenzieren:

- Liegt die Datei im Ordner `utilities` der Pipeline, kann sie ohne Pfadangabe referenziert werden:

  ```python
  from utilities import my_module
  ```

- Liegt die Datei an anderer Stelle, kann sie importiert werden, indem zunächst der Pfad des Moduls an `sys.path` angehängt wird:

  ```python
  import sys, os
  sys.path.append(os.path.abspath('<module-path>'))

  from my_module import *
  ```

- Alternativ kann der Pfad für alle Pipeline-Quelldateien zur Pipeline-Umgebung hinzugefügt werden (siehe Abschnitt 3).

---

## <a id="praxisbeispiel">5. Praxisbeispiel: Dataset-Queries als Python-Module importieren</a>

Das folgende, vollständig aus der Doku übernommene Beispiel demonstriert, wie Dataset-Queries als Python-Module aus Workspace-Dateien importiert werden. Obwohl das Beispiel Workspace-Dateien zur Speicherung des Pipeline-Quellcodes verwendet, lässt es sich laut Doku genauso mit in einem Git-Ordner gespeichertem Quellcode nutzen.

Vorgehen laut Doku:

1. In der Seitenleiste des Workspaces auf **Workspace** klicken, um den Workspace-Browser zu öffnen.
2. Im Workspace-Browser ein Verzeichnis für die Python-Module auswählen.
3. Im Kebab-Menü (⋮) der rechtesten Spalte des ausgewählten Verzeichnisses auf **Create → File** klicken.
4. Einen Dateinamen eingeben, zum Beispiel `clickstream_raw_module.py`. Der Datei-Editor öffnet sich. Um ein Modul zu erstellen, das Quelldaten in eine Tabelle einliest, folgenden Code eingeben:

   ```python
   from pyspark import pipelines as dp

   json_path = "/databricks-datasets/wikipedia-datasets/data-001/clickstream/raw-uncompressed-json/2015_2_clickstream.json"

   def create_clickstream_raw_table(spark):
     @dp.table
     def clickstream_raw():
       return (
         spark.read.json(json_path)
       )
   ```

5. Um ein Modul zu erstellen, das eine neue Tabelle mit aufbereiteten Daten anlegt, im selben Verzeichnis eine neue Datei anlegen, zum Beispiel `clickstream_prepared_module.py`, und Folgendes eingeben:

   ```python
   from clickstream_raw_module import *
   from pyspark import pipelines as dp
   from pyspark.sql.functions import *
   from pyspark.sql.types import *

   def create_clickstream_prepared_table(spark):
     create_clickstream_raw_table(spark)
     @dp.table
     @dp.expect("valid_current_page_title", "current_page_title IS NOT NULL")
     @dp.expect_or_fail("valid_count", "click_count > 0")
     def clickstream_prepared():
       return (
         spark.read("clickstream_raw")
           .withColumn("click_count", expr("CAST(n AS INT)"))
           .withColumnRenamed("curr_title", "current_page_title")
           .withColumnRenamed("prev_title", "previous_page_title")
           .select("current_page_title", "click_count", "previous_page_title")
       )
   ```

6. Anschließend im Pipeline-Editor eine Python-Datei im Pipeline-Quellcode anlegen: **Add** → **Transformation**.
7. Der Datei einen Namen geben und bestätigen, dass **Python** als Standardsprache eingestellt ist.
8. Auf **Create** klicken.
9. Folgenden Beispielcode in das Notebook eingeben:

   **Hinweis aus der Doku:** Importiert das Notebook Module oder Packages aus einem Workspace-Files-Pfad oder einem Git-Ordner-Pfad, der vom Notebook-Verzeichnis abweicht, muss der Pfad zu den Dateien manuell über `sys.path.append()` angehängt werden.

   Wird eine Datei aus einem Git-Ordner importiert, muss dem Pfad `/Workspace/` vorangestellt werden, zum Beispiel `sys.path.append('/Workspace/...')`. Wird `/Workspace/` im Pfad weggelassen, führt das zu einem Fehler.

   Liegen die Module oder Packages im selben Verzeichnis wie das Notebook, muss der Pfad nicht manuell angehängt werden. Ebenso ist beim Import aus dem Root-Verzeichnis eines Git-Ordners kein manuelles Anhängen nötig, da das Root-Verzeichnis automatisch an den Pfad angehängt wird.

   ```python
   import sys, os
   sys.path.append(os.path.abspath('<module-path>'))

   from pyspark import pipelines as dp
   from clickstream_prepared_module import *
   from pyspark.sql.functions import *
   from pyspark.sql.types import *

   create_clickstream_prepared_table(spark)

   @dp.table(
     comment="A table containing the top pages linking to the Apache Spark page."
   )
   def top_spark_referrers():
     return (
       spark.read.table("catalog_name.schema_name.clickstream_prepared")
         .filter(expr("current_page_title == 'Apache_Spark'"))
         .withColumnRenamed("previous_page_title", "referrer")
         .sort(desc("click_count"))
         .select("referrer", "click_count")
         .limit(10)
     )
   ```

   `<module-path>` ist durch den Pfad zum Verzeichnis mit den zu importierenden Python-Modulen zu ersetzen.
10. Zum Ausführen der Pipeline auf **Run pipeline** klicken.

---

## <a id="quellen">Quellen</a>

- [Import Python modules from Git folders or workspace files (AWS)](https://docs.databricks.com/aws/en/ldp/import-workspace-files) — abgerufen 2026-08-19
- [Import Python modules from Git folders or workspace files (Azure/Microsoft Learn, vollständiger Wortlaut)](https://learn.microsoft.com/en-us/azure/databricks/ldp/import-workspace-files) — abgerufen 2026-08-19
