# Inkrementelle Ingestion aus Amazon S3 einrichten
Diese Anleitung beschreibt, wie inkrementelle Datenaufnahme aus Amazon S3 in Databricks eingerichtet wird: sicherer Zugriff auf Quelldaten im Cloud-Speicher über Unity-Catalog-Volumes (empfohlen) oder External Locations, gefolgt von inkrementeller Ingestion in Managed Tables mittels Auto Loader und Lakeflow-Pipelines. Für die Einrichtung in Databricks SQL statt in einem Notebook siehe stattdessen "Standalone-Streaming-Tabellen verwenden".

## Voraussetzungen

Falls Sie kein Admin sind, wird in dieser Anleitung vorausgesetzt, dass ein Admin bereits Folgendes bereitgestellt hat:

- Zugriff auf einen Databricks-Workspace mit aktiviertem Unity Catalog
- Die Berechtigung `READ VOLUME` auf dem Unity-Catalog-External-Volume bzw. die Berechtigung `READ FILES` auf der Unity-Catalog-External-Location, die den Quelldaten im Cloud-Speicher entspricht
- Den Pfad zu den Quelldaten:
  - Volume-Pfad-Beispiel: `/Volumes/<catalog>/<schema>/<volume>/<path>/<folder>`
  - External-Location-Pfad-Beispiel: `s3://<bucket>/<folder>/`
- Die Berechtigungen `USE SCHEMA` und `CREATE TABLE` auf dem Zielschema
- Berechtigung zum Erstellen eines Clusters oder Zugriff auf eine Cluster-Policy, die einen Pipeline-Cluster definiert (`cluster_type` auf `dlt` gesetzt)
- Bei Verwendung von Volume-Pfaden: Databricks Runtime 13.3 LTS oder höher

Bei Fragen zu den Voraussetzungen wenden Sie sich an Ihren Account-Admin.

## Schritt 1: Cluster erstellen

1. In den Databricks-Workspace einloggen.
2. In der Seitenleiste **New** > **Cluster** anklicken.
3. In der Cluster-UI einen eindeutigen Cluster-Namen vergeben.
4. Bei Verwendung eines Volume-Pfads: als **Databricks Runtime-Version** mindestens Databricks Runtime 13.2 auswählen.
5. **Create cluster** anklicken.

## Schritt 2: Notebook zur Datenexploration erstellen

1. In der Seitenleiste **+New** > **Notebook** anklicken (das Notebook wird automatisch an den zuletzt genutzten Cluster aus Schritt 1 angehängt).
2. Einen Notebook-Namen vergeben.
3. Über den Sprachauswahl-Button `Python` oder `SQL` wählen (Python ist Standard).
4. Zum Prüfen des Datenzugriffs folgenden Code in eine Zelle einfügen und ausführen (Run Menu > **Run Cell**). `<path-to-source-data>` durch den tatsächlichen Pfad zum Datenverzeichnis ersetzen. Das Ergebnis zeigt den Verzeichnisinhalt:

```sql
%sql
LIST '<path-to-source-data>'
```

```text
%fs ls '<path-to-source-data>'
```

5. Um Beispieldatensätze anzuzeigen, folgenden Code in eine Zelle einfügen und ausführen. `<file-format>` durch ein unterstütztes Dateiformat ersetzen (siehe DataFrameReader-Optionen), `<path-to-source-data>` durch den Pfad zu einer Datei im Datenverzeichnis. Das Ergebnis zeigt die ersten zehn Datensätze:

```sql
%sql
SELECT * from read_files('<path-to-source-data>', format => '<file-format>') LIMIT 10
```

```python
spark.read.format('<file-format>').load('<path-to-source-data>').limit(10).display()
```

## Schritt 3: Rohdaten einlesen

1. In der Seitenleiste **New** > **Notebook** anklicken (wird automatisch an den zuletzt genutzten Cluster angehängt).
2. Einen Notebook-Namen vergeben.
3. Über den Sprachauswahl-Button `Python` oder `SQL` wählen (Python ist Standard).
4. Folgenden Code in eine Zelle einfügen. `<table-name>` durch den Namen der Zieltabelle ersetzen, `<path-to-source-data>` durch den Quelldatenpfad und `<file-format>` durch ein unterstütztes Dateiformat:

```sql
%sql
CREATE OR REFRESH STREAMING TABLE <table-name>
AS SELECT
  *
FROM
  STREAM read_files(
    '<path-to-source-data>',
    format => '<file-format>'
  )
```

```python
@dp.table(table_properties={'quality': 'bronze'})
def <table-name>():
  return (
     spark.readStream.format('cloudFiles')
     .option('cloudFiles.format', '<file-format>')
     .load(f'{<path-to-source-data>}')
  )
```

Lakeflow-Pipelines sind nicht für die interaktive Ausführung in Notebook-Zellen gedacht. Wird eine Zelle mit Lakeflow-Pipelines-Syntax in einem Notebook ausgeführt, liefert Databricks lediglich eine Meldung, ob die Abfrage syntaktisch gültig ist – die eigentliche Abfragelogik wird dabei nicht ausgeführt.

## Schritt 4: Pipeline erstellen und veröffentlichen

1. Im Workspace auf das Symbol **Jobs & Pipelines** in der Seitenleiste klicken.
2. Unter **New** auf **ETL pipeline** klicken.
3. Einen Pipeline-Namen vergeben.
4. Bei **Pipeline mode** die Option **Triggered** auswählen.
5. Bei **Source code** das Pipeline-Notebook aus Schritt 3 auswählen.
6. Bei **Destination** **Unity Catalog** auswählen.
7. Einen **Catalog** und ein **Target schema** auswählen, damit die Tabelle vom Unity Catalog verwaltet wird.
8. Falls keine Berechtigung zum Erstellen eines Clusters besteht: bei **Cluster policy** eine Policy auswählen, die Lakeflow-Pipelines unterstützt.
9. Unter **Advanced** den **Channel** auf **Preview** setzen.
10. Restliche Standardwerte übernehmen und **Create** anklicken.

## Schritt 5: Pipeline planen (Schedule)

1. Im Workspace auf das Symbol **Jobs & Pipelines** in der Seitenleiste klicken.
2. Den Namen der Pipeline anklicken.
3. **Schedule** > **Add a schedule** anklicken.
4. Bei **Job name** einen Job-Namen vergeben.
5. Bei **Schedule** die Option **Scheduled** wählen.
6. Periode, Startzeit und Zeitzone festlegen.
7. Optional E-Mail-Adressen für Benachrichtigungen bei Start, Erfolg oder Fehlschlag konfigurieren.
8. **Create** anklicken.

## Nächste Schritte

- Nutzern Zugriff auf die neue Tabelle gewähren (siehe Referenz zu Unity-Catalog-Berechtigungen).
- Nutzer mit Tabellenzugriff können die Tabelle anschließend in Notebooks oder im Databricks-SQL-Editor abfragen.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/onboard-data  
**Stand:** 2026-08-07
