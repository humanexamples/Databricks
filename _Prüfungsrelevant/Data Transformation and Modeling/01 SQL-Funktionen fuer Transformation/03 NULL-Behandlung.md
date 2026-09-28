# NULL-Behandlung

## `isnull` — prüft auf `NULL`

**Syntax:** `isnull(expr)` → `BOOLEAN`. Synonym für `IS NULL`.

> **VARIANT-Sonderfall:** Ist `expr` ein `VARIANT`-Wert aus einem JSON-Path-Ausdruck, `parse_json`, `variant_explode` oder `variant_explode_outer`, ist `isnull` **immer `false`** — auch wenn der enthaltene JSON-Wert `null` ist. Für die korrekte Prüfung `is_variant_null` verwenden, oder den `VARIANT` zuvor in einen konkreten Typ casten.

```sql
SELECT isnull(1);                                        -- false
SELECT isnull(NULL:INTEGER);                              -- true
SELECT isnull(parse_json('{"key": null}'):key);           -- false (VARIANT-Sonderfall!)
SELECT isnull(parse_json('{"key": null}'):key::STRING);   -- true (nach Cast in konkreten Typ)
SELECT isnull(parse_json('{"key": null}'):wrongkey);      -- true (Pfad existiert nicht)
SELECT is_variant_null(parse_json('{"key": null}'):key);  -- true (korrekte Prüfung auf VARIANT-NULL)
```

## `isnotnull` — prüft auf nicht-`NULL`

**Syntax:** `isnotnull(expr)`. Synonym für `expr IS NOT NULL`.

> Dieselbe VARIANT-Sonderregel wie bei `isnull`, spiegelbildlich: bei JSON-Path/`parse_json`/`variant_explode`/`variant_explode_outer` ist das Ergebnis **immer `true`**.

```sql
SELECT isnotnull(1);                                       -- true
SELECT isnotnull(NULL:INTEGER);                             -- false
SELECT isnotnull(parse_json('{"key": null}'):key);          -- true (VARIANT-Sonderfall!)
SELECT isnotnull(parse_json('{"key": null}'):wrongkey);     -- false
SELECT !is_variant_null(parse_json('{"key": null}'):key);   -- false (korrekte Prüfung)
```

## `coalesce` — erstes nicht-`NULL`-Argument

**Syntax:** `coalesce(expr1 [, ...])`

- Mind. ein Argument nötig; alle Argumente müssen einen gemeinsamen *Least Common Type* teilen (bestimmt den Ergebnistyp). Sind alle `NULL` → Ergebnis `NULL`.
- **Kurzschluss-Auswertung:** wertet von links nach rechts aus, stoppt beim ersten nicht-`NULL`-Wert — spätere Argumente werden nicht ausgewertet (anders als bei regulären Funktionen).
- Für `VARIANT` gelten dieselben Sonderregeln wie bei `isnull`.
- Nicht verwechseln mit `DataFrame.coalesce(numPartitions)` in Spark — das ist eine Partitionierungsoperation, keine NULL-Handling-Funktion.

```sql
SELECT coalesce(NULL, 1, NULL);        -- 1

-- Fehler: zweites Argument wird ausgewertet (erstes ist NULL)
SELECT coalesce(NULL, 5 / 0);          -- Error: DIVISION_BY_ZERO

-- Kein Fehler: erstes Argument ist bereits nicht NULL, 5/0 wird dank
-- Kurzschluss-Auswertung nie berechnet
SELECT coalesce(2, 5 / 0);             -- 2

SELECT coalesce(NULL, 'hello');        -- hello
```

**Stand:** 2026-09-14.
