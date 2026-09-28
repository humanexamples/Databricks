[← Übersicht](00%20Uebersicht.md)

# COPY INTO mit weiteren Quellen

`COPY INTO` liest nicht nur aus Cloud Object Storage. Die **Standard-Dateikonnektoren** von Lakeflow Connect für SharePoint, OneDrive und Google Drive funktionieren auch mit `COPY INTO`.

Das Prinzip ist immer gleich:

- Als Quelle steht die **URL** der Ressource.
- In `FORMAT_OPTIONS` kommt die **Unity-Catalog-Connection**: `'databricks.connection' = '<name>'`.
- Voraussetzung ist ein Workspace mit Unity Catalog.

Für die meisten Fälle empfiehlt Databricks allerdings die **Managed Connectors**, zum Beispiel den Managed SharePoint Connector. Sie sind vollständig verwaltet und brauchen weniger Pflege.

---

## SharePoint

```sql
CREATE TABLE IF NOT EXISTS sharepoint_pdf_table;
CREATE TABLE IF NOT EXISTS sharepoint_csv_table;
CREATE TABLE IF NOT EXISTS sharepoint_excel_table;

-- Neue PDF-Dateien inkrementell laden
COPY INTO sharepoint_pdf_table
  FROM "https://mytenant.sharepoint.com/sites/Marketing/Shared%20Documents"
  FILEFORMAT = BINARYFILE
  PATTERN = '*.pdf'
  FORMAT_OPTIONS ('databricks.connection' = 'my_sharepoint_conn')
  COPY_OPTIONS ('mergeSchema' = 'true');

-- CSV mit Schema-Inferenz und Schema-Evolution
COPY INTO sharepoint_csv_table
  FROM "https://mytenant.sharepoint.com/sites/Engineering/Data/IoT_Logs"
  FILEFORMAT = CSV
  PATTERN = '*.csv'
  FORMAT_OPTIONS ('databricks.connection' = 'my_sharepoint_conn', 'header' = 'true', 'inferSchema' = 'true')
  COPY_OPTIONS ('mergeSchema' = 'true');

-- Eine einzelne Excel-Datei
COPY INTO sharepoint_excel_table
  FROM "https://mytenant.sharepoint.com/sites/Finance/Shared%20Documents/Monthly/Report-Oct.xlsx"
  FILEFORMAT = EXCEL
  FORMAT_OPTIONS ('databricks.connection' = 'my_sharepoint_conn', 'headerRows' = '1')
  COPY_OPTIONS ('mergeSchema' = 'true');
```

Einschränkungen:
- **Site Pages (`.aspx`)** kann man ab Databricks Runtime 19 laden. `COPY INTO` behandelt sie wie jede andere Datei.
- Dateien kann man nur nach **Name** filtern (`PATTERN` / `pathGlobFilter`), nicht nach Ordnerpfad.
- SharePoint-Listen werden nicht unterstützt, Zurückschreiben auch nicht.
- Nicht unterstützt sind die Clouds GCC High (`.sharepoint.us`), DoD (`.sharepoint-mil.us`) und 21Vianet China (`.sharepoint.cn`).

---

## OneDrive (Beta)

Der OneDrive-Connector liest aus dem **persönlichen Laufwerk** eines Nutzers („My files“). Für Team-Sites und geteilte Bibliotheken nimmst du den SharePoint-Connector.

```sql
CREATE TABLE IF NOT EXISTS onedrive_pdf_table;
CREATE TABLE IF NOT EXISTS onedrive_csv_table;

-- Neue PDF-Dateien inkrementell laden
COPY INTO onedrive_pdf_table
  FROM "https://mytenant-my.sharepoint.com/personal/user_mytenant_onmicrosoft_com/Documents"
  FILEFORMAT = BINARYFILE
  PATTERN = '*.pdf'
  FORMAT_OPTIONS ('databricks.connection' = 'my_onedrive_conn')
  COPY_OPTIONS ('mergeSchema' = 'true');

-- CSV mit Schema-Inferenz und Schema-Evolution
COPY INTO onedrive_csv_table
  FROM "https://mytenant-my.sharepoint.com/personal/user_mytenant_onmicrosoft_com/Documents/IoT_Logs"
  FILEFORMAT = CSV
  PATTERN = '*.csv'
  FORMAT_OPTIONS ('databricks.connection' = 'my_onedrive_conn', 'header' = 'true', 'inferSchema' = 'true')
  COPY_OPTIONS ('mergeSchema' = 'true');
```

Der Connector kann nur lesen, nicht zurückschreiben.

---

## Google Drive (seit Januar 2026, damals als Beta)

Der Standard-Connector für Google Drive unterstützt `read_files`, `spark.read`, `COPY INTO` und Auto Loader. Als Quelle nimmst du die Google-Drive-URL einer Datei, eines Ordners oder eines ganzen Laufwerks. Dazu kommt die Connection über `databricks.connection`.

```sql
CREATE TABLE IF NOT EXISTS gdrive_csv_table;

COPY INTO gdrive_csv_table
  FROM "https://drive.google.com/drive/u/0/folders/12345"
  FILEFORMAT = CSV
  FORMAT_OPTIONS ('databricks.connection' = 'my_gdrive_conn', 'header' = 'true')
  COPY_OPTIONS ('mergeSchema' = 'true');
```

Der Connector unterstützt alle Format-Optionen von Auto Loader, `COPY INTO` und Spark. Soll jede Datei eine eigene Delta-Tabelle werden, brauchst du pro Datei eine eigene Ingestion-Abfrage.

Einschränkungen:
- Der Connector geht nur über die API. Pipelines lassen sich nicht in der UI anlegen.
- `pathGlobFilter` filtert nur nach Namen. Native Google-Formate wie Docs oder Sheets lassen sich damit nicht filtern.
- Google Forms, Sites, Jams und Vids werden übersprungen.

---

## Zerobus Ingest: Fallback-Dateien nachladen

Ändert sich die Zieltabelle so, dass sie nicht mehr passt, schreibt Zerobus Ingest die Daten nicht in die Tabelle. Stattdessen landen sie als Parquet-Dateien in einem Fallback-Ordner unter dem Speicherort der Tabelle: `_zerobus/table_rejected_parquets/`.

**1. Ursache beheben:** Das Schema der Tabelle oder der Produzenten anpassen.

**2. Daten ansehen:**

```sql
SELECT * FROM parquet.`<table-storage-root>/_zerobus/table_rejected_parquets/` LIMIT 10;
```

**3. Mit `COPY INTO` laden.** Die Idempotenz verhindert, dass Dateien bei einer Wiederholung doppelt geladen werden.

```sql
COPY INTO <catalog>.<schema>.<table>
FROM '<table-storage-root>/_zerobus/table_rejected_parquets/'
FILEFORMAT = PARQUET
COPY_OPTIONS ('mergeSchema' = 'false');
```

**4. Zeilenzahl prüfen** und den Fallback-Ordner danach aufräumen.

Zerobus liefert mindestens einmal (at-least-once). Ein Datensatz kann also sowohl in der Tabelle als auch im Fallback-Ordner stehen. Wenn Duplikate stören, musst du danach deduplizieren. Für eine laufende, automatische Verarbeitung kann Auto Loader auf den Fallback-Pfad zeigen.
