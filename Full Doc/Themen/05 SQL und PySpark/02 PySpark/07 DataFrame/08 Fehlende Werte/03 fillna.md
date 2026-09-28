# `DataFrame.fillna()`

Gibt einen neuen DataFrame zurück, in dem NULL-Werte durch einen neuen Wert ersetzt sind. `DataFrame.fillna` und `DataFrameNaFunctions.fill` sind Aliase voneinander.

## Signatur

```python
fillna(value: Union["LiteralType", Dict[str, "LiteralType"]], subset: Optional[Union[str, Tuple[str, ...], List[str]]] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `value` | `int`, `float`, `string`, `bool` oder `dict` | Der Wert, durch den NULL-Werte ersetzt werden. Ist der Wert ein `dict`, wird `subset` ignoriert und `value` muss eine Abbildung von Spaltenname (String) auf Ersatzwert sein. Der Ersatzwert muss ein `int`, `float`, `bool` oder `string` sein. |
| `subset` | `str`, `tuple` oder `list`, optional | Optionale Liste der zu berücksichtigenden Spaltennamen. Spalten in `subset`, deren Datentyp nicht passt, werden ignoriert. |

## Rückgabewert

`DataFrame`: DataFrame mit ersetzten NULL-Werten.

## Beispiel

```python
df = spark.createDataFrame([
    (10, 80.5, "Alice", None),
    (5, None, "Bob", None),
    (None, None, "Tom", None),
    (None, None, None, True)],
    schema=["age", "height", "name", "bool"])

df.na.fill(50).show()
# +---+------+-----+----+
# |age|height| name|bool|
# +---+------+-----+----+
# | 10|  80.5|Alice|NULL|
# |  5|  50.0|  Bob|NULL|
# | 50|  50.0|  Tom|NULL|
# | 50|  50.0| NULL|true|
# +---+------+-----+----+

df.na.fill(False).show()
# +----+------+-----+-----+
# | age|height| name| bool|
# +----+------+-----+-----+
# |  10|  80.5|Alice|false|
# |   5|  NULL|  Bob|false|
# |NULL|  NULL|  Tom|false|
# |NULL|  NULL| NULL| true|
# +----+------+-----+-----+

df.na.fill({'age': 50, 'name': 'unknown'}).show()
# +---+------+-------+----+
# |age|height|   name|bool|
# +---+------+-------+----+
# | 10|  80.5|  Alice|NULL|
# |  5|  NULL|    Bob|NULL|
# | 50|  NULL|    Tom|NULL|
# | 50|  NULL|unknown|true|
# +---+------+-------+----+
```

Siehe auch [`dropna`](02%20dropna.md), [`replace`](04%20replace.md), [`na`](01%20na.md).

## Quellen

- DataFrame.fillna: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/fillna

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
