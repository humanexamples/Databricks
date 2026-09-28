# cloudFiles.schemaHints

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | Schema-String (SQL-Schema-Spezifikationssyntax) |
| **`read_files`-Parameter** | `schemaHints` |
| **Seit** | alle Versionen; Array-/Map-Hints ab Databricks Runtime 9.1 LTS |

## Beschreibung

> „Schema information that you specify to Auto Loader during schema inference."

Erzwingt bekannte Typen für einzelne (auch verschachtelte) Felder, während der Rest weiterhin inferiert wird. Wird **nur verwendet, wenn kein explizites `schema` angegeben ist**, und funktioniert unabhängig von `cloudFiles.inferColumnTypes`. Noch nicht vorhandene Spalten lassen sich damit vorab deklarieren (alte Datensätze erhalten dann `NULL`).

Punktnotation für Struct-Felder, `.element` für Array-Elemente, `.key`/`.value` für Map-Einträge.

## Beispiel

```python
.option("cloudFiles.schemaHints", "tags map<string,string>, version int, user_info.dob DATE")
```

```sql
... FROM STREAM read_files('/Volumes/analytics/bronze/events', format => 'json',
  schemaHints => 'loyalty_tier STRING, region_code STRING')
```

## Siehe auch

- [../01 Schema-Inferenz und -Evolution.md](../01%20Schema-Inferenz%20und%20-Evolution.md) — vollständige Beispiele mit Vorher/Nachher-Schema-Bäumen
- [cloudFiles.schemaEvolutionMode.md](cloudFiles.schemaEvolutionMode.md)
