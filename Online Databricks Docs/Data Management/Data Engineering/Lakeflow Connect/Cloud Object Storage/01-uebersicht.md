# Daten aus Cloud Object Storage laden – Übersicht
Diese Seite listet die verschiedenen Wege auf, um inkrementelle Datenaufnahme (Ingestion) aus Cloud Object Storage in Databricks einzurichten.

## Add-Data-UI

Über die Add-Data-UI lässt sich eine Managed Table direkt aus Daten in Cloud Object Storage erstellen, indem eine Unity-Catalog External Location genutzt wird. Details dazu siehe die Seite "Daten laden über einen Unity-Catalog External Location".

## Notebook oder SQL-Editor

Für die programmatische Ingestion über Notebook oder SQL-Editor stehen zwei Werkzeuge zur Verfügung: Auto Loader und `COPY INTO`.

### Auto Loader

Auto Loader verarbeitet neue Datendateien inkrementell und effizient, sobald sie im Cloud-Speicher ankommen – ohne zusätzlichen Setup-Aufwand. Er nutzt die Structured-Streaming-Quelle `cloudFiles` und verarbeitet automatisch neue Dateien; optional können auch bereits vorhandene Dateien im Verzeichnis mitverarbeitet werden.

### COPY INTO

Mit `COPY INTO` können SQL-Nutzer Daten aus Cloud Object Storage idempotent und inkrementell in Delta-Tabellen laden. `COPY INTO` steht in Databricks SQL, in Notebooks und in Lakeflow Jobs zur Verfügung.

### Wann COPY INTO, wann Auto Loader?

- Bei einigen Tausend Dateien insgesamt: `COPY INTO` verwenden. Bei Millionen oder mehr Dateien: Auto Loader verwenden. Auto Loader benötigt weniger Gesamtoperationen zur Dateierkennung und kann die Verarbeitung in mehrere Batches aufteilen.
- Auto Loader bietet bessere Grundfunktionen bei der Schema-Inferenz und -Evolution.
- `COPY INTO` eignet sich besser, wenn nur eine Teilmenge von Dateien erneut verarbeitet werden soll.
- Auto Loader ermöglicht es SQL-Nutzern, Streaming-Tabellen zu verwenden.

## ETL mit Lakeflow-Pipelines und Auto Loader automatisieren

Lakeflow-Pipelines sind nicht für die interaktive Ausführung in Notebooks gedacht wie klassische Notebook-Zellen. Stattdessen liegt der Fokus auf der Bereitstellung produktionsreifer Infrastruktur. Databricks empfiehlt, Auto Loader in Kombination mit Lakeflow-Pipelines einzusetzen, um produktionsreife ETL-Strecken aufzubauen – inklusive Streaming-Tabellen für bessere Skalierbarkeit.

## Ingestion-Tools von Drittanbietern

Databricks validiert Integrationen von Technologiepartnern, die eine Ingestion aus verschiedenen Quellen – darunter Cloud Object Storage – ermöglichen. Diese Integrationen erlauben eine skalierbare Low-Code-Ingestion in Databricks, unter anderem über Partner Connect.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/  
**Stand:** 2026-08-07
