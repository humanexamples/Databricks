# `slice` — Teilausschnitt eines Arrays

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/slice>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt eine Teilmenge eines Arrays zurück.

## Syntax

```
slice(expr, start, length)
```

## Argumente

- **`expr`**: ein `ARRAY`-Ausdruck.
- **`start`**: ein `INTEGER`-Ausdruck.
- **`length`**: ein `INTEGER`-Ausdruck `>= 0`.

## Rückgabe

Das Ergebnis entspricht dem Typ von `expr`. Extrahiert einen Ausschnitt des Arrays `expr` ab Index `start` (Array-Indizierung beginnt bei 1), bzw. vom Ende, wenn `start` negativ ist, über die angegebene `length`. Fällt der angeforderte Ausschnitt außerhalb der Array-Grenzen, wird ein leeres Array zurückgegeben.

Databricks löst `INVALID_PARAMETER_VALUE` aus, wenn `start` gleich 0 oder `length` negativ ist.

## Beispiele

```sql
> SELECT slice(array(1, 2, 3, 4), 2, 2);
[2,3]

> SELECT slice(array(1, 2, 3, 4), -2, 2);
[3,4]

> SELECT slice(array(1, 2, 3), 0, 1);
Error: INVALID_PARAMETER_VALUE.START
```

## Verwandte Funktionen

- `array` function
