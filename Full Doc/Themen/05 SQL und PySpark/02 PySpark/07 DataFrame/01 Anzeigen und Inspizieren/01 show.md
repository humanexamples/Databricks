# `DataFrame.show()`

Gibt die ersten `n` Zeilen des DataFrames auf der Konsole aus.

## Signatur

```python
show(n: int = 20, truncate: Union[bool, int] = True, vertical: bool = False)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `n` | `int`, optional, Standard 20 | Anzahl der anzuzeigenden Zeilen. |
| `truncate` | `bool` oder `int`, optional, Standard `True` | Bei `True` werden Strings mit mehr als 20 Zeichen abgeschnitten. Bei einer Zahl größer 1 werden lange Strings auf die Länge `truncate` gekürzt und die Zellen rechtsbündig ausgerichtet. |
| `vertical` | `bool`, optional | Bei `True` werden die Zeilen vertikal ausgegeben (eine Zeile pro Spaltenwert). |

## Beispiel

```python
df = spark.createDataFrame([
    (14, "Tom"), (23, "Alice"), (16, "Bob"), (19, "This is a super long name")],
    ["age", "name"])

df.show()
# +---+--------------------+
# |age|                name|
# +---+--------------------+
# | 14|                 Tom|
# | 23|               Alice|
# | 16|                 Bob|
# | 19|This is a super l...|
# +---+--------------------+

df.show(2)
# +---+-----+
# |age| name|
# +---+-----+
# | 14|  Tom|
# | 23|Alice|
# +---+-----+
# only showing top 2 rows

df.show(truncate=False)
# +---+-------------------------+
# |age|name                     |
# +---+-------------------------+
# |14 |Tom                      |
# |23 |Alice                    |
# |16 |Bob                      |
# |19 |This is a super long name|
# +---+-------------------------+

df.show(truncate=3)
# +---+----+
# |age|name|
# +---+----+
# | 14| Tom|
# | 23| Ali|
# | 16| Bob|
# | 19| Thi|
# +---+----+

df.show(vertical=True)
# -RECORD 0--------------------
# age  | 14
# name | Tom
# -RECORD 1--------------------
# age  | 23
# name | Alice
# -RECORD 2--------------------
# age  | 16
# name | Bob
# -RECORD 3--------------------
# age  | 19
# name | This is a super l...
```

## Quellen

- DataFrame.show: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/show

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
