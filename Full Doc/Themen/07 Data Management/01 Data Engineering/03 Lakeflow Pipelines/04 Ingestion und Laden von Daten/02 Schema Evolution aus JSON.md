# Schema-Inferenz und -Evolution mit `from_json` in Pipelines — Referenz

Dieses Dokument beschreibt, wie die SQL-Funktion `from_json` innerhalb von Lakeflow-Declarative-Pipelines (LDP) Schema von JSON-Blobs automatisch inferieren und weiterentwickeln kann, ohne dass ein explizites Schema angegeben wird. **Diese Funktion befindet sich in Public Preview.** Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/from-json-schema-evolution`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte.

Für die analoge, bereits ausführlich verifizierte Schema-Evolution bei Auto Loader (`cloudFiles.schemaEvolutionMode`) siehe `Lakeflow Connect/Lakeflow Connect Standard Connectors/Working with Files/06 Auto Loader/01 Schema-Inferenz und -Evolution.md` (Abschnitt Schema-Evolution-Modi) in diesem Projekt — die Modi sind laut Doku explizit konsistent ("These modes are consistent with Auto Loader").

## Abschnittsübersicht

1. [Funktionsweise von `from_json` in Pipelines](#funktionsweise)
2. [Syntax: automatische Schema-Inferenz und -Evolution](#syntax-auto)
3. [Syntax: festes Schema](#syntax-fest)
4. [Schema-Inferenz im Detail](#inferenz)
5. [Schema-Inferenz mit Schema Hints überschreiben](#schema-hints)
6. [Schema-Evolution mit `schemaEvolutionMode`](#evolution-modi)
7. [Rescued-Data-Spalte](#rescued-data)
8. [Umgang mit beschädigten Datensätzen](#corrupt-records)
9. [Auf ein Feld im `from_json`-Ergebnis referenzieren](#referenzieren)
10. [Beispiele: automatische Inferenz und Evolution](#beispiele)
11. [`from_json` vs. `parse_json`](#vs-parse-json)
12. [FAQ](#faq)
13. [Quellen](#quellen)

---

## <a id="funktionsweise">1. Funktionsweise von `from_json` in Pipelines</a>

Die SQL-Funktion `from_json` parst eine JSON-String-Spalte und gibt einen Struct-Wert zurück. Außerhalb einer Pipeline muss das Schema des Rückgabewerts explizit über das `schema`-Argument angegeben werden. Innerhalb einer Pipeline lassen sich stattdessen Schema-Inferenz und -Evolution aktivieren, die das Schema des Rückgabewerts automatisch verwalten. Das vereinfacht sowohl die initiale Einrichtung (besonders bei unbekanntem Schema) als auch den laufenden Betrieb bei häufigen Schema-Änderungen. Es verarbeitet beliebige JSON-Blobs aus streamenden Datenquellen wie Auto Loader, Kafka oder Kinesis.

Innerhalb einer Pipeline kann Schema-Inferenz und -Evolution für `from_json`:

- neue Felder in eingehenden JSON-Datensätzen erkennen (einschließlich verschachtelter JSON-Objekte),
- Feldtypen inferieren und auf passende Spark-Datentypen abbilden,
- das Schema automatisch um neue Felder erweitern,
- Daten, die nicht mit dem aktuellen Schema übereinstimmen, automatisch behandeln.

## <a id="syntax-auto">2. Syntax: automatische Schema-Inferenz und -Evolution</a>

Um Schema-Inferenz mit `from_json` in einer Pipeline zu aktivieren, wird das Schema auf `NULL` gesetzt und die Option `schemaLocationKey` angegeben:

```sql
from_json(jsonStr, NULL, map("schemaLocationKey", "<uniqueKey>" [, otherOptions]))
```

```python
from_json(jsonStr, None, {"schemaLocationKey": "<uniqueKey>"[, otherOptions]})
```

Eine Query kann mehrere `from_json`-Ausdrücke enthalten, aber jeder Ausdruck muss einen eindeutigen `schemaLocationKey` haben. Der `schemaLocationKey` muss zudem pro Pipeline eindeutig sein.

```sql
SELECT
  value,
  from_json(value, NULL, map('schemaLocationKey', 'keyX')) parsedX,
  from_json(value, NULL, map('schemaLocationKey', 'keyY')) parsedY,
FROM STREAM READ_FILES('/databricks-datasets/nyctaxi/sample/json/', format => 'text')
```

```python
(spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "text")
    .load("/databricks-datasets/nyctaxi/sample/json/")
    .select(
      col("value"),
      from_json(col("value"), None, {"schemaLocationKey": "keyX"}).alias("parsedX"),
      from_json(col("value"), None, {"schemaLocationKey": "keyY"}).alias("parsedY"))
)
```

## <a id="syntax-fest">3. Syntax: festes Schema</a>

Soll stattdessen ein bestimmtes Schema erzwungen werden, wird die reguläre `from_json`-Syntax verwendet:

```
from_json(jsonStr, schema, [, options])
```

Diese Syntax lässt sich in jeder Databricks-Umgebung verwenden, auch außerhalb von Pipelines.

## <a id="inferenz">4. Schema-Inferenz im Detail</a>

`from_json` inferiert das Schema aus dem ersten Batch der JSON-Datenspalten und indiziert es intern über den (erforderlichen) `schemaLocationKey`.

Ist der JSON-String ein einzelnes Objekt (z. B. `{"id": 123, "name": "John"}`), inferiert `from_json` ein Schema vom Typ `STRUCT` und ergänzt eine `rescuedDataColumn` in der Feldliste:

```
STRUCT<id LONG, name STRING, _rescued_data STRING>
```

Enthält der JSON-String jedoch ein Top-Level-Array (z. B. `["id": 123, "name": "John"]`), umschließt `from_json` das `ARRAY` mit einem `STRUCT`. Dieser Ansatz erlaubt es, mit dem inferierten Schema inkompatible Daten zu retten. Die Array-Werte können anschließend downstream mit `explode` in separate Zeilen aufgesplittet werden:

```
STRUCT<value ARRAY<id LONG, name STRING>, _rescued_data STRING>
```

## <a id="schema-hints">5. Schema-Inferenz mit Schema Hints überschreiben</a>

Optional lassen sich `schemaHints` angeben, um zu beeinflussen, wie `from_json` den Typ einer Spalte inferiert — hilfreich, wenn der Typ einer Spalte bereits bekannt ist oder ein allgemeinerer Typ gewünscht wird (z. B. ein `double` statt eines `integer`). Eine beliebige Anzahl von Hints für Spaltendatentypen lässt sich über die SQL-Schema-Spezifikationssyntax angeben. Die Semantik der Schema Hints ist dieselbe wie bei Auto Loader (siehe `Lakeflow Connect/Lakeflow Connect Standard Connectors/Working with Files/06 Auto Loader/01 Schema-Inferenz und -Evolution.md`, Abschnitt `schemaHints`). Beispiel:

```sql
SELECT
-- The JSON `{"a": 1}` will treat `a` as a BIGINT
from_json(data, NULL, map('schemaLocationKey', 'w', 'schemaHints', '')),
-- The JSON `{"a": 1}` will treat `a` as a STRING
from_json(data, NULL, map('schemaLocationKey', 'x', 'schemaHints', 'a STRING')),
-- The JSON `{"a": {"b": 1}}` will treat `a` as a MAP<STRING, BIGINT>
from_json(data, NULL, map('schemaLocationKey', 'y', 'schemaHints', 'a MAP<STRING, BIGINT'>)),
-- The JSON `{"a": {"b": 1}}` will treat `a` as a STRING
from_json(data, NULL, map('schemaLocationKey', 'z', 'schemaHints', 'a STRING')),
FROM STREAM READ_FILES(...)
```

Enthält der JSON-String ein Top-Level-`ARRAY`, wird dieses mit einem `STRUCT` umschlossen. In diesem Fall werden Schema Hints auf das `ARRAY`-Schema angewendet, nicht auf das umschließende `STRUCT`. Beispiel für ein JSON-Array:

```
[{"id": 123, "name": "John"}]
```

Das inferierte `ARRAY`-Schema wird mit einem `STRUCT` umschlossen:

```
STRUCT<value ARRAY<id LONG, name STRING>, _rescued_data STRING>
```

Um den Datentyp von `id` zu ändern, wird der Schema Hint als `element.id STRING` angegeben. Um eine neue Spalte vom Typ `DOUBLE` zu ergänzen: `element.new_col DOUBLE`. Das resultierende Schema für das Top-Level-JSON-Array:

```
struct<value array<id STRING, name STRING, new_col DOUBLE>, _rescued_data STRING>
```

## <a id="evolution-modi">6. Schema-Evolution mit `schemaEvolutionMode`</a>

`from_json` erkennt das Hinzufügen neuer Spalten während der Verarbeitung. Wird ein neues Feld erkannt, aktualisiert `from_json` das inferierte Schema mit dem neuesten Stand, indem neue Spalten an das Ende des Schemas angefügt werden. Die Datentypen bestehender Spalten bleiben unverändert. Nach der Schema-Aktualisierung startet die Pipeline automatisch mit dem aktualisierten Schema neu.

`from_json` unterstützt folgende Modi über die optionale Einstellung `schemaEvolutionMode` — konsistent mit Auto Loader:

| `schemaEvolutionMode` | Verhalten beim Lesen einer neuen Spalte |
|---|---|
| `addNewColumns` (Standard) | Stream schlägt fehl. Neue Spalten werden zum Schema hinzugefügt. Datentypen bestehender Spalten entwickeln sich nicht weiter. |
| `rescue` | Schema wird nie weiterentwickelt, Stream schlägt nicht wegen Schema-Änderungen fehl. Alle neuen Spalten werden in der Rescued-Data-Spalte aufgezeichnet. |
| `failOnNewColumns` | Stream schlägt fehl. Stream startet nicht neu, es sei denn `schemaHints` werden aktualisiert oder die betroffenen Daten entfernt. |
| `none` | Entwickelt das Schema nicht weiter, neue Spalten werden ignoriert, Daten werden nicht gerettet, sofern nicht `rescuedDataColumn` gesetzt ist. Stream schlägt nicht wegen Schema-Änderungen fehl. |

```sql
SELECT
-- If a new column appears, the pipeline will automatically add it to the schema:
from_json(a, NULL, map('schemaLocationKey', 'w', 'schemaEvolutionMode', 'addNewColumns')),
-- If a new column appears, the pipeline will add it to the rescued data column:
from_json(b, NULL, map('schemaLocationKey', 'x', 'schemaEvolutionMode', 'rescue')),
-- If a new column appears, the pipeline will ignore it:
from_json(c, NULL, map('schemaLocationKey', 'y', 'schemaEvolutionMode', 'none')),
-- If a new column appears, the pipeline will fail:
from_json(d, NULL, map('schemaLocationKey', 'z', 'schemaEvolutionMode', 'failOnNewColumns')),
FROM STREAM READ_FILES(...)
```

## <a id="rescued-data">7. Rescued-Data-Spalte</a>

Eine Rescued-Data-Spalte wird automatisch als `_rescued_data` zum Schema hinzugefügt. Sie lässt sich über die Option `rescuedDataColumn` umbenennen:

```
from_json(jsonStr, None, {"schemaLocationKey": "keyX", "rescuedDataColumn": "my_rescued_data"})
```

Ist die Rescued-Data-Spalte aktiv, werden Spalten, die nicht mit dem inferierten Schema übereinstimmen, gerettet statt verworfen. Gründe dafür: Typkonflikt, fehlende Spalte im Schema, oder eine abweichende Groß-/Kleinschreibung des Spaltennamens.

## <a id="corrupt-records">8. Umgang mit beschädigten Datensätzen</a>

Um fehlerhafte, nicht parsbare Datensätze zu speichern, wird eine `_corrupt_record`-Spalte über Schema Hints ergänzt:

```sql
CREATE STREAMING TABLE bronze AS
  SELECT
    from_json(value, NULL,
      map('schemaLocationKey', 'nycTaxi',
          'schemaHints', '_corrupt_record STRING',
          'columnNameOfCorruptRecord', '_corrupt_record')) jsonCol
  FROM STREAM READ_FILES('/databricks-datasets/nyctaxi/sample/json/', format => 'text')
```

Zum Umbenennen der Corrupt-Record-Spalte dient die Option `columnNameOfCorruptRecord`. Der JSON-Parser unterstützt drei Modi für beschädigte Datensätze:

| Modus | Beschreibung |
|---|---|
| `PERMISSIVE` | Legt bei beschädigten Datensätzen den fehlerhaften String in das über `columnNameOfCorruptRecord` konfigurierte Feld und setzt fehlerhafte Felder auf `null`. Um beschädigte Datensätze zu behalten, kann ein String-Feld mit dem Namen `columnNameOfCorruptRecord` im benutzerdefinierten Schema gesetzt werden — fehlt dieses Feld im Schema, werden beschädigte Datensätze beim Parsen verworfen. Bei Schema-Inferenz fügt der Parser implizit ein `columnNameOfCorruptRecord`-Feld zum Ausgabeschema hinzu. |
| `DROPMALFORMED` | Ignoriert beschädigte Datensätze. In Kombination mit `rescuedDataColumn` führen Typkonflikte nicht zum Verwerfen von Datensätzen — nur echte Corrupt Records (unvollständiges/fehlerhaft formatiertes JSON) werden verworfen. |
| `FAILFAST` | Wirft eine Exception, sobald der Parser beschädigte Datensätze antrifft. In Kombination mit `rescuedDataColumn` werfen Typkonflikte keinen Fehler — nur echte Corrupt Records werfen Fehler. |

## <a id="referenzieren">9. Auf ein Feld im `from_json`-Ergebnis referenzieren</a>

`from_json` inferiert das Schema während der Pipeline-Ausführung. Referenziert eine nachgelagerte Query ein `from_json`-Feld, bevor `from_json` mindestens einmal erfolgreich ausgeführt wurde, löst sich das Feld nicht auf und die Query wird übersprungen. Im folgenden Beispiel wird die Analyse der Silver-Table-Query übersprungen, bis die `from_json`-Funktion in der Bronze-Query mindestens einmal erfolgreich gelaufen ist und das Schema inferiert hat:

```sql
CREATE STREAMING TABLE bronze AS
  SELECT
    from_json(value, NULL, map('schemaLocationKey', 'nycTaxi')) jsonCol
  FROM STREAM READ_FILES('/databricks-datasets/nyctaxi/sample/json/', format => 'text')

CREATE STREAMING TABLE silver AS
  SELECT jsonCol.VendorID, jsonCol.total_amount
  FROM bronze
```

Werden die `from_json`-Funktion und die davon inferierten Felder in derselben Query referenziert, kann die Analyse fehlschlagen:

```sql
CREATE STREAMING TABLE bronze AS
  SELECT
    from_json(value, NULL, map('schemaLocationKey', 'nycTaxi')) jsonCol
  FROM STREAM READ_FILES('/databricks-datasets/nyctaxi/sample/json/', format => 'text')
  WHERE jsonCol.total_amount > 100.0
```

Beheben lässt sich das, indem die Referenz auf das `from_json`-Feld in eine nachgelagerte Query verschoben wird (wie im Bronze/Silver-Beispiel oben), oder indem `schemaHints` angegeben werden, die die referenzierten `from_json`-Felder enthalten:

```sql
CREATE STREAMING TABLE bronze AS
  SELECT
    from_json(value, NULL, map('schemaLocationKey', 'nycTaxi', 'schemaHints', 'total_amount DOUBLE')) jsonCol
  FROM STREAM READ_FILES('/databricks-datasets/nyctaxi/sample/json/', format => 'text')
  WHERE jsonCol.total_amount > 100.0
```

## <a id="beispiele">10. Beispiele: automatische Inferenz und Evolution</a>

**Streaming Table aus Cloud-Objektspeicher**, über `read_files`-Syntax:

```sql
CREATE STREAMING TABLE bronze AS
  SELECT
    from_json(value, NULL, map('schemaLocationKey', 'nycTaxi')) jsonCol
  FROM STREAM READ_FILES('/databricks-datasets/nyctaxi/sample/json/', format => 'text')
```

```python
@dp.table(comment="from_json autoloader example")
def bronze():
  return (
    spark.readStream
         .format("cloudFiles")
         .option("cloudFiles.format", "text")
         .load("/databricks-datasets/nyctaxi/sample/json/")
         .select(from_json(col("value"), None, {"schemaLocationKey": "nycTaxi"}).alias("jsonCol"))
)
```

**Streaming Table aus Kafka**, über `read_kafka`-Syntax:

```sql
CREATE STREAMING TABLE bronze AS
  SELECT
    value,
    from_json(value, NULL, map('schemaLocationKey', 'keyX')) jsonCol,
  FROM READ_KAFKA(
    bootstrapSevers => '<server:ip>',
    subscribe => 'events',
    "startingOffsets", "latest"
)
```

```python
@dp.table(comment="from_json kafka example")
def bronze():
  return (
    spark.readStream
         .format("kafka")
         .option("kafka.bootstrap.servers", "<server:ip>")
         .option("subscribe", "<topic>")
         .option("startingOffsets", "latest")
         .load()
         .select(col("value"), from_json(col("value"), None, {"schemaLocationKey": "keyX"}).alias("jsonCol"))
)
```

## <a id="vs-parse-json">11. `from_json` vs. `parse_json`</a>

`parse_json` gibt einen `VARIANT`-Wert aus dem JSON-String zurück. `VARIANT` bietet eine flexible und effiziente Möglichkeit, semi-strukturierte Daten zu speichern — dabei werden Schema-Inferenz und -Evolution durch den Verzicht auf strikte Typen umgangen. Soll dagegen zur Schreibzeit ein Schema erzwungen werden, ist `from_json` die passendere Wahl.

| Funktion | Anwendungsfälle | Verfügbarkeit |
|---|---|---|
| `from_json` | Schema-Evolution mit `from_json` behält das Schema bei. Hilfreich, wenn: das Datenschema erzwungen werden soll (z. B. jede Schema-Änderung vor Persistierung überprüfen); Speicher optimiert und niedrige Query-Latenz/-Kosten benötigt werden; bei Typkonflikten fehlgeschlagen werden soll; Teilergebnisse aus beschädigten JSON-Datensätzen extrahiert und der fehlerhafte Datensatz in der `_corrupt_record`-Spalte gespeichert werden soll (VARIANT-Ingestion gibt dagegen bei ungültigem JSON einen Fehler zurück). | Nur mit Schema-Inferenz/-Evolution in Pipelines verfügbar |
| `parse_json` | VARIANT eignet sich besonders für Daten, die nicht schematisiert werden müssen. Etwa: die Daten sollen wegen ihrer Flexibilität semi-strukturiert bleiben; das Schema ändert sich zu schnell, um es ohne häufige Stream-Fehlschläge/-Neustarts in ein Schema zu zwingen; bei Typkonflikten soll nicht fehlgeschlagen werden (VARIANT-Ingestion gelingt bei gültigen JSON-Datensätzen immer, auch bei Typkonflikten); Nutzer wollen sich nicht mit der Rescued-Data-Spalte für nicht-konforme Felder befassen. | In und außerhalb von Pipelines verfügbar |

## <a id="faq">12. FAQ</a>

**Lässt sich die `from_json`-Schema-Inferenz-/-Evolution-Syntax außerhalb von Pipelines nutzen?** Nein.

**Wie greift man auf das von `from_json` inferierte Schema zu?** Über das Schema der Ziel-Streaming-Table.

**Lässt sich `from_json` sowohl ein Schema übergeben als auch Evolution nutzen?** Nein — es lassen sich jedoch Schema Hints angeben, um einzelne oder alle von `from_json` inferierten Felder zu überschreiben.

**Was passiert mit dem Schema bei einem vollständigen Full Refresh der Tabelle?** Die mit der Tabelle verknüpften Schema-Speicherorte werden geleert, das Schema wird von Grund auf neu inferiert.

---

## <a id="quellen">13. Quellen</a>

- Infer and evolve the schema using from_json in pipelines (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/ldp/from-json-schema-evolution
- Infer and evolve the schema using from_json in pipelines (AWS): https://docs.databricks.com/aws/en/ldp/from-json-schema-evolution
- Verwandte Dateien in diesem Projekt: Ordner `Lakeflow Connect/Lakeflow Connect Standard Connectors/Working with Files/06 Auto Loader/` (Auto-Loader-eigene Schema-Evolution-Modi, mit denen `from_json`s Modi laut Doku konsistent sind)

**Stand:** 2026-08-19.
