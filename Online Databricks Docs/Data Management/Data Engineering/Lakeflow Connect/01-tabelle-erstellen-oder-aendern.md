# Tabelle per Datei-Upload erstellen oder ändern

Mit dem Datei-Upload lassen sich Managed-Delta-Lake-Tabellen direkt aus hochgeladenen Dateien erstellen oder überschreiben – sowohl in Unity Catalog als auch im Hive Metastore.

## Unterstützte Dateiformate

- CSV, TSV oder TAB
- JSON
- Avro
- Parquet
- Text

**Upload-Grenzen:**

- Maximal 10 Dateien pro Upload-Sitzung
- Gesamtgröße maximal 2 Gigabyte
- Komprimierte Formate (zip, tar) werden nicht unterstützt
- Dateien benötigen die korrekten Endungen (.csv, .tsv, .tab, .json, .avro, .parquet oder .txt)

## Ablauf des Uploads

1. **Datei-Upload**: Über das "Neu"-Symbol "Daten hinzufügen/hochladen" und dann "Tabelle erstellen oder ändern" wählen; Dateien per Drag-and-drop in die Drop-Zone ziehen oder durchsuchen.
2. **Konfiguration**: Eine aktive Recheneinheit verbinden, um Vorschau und Einstellungen zu konfigurieren. Unterstützt werden SQL-Warehouses, serverloses Compute und dediziertes Compute (Cluster werden nicht unterstützt).
3. **Tabelle erstellen**: Ziel-Katalog/-Schema auswählen, optional den Tabellennamen bearbeiten, Formatoptionen konfigurieren und auf "Create" klicken.

## Formatoptionen

**CSV/TSV:**

- "Erste Zeile enthält Header" ist standardmäßig aktiviert
- Anpassbares Spaltentrennzeichen (nur ein Zeichen)
- Automatische Spaltentyp-Erkennung (standardmäßig aktiviert)
- Unterstützung mehrzeilig umbrochener Felder
- Schema-Merging über mehrere Dateien hinweg

**JSON:**

- Automatische Typerkennung
- Mehrzeilenunterstützung (standardmäßig aktiviert)
- Kommentare erlaubt
- Einfache Anführungszeichen werden unterstützt
- Timestamp-Erkennung möglich

## Unterstützte Datentypen

BIGINT, BOOLEAN, DATE, DOUBLE, STRING, TIMESTAMP, STRUCT, ARRAY, DECIMAL(P,S)

## Wichtige Einschränkungen

- Verschachtelte Typen (`STRUCT` oder `ARRAY`) können nicht bearbeitet werden.
- Spaltennamen dürfen keine Kommas, Backslashes oder Unicode-Zeichen enthalten.
- Ein Casting von BIGINT zu DATE oder TIMESTAMP wird nicht unterstützt.
- Beim Hochladen mehrerer Dateien müssen die Header konsistent sein, sonst gehen Daten verloren.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/create-or-modify-table  
**Stand:** 2026-08-07
