# `DeltaTableBuilder` — Python-Referenz (Delta Lake)

## Abschnittsübersicht
1. [Zweck](#zweck)
2. [`tableName()`](#tablename)
3. [`location()`](#location)
4. [`comment()`](#comment)
5. [`addColumn()`](#addcolumn)
6. [`addColumns()`](#addcolumns)
7. [`partitionedBy()`](#partitionedby)
8. [`clusterBy()`](#clusterby)
9. [`property()`](#property)
10. [`execute()`](#execute)
11. [Quellen](#quellen)

## <a id="zweck">1. Zweck</a>

`DeltaTableBuilder` ist das Builder-Objekt zum programmatischen Anlegen (oder Ersetzen) einer Delta-Tabelle mit Schema, Partitionierung und Tabelleneigenschaften. Man erhält eine Instanz über `DeltaTable.create(sparkSession)` (Fehler, falls Tabelle existiert), `DeltaTable.createIfNotExists(sparkSession)` (nur anlegen, falls nicht vorhanden), `DeltaTable.replace(sparkSession)` (existierende Tabelle ersetzen) oder `DeltaTable.createOrReplace(sparkSession)` (anlegen oder ersetzen). Die Methoden werden verkettet und mit `execute()` abgeschlossen, was eine `DeltaTable`-Instanz zurückgibt.

## <a id="tablename">2. `tableName()`</a>

- Legt den Tabellennamen fest, optional mit Datenbank-Qualifizierung (`datenbank_name.tabellen_name`).
- Parameter:
  - `identifier` (str) — Tabellenname, ggf. mit vorangestelltem Datenbanknamen.
- Rückgabe: `DeltaTableBuilder` (Chaining).

```python
DeltaTable.create(spark).tableName("testTable")
```

## <a id="location">3. `location()`</a>

- Legt den Pfad fest, unter dem die Tabellendaten gespeichert werden (kann ein Pfad auf verteiltem Storage sein).
- Parameter:
  - `location` (str) — Verzeichnispfad für die Tabellendaten.
- Rückgabe: `DeltaTableBuilder`.

```python
DeltaTable.create(spark).tableName("testTable").location("/mnt/data/testTable")
```

## <a id="comment">4. `comment()`</a>

- Setzt einen beschreibenden Kommentar für die Tabelle.
- Parameter:
  - `comment` (str) — Freitext-Beschreibung der Tabelle.
- Rückgabe: `DeltaTableBuilder`.

```python
DeltaTable.create(spark).tableName("testTable").comment("Rohdaten aus dem Ingest-Prozess")
```

## <a id="addcolumn">5. `addColumn()`</a>

- Fügt der Tabelle eine einzelne Spalte hinzu. Die Docs zeigen zwei Aufrufformen: Übergabe von Name/Datentyp mit Keyword-Argumenten, oder Übergabe eines fertigen `StructField`-Objekts.
- Parameter (Name+Typ-Form):
  - `colName` (str) — Spaltenname.
  - `dataType` (str oder `pyspark.sql.types.DataType`) — Datentyp, z. B. `"INT"` oder `IntegerType()`.
  - `nullable` (bool, Default `True`) — ob NULL-Werte erlaubt sind.
  - `generatedAlwaysAs` (str oder `IdentityGenerator`, optional) — SQL-Ausdruck für berechnete Spalten (z. B. `"c1 + 1"`) oder `IdentityGenerator` für Identity-Spalten.
  - `generatedByDefaultAs` (`IdentityGenerator`, optional) — `IdentityGenerator` für Identity-Werte, die nur greifen, wenn der Nutzer keinen eigenen Wert angibt.
  - `comment` (str, optional) — Spaltenbeschreibung.

**Form 1 — Name, Datentyp und Keyword-Argumente:**

```python
from pyspark.sql.types import IntegerType

deltaTable = DeltaTable.create(spark) \
    .tableName("testTable") \
    .addColumn("c1", dataType="INT", nullable=False) \
    .addColumn("c2", dataType=IntegerType(), generatedAlwaysAs="c1 + 1") \
    .partitionedBy("c1") \
    .execute()
```

**Form 2 — Identity-Spalte über `IdentityGenerator`:**

```python
from delta.tables import IdentityGenerator

deltaTable = DeltaTable.create(spark) \
    .tableName("testTable") \
    .addColumn("id", dataType="BIGINT", generatedAlwaysAs=IdentityGenerator(start=1, step=1)) \
    .addColumn("value", dataType="STRING", comment="Nutzdaten") \
    .execute()
```

## <a id="addcolumns">6. `addColumns()`</a>

- Übernimmt mehrere Spalten auf einmal aus einem bestehenden Schema, z. B. dem Schema eines DataFrames.
- Parameter:
  - `cols` (`pyspark.sql.types.StructType` oder `List[StructField]`) — Spaltendefinitionen, die übernommen werden sollen.
- Rückgabe: `DeltaTableBuilder`.

```python
df = spark.createDataFrame([('a', 1), ('b', 2), ('c', 3)], ["key", "value"])

deltaTable = DeltaTable.replace(spark) \
    .tableName("testTable") \
    .addColumns(df.schema) \
    .execute()
```

## <a id="partitionedby">7. `partitionedBy()`</a>

- Legt die Partitionierungsspalten der Tabelle fest. Akzeptiert entweder mehrere einzelne String-Argumente oder eine Liste/Tuple von Strings.
- Parameter:
  - `*cols` (str) — Spaltennamen als Einzelargumente, **oder**
  - `cols` (`List[str]` bzw. `Tuple[str, ...]`) — Spaltennamen als Liste/Tuple.
- Rückgabe: `DeltaTableBuilder`.

```python
DeltaTable.create(spark).tableName("t").addColumn("c1", "INT").partitionedBy("c1")

# alternativ mit Liste:
DeltaTable.create(spark).tableName("t").addColumn("c1", "INT").partitionedBy(["c1"])
```

## <a id="clusterby">8. `clusterBy()`</a>

- Legt Liquid-Clustering-Spalten der Tabelle fest (Alternative zu `partitionedBy()`). Akzeptiert dieselben zwei Aufrufformen wie `partitionedBy()`.
- Parameter:
  - `*cols` (str) — Spaltennamen als Einzelargumente, **oder**
  - `cols` (`List[str]` bzw. `Tuple[str, ...]`) — Spaltennamen als Liste/Tuple.
- Rückgabe: `DeltaTableBuilder`.

```python
DeltaTable.create(spark).tableName("t").addColumn("c1", "INT").clusterBy("c1")
```

## <a id="property">9. `property()`</a>

- Setzt eine einzelne Tabelleneigenschaft (Key-Value-Paar), z. B. eine Delta-Table-Property.
- Parameter:
  - `key` (str) — Name der Eigenschaft.
  - `value` (str) — Wert der Eigenschaft.
- Rückgabe: `DeltaTableBuilder`.

```python
DeltaTable.create(spark).tableName("t").addColumn("c1", "INT") \
    .property("delta.appendOnly", "true")
```

## <a id="execute">10. `execute()`</a>

- Führt die Tabellenerstellung (bzw. das Ersetzen) mit allen konfigurierten Angaben aus.
- Parameter: keine.
- Rückgabe: `DeltaTable` — Instanz, die auf die neu erstellte/ersetzte Tabelle zeigt.

```python
deltaTable = DeltaTable.create(spark) \
    .tableName("testTable") \
    .addColumn("c1", dataType="INT", nullable=False) \
    .execute()
```

## <a id="quellen">11. Quellen</a>
- `DeltaTableBuilder` — vollständige Klassenreferenz (Signaturen, Parameter, Beispiele): https://docs.delta.io/api/latest/python/spark/

**Stand:** 2026-09-21.
