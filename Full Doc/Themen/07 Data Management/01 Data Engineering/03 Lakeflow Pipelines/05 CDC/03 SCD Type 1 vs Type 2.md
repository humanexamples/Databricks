# SCD Type 1 vs. Type 2 — konzeptioneller Vergleich

Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/data-engineering/what-is-cdc`, vollständig als Rohtext abgerufen) und die inhaltlich übereinstimmende AWS-Seite (`docs.databricks.com/aws/en/data-engineering/what-is-cdc`). Ergänzend gegen die `AUTO CDC`-API-Referenz (`docs.databricks.com/aws/en/ldp/cdc`) abgeglichen — Details zur Syntax dort bzw. in `CDC-Grundlagen.md` (dieser Ordner).

## Abschnittsübersicht

1. [Was ist eine Slowly Changing Dimension (SCD)?](#was-ist-scd)
2. [SCD Typ 1: Nur der aktuelle Zustand](#scd-typ-1)
3. [SCD Typ 2: Vollständige Historie](#scd-typ-2)
4. [Verhalten bei Insert/Update/Delete im Vergleich](#verhalten-vergleich)
5. [Entscheidungskriterien: Wann welchen Typ wählen?](#entscheidung)
6. [Bezug zu den AUTO-CDC-APIs](#bezug-auto-cdc)
7. [Quellen](#quellen)

---

## <a id="was-ist-scd">1. Was ist eine Slowly Changing Dimension (SCD)?</a>

Slowly Changing Dimensions (SCD) legen fest, wie Änderungen aus vorgelagerten Systemen angewendet und modelliert werden, nachdem sie in analytischen Tabellen ankommen. Organisationen wählen je nach Datenbedarf unterschiedliche Ansätze.

Wörtliches Zitat aus der Doku: *"SCD Type 1 allows you to save only the current state of the dataset. SCD Type 2 saves the complete history of changes to the dataset."* — Übersetzung: "SCD Typ 1 erlaubt es, nur den aktuellen Zustand des Datasets zu speichern. SCD Typ 2 speichert die vollständige Historie der Änderungen am Dataset."

## <a id="scd-typ-1">2. SCD Typ 1: Nur der aktuelle Zustand</a>

Wörtliches Zitat: *"SCD Type 1 overwrites old data with new data whenever changes occur, keeping only the latest version of each record. History is not retained."* — Übersetzung: "SCD Typ 1 überschreibt alte Daten mit neuen Daten, sobald Änderungen auftreten, und behält nur die neueste Version jedes Datensatzes. Es wird keine Historie bewahrt."

Nur die neueste Version der Daten ist bei SCD Typ 1 verfügbar — vergleichbar mit dem Speichern ausschließlich der finalen Tabelle. Ändert sich beispielsweise die Rolle eines Datensatzes von "Owner" zu "Manager", bleibt in der Tabelle nur noch "Manager" stehen; der vorherige Wert ist nicht mehr abrufbar.

Laut Doku SCD Typ 1 einsetzen, wenn:

- nur der aktuelle Zustand der Daten benötigt wird,
- nachgelagerte Materialized Views inkrementell statt vollständig neu berechnet werden sollen,
- stabile Surrogate Keys für Joins benötigt werden.

## <a id="scd-typ-2">3. SCD Typ 2: Vollständige Historie</a>

Wörtliches Zitat: *"SCD Type 2 maintains a complete historical record by creating multiple versions of data over time, each timestamped with metadata."* — Übersetzung: "SCD Typ 2 bewahrt einen vollständigen historischen Datensatz, indem mehrere Versionen der Daten über die Zeit erzeugt werden, jeweils mit Metadaten-Zeitstempel versehen."

Die Spalten `__START_AT` und `__END_AT` definieren die Gültigkeitsperiode jeder Version eines Datensatzes. Aktive Datensätze haben `__END_AT = NULL`. Damit lässt sich der Zustand des Datasets zu jedem beliebigen Zeitpunkt rekonstruieren.

Beispiel laut Doku: Hat ein Datensatz aktuell den Wert `Manager` im Feld `role`, lässt sich zugleich nachvollziehen, dass die Rolle zuvor `Owner` war — der aktuelle (aktive) Datensatz ist an einem `null`-Wert im End-Zeitstempel-Feld erkennbar.

Laut Doku SCD Typ 2 einsetzen, wenn:

- Auditierbarkeit oder regulatorische Anforderungen historische Nachverfolgung verlangen,
- Kundenanalysen ein Verständnis dafür erfordern, wie sich Entitäten über die Zeit entwickelt haben,
- Geschäftslogik Point-in-Time-Reporting erfordert,
- Trends analysiert oder historische Zustände verglichen werden müssen.

## <a id="verhalten-vergleich">4. Verhalten bei Insert/Update/Delete im Vergleich</a>

| Operation | SCD Typ 1 | SCD Typ 2 |
|---|---|---|
| **INSERT** | Neuer Datensatz wird eingefügt. | Neuer Datensatz wird als erste aktive Version eingefügt (`__START_AT` gesetzt, `__END_AT = NULL`). |
| **UPDATE** | Bestehender Datensatz wird direkt überschrieben — der alte Wert ist danach nicht mehr abrufbar. | Die bisherige aktive Version wird geschlossen (`__END_AT` erhält den Sequenzwert des Updates), eine neue Version wird als aktiv eingefügt (`__END_AT = NULL`). Beide Zeilen bleiben in der Zieltabelle erhalten. |
| **DELETE** | Datensatz wird aus der Zieltabelle entfernt (via `APPLY AS DELETE WHEN`). | Die Historie bleibt erhalten: Die aktive Version wird geschlossen (`__END_AT` gesetzt), es wird jedoch keine neue aktive Version eingefügt — der Datensatz erscheint dann in keiner aktiven Zeile mehr. |

Diese Zeilen sind aus den `AUTO CDC`-Beispielen in `CDC-Grundlagen.md` (dieser Ordner, Abschnitt 6) abgeleitet, dort mit konkreten Beispieldaten und vollständigen Ergebnistabellen durchgespielt (inklusive nicht-chronologisch eintreffender Updates).

## <a id="entscheidung">5. Entscheidungskriterien: Wann welchen Typ wählen?</a>

Wörtliches Zitat (Empfehlung am Ende der Doku-Seite): *"In both cases, choose SCD Type 1 if you only need the current state of each record, or SCD Type 2 if you need to preserve a full history of changes for auditing, point-in-time reporting, or trend analysis."* — Übersetzung: "In beiden Fällen SCD Typ 1 wählen, wenn nur der aktuelle Zustand jedes Datensatzes benötigt wird, oder SCD Typ 2, wenn eine vollständige Änderungshistorie für Auditing, Point-in-Time-Reporting oder Trendanalyse bewahrt werden muss."

Zusätzlicher, in der Doku genannter Vorteil von SCD Typ 1: Da nur der aktuelle Stand gespeichert wird, können nachgelagerte Materialized Views inkrementell aktualisiert werden, statt bei jeder Änderung vollständig neu berechnet zu werden — ein Aspekt, der bei der Wahl des Typs mit abgewogen werden sollte, wenn Performance/Kosten nachgelagerter Views relevant sind.

## <a id="bezug-auto-cdc">6. Bezug zu den AUTO-CDC-APIs</a>

Beide `AUTO CDC`-APIs (`AUTO CDC ... INTO` in SQL, `create_auto_cdc_flow()` / `create_auto_cdc_from_snapshot_flow()` in Python) unterstützen SCD Typ 1 und Typ 2 über die Klausel `STORED AS SCD TYPE 1` bzw. `STORED AS SCD TYPE 2` (SQL) oder den Parameter `stored_as_scd_type` (Python). Standardmäßig speichert `AUTO CDC` Datensätze als SCD Typ 1, wenn `STORED AS` nicht angegeben wird.

Konkrete Syntax, durchgerechnete Beispiele mit Eingabe- und Ausgabetabellen sowie das Tracking von Spaltenteilmengen bei SCD Typ 2 (`TRACK HISTORY ON`) siehe:

- `CDC-Grundlagen.md` (dieser Ordner), Abschnitt 6 — `AUTO CDC`-Beispiele: SCD Typ 1 und Typ 2.
- `14 Developer Reference/SQL-Referenz/AUTO CDC INTO.md` — vollständige Syntax- und Parameterreferenz.
- `CDC fortgeschritten.md` (dieser Ordner) — DML auf SCD-Zieltabellen, Change Data Feed vom CDC-Ziel, Bitemporal AUTO CDC (SCD Typ 2 plus zweite Zeitdimension).

## <a id="quellen">7. Quellen</a>

- Change data capture and snapshots (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/data-engineering/what-is-cdc
- What is change data capture (CDC)? (AWS): https://docs.databricks.com/aws/en/data-engineering/what-is-cdc
- The AUTO CDC APIs (AWS, zum Abgleich der SCD-Syntax-Referenzen): https://docs.databricks.com/aws/en/ldp/cdc
- Verwandte Dateien in diesem Projekt: `CDC-Grundlagen.md`, `CDC fortgeschritten.md`, `14 Developer Reference/SQL-Referenz/AUTO CDC INTO.md`

**Stand:** 2026-08-21.
