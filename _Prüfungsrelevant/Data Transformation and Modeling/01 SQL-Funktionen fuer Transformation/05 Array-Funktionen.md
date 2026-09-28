# Array-Funktionen

## `slice` — Teilausschnitt eines Arrays

**Syntax:** `slice(expr, start, length)`

- `expr`: `ARRAY`-Ausdruck. `start`: `INTEGER` — Startposition, Indizierung beginnt bei **1**; negativ → vom Ende gezählt.
- `length`: `INTEGER >= 0` — Länge des Ausschnitts.
- Ausschnitt außerhalb der Array-Grenzen → **leeres Array** (kein Fehler).
- Fehlerklasse `INVALID_PARAMETER_VALUE`: wenn `start = 0` oder `length` negativ.

```sql
SELECT slice(array(1, 2, 3, 4), 2, 2);    -- [2,3]
SELECT slice(array(1, 2, 3, 4), -2, 2);   -- [3,4]  (vom Ende gezählt)
SELECT slice(array(1, 2, 3), 0, 1);       -- Error: INVALID_PARAMETER_VALUE.START
```

**Stand:** 2026-09-14.
