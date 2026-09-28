# Unity Catalog mit Structured Streaming — Referenz

Dieses Dokument beschreibt, wie Structured Streaming mit Unity Catalog zusammenspielt: welche Streaming-Funktionalität unterstützt wird, wie sich Unity-Catalog-Views als Stream lesen lassen (inklusive unterstützter Optionen und Operationen) sowie die geltenden Limitierungen. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/unity-catalog`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte (die GCP-Originalseite lieferte über WebFetch nur eine gekürzte/zusammengefasste Version).

## Abschnittsübersicht

1. [Welche Structured-Streaming-Funktionalität unterstützt Unity Catalog?](#unterstuetzung)
2. [Eine Unity-Catalog-View als Stream lesen](#view-als-stream)
3. [Unterstützte Streaming-Optionen](#optionen)
4. [Unterstützte Streaming-Operationen](#operationen)
5. [Limitierungen](#limitierungen)
6. [Quellen](#quellen)

---

## <a id="unterstuetzung">1. Welche Structured-Streaming-Funktionalität unterstützt Unity Catalog?</a>

Diese Seite zeigt, wie Structured Streaming zusammen mit Unity Catalog genutzt wird, um die Data Governance für inkrementelle und Streaming-Workloads auf Databricks zu verwalten.

Unity Catalog fügt keine expliziten Beschränkungen für die auf Databricks verfügbaren Structured-Streaming-Quellen und -Senken hinzu.

Mit Unity Catalog und Structured Streaming können Sie:

- Daten sowohl aus verwalteten (managed) als auch aus externen Tabellen streamen. Siehe die separate Doku-Seite "Unity Catalog managed tables for Delta Lake and Apache Iceberg".
- Externe Speicherorte (external locations), die von Unity Catalog verwaltet werden, nutzen, um über Object-Storage-URIs mit Daten zu interagieren.
- In externe Tabellen entweder über Tabellennamen oder Dateipfade schreiben. Um mit verwalteten (managed) Tabellen zu interagieren, muss der Tabellenname verwendet werden.

Für Structured-Streaming-Checkpoints müssen Pfade in von Unity Catalog verwalteten externen Speicherorten verwendet werden. Weitere Informationen zur sicheren Anbindung von Storage an Unity Catalog finden Sie in der separaten Doku-Seite "Connect to cloud object storage using Unity Catalog".

## <a id="view-als-stream">2. Eine Unity-Catalog-View als Stream lesen</a>

Ab Databricks Runtime 14.3 LTS können Sie mit Structured Streaming aus Views lesen, die bei Unity Catalog registriert sind. Die zugrunde liegenden Tabellen müssen das Delta-Lake-Format verwenden. Weitere Einschränkungen siehe Abschnitt "Limitierungen".

Um eine View mit Structured Streaming zu lesen, verwenden Sie die Methode `.table()` mit dem Bezeichner der View:

```python
df = (spark.readStream
  .table("demoView")
)
```

Nutzer benötigen `SELECT`-Rechte auf die Ziel-View.

Wenn Sie die View-Definition ändern, um referenzierte Tabellen hinzuzufügen oder zu ändern, kann derselbe Streaming-Checkpoint nicht mehr verwendet werden.

## <a id="optionen">3. Unterstützte Streaming-Optionen</a>

Der Streaming-Reader wendet Optionen auf die Dateien und Metadaten der zugrunde liegenden Delta-Lake-Tabellen der angegebenen View an.

Folgende Optionen werden unterstützt:

- `maxFilesPerTrigger`
- `maxBytesPerTrigger`
- `ignoreDeletes`
- `skipChangeCommits`
- `withEventTimeOrder`
- `startingTimestamp`
- `startingVersion`

Lesevorgänge auf Views mit `UNION ALL` unterstützen die Optionen `withEventTimeOrder` und `startingVersion` nicht.

Wenn nicht unterstützte Optionen angegeben werden, etwa `readChangeFeed`, wirft Spark folgende Exception:

```console
AnalysisException: [UNSUPPORTED_STREAMING_OPTIONS_FOR_VIEW.UNSUPPORTED_OPTION] Unsupported for streaming a view. Reason: option <option> is not supported.
```

## <a id="operationen">4. Unterstützte Streaming-Operationen</a>

Folgende Operationen werden unterstützt:

| Operation | Beschreibung | Operator | Beispiel |
| --- | --- | --- | --- |
| Project | Steuert Berechtigungen auf Spaltenebene | `SELECT... FROM...` | `CREATE VIEW project_view AS SELECT id, value FROM source_table` |
| Filter | Steuert Berechtigungen auf Zeilenebene | `WHERE...` | `CREATE VIEW filter_view AS SELECT * FROM source_table WHERE value > 100` |
| Union all | Ergebnisse aus mehreren Tabellen | `UNION ALL` | `CREATE VIEW union_view AS SELECT id, value FROM source_table1 UNION ALL SELECT * FROM source_table2` |

Nicht unterstützt werden Aggregationen, Sortierungen sowie Table-Valued Functions wie `table_changes()`. Details zu Table-Valued Functions finden Sie in der separaten Doku-Seite "Table-valued function (TVF) invocation".

Wenn Sie aus einer View mit einer nicht unterstützten Operation streamen, wirft Spark folgende Exception:

```console
UnsupportedOperationException: [UNEXPECTED_OPERATOR_IN_STREAMING_VIEW] Unexpected operator <operator> in the CREATE VIEW statement as a streaming source. A streaming view query must consist only of SELECT, WHERE, and UNION ALL operations.
```

## <a id="limitierungen">5. Limitierungen</a>

- Der Continuous-Processing-Modus von Apache Spark wird nicht unterstützt. Siehe "Continuous Processing" im Spark Structured Streaming Programming Guide (https://spark.apache.org/docs/latest/streaming/performance-tips.html#continuous-processing).
- Eine Liste der Structured-Streaming-Funktionen, die je nach Compute-Zugriffsmodus unter Unity Catalog nicht unterstützt werden, finden Sie in den separaten Doku-Seiten "Streaming limitations" (Standard-Compute) und "Streaming and materialized view requirements on dedicated compute" (dediziertes Compute).
- Views als Streaming-Quelle unterliegen zusätzlichen Einschränkungen:
  - Es lässt sich nur aus Views streamen, die Delta-Lake-Tabellen abfragen. Andere Datenquellen werden nicht unterstützt.
  - Views müssen bei Unity Catalog registriert sein. Siehe die separate Doku-Seite "Create a view".
  - Streaming-Lesevorgänge auf Views unterstützen nicht alle Operationen oder Optionen. Siehe Abschnitte "Unterstützte Streaming-Operationen" und "Unterstützte Streaming-Optionen".
  - Wird der View eine neue Spalte hinzugefügt, bevor ein Stream das Schema der zugrunde liegenden Tabelle aktualisiert, schlägt der Stream mit einem Fehler wegen fehlender Spalte fehl. Die neue Spalte muss zunächst zur zugrunde liegenden Tabelle hinzugefügt werden; nachdem der Stream diese Tabellenversion verarbeitet hat, kann die Spalte anschließend zur View hinzugefügt werden.

---

## <a id="quellen">6. Quellen</a>

- Using Unity Catalog with Structured Streaming (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/unity-catalog
- Using Unity Catalog with Structured Streaming - Azure Databricks (Mirror, verifiziert/vollständig abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/unity-catalog
- Using Unity Catalog with Structured Streaming (AWS): https://docs.databricks.com/aws/en/structured-streaming/unity-catalog

**Stand:** 2026-08-22.
