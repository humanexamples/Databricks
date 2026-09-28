# PySpark Custom Data Sources (Python DataSource API)

Zusammenfassung der Seite `pyspark/datasources`. Verifiziert per `WebFetch` gegen die offizielle AWS-Dokumentation.

## Abschnittsübersicht
1. [Zweck](#zweck)
2. [Voraussetzungen](#voraussetzungen)
3. [Grundbausteine](#bausteine)
4. [Vollständiges Beispiel](#beispiel)
5. [Weitere Beispiele in der Dokumentation](#weitere)
6. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck</a>

Die Python-DataSource-API erlaubt es, Connectors zu Systemen ohne native Spark-Unterstützung — z. B. REST-APIs, Google Sheets oder proprietäre Dienste — **in reinem Python** zu bauen, ohne JVM-basierte Connector-Entwicklung.

## <a id="voraussetzungen">2. Voraussetzungen</a>

- **Databricks Runtime 15.4 LTS oder höher**, bzw. eine Serverless-Umgebung ab Version 2.
- Alle benutzerdefinierten Klassen (`DataSource`, `DataSourceReader`, `DataSourceWriter`, `DataSourceStreamReader`, `DataSourceStreamWriter`) und deren Methoden müssen **serialisierbar** sein — d. h., sie dürfen nur aus Dictionaries bzw. verschachtelten Dictionaries mit primitiven Typen bestehen.

## <a id="bausteine">3. Grundbausteine</a>

| Baustein | Beschreibung |
| --- | --- |
| `DataSource` (Basisklasse) | Muss `name` (Bezeichner) und `schema` bereitstellen. |
| `reader()` / `writer()` | Geben die passenden Reader-/Writer-Objekte für Batch-Operationen zurück. |
| `streamReader()` / `simpleStreamReader()` | Für Streaming-Lesevorgänge. |
| `streamWriter()` | Für Streaming-Schreibvorgänge. |
| `spark.dataSource.register(...)` | Registriert die eigene Datenquelle, bevor sie über `spark.read.format("name")` genutzt werden kann. |

## <a id="beispiel">4. Vollständiges Beispiel: Batch-Reader mit `faker`</a>

Das folgende Beispiel implementiert eine einfache Datenquelle `"fake"`, die mit der Bibliothek `faker` zufällige Testdaten erzeugt:

```python
from pyspark.sql.datasource import DataSource, DataSourceReader
from pyspark.sql.types import StructType

class FakeDataSourceReader(DataSourceReader):
    def __init__(self, schema, options):
        self.schema: StructType = schema
        self.options = options
    def read(self, partition):
        from faker import Faker
        fake = Faker()
        num_rows = int(self.options.get("numRows", 3))
        for _ in range(num_rows):
            row = []
            for field in self.schema.fields:
                value = getattr(fake, field.name)()
                row.append(value)
            yield tuple(row)

class FakeDataSource(DataSource):
    @classmethod
    def name(cls):
        return "fake"
    def schema(self):
        return "name string, date string, zipcode string, state string"
    def reader(self, schema: StructType):
        return FakeDataSourceReader(schema, self.options)

spark.dataSource.register(FakeDataSource)
spark.read.format("fake").load().show()
```

**Ablauf:**
1. `FakeDataSourceReader.read()` ist ein Generator, der für jede Partition Zeilen als Tupel liefert (`yield tuple(row)`).
2. `FakeDataSource.name()` legt den String fest, unter dem die Quelle über `.format(...)` ansprechbar ist.
3. `FakeDataSource.schema()` definiert das Schema als DDL-String.
4. `spark.dataSource.register(FakeDataSource)` macht die Klasse für die aktuelle `SparkSession` bekannt.
5. `spark.read.format("fake").load()` liest wie bei jeder eingebauten Quelle — Optionen (z. B. `numRows`) werden per `.option(...)` gereicht und sind in `self.options` verfügbar.

## <a id="weitere">5. Weitere Beispiele in der Dokumentation</a>

Die Originalseite enthält zusätzlich vollständige, lauffähige Beispiele für:

| Beispiel | Inhalt |
| --- | --- |
| Batch-Writer | Persistiert DataFrame-Partitionen als Dateien. |
| GitHub-Integration | Zeigt Unterstützung des `variant`-Datentyps. |
| Streaming-Reader/-Writer | Kontinuierliche Dateneingabe über `streamReader`/`streamWriter`. |
| BigQuery-Connector | Inkrementelles Checkpointing und parallele Verarbeitung. |
| API-Authentifizierung | Sichere Credential-Verwaltung über Unity-Catalog-HTTP-Connections. |

Für den genauen Code dieser weiteren Beispiele empfiehlt sich der direkte Blick in die Originaldokumentation (siehe Quellen).

---

## <a id="quellen">6. Quellen</a>

- PySpark Custom Data Sources: https://docs.databricks.com/aws/en/pyspark/datasources

**Stand:** 2026-08-25, per `WebFetch` verifiziert (Kernbeispiel wörtlich abgeglichen).
