# `DataFrame.executionInfo` (Eigenschaft)

Gibt nach der Ausführung der Query ein `ExecutionInfo`-Objekt zurück.

Mit der Eigenschaft `executionInfo` lassen sich nach einer erfolgreichen Ausführung Informationen über die tatsächliche Query-Ausführung untersuchen. Ein Zugriff vor der Ausführung liefert `None`. Wird derselbe DataFrame mehrfach ausgeführt, überschreibt die jeweils letzte Operation die Ausführungsinformationen.

> **Hinweis:** Diese Eigenschaft ist ausschließlich für den Spark-Connect-Client vorgesehen. Mit einer regulären Spark-Session wird eine Exception ausgelöst.

## Rückgabewert

`ExecutionInfo` oder `None`

## Beispiel

Die offizielle Referenz enthält für diese Eigenschaft kein Beispiel.

## Quellen

- DataFrame.executionInfo: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/executionInfo

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
