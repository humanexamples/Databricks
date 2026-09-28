# Structured Streaming Checkpoints — Referenz

Dieses Dokument beschreibt Checkpoints bei Structured Streaming: was ein Checkpoint-Verzeichnis enthält, wie Checkpointing aktiviert wird, welche Änderungen an einer Streaming-Query zwischen Neustarts von demselben Checkpoint aus erlaubt sind, und wie Streaming-Quellen per "Source Evolution" umbenannt, hinzugefügt oder entfernt werden können. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/checkpoints`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte (die GCP-Originalseite lieferte über WebFetch nur eine gekürzte Fassung).

## Abschnittsübersicht

1. [Was ein Checkpoint-Verzeichnis enthält](#inhalt)
2. [Checkpointing für Structured-Streaming-Queries aktivieren](#aktivieren)
3. [Wiederherstellung nach Änderungen an einer Structured-Streaming-Query](#wiederherstellung)
4. [Arten von Änderungen an Structured-Streaming-Queries](#aenderungsarten)
5. [Streaming-Quellen mit Source Evolution ändern](#source-evolution)
6. [Quellen](#quellen)

---

## <a id="inhalt">1. Was ein Checkpoint-Verzeichnis enthält</a>

Checkpoints und Write-Ahead-Logs arbeiten zusammen, um Verarbeitungsgarantien für Structured-Streaming-Workloads bereitzustellen. Der Checkpoint verfolgt die Informationen, die die Query identifizieren, einschließlich Zustandsinformationen und verarbeiteter Datensätze. Wenn die Dateien in einem Checkpoint-Verzeichnis gelöscht werden oder zu einem neuen Checkpoint-Speicherort gewechselt wird, beginnt der nächste Lauf der Query von vorn.

Ein Checkpoint-Verzeichnis enthält Folgendes:

- **Offsets**: Die in jedem Micro-Batch verarbeiteten Quell-Offsets. Dies ermöglicht es der Query, genau dort fortzusetzen, wo sie aufgehört hat, ohne Daten erneut zu verarbeiten.
- **Commits**: Ein Protokoll darüber, welche Micro-Batches an die Senke (Sink) committet wurden, was Exactly-once-Semantik ermöglicht.
- **State**: Für zustandsbehaftete Queries (Aggregationen, Stream-Stream-Joins, Deduplizierung und benutzerdefinierte zustandsbehaftete Operatoren wie `transformWithState`) speichert der Checkpoint Metadaten über den zustandsbehafteten Operator, das State-Schema und den vom State-Store-Provider verwalteten, gecheckpointeten Inhalt des State Stores.
- **Metadata**: Die eindeutige Query-ID, mit der die Query identifiziert wird. Konfigurationseinstellungen werden als Teil des Offset-Logs gespeichert.

Jede Query muss einen anderen Checkpoint-Speicherort haben. Mehrere Queries sollten niemals denselben Speicherort teilen.

**Hinweis:** Dieser Artikel behandelt Structured-Streaming-Checkpoints für Streaming-Queries. Für Informationen zur Verwendung von `DataFrame.checkpoint()` mit Unity-Catalog-Volumes zum Abschneiden von Ausführungsplänen nicht-streamender DataFrames siehe die Dokumentation zu DataFrame-Checkpoints in Volumes.

## <a id="aktivieren">2. Checkpointing für Structured-Streaming-Queries aktivieren</a>

Die Option `checkpointLocation` muss angegeben werden, bevor eine Streaming-Query ausgeführt wird, wie im folgenden Beispiel:

**Python**

```python
(df.writeStream
  .option("checkpointLocation", "/Volumes/catalog/schema/volume/path")
  .toTable("catalog.schema.table")
)
```

**Hinweis:** Einige Senken, wie z. B. die Ausgabe von `display()` in Notebooks und die `memory`-Senke, generieren automatisch einen temporären Checkpoint-Speicherort, wenn diese Option weggelassen wird. Diese temporären Checkpoint-Speicherorte gewährleisten weder Fehlertoleranz noch Datenkonsistenz-Garantien und werden möglicherweise nicht ordnungsgemäß bereinigt. Databricks empfiehlt, für diese Senken immer einen Checkpoint-Speicherort anzugeben.

## <a id="wiederherstellung">3. Wiederherstellung nach Änderungen an einer Structured-Streaming-Query</a>

Es gibt Einschränkungen bezüglich der Änderungen an einer Streaming-Query, die zwischen Neustarts von demselben Checkpoint-Speicherort aus erlaubt sind.

Änderungen, die im Allgemeinen einen neuen Checkpoint erfordern, umfassen: die Anzahl oder den Typ der Eingabequellen, abonnierte Kafka-Topics oder Auto-Loader-Pfade, Typen zustandsbehafteter Operationen, das State-Schema und den Typ der Ausgabesenke.

Änderungen, die im Allgemeinen sicher sind, umfassen: das Hinzufügen oder Entfernen von Filtern, das Ändern von Rate Limits, von Trigger-Intervallen sowie das Aktualisieren der Logik benutzerdefinierter Funktionen innerhalb von `mapGroupsWithState` (wobei sich die Semantik ändern kann).

Der folgende Abschnitt beschreibt Änderungen, die entweder nicht erlaubt sind oder deren Auswirkung nicht wohldefiniert ist, wobei gilt:

- Der Begriff *erlaubt* bedeutet, dass die angegebene Änderung durchgeführt werden kann, wobei aber davon abhängt, ob die Semantik ihrer Auswirkung wohldefiniert ist — abhängig von der Query und der Änderung.
- Der Begriff *nicht erlaubt* bedeutet, dass die angegebene Änderung nicht vorgenommen werden sollte, da die neu gestartete Query wahrscheinlich mit unvorhersehbaren Fehlern fehlschlägt.
- `sdf` repräsentiert ein Streaming-DataFrame/-Dataset, das mit `sparkSession.readStream` erzeugt wurde.

## <a id="aenderungsarten">4. Arten von Änderungen an Structured-Streaming-Queries</a>

- **Änderungen der Anzahl oder des Typs von Eingabequellen**: Dies ist standardmäßig nicht erlaubt, da Structured Streaming Quellen anhand ihrer Position im Query-Plan identifiziert. Wird Source Naming aktiviert, können bestehende Quellen umgeordnet und neue Quellen hinzugefügt werden, ohne von einem frischen Checkpoint zu starten. Siehe [Streaming-Quellen mit Source Evolution ändern](#source-evolution).

- **Änderungen der Parameter von Eingabequellen**: Ob dies erlaubt ist und ob die Semantik der Änderung wohldefiniert ist, hängt von der Quelle und der Query ab, einschließlich Admission Controls wie `maxFilesPerTrigger` oder `maxOffsetsPerTrigger`. Hier ein paar Beispiele:

  - Hinzufügen, Löschen und Ändern von Rate Limits ist erlaubt, z. B. von

    ```scala
    spark.readStream.format("kafka").option("subscribe", "article")
    ```

    zu

    ```scala
    spark.readStream.format("kafka").option("subscribe", "article").option("maxOffsetsPerTrigger", ...)
    ```

    Details siehe die Doku-Seite "Configure Structured Streaming batch size on Azure Databricks" (siehe `Batch-Groesse.md` in diesem Verzeichnis).
  - Änderungen an abonnierten Articles und Dateien sind im Allgemeinen nicht erlaubt, da die Ergebnisse unvorhersehbar sind: `spark.readStream.format("kafka").option("subscribe", "article")` zu `spark.readStream.format("kafka").option("subscribe", "newarticle")`

- **Änderungen des Trigger-Intervalls**: Es kann zwischen inkrementellen Batches und Zeitintervallen gewechselt werden. Siehe "Trigger-Intervalle zwischen Läufen ändern" (siehe `Trigger.md` in diesem Verzeichnis).

- **Änderungen des Typs der Ausgabesenke**: Änderungen zwischen ein paar bestimmten Kombinationen von Senken sind erlaubt. Dies muss von Fall zu Fall überprüft werden. Hier ein paar Beispiele.

  - File-Senke zu Kafka-Senke ist erlaubt. Kafka sieht nur die neuen Daten.
  - Kafka-Senke zu File-Senke ist nicht erlaubt.
  - Kafka-Senke zu Foreach geändert, oder umgekehrt, ist erlaubt.

- **Änderungen der Parameter der Ausgabesenke**: Ob dies erlaubt ist und ob die Semantik der Änderung wohldefiniert ist, hängt von der Senke und der Query ab. Hier ein paar Beispiele.

  - Änderungen am Ausgabeverzeichnis einer File-Senke sind nicht erlaubt: `sdf.writeStream.format("parquet").option("path", "/somePath")` zu `sdf.writeStream.format("parquet").option("path", "/anotherPath")`
  - Änderungen am Ausgabe-Topic sind erlaubt: `sdf.writeStream.format("kafka").option("topic", "topic1")` zu `sdf.writeStream.format("kafka").option("topic", "topic2")`
  - Änderungen an der benutzerdefinierten Foreach-Senke (also am `ForeachWriter`-Code) sind erlaubt, wobei die Semantik der Änderung vom Code abhängt.

- **Änderungen in Projektions-/Filter-/Map-artigen Operationen**: Manche Fälle sind erlaubt. Zum Beispiel:

  - Hinzufügen/Löschen von Filtern ist erlaubt: `sdf.selectExpr("a")` zu `sdf.where(...).selectExpr("a").filter(...)`.
  - Änderungen an Projektionen mit gleichem Ausgabeschema sind erlaubt: `sdf.selectExpr("stringColumn AS json").writeStream` zu `sdf.select(to_json(...).as("json")).writeStream`.
  - Änderungen an Projektionen mit unterschiedlichem Ausgabeschema sind bedingt erlaubt: `sdf.selectExpr("a").writeStream` zu `sdf.selectExpr("b").writeStream` ist nur erlaubt, wenn die Ausgabesenke die Schemaänderung von `"a"` zu `"b"` zulässt.

- **Änderungen an zustandsbehafteten Operationen**: Manche Operationen in Streaming-Queries müssen Zustandsdaten pflegen, um das Ergebnis kontinuierlich zu aktualisieren. Structured Streaming checkpointet die Zustandsdaten automatisch in fehlertolerantem Storage (z. B. DBFS, Azure Blob Storage) und stellt sie nach einem Neustart wieder her. Dies setzt jedoch voraus, dass das Schema der Zustandsdaten über Neustarts hinweg gleich bleibt. Das bedeutet: *Jegliche Änderungen (also Hinzufügungen, Löschungen oder Schemaänderungen) an den zustandsbehafteten Operationen einer Streaming-Query sind zwischen Neustarts nicht erlaubt.* Hier die Liste der zustandsbehafteten Operationen, deren Schema zwischen Neustarts nicht geändert werden sollte, um die Zustandswiederherstellung sicherzustellen:

  - **Streaming-Aggregation**: Zum Beispiel `sdf.groupBy("a").agg(...)`. Jede Änderung der Anzahl oder des Typs von Gruppierungsschlüsseln oder Aggregaten ist nicht erlaubt.
  - **Streaming-Deduplizierung**: Zum Beispiel `sdf.dropDuplicates("a")`. Jede Änderung der Anzahl oder des Typs von Gruppierungsschlüsseln oder Aggregaten ist nicht erlaubt.
  - **Stream-Stream-Join**: Zum Beispiel `sdf1.join(sdf2, ...)` (d. h. beide Eingaben werden mit `sparkSession.readStream` erzeugt). Änderungen am Schema oder an den Equi-Join-Spalten sind nicht erlaubt. Änderungen am Join-Typ (Outer oder Inner) sind nicht erlaubt. Andere Änderungen an der Join-Bedingung sind unscharf definiert.
  - **Beliebige zustandsbehaftete Operation**: Zum Beispiel `sdf.groupByKey(...).mapGroupsWithState(...)` oder `sdf.groupByKey(...).flatMapGroupsWithState(...)`. Jede Änderung am Schema des benutzerdefinierten Zustands und am Typ des Timeouts ist nicht erlaubt. Änderungen innerhalb der benutzerdefinierten Zustands-Mapping-Funktion sind erlaubt, wobei der semantische Effekt der Änderung von der benutzerdefinierten Logik abhängt. Wer wirklich Änderungen am State-Schema unterstützen möchte, kann komplexe Zustandsdatenstrukturen explizit mittels eines Encoding-/Decoding-Schemas, das Schema-Migration unterstützt, in Bytes kodieren/dekodieren. Wird der Zustand z. B. als Avro-kodierte Bytes gespeichert, kann das Avro-State-Schema zwischen Query-Neustarts geändert werden, da dies den binären Zustand wiederherstellt.

**Wichtig:** Die zustandsbehafteten Operatoren `dropDuplicates()` und `dropDuplicatesWithinWatermark()` können beim Neustart aufgrund einer Prüfung der State-Schema-Kompatibilität fehlschlagen, wenn zwischen Compute-Access-Modes gewechselt wird.

Der Wechsel zwischen den Access Modes "dedicated" und "no isolation" ist erlaubt. Der Wechsel zwischen "standard" und "serverless" ist erlaubt. Es sollte nicht zwischen anderen Kombinationen von Access Modes gewechselt werden.

Um diesen Fehler zu vermeiden, sollte der Compute-Access-Mode für Streaming-Queries, die diese Operatoren enthalten, nicht geändert werden.

## <a id="source-evolution">5. Streaming-Quellen mit Source Evolution ändern</a>

Standardmäßig identifiziert Structured Streaming Quellen anhand ihrer Position im Query-Plan, also z. B. `0`, `1`, `2` usw. Jede Änderung an der Anzahl oder Reihenfolge der Eingabequellen bricht die Checkpoint-Kompatibilität und erfordert einen frischen Checkpoint. Source Evolution ermöglicht es, jeder Streaming-Quelle einen stabilen, benutzerdefinierten Namen zuzuweisen, sodass Quellen einer Query umgeordnet, hinzugefügt oder entfernt werden können, ohne den Checkpoint-Zustand zu verlieren.

Source Evolution erfordert Databricks Runtime 18.2 oder höher.

### Erforderliche Konfiguration

Um Source Evolution zu aktivieren, muss folgende Spark-Konfiguration gesetzt werden:

- `spark.sql.streaming.queryEvolution.enableSourceEvolution`: Wenn `true`, müssen alle Streaming-Quellen der Query explizit über die `.name()`-API benannt werden. Standardwert ist `false`.

Die Konfiguration muss gesetzt werden, bevor die Streaming-Query definiert wird:

```python
spark.conf.set("spark.sql.streaming.queryEvolution.enableSourceEvolution", "true")
```

### Benennungsregeln

- Namen dürfen nur alphanumerische Zeichen und Unterstriche enthalten (`[a-zA-Z0-9_]+`).
- Jeder Quellenname muss innerhalb einer Query eindeutig sein.
- Wenn Source Evolution aktiviert ist, muss jede Streaming-Quelle einen Namen haben. Unbenannte Quellen verursachen einen `UNNAMED_STREAMING_SOURCES_WITH_ENFORCEMENT`-Fehler.

### Quellen umordnen, hinzufügen und entfernen

Folgende Änderungen sind über Query-Neustarts hinweg mit demselben Checkpoint sicher:

- **Quellen umordnen**: Die Query wird mit einer anderen Reihenfolge der Quellen neu gestartet. Jede Quelle setzt anhand ihres Namens beim letzten committeten Offset fort und ändert den Checkpoint-Zustand nicht.
- **Neue Quellen hinzufügen**: Die Query wird mit einer neuen Quelle neu gestartet. Die neue Quelle verarbeitet von Beginn an, bestehende Quellen setzen bei ihren letzten Offsets fort.
- **Quellen entfernen**: Die Query wird ohne die Quelle neu gestartet. Die Quelle wird dauerhaft aus dem Checkpoint entfernt. Eine entfernte Quelle kann nicht mit demselben Namen erneut hinzugefügt werden.

### Beispiel

`.name()` wird auf `DataStreamReader` verwendet, bevor `.load()` oder `.table()` aufgerufen wird:

**Python**

```python
orders_us = (spark.readStream
  .name("orders_us")
  .table("catalog.schema.orders_us")
)

orders_eu = (spark.readStream
  .name("orders_eu")
  .table("catalog.schema.orders_eu")
)

all_orders = orders_us.union(orders_eu)
```

### Einschränkungen

- Source Naming erfordert einen frischen Checkpoint. Source Evolution kann nicht auf einem bestehenden Checkpoint aktiviert werden, der ohne Source Evolution erstellt wurde.
- Source Evolution ist eine unumkehrbare Änderung für Checkpoints. Nachdem Source Evolution für eine Query aktiviert wurde, kann sie nicht wieder deaktiviert werden, während derselbe Checkpoint weiterverwendet wird.
- Quellennamen sind dauerhaft. Um eine Quelle umzubenennen, muss sie entfernt und mit einem neuen Namen wieder hinzugefügt werden. Die umbenannte Quelle verarbeitet von Beginn an.

---

## <a id="quellen">6. Quellen</a>

- Structured Streaming checkpoints (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/checkpoints
- Structured Streaming checkpoints (Azure-Spiegelseite, vollständig als Rohtext abgerufen und für diese Zusammenfassung verwendet): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/checkpoints

**Stand:** 2026-08-22; Codebeispiele am 2026-09-28 gegen die AWS-Doku abgeglichen und ergänzt.
