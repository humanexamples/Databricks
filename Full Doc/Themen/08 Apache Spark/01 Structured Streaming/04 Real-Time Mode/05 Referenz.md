# Real-Time-Mode-Referenz — Referenz

Dieses Dokument ist die Referenzseite zu Real-Time Mode: unterstützte Sprachen, Compute-Typen, Ausführungsmodi, Quellen/Senken, Operatoren sowie besondere Verhaltensweisen (u. a. `transformWithState` und Python-UDFs) in Real-Time Mode. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/reference`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte.

## Abschnittsübersicht

1. [Unterstützte Sprachen](#sprachen)
2. [Compute-Typen](#compute-typen)
3. [Ausführungsmodi](#ausfuehrungsmodi)
4. [Quellen und Senken](#quellen-senken)
5. [Operatoren](#operatoren)
6. [Besondere Überlegungen](#besondere-ueberlegungen)
7. [Quellen (Dokumentation)](#quellen)

---

## <a id="sprachen">1. Unterstützte Sprachen</a>

Real-Time Mode unterstützt Scala, Java und Python.

## <a id="compute-typen">2. Compute-Typen</a>

Real-Time Mode unterstützt folgende Compute-Typen:

| Compute-Typ | Unterstützt |
| --- | --- |
| Dedicated (früher: Single User) | ✓ |
| Standard (früher: Shared) | ✓ (nur Python) |
| Lakeflow Pipelines auf Classic | Nicht als Structured Streaming unterstützt. Über Pipeline-Konfiguration unterstützt (siehe "Use real-time mode in Lakeflow pipelines"). |
| Lakeflow Pipelines auf Serverless | Nicht als Structured Streaming unterstützt. Über Pipeline-Konfiguration unterstützt (siehe "Use real-time mode in Lakeflow pipelines"). |
| Serverless | Nicht unterstützt |

Für latenzsensitive Workloads mit UDFs empfiehlt Databricks, Dedicated Access Mode zu verwenden (siehe Abschnitt "Table functions").

## <a id="ausfuehrungsmodi">3. Ausführungsmodi</a>

Real-Time Mode unterstützt ausschließlich den Update-Modus:

| Ausführungsmodus | Unterstützt |
| --- | --- |
| Update-Modus | ✓ |
| Append-Modus | Nicht unterstützt |
| Complete-Modus | Nicht unterstützt |

## <a id="quellen-senken">4. Quellen und Senken</a>

Real-Time Mode unterstützt folgende Quellen und Senken:

| Quelle oder Senke | Als Quelle | Als Senke |
| --- | --- | --- |
| Apache Kafka | ✓ | ✓ |
| Event Hubs (über Kafka-Connector) | ✓ | ✓ |
| Kinesis | ✓ (EFO-Modus empfohlen) | Nicht unterstützt |
| AWS MSK | ✓ | Nicht unterstützt |
| Delta | Nicht unterstützt | Nicht unterstützt |
| Google Pub/Sub | Nicht unterstützt | Nicht unterstützt |
| Apache Pulsar | Nicht unterstützt | Nicht unterstützt |
| Beliebige Senken (mittels `forEachWriter`) | Nicht zutreffend | ✓ |

## <a id="operatoren">5. Operatoren</a>

Real-Time Mode unterstützt die meisten Structured-Streaming-Operatoren.

### Zustandslose Operationen

| Operator | Unterstützt |
| --- | --- |
| Selection | ✓ |
| Projection | ✓ |
| `mapPartitions` | Nicht unterstützt (siehe Einschränkung `mapPartitions` in der Datei `Einschraenkungen.md`) |
| Union | ✓ (mit einigen Einschränkungen, siehe Union-Einschränkungen in der Datei `Einschraenkungen.md`) |

### UDFs

| Operator | Unterstützt |
| --- | --- |
| Scala UDF | ✓ (mit einigen Einschränkungen, siehe Einschränkung `mapPartitions`) |
| Python UDF | ✓ (mit einigen Einschränkungen) |

### Aggregation

| Funktion | Unterstützt |
| --- | --- |
| sum | ✓ |
| count | ✓ |
| max | ✓ |
| min | ✓ |
| avg | ✓ |
| Aggregationsfunktionen (Apache-Spark-Dokumentation) | ✓ |

### Windowing

| Operator | Unterstützt |
| --- | --- |
| Tumbling | ✓ |
| Sliding | ✓ |
| Session | Nicht unterstützt |

### Deduplizierung

| Operator | Unterstützt |
| --- | --- |
| dropDuplicates | ✓ |
| dropDuplicatesWithinWatermark | ✓ |

### Stream-to-Table-Join

| Operator | Unterstützt |
| --- | --- |
| Inner Join | ✓ |
| Outer Join | ✓ |
| Broadcast-Table-Join (Tabellengröße bis 10 MB) | ✓ |
| Table-Join (ohne Broadcast) | Nicht unterstützt |

### Stream-to-Stream-Join

| Operator | Unterstützt |
| --- | --- |
| Inner Join | ✓ (Databricks Runtime 18 LTS und höher, mit bestimmten Konfigurationen) |
| Outer Join | Nicht unterstützt |

**Hinweis:** Um Stream-to-Stream-Joins in Real-Time Mode zu verwenden, müssen zusätzliche Spark-Konfigurationen gesetzt werden. Weitere Informationen zu den Konfigurationen und den Anforderungen für das Ausführen mehrerer Streams finden sich im Abschnitt "Stream to stream joins" der Datei `Setup.md`.

### Beliebiger zustandsbehafteter Operator

| Operator | Unterstützt |
| --- | --- |
| (flat)MapGroupsWithState | Nicht unterstützt |
| transformWithState | ✓ (mit einigen Unterschieden) |

### Benutzerdefinierte Senken

| Senke | Unterstützt |
| --- | --- |
| forEach | ✓ |
| forEachBatch | Nicht unterstützt |

## <a id="besondere-ueberlegungen">6. Besondere Überlegungen</a>

Manche Operatoren und Features weisen in Real-Time Mode besondere Überlegungen oder Unterschiede auf.

### `transformWithState` in Real-Time Mode

Für den Bau benutzerdefinierter zustandsbehafteter Anwendungen unterstützt Databricks `transformWithState`, eine API in Apache Spark Structured Streaming (siehe "Build a custom stateful application with `transformWithState`" für weitere Informationen zur API und Code-Beispiele).

Die API verhält sich in Real-Time Mode jedoch anders als bei Micro-Batch-Queries.

- Real-Time Mode ruft die Methode `handleInputRows(key: String, inputRows: Iterator[T], timerValues: TimerValues)` für jede Zeile auf.
    - Der Iterator `inputRows` liefert einen einzelnen Wert. Micro-Batch-Modus ruft die Methode einmal pro Schlüssel auf, wobei der Iterator `inputRows` alle Werte für einen Schlüssel im Micro-Batch liefert.
    - Dieser Unterschied sollte beim Schreiben des Codes berücksichtigt werden.
- Event-Time-Timer werden in Real-Time Mode nicht unterstützt.
- `transformWithStateInPandas` wird in Real-Time Mode nicht unterstützt. Stattdessen sollte die zeilenbasierte `transformWithState`-API verwendet werden, die `Row`-Objekte anstelle von Pandas-DataFrames nutzt.
- In Real-Time Mode verzögert sich das Auslösen von Timern abhängig vom Dateneingang:
    - Ist ein Timer für 10:00:00 geplant, treffen aber keine Daten ein, löst der Timer nicht sofort aus.
    - Treffen Daten um 10:00:10 ein, löst der Timer mit 10 Sekunden Verzögerung aus.
    - Treffen keine Daten ein und der lang laufende Batch terminiert, löst der Timer vor Beendigung des Batches aus.

**Hinweis:** In Databricks Runtime 18.1 und darunter können bei Verwendung von `transformWithState` und Real-Time Mode für Python mit niedrigem Durchsatz (weniger als 5 Datensätze pro Sekunde) erhöhte Latenzen von bis zu einigen hundert Millisekunden auftreten. Databricks empfiehlt ein Upgrade auf Databricks Runtime 18.2 oder höher, um dies zu beheben.

### Python-UDFs in Real-Time Mode

Databricks unterstützt die Mehrheit der Python-User-Defined-Functions (UDFs) in Real-Time Mode:

#### Zustandslos

| UDF-Typ | Unterstützt |
| --- | --- |
| Python-Scalar-UDF | ✓ |
| Arrow-Scalar-UDF | ✓ |
| Pandas-Scalar-UDF | ✓ |
| Arrow-Funktion (`mapInArrow`) | ✓ |
| Pandas-Funktion (Map) | ✓ |

#### Zustandsbehaftete Gruppierung (UDAF)

| UDF-Typ | Unterstützt |
| --- | --- |
| `transformWithState` (nur `Row`-Interface) | ✓ |
| `transformWithStateInPandas` | Nicht unterstützt. Stattdessen die zeilenbasierte `transformWithState`-API verwenden, die `Row`-Objekte anstelle von Pandas-DataFrames nutzt (siehe Einschränkung `transformWithStateInPandas` in der Datei `Einschraenkungen.md`). |
| `applyInPandasWithState` | Nicht unterstützt |

#### Nicht-zustandsbehaftete Gruppierung (UDAF)

| UDF-Typ | Unterstützt |
| --- | --- |
| `apply` | Nicht unterstützt |
| `applyInArrow` | Nicht unterstützt |
| `applyInPandas` | Nicht unterstützt |

#### Table Functions

| UDF-Typ | Unterstützt |
| --- | --- |
| UDTF | Nicht unterstützt |
| UC UDF | Nicht unterstützt |

Bei der Verwendung von Python-UDFs in Real-Time Mode sind mehrere Punkte zu beachten:

- Um die Latenz zu minimieren, sollte die Arrow-Batch-Größe (`spark.sql.execution.arrow.maxRecordsPerBatch`) auf 1 gesetzt werden.
    - Trade-off: Diese Konfiguration optimiert auf Kosten des Durchsatzes für Latenz. Für die meisten Workloads wird diese Einstellung empfohlen.
    - Die Batch-Größe sollte nur erhöht werden, wenn ein höherer Durchsatz erforderlich ist, um das Eingabevolumen zu bewältigen — unter Inkaufnahme einer potenziell höheren Latenz.
- Pandas-UDFs und -Funktionen funktionieren mit einer Arrow-Batch-Größe von 1 nicht gut.
    - Bei Verwendung von Pandas-UDFs oder -Funktionen sollte die Arrow-Batch-Größe auf einen höheren Wert gesetzt werden (z. B. 100 oder mehr).
    - Dies bedeutet höhere Latenz. Databricks empfiehlt, nach Möglichkeit eine Arrow-UDF bzw. -Funktion zu verwenden.
- `transformWithStateInPandas` wird in Real-Time Mode nicht unterstützt. Stattdessen sollte die zeilenbasierte `transformWithState`-API verwendet werden, die `Row`-Objekte anstelle von Pandas-DataFrames nutzt (siehe Einschränkung `transformWithStateInPandas` sowie ein funktionierendes Python-Beispiel mit der zeilenbasierten API in der Datei `Beispiele.md`).
- Für latenzsensitive Workloads mit UDFs empfiehlt Databricks, Dedicated Access Mode zu verwenden. Im Standard Access Mode kann der Overhead durch Sicherheitsisolation die UDF-Performance verlangsamen.

---

## <a id="quellen">7. Quellen (Dokumentation)</a>

- Real-time mode reference (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/real-time/reference
- Real-time mode reference (Mirror, Azure, verifiziert/vollständig abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/reference
- Real-time mode reference (AWS): https://docs.databricks.com/aws/en/structured-streaming/real-time/reference

**Stand:** 2026-08-22.
