# Daten laden über eine Unity-Catalog External Location
Diese Seite beschreibt, wie über die Add-Data-UI eine Managed Table aus Daten in Amazon S3 erstellt wird, indem eine Unity-Catalog External Location genutzt wird. Dieses Feature befindet sich in Public Preview.

## Übersicht

Eine External Location kombiniert einen Cloud-Speicherpfad mit Storage-Credentials für autorisierten Zugriff. Databricks empfiehlt diesen Ansatz gegenüber dem älteren S3-Tabellen-Import, der nur Hive-Metastore-Tabellen unterstützt und Compute-Ressourcen mit Instance-Profile-Anbindung erfordert.

## Voraussetzungen

- Ein Workspace mit aktiviertem Unity Catalog
- Die Berechtigung `READ FILES` auf der External Location
- Die Berechtigung `CREATE TABLE` auf dem Zielschema, `USE SCHEMA` auf dem Schema sowie `USE CATALOG` auf dem übergeordneten Katalog

## Unterstützte Dateiformate

Folgende Formate werden unterstützt:

- CSV
- TSV
- JSON
- XML
- AVRO
- Parquet

## Schritt 1: Zugriff auf die External Location bestätigen

1. In der Seitenleiste **Catalog** anklicken.
2. Im Catalog Explorer auf das Stecker-Symbol **Connect** klicken und dann **External locations** auswählen.

## Schritt 2: Managed Table erstellen

1. In der Seitenleiste **+ New** > **Add data** anklicken.
2. **Amazon S3** auswählen.
3. Eine External Location aus dem Dropdown-Menü auswählen.
4. Ordner und Dateien zum Laden auswählen, dann **Preview table** anklicken.
5. Katalog und Schema auswählen.
6. Optional: Tabellennamen bearbeiten.
7. Optional: Über **Advanced attributes** die Formatoptionen je Dateityp festlegen.
8. Optional: Spaltennamen bearbeiten (Hinweis: Kommas, Backslashes und Unicode-Zeichen werden nicht unterstützt).
9. Optional: Spaltentypen über das Typ-Symbol bearbeiten.
10. **Create table** anklicken.

## Formatoptionen nach Dateityp

| Formatoption | Beschreibung | Unterstützte Dateitypen |
| --- | --- | --- |
| Column delimiter | Trennzeichen zwischen Spalten; nur ein einzelnes Zeichen, Backslash nicht unterstützt. Standard: Komma | CSV |
| Escape character | Zeichen zum Escapen beim Parsen. Standard: Anführungszeichen | CSV |
| First row contains the header | Gibt an, ob die Datei eine Kopfzeile enthält. Standardmäßig aktiviert | CSV |
| Automatically detect file type | Dateityp automatisch erkennen. Standard: `true` | XML |
| Automatically detect column types | Spaltentypen automatisch aus dem Inhalt ableiten; in der Vorschau editierbar. Falls deaktiviert, werden alle Typen als STRING interpretiert. Standardmäßig aktiviert | CSV, JSON, XML |
| Rows span multiple lines | Ob Spaltenwerte über mehrere Zeilen reichen können. Standardmäßig deaktiviert | CSV, JSON |
| Merge the schema across multiple files | Ob das Schema über mehrere Dateien hinweg abgeleitet und zusammengeführt wird. Standardmäßig aktiviert | CSV |
| Allow comments | Ob Kommentare erlaubt sind. Standardmäßig aktiviert | JSON |
| Allow single quotes | Ob einfache Anführungszeichen erlaubt sind. Standardmäßig aktiviert | JSON |
| Infer timestamp | Ob Zeitstempel-Strings als `TimestampType` interpretiert werden. Standardmäßig aktiviert | JSON |
| Rescued data column | Ob nicht zum Schema passende Spalten gesichert werden. Standardmäßig aktiviert | CSV, JSON, Avro, Parquet |
| Exclude attribute | Ob Attribute in Elementen ausgeschlossen werden. Standard: `false` | XML |
| Attribute prefix | Präfix für Attribute zur Unterscheidung von Elementen. Standard: `_` | XML |

## Unterstützte Spaltendatentypen

| Datentyp | Beschreibung |
| --- | --- |
| BIGINT | 8-Byte-Ganzzahl mit Vorzeichen |
| BOOLEAN | Boolesche Werte (`true`, `false`) |
| DATE | Datum ohne Zeitzone |
| DECIMAL (P,S) | Zahlen mit maximaler Präzision P und fester Skala S |
| DOUBLE | 8-Byte-Gleitkommazahl doppelter Genauigkeit |
| STRING | Zeichenketten |
| TIMESTAMP | Jahr, Monat, Tag, Stunde, Minute, Sekunde mit sitzungslokaler Zeitzone |

## Bekannte Einschränkungen

- Sonderzeichen in komplexen Datentypen können Probleme verursachen (z. B. JSON-Schlüssel mit Backticks oder Doppelpunkten).
- Manche JSON-Dateien erfordern eine manuelle Auswahl: Nach der Dateiauswahl **Advanced attributes** öffnen, **Automatically detect file type** deaktivieren und dann **JSON** explizit auswählen.
- Verschachtelte Zeitstempel und Dezimalzahlen innerhalb komplexer Typen können zu Problemen führen.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/add-data-external-locations  
**Stand:** 2026-08-07
