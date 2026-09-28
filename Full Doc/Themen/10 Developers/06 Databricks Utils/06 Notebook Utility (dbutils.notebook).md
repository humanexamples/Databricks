# Notebook Utility (`dbutils.notebook`)

Befehle zum Verketten von Notebooks und zum Reagieren auf deren Ergebnisse — der Kern klassischer Notebook-Workflows. Teil der [Databricks Utils](00%20Uebersicht.md)-Reihe.

## Befehl: `exit`

**Signatur:**

```python
dbutils.notebook.exit(value: String): void
```

Beendet die Notebook-Ausführung mit einem Rückgabewert.

```python
dbutils.notebook.exit("Exiting from My Other Notebook")
# Output: Notebook exited: Exiting from My Other Notebook
```

**Verfügbarkeit:** Python, R, Scala.

**Wichtiger Vorbehalt:** Laufen im Hintergrund Structured-Streaming-Queries, beendet `exit()` den Lauf **nicht** — die Ausführung läuft weiter, bis die Query gestoppt wird. Hintergrund-Queries müssen manuell über die Notebook-UI abgebrochen oder per `query.stop()` beendet werden, bevor `exit()` greift.

## Befehl: `run`

**Signatur:**

```python
dbutils.notebook.run(path: String, timeoutSeconds: int, arguments: Map): String
```

Führt ein anderes Notebook aus und liefert dessen Exit-Wert zurück.

| Parameter | Bedeutung |
|---|---|
| `path` | Dateipfad zum auszuführenden Notebook |
| `timeoutSeconds` | maximale Ausführungszeit in Sekunden, bevor eine Timeout-Exception ausgelöst wird |
| `arguments` | optionale Key-Value-Paare, die als Parameter an das aufgerufene Notebook übergeben werden |

**Rückgabewert:** String (der Exit-Wert des aufgerufenen Notebooks) — maximal **5 MB**.

```python
dbutils.notebook.run("My Other Notebook", 60)
# Output: 'Exiting from My Other Notebook'
```

**Wichtige Einschränkungen:**

- maximale Länge des Rückgabe-Strings: 5 MB.
- Läuft im **aktuellen Cluster**.
- Wirft eine Exception, wenn die Ausführung `timeoutSeconds` überschreitet.

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/databricks-utils#notebook-utility-dbutilsnotebook

**Stand:** 2026-08-26.
