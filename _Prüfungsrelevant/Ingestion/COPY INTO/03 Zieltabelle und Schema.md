[← Übersicht](00%20Uebersicht.md)

# Zieltabelle und Schema

## Die Zieltabelle muss existieren

`COPY INTO` legt keine Tabelle an. Fehlt sie, kommt der Fehler `DELTA_MISSING_DELTA_TABLE_COPY_INTO`. Ist das Ziel keine Delta-Tabelle, kommt `DELTA_COPY_INTO_TARGET_FORMAT`.

```sql
CREATE TABLE IF NOT EXISTS my_table
[(col_1 col_1_type, col_2 col_2_type, ...)]
[COMMENT <table-description>]
[TBLPROPERTIES (<table-properties>)];
```

Es gibt zwei Wege: mit festem Schema oder als leere Tabelle ohne Schema.

---

## Weg 1: Schema vorher festlegen

```sql
CREATE TABLE main.bronze.booking_updates (
  booking_id   BIGINT,
  user_id      BIGINT,
  status       STRING,
  total_amount DOUBLE
);

COPY INTO main.bronze.booking_updates
FROM '/Volumes/main/raw/landing/wanderbricks/booking_updates'
FILEFORMAT = JSON
FORMAT_OPTIONS ('multiLine' = 'true');
```

Die Datei muss zum Schema passen. Tut sie das nicht, bricht der Befehl mit `COPY_INTO_SCHEMA_MISMATCH_WITH_TARGET_TABLE` ab. Die Fehlermeldung schlägt selbst die Lösung vor: `COPY_OPTIONS ('mergeSchema' = 'true')`.

---

## Weg 2: Leere Tabelle ohne Schema (ab Databricks Runtime 11.3 LTS)

Du legst nur den Namen an. Das Schema entsteht beim ersten `COPY INTO`. Dafür muss `mergeSchema` in den `COPY_OPTIONS` auf `true` stehen.

```sql
CREATE TABLE IF NOT EXISTS main.bronze.booking_updates_schemaless;

COPY INTO main.bronze.booking_updates_schemaless
FROM '/Volumes/main/raw/landing/wanderbricks/booking_updates'
FILEFORMAT = JSON
FORMAT_OPTIONS ('mergeSchema' = 'true', 'multiLine' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');
```

Das geht nur mit Formaten, die Schema-Evolution unterstützen.

**Einschränkung:** Solange noch nichts geladen wurde, ist die leere Tabelle nur für `COPY INTO` nutzbar. `INSERT INTO` und `MERGE INTO` in eine Tabelle ohne Schema gehen nicht. Erst nach dem ersten `COPY INTO` kann man die Tabelle abfragen.

```sql
CREATE TABLE IF NOT EXISTS t_empty;
INSERT INTO t_empty VALUES (1);   -- geht nicht, die Tabelle hat noch kein Schema
```

---

## `mergeSchema` gibt es zweimal

Der Name ist gleich, die Wirkung ist verschieden.

**In `FORMAT_OPTIONS` – beim Lesen:** Das Schema wird über **mehrere Quelldateien** abgeleitet und zusammengeführt. Das ist sinnvoll, wenn die Dateien unterschiedlich aussehen. Haben alle Dateien dasselbe Schema, lass den Standardwert `false` stehen.

**In `COPY_OPTIONS` – beim Schreiben:** Das Schema der **Zieltabelle** darf sich weiterentwickeln, zum Beispiel durch neue Spalten. Sind Eingabe- und Zielschema gleich, reicht `false`.

```sql
COPY INTO my_pipe_data
FROM 's3://my-bucket/pipeData'
FILEFORMAT = CSV
FORMAT_OPTIONS ('mergeSchema' = 'true',   -- Dateien können sich in Kopfzeile/Trennzeichen unterscheiden
                'delimiter' = '|',
                'header' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');    -- Zieltabelle darf neue Spalten bekommen
```

Beispiel für die Schema-Evolution:

```
Lauf 1: orders_1.csv → id, amount          → Tabelle: id, amount
Lauf 2: orders_2.csv → id, amount, currency
        ohne mergeSchema in COPY_OPTIONS  → COPY_INTO_SCHEMA_MISMATCH_WITH_TARGET_TABLE
        mit  mergeSchema in COPY_OPTIONS  → Tabelle: id, amount, currency
                                            (currency ist NULL für die alten Zeilen)
```

---

## `inferSchema` – Datentypen ableiten

- `inferSchema = false`: Alle Spalten werden als `STRING` gelesen. Das ist der Standard für CSV.
- `inferSchema = true`: Die Datentypen werden aus den Daten abgeleitet.

```sql
COPY INTO my_table
FROM '/path/to/files'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true', 'mergeSchema' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');
```

---

## Typen und Namen selbst setzen

Statt Typen ableiten zu lassen, kannst du im `SELECT` casten und umbenennen. Das ist nützlich bei CSV ohne Kopfzeile, deren Spalten `_c0`, `_c1` usw. heißen.

```sql
COPY INTO target_table
FROM (SELECT _c0::bigint key, _c1::int index, _c2 textData
      FROM 's3://bucket/base/path')
FILEFORMAT = CSV
PATTERN = 'folder1/file_[a-g].csv';
```

---

## Kein Rescued Data Column und kein `_corrupt_record`

- **`rescuedDataColumn`** wird von `COPY INTO` **nicht unterstützt**. Der Grund: Mit `COPY INTO` kann man das Schema nicht manuell setzen. Für diese Fälle empfiehlt Databricks Auto Loader.
- **`columnNameOfCorruptRecord`** funktioniert bei Auto Loader, aber nicht bei `COPY INTO`.

Siehe auch [../Rescued Data.md](../Rescued%20Data.md) und [../Corrupt Record.md](../Corrupt%20Record.md).

---

## Deletion Vectors

`COPY INTO` beachtet die Workspace-Einstellung für Deletion Vectors. Ist sie aktiv, schaltet ein `COPY INTO` auf einem SQL Warehouse oder auf Databricks Runtime 14.0+ die Deletion Vectors auf der Zieltabelle ein. Danach kann Databricks Runtime 11.3 LTS und älter die Tabelle **nicht mehr lesen**.
