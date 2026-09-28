# `ANALYZE TABLE ... COMPUTE STATISTICS`

Sammelt geschätzte Statistiken über Tabellen (Zeilenanzahl, Größe, optional Spaltenstatistiken) zur Nutzung durch den Query-Optimizer. Databricks empfiehlt, für Unity-Catalog-Managed-Tables stattdessen **Predictive Optimization** zu aktivieren, das `ANALYZE` automatisch ausführt und so manuelle Wartung überflüssig macht.

Ausführlicher Kontext zu Data Skipping, Statistik-Typen und Predictive Optimization für Statistiken: [Data Skipping und Tabellenstatistiken.md](../../../09%20Performance%20Optimization/01%20Foundation%20Design/04%20Data%20Skipping%20und%20Tabellenstatistiken.md).

## Syntax

```sql
ANALYZE TABLE table_name [ PARTITION clause ]
    COMPUTE [ DELTA ] STATISTICS [ NOSCAN | FOR COLUMNS col1 [, ...] | FOR ALL COLUMNS ]

ANALYZE TABLES [ { FROM | IN } schema_name ] COMPUTE STATISTICS [ NOSCAN ]
```

## Parameter

| Parameter/Klausel | Bedeutung |
|---|---|
| `table_name` | Zieltabelle (ohne zeitliche oder Options-Spezifikation); löst `TABLE_OR_VIEW_NOT_FOUND` aus, falls nicht vorhanden |
| `PARTITION`-Klausel | beschränkt die Analyse auf bestimmte Partitionen — **nicht unterstützt** für Delta-Lake-Tabellen |
| `DELTA` | ab Databricks Runtime 14.3 LTS — berechnet die im Delta-Log gespeicherten, für Data Skipping konfigurierten Spaltenstatistiken neu; sammelt **keine** klassischen Query-Optimizer-Statistiken |
| ohne Zusatzoption | sammelt Zeilenanzahl und Tabellengröße |
| `NOSCAN` | sammelt nur die Tabellengröße, ohne die gesamte Tabelle zu scannen |
| `FOR COLUMNS col [, ...]` | sammelt Spaltenstatistiken für die genannten Spalten zusätzlich zu den Tabellenstatistiken — nicht kombinierbar mit `PARTITION` |
| `FOR ALL COLUMNS` | sammelt Statistiken für jede Spalte zusätzlich zu den Tabellenstatistiken — nicht kombinierbar mit `PARTITION` |
| `schema_name` | zu analysierendes Schema; ohne Angabe werden alle Tabellen im aktuellen Schema analysiert (im Rahmen der Nutzerrechte) |

**Hinweis zur Reihenfolge bei Delta-Statistiken:** Nach dem Konfigurieren neuer Spalten für Data Skipping empfiehlt sich zunächst `ANALYZE TABLE table_name COMPUTE DELTA STATISTICS`, gefolgt von `ANALYZE TABLE table_name COMPUTE STATISTICS` für optimierte Query-Pläne.

## Beispiele

```sql
-- Setup
CREATE TABLE students (name STRING, student_id INT) PARTITIONED BY (student_id);
INSERT INTO students PARTITION (student_id = 111111) VALUES ('Mark');
INSERT INTO students PARTITION (student_id = 222222) VALUES ('John');

-- Nur Größe, ohne vollständigen Scan
ANALYZE TABLE students COMPUTE STATISTICS NOSCAN;
DESC EXTENDED students;

-- Vollständige Statistiken (Zeilenanzahl + Größe)
ANALYZE TABLE students COMPUTE STATISTICS;
DESC EXTENDED students;

-- Nur eine bestimmte Partition analysieren
ANALYZE TABLE students PARTITION (student_id = 111111) COMPUTE STATISTICS;
DESC EXTENDED students PARTITION (student_id = 111111);

-- Statistik für eine bestimmte Spalte
ANALYZE TABLE students COMPUTE STATISTICS FOR COLUMNS name;
DESC EXTENDED students name;

-- Alle Tabellen eines bestimmten Schemas
ANALYZE TABLES IN school_schema COMPUTE STATISTICS NOSCAN;
DESC EXTENDED teachers;
DESC EXTENDED students;

-- Alle Tabellen des aktuellen Schemas
ANALYZE TABLES COMPUTE STATISTICS;
DESC EXTENDED teachers;
DESC EXTENDED students;

-- Delta-Log-Statistiken neu berechnen (Runtime 14.3 LTS+)
ANALYZE TABLE some_delta_table COMPUTE DELTA STATISTICS;
```

**Quellen:**
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-analyze-compute-statistics
- https://docs.databricks.com/aws/en/optimizations/predictive-optimization
