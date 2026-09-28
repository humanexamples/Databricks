# Jobs Utility (`dbutils.jobs`)

Befehle zum Nutzen von Job-Features — im Kern die `taskValues`-Subutility zum Austausch beliebiger Werte zwischen Tasks eines Jobs. Ausführliche Praxisbeispiele (Listen, Query-Ergebnisse, Nutzung in dynamischen Wertreferenzen) bereits in [Task-Values.md](../../07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/07%20Parameter/05%20Task-Values.md); diese Seite ist die vollständige API-Referenz des Moduls. Teil der [Databricks Utils](00%20Uebersicht.md)-Reihe.

## Verfügbarkeit

**Nur Python** — weder `dbutils.jobs` noch `dbutils.jobs.taskValues` werden in R oder Scala unterstützt.

## Subutility: `taskValues`

Ermöglicht Tasks, während eines Job-Laufs beliebige Werte zu setzen und in anderen Tasks desselben Laufs wieder abzurufen — z. B. um IDs, Metriken oder Auswertungsergebnisse weiterzugeben.

**Wichtige Grenze:** maximal **250 Task Values pro Task und Job-Lauf**.

### `get`

**Signatur:**

```
get(taskKey: String, key: String, default: int, debugValue: int): Seq
```

| Parameter | Pflicht | Bedeutung |
|---|---|---|
| `taskKey` | ja | Name des Tasks, der den Wert gesetzt hat |
| `key` | ja | Name des Task-Value-Keys |
| `default` | optional | Rückgabewert, falls `key` nicht gefunden wird |
| `debugValue` | optional | Rückgabewert, wenn außerhalb eines Job-Kontexts ausgeführt |

**Verhalten:** Löst `ValueError` aus, wenn `taskKey`/`key` nicht gefunden werden (außer `default` ist gesetzt); löst `TypeError` aus, wenn außerhalb eines Job-Kontexts aufgerufen (außer `debugValue` ist gesetzt). `default` und `debugValue` dürfen nicht `None` sein. **Auf Databricks Runtime 10.4 und früher** wird stattdessen `Py4JJavaError` statt `ValueError` ausgelöst, wenn der Task nicht gefunden wird.

```python
dbutils.jobs.taskValues.get(taskKey    = "my-task",
                            key        = "my-key",
                            default    = 7,
                            debugValue = 42)
```

### `set`

**Signatur:**

```
set(key: String, value: String): boolean
```

| Parameter | Pflicht | Bedeutung |
|---|---|---|
| `key` | ja | Key des Task Value — muss innerhalb des Tasks eindeutig sein |
| `value` | ja | zu speichernder Wert — muss JSON-darstellbar sein, maximal 48 KiB |

**Verhalten:** Tut nichts, wenn außerhalb eines Job-Kontexts aufgerufen. Gibt `True` bei Erfolg zurück.

```python
dbutils.jobs.taskValues.set(key   = "my-key",
                            value = 5)

dbutils.jobs.taskValues.set(key   = "my-other-key",
                            value = "my other value")
```

## Weitere Hinweise

- `dbutils`-Aufrufe innerhalb von Executors können zu unerwarteten Ergebnissen oder Fehlern führen.
- Für die Verwendung von Task Values in dynamischen Wertreferenzen anderer Tasks siehe [Dynamische Wertreferenzen.md](../../07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/07%20Parameter/04%20Dynamische%20Wertreferenzen.md).

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/databricks-utils#jobs-utility-dbutilsjobs

**Stand:** 2026-08-26.
