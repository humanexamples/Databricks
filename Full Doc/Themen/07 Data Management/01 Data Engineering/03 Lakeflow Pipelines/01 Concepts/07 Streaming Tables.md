# Streaming Tables

Referenz zum Konzept "Streaming Table" in Lakeflow-Pipelines, basierend auf `https://docs.databricks.com/aws/en/ldp/concepts/streaming-tables` (AWS) und der inhaltsgleichen GCP-Fassung `https://docs.databricks.com/gcp/en/ldp/concepts/streaming-tables`.

## Abschnittsübersicht

1. [Was ist eine Streaming Table?](#definition)
2. [Primärer Anwendungsfall: Dateneingang](#dateneingang)
3. [Anwendungsfall: Low-Latency-Streaming](#low-latency)
4. [Eigentümerschaft und Ownership](#ownership)
5. [Wichtige Einschränkungen](#einschraenkungen)
6. [Quellen](#quellen)

---

## <a id="definition">1. Was ist eine Streaming Table?</a>

Eine Streaming Table ist "eine Delta-Tabelle mit zusätzlicher Unterstützung für Streaming- bzw. inkrementelle Datenverarbeitung". Sie kann als Target von Flows innerhalb einer Pipeline dienen.

## <a id="dateneingang">2. Primärer Anwendungsfall: Dateneingang</a>

Für den Dateneingang (Ingestion) verarbeitet eine Streaming Table "jede eingehende Zeile … nur einmal, was die überwiegende Mehrheit der Ingestion-Workloads abbildet". Sie eignet sich damit besonders für die Verarbeitung großer Mengen an **Append-only**-Daten. Unterstützt werden:

- Cloud-Speicher über **Auto Loader**
- Message-Busse: **Apache Kafka**, **Azure Event Hubs**, **Google Pub/Sub**

> **Wichtig:** Für Quelldaten, die sich über die Zeit **ändern** (Updates oder Deletes), sollte statt einfachem Anhängen **`AUTO CDC`** verwendet werden.

### Wie Append-only-Verarbeitung funktioniert

*"A row that has already been appended to a streaming table will not be re-queried with later updates to the pipeline."* Query-Änderungen wirken sich nur auf **neu** eingehende Zeilen aus — bestehende Zeilen behalten ihren ursprünglich verarbeiteten Zustand, sofern kein Full Refresh ausgelöst wird.

## <a id="low-latency">3. Anwendungsfall: Low-Latency-Streaming</a>

Streaming Tables ermöglichen die Verarbeitung von "Zeilen und Zeitfenstern" mit niedriger Latenz und nutzen dafür Checkpoint-Management. Sie benötigen entweder **natürlich begrenzte** (naturally bounded) Streams **oder** Streams, die durch **Watermarks** begrenzt sind:

- **Natürlich begrenzt (naturally bounded):** Streaming-Quellen mit definiertem Anfang und Ende, z. B. das Lesen endlicher Dateiverzeichnisse.
- **Watermark-begrenzt:** Ein Mechanismus, der festlegt, wie lange das System auf verspätete Events wartet, bevor ein Zeitfenster als abgeschlossen gilt.

### Real-Time Mode

Für operative Workloads mit minimaler Latenz können Pipelines im **Real-Time Mode** laufen und Datensätze mit *"sub-second, end-to-end latency"* verarbeiten.

## <a id="ownership">4. Eigentümerschaft und Ownership</a>

Eine Streaming Table wird ausschließlich von einer einzigen Pipeline besessen und aktualisiert. Andere Pipelines können sie nicht verändern. Mehrere Flows können jedoch an dieselbe Streaming Table anhängen (append). Databricks legt zur Unterstützung der Verarbeitung zusätzlich interne Systemtabellen an.

## <a id="einschraenkungen">5. Wichtige Einschränkungen</a>

Die GCP-Fassung der Doku listet **fünf** wesentliche Einschränkungen von Streaming Tables (die AWS-Fassung nur die ersten vier):

1. **Begrenzte Evolution ("limited evolution"):** Query-Änderungen wirken sich nur auf neu verarbeitete Zeilen aus, sofern kein Full Refresh durchgeführt wird. Beispiel: Wird `UPPER()` zur Query hinzugefügt, *"only rows processed after the change will be in uppercase"*.
2. **State-Management-Anforderungen:** Low-Latency-Anforderungen erfordern natürlich begrenzte oder watermark-begrenzte Streams, um Fehlschläge durch Speicherdruck (memory pressure) zu vermeiden.
3. **Joins werden bei Änderungen der Dimensionstabellen nicht neu berechnet** — unterstützt "fast-but-wrong"-Szenarien; im Unterschied zu Materialized Views, die für Korrektheit automatisch neu berechnen.
4. **Keine `CLONE`-Unterstützung:** *"Streaming tables cannot be used as the source or target of a deep or shallow clone."*
5. **`REFRESH`-Privileg erforderlich:** Nicht-Admin-Nutzer benötigen `REFRESH`-Privilegien auf der Streaming Table, um die dahinterliegenden Pipelines einsehen zu können — über die üblichen Pipeline-Berechtigungen hinaus.

Streaming Tables eignen sich also hervorragend für Append-only-Workloads; werden dagegen stets korrekte, vollständig aktuelle Ergebnisse benötigt (etwa bei Joins gegen sich ändernde Dimensionen), sind Materialized Views die passendere Wahl (siehe "Materialized Views.md").

Eine vollständige Entscheidungshilfe View vs. Materialized View vs. Streaming Table (inkl. Diagramm) steht in `Views.md` in diesem Ordner.

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/concepts/streaming-tables
- https://docs.databricks.com/gcp/en/ldp/concepts/streaming-tables (fünfte Einschränkung, Real-Time Mode, bounded/watermark-Details, `AUTO CDC`-Hinweis)
- What are Lakeflow pipelines? — Concepts-Übersicht: https://learn.microsoft.com/en-us/azure/databricks/ldp/concepts/

**Verwandte Doku-Ressourcen:** Load data in pipelines · Full refresh for streaming tables · Change data capture and snapshots · Real-time mode in Lakeflow pipelines · Optimize stateful processing with watermarks · Materialized views comparison · Stream-static joins examples
