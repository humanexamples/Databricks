# Library Utility (`dbutils.library`)

Modul zur Verwaltung sitzungsbezogener Bibliotheken — inzwischen **größtenteils deprecated**. Teil der [Databricks Utils](00%20Uebersicht.md)-Reihe.

## Status

„Die meisten Methoden des Moduls `dbutils.library` sind deprecated" — für die vormals dort dokumentierten Befehle (u. a. `install`) verweist Databricks auf die separate Legacy-Doku „Library utility (dbutils.library) (legacy)". Diese Befehle werden auf der aktuellen Referenzseite nicht mehr aufgeführt oder mit Syntax/Parametern dokumentiert.

**Empfehlung:** Statt der veralteten `dbutils.library`-Methoden moderne Bibliotheksverwaltung nutzen — für Bundles siehe [22 Bibliotheksabhaengigkeiten.md](../03%20Databricks%20Asset%20Bundles/22%20Bibliotheksabhaengigkeiten.md), für Notebooks `%pip install`.

## Aktiver Befehl: `restartPython`

Einziger auf der aktuellen Referenzseite noch aktiv dokumentierte (nicht deprecated) Befehl.

**Syntax:** `dbutils.library.restartPython`

**Zweck:** „Startet den Python-Prozess auf Databricks programmatisch neu, um sicherzustellen, dass lokal installierte oder aktualisierte Bibliotheken im Python-Kernel der aktuellen SparkSession korrekt funktionieren."

**Parameter:** keine dokumentiert.

**Verfügbarkeit:** in Python-Notebooks.

**Hinweis:** Für Details verweist die Doku auf den eigenständigen Leitfaden „Restart the Python process on Databricks" — in der Praxis meist über die Magic-Command-Kurzform `%restart_python` verwendet (vgl. `%pip install` gefolgt von `%restart_python` in mehreren Beispielen dieses Projekts, u. a. [03 Jobs automatisieren.md](../../07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/01%20Uebersicht/03%20Jobs%20automatisieren.md)).

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/databricks-utils#library-utility-dbutilslibrary

**Stand:** 2026-08-26.
