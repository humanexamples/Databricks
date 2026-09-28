# Unity Catalog Volumes

Unity Catalog Volumes sind Databricks' empfohlener Weg, um nicht-tabellarische Daten mit zentraler Governance zu speichern und zu organisieren — der Nachfolger von Workspace Files und DBFS für alles, was über kleine Entwicklungsdateien hinausgeht. Dieses Dokument behandelt Volumes selbst, konkrete Speicherempfehlungen je Dateityp, das Schreiben beliebiger Dateien und das Entpacken von ZIP-Archiven. Basierend auf offiziellen Databricks-Doku-Seiten (jeweils am Ende jedes Abschnitts referenziert).

## Abschnittsübersicht

1. [Was sind Unity Catalog Volumes?](#was-sind)
2. [Managed vs. External Volumes](#volume-typen)
3. [Zugriffsmethoden](#zugriffsmethoden)
4. [Integrations-Anwendungsfälle](#integrationen)
5. [Speicherempfehlungen: Volumes vs. Workspace Files](#empfehlungen)
6. [Dateien in Volumes schreiben](#schreiben)
7. [ZIP-Dateien entpacken](#entpacken)
8. [Zusammenfassung](#zusammenfassung)

---

## <a id="was-sind">1. Was sind Unity Catalog Volumes?</a>

„Volumes sind Unity-Catalog-Objekte, die den Zugriff auf nicht-tabellarische Daten regeln. Sie bieten eine logische Schicht über dem Cloud-Object-Storage, sodass Dateien mit zentralisierter Governance gespeichert, organisiert und verwaltet werden können."

### Quelle

- https://docs.databricks.com/aws/en/files/volumes

---

## <a id="volume-typen">2. Managed vs. External Volumes</a>

Databricks unterstützt zwei Kategorien:

| Typ | Beschreibung |
|---|---|
| **Managed Volumes** | die Plattform verwaltet Storage-Lebenszyklus und Cloud-Speicherort |
| **External Volumes** | Nutzer kontrollieren Speicherort und Lebenszyklusverwaltung selbst |

### Quelle

- https://docs.databricks.com/aws/en/files/volumes

---

## <a id="zugriffsmethoden">3. Zugriffsmethoden</a>

### 3.1 Browser-Oberfläche

Dateien lassen sich über Catalog Explorer hochladen, herunterladen und durchsuchen. Die Plattform bietet zudem **„My Files"** — ein Beta-Feature mit einem Volume pro Nutzer für schnelle Dateispeicherung ohne den Aufbau eigener Catalog-Infrastruktur.

### 3.2 Programmatischer Zugriff

Daten lassen sich lesen und schreiben über:

- Apache Spark
- pandas
- SQL-Queries

### 3.3 Kommandozeilen-Tools

Dateiverwaltung ist verfügbar über:

- `dbutils.fs`-Utilities
- Magic Commands
- Bash-Shell-Befehle

### Quelle

- https://docs.databricks.com/aws/en/files/volumes

---

## <a id="integrationen">4. Integrations-Anwendungsfälle</a>

Volumes arbeiten mit mehreren Databricks-Features zusammen: Daten-Ingestion (`COPY INTO`, Auto Loader, Spark-APIs), Compute-Log-Zustellung, File-Arrival-Trigger, Cluster-Bibliotheken, Init-Skripte und MLflow-Experiment-Artefakt-Speicherung.

### Quelle

- https://docs.databricks.com/aws/en/files/volumes

---

## <a id="empfehlungen">5. Speicherempfehlungen: Volumes vs. Workspace Files</a>

Databricks empfiehlt, „Unity Catalog Volumes zum Speichern von Daten, Bibliotheken und Build-Artefakten" zu nutzen, während „Notebooks, SQL-Queries und Code-Dateien als Workspace Files" gespeichert werden. Kleine Testdatendateien können ebenfalls in Workspace-Storage liegen.

### 5.1 In Unity Catalog Volumes speichern

- Strukturierte Daten (Parquet-, ORC-Dateien)
- Semi-strukturierte Daten (CSV-, TXT-, JSON-Dateien)
- Unstrukturierte Inhalte (Bilder, Audio, PDFs, Dokumente)
- Rohdaten zur Exploration
- Betriebs-/Log-Dateien
- Große Archive (ZIP-Dateien, siehe Abschnitt 7)
- Build-Artefakte und Bibliotheken (Wheels, JAR-Dateien)
- Workspace-übergreifende Konfigurationsdateien

### 5.2 Als Workspace Files speichern

- Databricks-Objekte (Notebooks, Queries)
- Quellcode-Dateien (Python, Java, Scala) — vorzugsweise in Git-Ordnern für Versionskontrolle
- Projektspezifische Konfigurationsdateien innerhalb von Git-Repositories
- Kleine Dateien unter 500 MB

### 5.3 Wichtige operative Unterschiede

| Aspekt | Workspace Files | Unity Catalog Volumes |
|---|---|---|
| **Zugänglichkeit** | nur ein Workspace | über alle Workspaces zugänglich |
| **Max. Upload/Download** | 500 MB | 5 GB |
| **Berechtigungsmodell** | Workspace-ACLs | Unity-Catalog-verwaltet, workspace-übergreifend |
| **Tabellenerstellung** | nicht unterstützt | unterstützt über `COPY INTO`, Auto Loader |
| **External Storage** | nicht unterstützt | unterstützt External Volumes |
| **UDF-Unterstützung** | nicht unterstützt | unterstützt über FUSE |

### Quelle

- https://docs.databricks.com/aws/en/files/files-recommendations

---

## <a id="schreiben">6. Dateien in Volumes schreiben</a>

Über Apache Spark lassen sich Dateien nach folgendem Pfadmuster in Unity-Catalog-Volumes schreiben:

```
/Volumes/<catalog>/<schema>/<volume>/<path>/<file-name>
```

**Hinweis zur Quelldokumentation:** Die offizielle Seite beschränkt sich auf diese Pfadsyntax — sie erklärt primär, *wohin* Databricks Daten schreibt, ohne eigene Implementierungsbeispiele für DataFrame-Exporte, Uploads von der lokalen Maschine oder das Speichern von Plots/Bildern zu liefern. Für konkrete Lese-/Schreib-Codebeispiele siehe Abschnitt 9.3 in [Datei-Speicheroptionen und Workspace Files.md](Datei-Speicheroptionen%20und%20Workspace%20Files.md) (analog auf Volume-Pfade übertragbar) sowie das ZIP-Beispiel in Abschnitt 7 dieses Dokuments, das einen vollständigen Schreib-in-Volume-Workflow zeigt.

### Quelle

- https://docs.databricks.com/aws/en/files/write-data

---

## <a id="entpacken">7. ZIP-Dateien entpacken</a>

### 7.1 Bash-Befehl-Ansatz

Die primäre dokumentierte Methode nutzt den `unzip`-Bash-Befehl: „Der `unzip`-Bash-Befehl lässt sich nutzen, um ZIP-komprimierte Dateien oder Verzeichnisse von Dateien zu expandieren." Der Databricks-`%sh`-Magic-Command erlaubt die Ausführung von Bash-Operationen einschließlich des Entpackens.

### 7.2 Apache-Spark-native Unterstützung

Für Parquet-Dateien bietet Spark eingebaute Codec-Unterstützung: „Die meisten von Databricks geschriebenen Parquet-Dateien enden auf `.snappy.parquet`, was auf Snappy-Kompression hinweist" — Parquet-Dateien müssen also in der Regel nicht manuell entpackt werden.

### 7.3 Vollständiges Beispiel: Herunterladen, Entpacken, in Volume verschieben, lesen

```bash
%sh curl https://resources.lendingclub.com/LoanStats3a.csv.zip --output /tmp/LoanStats3a.csv.zip
unzip /tmp/LoanStats3a.csv.zip
```

```python
%sh mv /tmp/LoanStats3a.csv /Volumes/my_catalog/my_schema/my_volume/LoanStats3a.csv
```

```python
df = spark.read.format("csv").option("skipRows", 1).option("header", True).load("/Volumes/my_catalog/my_schema/my_volume/LoanStats3a.csv")
display(df)
```

### Quelle

- https://docs.databricks.com/aws/en/files/unzip-files

---

## <a id="zusammenfassung">8. Zusammenfassung</a>

- **Unity Catalog Volumes** bieten eine governte, workspace-übergreifende Schicht über Cloud-Object-Storage für nicht-tabellarische Daten — in **Managed** (Plattform verwaltet Lebenszyklus) und **External** (Nutzer verwaltet Speicherort) Varianten.
- Zugriff über Catalog Explorer, Spark, pandas, SQL, `dbutils.fs`, Magic Commands oder Bash-Shell.
- **Klare Arbeitsteilung:** Volumes für Daten/Bibliotheken/Build-Artefakte, Workspace Files für Notebooks/Quellcode/kleine Testdaten — Volumes erlauben größere Uploads (5 GB vs. 500 MB), workspace-übergreifenden Zugriff, Tabellenerstellung über `COPY INTO`/Auto Loader und UDF-Zugriff über FUSE.
- Dateien werden nach dem Muster `/Volumes/<catalog>/<schema>/<volume>/<path>/<file-name>` referenziert — sowohl beim Lesen als auch beim Schreiben.
- **ZIP-Archive** lassen sich unkompliziert über den Bash-Befehl `unzip` (via `%sh`-Magic-Command) entpacken und anschließend per `mv` in ein Volume verschieben.
