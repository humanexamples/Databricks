# Tabellen-Konzepte in Databricks

Databricks bietet verschiedene Tabellentypen und Speicherformate. Diese Seite erklärt die wichtigsten Konzepte und hilft bei der Auswahl.

## Speicherformate

Databricks unterstützt zwei offene Speicherformate für Tabellen:

- **Delta Lake**: das Standardformat für Managed Tables und External Tables. Auch Foreign Tables können Delta Lake nutzen.
- **Apache Iceberg**: unterstützt für Managed Tables und Foreign Tables. Nützlich für die Integration in das Iceberg-Ökosystem.

Beide Formate bilden eine transaktionale Speicherschicht. Sie verfolgen Metadaten und unterstützen ACID-Eigenschaften (Atomicity, Consistency, Isolation, Durability). Außerdem bieten sie Time Travel und weitere Funktionen.

## Vergleich der Tabellentypen

| Tabellentyp | Verwaltender Katalog | Lesen/Schreiben | Performance-Optimierung | Speicherkosten-Optimierung |
| --- | --- | --- | --- | --- |
| Managed | Unity Catalog | Ja | Ja | Ja |
| Temporär | Keine (sitzungsgebunden) | Ja | Ja | Ja |
| External | Keiner (nur Dateien) | Ja | Nur manuell | Nur manuell |
| Foreign | Externes System / Catalog Service | Nur lesend | Nein | Nein |

## Managed Tables

Bei Managed Tables verwaltet Unity Catalog sowohl die Datendateien als auch die Tabellen-Metadaten. Managed Tables sind der Standard-Tabellentyp in Databricks. Databricks empfiehlt: Nutzen Sie Managed Tables, wann immer Sie eine neue Tabelle anlegen.

## External Tables

External Tables verweisen auf Daten in externem Speicher. Databricks verwaltet nur die Metadaten, nicht die zugrunde liegenden Dateien.

## Foreign Tables

Foreign Tables bieten einen lesenden Zugriff auf Daten in externen Systemen. Der Zugriff erfolgt über Lakehouse Federation.

## Temporäre Tabellen

Temporäre Tabellen sind an eine Sitzung gebunden. Sie werden automatisch gelöscht, wenn die Sitzung endet. Für temporäre Tabellen sind keine Katalog- oder Schema-Berechtigungen nötig.

## Auswahlhilfe: Welchen Tabellentyp nutzen?

**Managed Tables** sind für die meisten neuen Tabellen die richtige Wahl.

**External Tables** eignen sich, wenn:

- vorhandene Daten im Cloud-Speicher registriert werden sollen, ohne sie zu verschieben
- ein direkter, pfadbasierter Zugriff von Nicht-Databricks-Clients nötig ist
- nicht unterstützte Formate wie CSV oder JSON verwendet werden
- beim Löschen der Tabelle die zugrunde liegenden Dateien erhalten bleiben sollen

**Foreign Tables** eignen sich für den lesenden Zugriff auf externe Systeme über Lakehouse Federation.

## Berechtigungen in Unity Catalog

| Vorgang | Benötigte Berechtigung |
| --- | --- |
| Tabelle erstellen | `CREATE TABLE` auf dem übergeordneten Schema |
| Tabelle abfragen | `SELECT` auf der Tabelle |
| Daten aktualisieren, löschen, mergen, einfügen | `SELECT` und `MODIFY` auf der Tabelle |
| Tabelle löschen (DROP) | `MANAGE` auf der Tabelle |
| Tabelle ersetzen (REPLACE) | `MANAGE` auf der Tabelle, `CREATE TABLE` auf dem Schema |

## Relevante SQL-Befehle

Für die Arbeit mit Tabellen sind folgende SQL-Befehle relevant:

- `CREATE TABLE ... USING ...`
- `ALTER TABLE`
- `DROP TABLE`
- `SHOW TABLES`

---
**Quelle:** https://docs.databricks.com/aws/en/tables/tables-concepts  
**Stand:** 2026-08-06
