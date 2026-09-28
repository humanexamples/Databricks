# Tabellen löschen oder ersetzen

Es gibt zwei Wege, eine Tabelle zu entfernen oder neu zu befüllen: `DROP TABLE` und `CREATE OR REPLACE TABLE`. Beide Befehle haben unterschiedliche Auswirkungen.

## DROP TABLE

`DROP TABLE` entfernt eine Tabelle aus dem Metastore. Das genaue Verhalten hängt vom Tabellentyp ab:

- **Managed Tables in Unity Catalog:** Die Daten werden zum Löschen markiert. Innerhalb von 7 Tagen lassen sie sich mit `UNDROP` wiederherstellen.
- **Managed Tables im Hive Metastore:** Die Daten werden dauerhaft gelöscht.
- **External Tables:** Nur der Eintrag im Metastore wird entfernt. Die zugrunde liegenden Daten bleiben erhalten.

## CREATE OR REPLACE TABLE

`CREATE OR REPLACE TABLE` überschreibt den gesamten Tabelleninhalt vollständig. Die Tabellenidentität bleibt dabei erhalten.

```sql
%sql
CREATE OR REPLACE TABLE table_name AS SELECT * FROM parquet.`/path/to/files`
```

## Empfehlung von Databricks

Databricks empfiehlt, immer `CREATE OR REPLACE TABLE` zu verwenden. Das gilt besonders bei gleichzeitigem (concurrent) Zugriff. Das Muster "Tabelle löschen und neu erstellen" gilt als Anti-Pattern. Es kann zu einem Fehler, verlorenen Datensätzen oder fehlerhaften Ergebnissen führen.

Vorteile von `CREATE OR REPLACE TABLE`:

- Die Tabellenidentität bleibt erhalten.
- Die Transaktion ist atomar. Die Tabelle existiert während der gesamten Operation.
- Laufende Abfragen können ohne Unterbrechung weiterlaufen.
- Tabellenhistorie und Column Masks bleiben erhalten.

Das ist besonders wichtig für Produktionspipelines und Systeme mit gleichzeitigem Zugriff.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/operations/drop-table  
**Stand:** 2026-08-06
