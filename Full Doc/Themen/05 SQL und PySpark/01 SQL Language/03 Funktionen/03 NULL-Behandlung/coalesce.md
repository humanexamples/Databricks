# `coalesce`-Funktion

> **Gilt für:** Databricks SQL, Databricks Runtime

Gibt das **erste nicht-`NULL`-Argument** zurück.

---

## Syntax

```
coalesce(expr1 [, ...] )
```

## Argumente

- **`exprN`**: Ein beliebiger Ausdruck, der über alle `exprN` hinweg einen gemeinsamen [Least Common Type](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-datatype-rules#least-common-type-resolution) teilt.

## Rückgabewert

Der Ergebnistyp ist der **Least Common Type** der Argumente.

- Es muss **mindestens ein** Argument geben.
- **Kurzschluss-Auswertung (short-circuit):** *"Unlike for regular functions where all arguments are evaluated before invoking the function, `coalesce` evaluates arguments left to right until a non-null value is found."* — die Argumente werden also **von links nach rechts** ausgewertet, und die Auswertung stoppt beim ersten nicht-`NULL`-Wert. (Anders als bei normalen Funktionen, bei denen alle Argumente vor dem Aufruf ausgewertet werden.)
- Sind **alle** Argumente `NULL`, ist das Ergebnis `NULL`.
- Für `VARIANT`-Typen gelten Sonderregeln — siehe [`isnull`](isnull.md).

---

## Beispiele

```sql
> SELECT coalesce(NULL, 1, NULL);
 1

-- The following example raises a runtime error because the second argument is evaluated.
>  SELECT coalesce(NULL, 5 / 0);
Error: DIVISION_BY_ZERO

-- The following example raises no runtime error because the second argument is not evaluated.
> SELECT coalesce(2, 5 / 0);
 2

> SELECT coalesce(NULL, 'hello');
 hello
```

Das zweite und dritte Beispiel zeigen den praktischen Effekt der Kurzschluss-Auswertung: `coalesce(NULL, 5 / 0)` wertet `5 / 0` aus (→ `DIVISION_BY_ZERO`), weil das erste Argument `NULL` ist; `coalesce(2, 5 / 0)` wertet `5 / 0` **nicht** aus, weil bereits das erste Argument nicht `NULL` ist.

---

## Verwandte Funktionen

- `nvl`-Funktion — `/aws/en/sql/language-manual/functions/nvl`
- `nvl2`-Funktion — `/aws/en/sql/language-manual/functions/nvl2`
- [`isnull`](isnull.md) / [`isnotnull`](isnotnull.md) (Sonderregeln für `VARIANT`)
- SQL data type rules — `/aws/en/sql/language-manual/sql-ref-datatype-rules`

> **Nicht verwechseln mit** `DataFrame.coalesce(numPartitions)` / `Dataset.coalesce` in Spark — das ist eine Partitionierungsoperation zum Reduzieren der Partitionsanzahl (siehe `../../../09 Performance Optimization/03 Code Optimization/01 Shuffles.md`), keine NULL-Handling-Funktion.

---

## Quellen

- coalesce function — SQL-Sprachreferenz: https://docs.databricks.com/aws/en/sql/language-manual/functions/coalesce

**Stand:** 2026-09-02.
