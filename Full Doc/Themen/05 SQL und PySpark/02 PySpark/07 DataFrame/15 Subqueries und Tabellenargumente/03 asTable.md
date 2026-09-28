# `DataFrame.asTable()`

Wandelt den DataFrame in ein `TableArg`-Objekt um, das als Tabellenargument in einer TVF (Table-Valued Function) verwendet werden kann – einschließlich UDTFs (User-Defined Table Functions).

## Signatur

```python
asTable()
```

## Rückgabewert

`TableArg`: Ein `TableArg`-Objekt, das ein Tabellenargument repräsentiert.

## Hinweise

Nachdem man mit dieser Methode ein `TableArg` erhalten hat, lassen sich Partitionierung und Sortierung des Tabellenarguments über Methoden wie `partitionBy`, `orderBy` und `withSinglePartition` auf der `TableArg`-Instanz festlegen.

## Beispiel

```python
from pyspark.sql.functions import udtf

@udtf(returnType="id: int, doubled: int")
class DoubleUDTF:
    def eval(self, row):
        yield row["id"], row["id"] * 2

df = spark.createDataFrame([(1,), (2,), (3,)], ["id"])

result = DoubleUDTF(df.asTable())
result.show()
# +---+-------+
# | id|doubled|
# +---+-------+
# |  1|      2|
# |  2|      4|
# |  3|      6|
# +---+-------+

df2 = spark.createDataFrame(
    [(1, "a"), (1, "b"), (2, "c"), (2, "d")], ["key", "value"]
)

@udtf(returnType="key: int, value: string")
class ProcessUDTF:
    def eval(self, row):
        yield row["key"], row["value"]

result2 = ProcessUDTF(df2.asTable().partitionBy("key").orderBy("value"))
result2.show()
# +---+-----+
# |key|value|
# +---+-----+
# |  1|    a|
# |  1|    b|
# |  2|    c|
# |  2|    d|
# +---+-----+
```

## Quellen

- DataFrame.asTable: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/asTable

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
