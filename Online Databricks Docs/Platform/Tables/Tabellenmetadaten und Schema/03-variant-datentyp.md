# Der VARIANT-Datentyp

Der Datentyp `VARIANT` speichert semi-strukturierte Daten in Databricks-Tabellen. Apache-Iceberg-v3-Tabellen unterstützen ihn automatisch. Bei Delta-Lake-Tabellen muss er explizit aktiviert werden.

## Voraussetzungen

Zum Lesen und Schreiben von Tabellen mit aktiviertem VARIANT-Support ist Databricks Runtime 15.4 LTS oder höher erforderlich.

## VARIANT-Support aktivieren

### Für neue Tabellen

Eine Tabelle mit VARIANT-Spalte lässt sich direkt anlegen.

```sql
%sql
CREATE TABLE table_name (variant_column VARIANT)
```

### Für bestehende Tabellen

Für bestehende Tabellen wird das Feature per Tabelleneigenschaft aktiviert.

```sql
%sql
ALTER TABLE table_name SET TBLPROPERTIES('delta.feature.variantType-preview' = 'supported')
```

Das Aktivieren dieses Features hebt das Writer-Protokoll der Tabelle an. Das kann die Kompatibilität mit externen Delta-Lake-Clients beeinträchtigen.

## Einschränkungen von VARIANT-Spalten

- Können nicht als Partitionierungsspalte verwendet werden.
- Können nicht als Clustering-Key dienen.
- Sind nicht kompatibel mit `GROUP BY` und `ORDER BY`.
- Können nicht mit `DISTINCT` verwendet werden.
- Können nicht in SQL-Mengenoperationen (`INTERSECT`, `UNION`, `EXCEPT`) verwendet werden.
- Können nicht über Column Generation erzeugt werden.
- Unterstützen keine `minValues`- oder `maxValues`-Statistiken.
- Werte sind auf maximal 128 MiB begrenzt (16 MiB in Runtime 17.1 und früher).

---
**Quelle:** https://docs.databricks.com/aws/en/tables/features/variant  
**Stand:** 2026-08-06
