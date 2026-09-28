# Zeilenfilterung (Row Filtering)

Mit Zeilenfilterung lässt sich die Datenaufnahme über SQL-ähnliche WHERE-Bedingungen selektiv steuern. Das reduziert die übertragene Datenmenge, verbessert die Performance beim initialen Laden und verringert Duplizierung in Entwicklungsumgebungen.

## Unterstützte Connectors

- Google Analytics
- Salesforce
- ServiceNow
- Query-basierte Connectors (Oracle, Teradata, SQL Server, MySQL, MariaDB, PostgreSQL)

## Funktionsweise

Die Filterbedingungen gelten sowohl beim initialen Laden als auch bei nachfolgenden inkrementellen Updates und funktionieren ähnlich wie SQL-WHERE-Klauseln über mehrere Datentypen hinweg.

## Wichtige Einschränkungen

**Salesforce:** Zeilenfilterung wird nur auf zwei Spalten unterstützt: den Primärschlüssel (ID, falls vorhanden) und die Cursor-Spalte.

**ServiceNow:** Nur der Operator AND funktioniert, OR wird nicht unterstützt. Zeitstempel benötigen das Format `YYYY-MM-DD HH:mm:SS`. Referenzfelder erfordern den Vergleich des Unterfelds `value` mit der `sys_id`.

**Allgemein:** Der Connector löscht keine Zeilen, die nicht mehr zu aktualisierten Filtern passen, und nimmt auch keine zuvor nicht passenden Zeilen nachträglich auf, wenn sie später passen würden.

## Konfiguration

Der Filter wird als `row_filter` innerhalb von `table_configuration` in der Pipeline-Spezifikation angegeben.

## Beispiel-Filter

- Zeitstempelbasiert: `SystemModstamp > '2025-06-10T23:40:11.000-07:00'`
- Boolean: `u_active = TRUE`
- Vergleich: `event_timestamp >= 1712224270703246`
- Komplex: `event_timestamp >= 1712224270703246 AND (platform != 'WEB' OR is_active_user = FALSE)`

## Unterstützte Operatoren

**Unterstützt:** `AND`, `OR` (nur Salesforce/Google Analytics), `=`, `!=`, `<`, `<=`, `>`, `>=`

**Nicht unterstützt:** `LIKE`, `IN`

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/row-filtering  
**Stand:** 2026-08-07
