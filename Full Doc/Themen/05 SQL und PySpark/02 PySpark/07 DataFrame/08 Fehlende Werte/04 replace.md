# `DataFrame.replace()`

Gibt einen neuen DataFrame zurück, in dem ein Wert durch einen anderen ersetzt ist. `DataFrame.replace` und `DataFrameNaFunctions.replace` sind Aliase voneinander. `to_replace` und `value` müssen denselben Typ haben und dürfen nur numerisch, boolesch oder Strings sein; `value` darf `None` sein. Beim Ersetzen wird der neue Wert in den Typ der bestehenden Spalte gecastet.

## Signatur

```python
replace(to_replace: Union["LiteralType", List["LiteralType"], Dict["LiteralType", "OptionalPrimitiveType"]], value: Optional[Union["OptionalPrimitiveType", List["OptionalPrimitiveType"]]] = _NoValue, subset: Optional[List[str]] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `to_replace` | `bool`, `int`, `float`, `string`, `list` oder `dict` | Der zu ersetzende Wert. Ist es ein `dict`, wird `value` ignoriert oder kann weggelassen werden, und `to_replace` muss eine Abbildung von Wert auf Ersatzwert sein. |
| `value` | `bool`, `int`, `float`, `string` oder `None`, optional | Der Ersatzwert (`bool`, `int`, `float`, `string` oder `None`). Ist `value` eine Liste, muss sie dieselbe Länge und denselben Typ wie `to_replace` haben. Ist `value` ein Skalar und `to_replace` eine Sequenz, wird `value` als Ersatz für jedes Element von `to_replace` verwendet. |
| `subset` | `list`, optional | Optionale Liste der zu berücksichtigenden Spaltennamen. Spalten in `subset`, deren Datentyp nicht passt, werden ignoriert. |

## Rückgabewert

`DataFrame`: DataFrame mit ersetzten Werten.

## Beispiel

```python
df = spark.createDataFrame([
    (10, 80, "Alice"),
    (5, None, "Bob"),
    (None, 10, "Tom"),
    (None, None, None)],
    schema=["age", "height", "name"])

df.na.replace(10, 20).show()
# +----+------+-----+
# | age|height| name|
# +----+------+-----+
# |  20|    80|Alice|
# |   5|  NULL|  Bob|
# |NULL|    20|  Tom|
# |NULL|  NULL| NULL|
# +----+------+-----+

df.na.replace('Alice', None).show()
# +----+------+----+
# | age|height|name|
# +----+------+----+
# |  10|    80|NULL|
# |   5|  NULL| Bob|
# |NULL|    10| Tom|
# |NULL|  NULL|NULL|
# +----+------+----+

df.na.replace(['Alice', 'Bob'], ['A', 'B'], 'name').show()
# +----+------+----+
# | age|height|name|
# +----+------+----+
# |  10|    80|   A|
# |   5|  NULL|   B|
# |NULL|    10| Tom|
# |NULL|  NULL|NULL|
# +----+------+----+
```

Siehe auch [`fillna`](03%20fillna.md), [`na`](01%20na.md).

## Quellen

- DataFrame.replace: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/replace

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
