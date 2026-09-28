# SQL-Entwicklung für Lakeflow Declarative Pipelines

## Abschnittsübersicht

1. [Grundlagen](#grundlagen)
2. [Materialized View mit SQL erstellen](#mv-erstellen)
3. [Streaming Table mit SQL erstellen](#st-erstellen)
4. [Daten aus Object Storage laden](#object-storage)
5. [Datenqualität mit Expectations prüfen](#expectations)
6. [Materialized Views und Streaming Tables der eigenen Pipeline abfragen](#abfragen)
7. [Private Tabelle definieren](#private-tabelle)
8. [Datensätze dauerhaft löschen](#loeschen)
9. [Werte parametrisieren](#parametrisieren)
10. [Einschränkungen](#einschraenkungen)
11. [Quellen](#quellen)

---

## <a id="grundlagen">1. Grundlagen</a>

Lakeflow Declarative Pipelines führen mehrere neue SQL-Schlüsselwörter und Funktionen ein, um Materialized Views und Streaming Tables in Pipelines zu definieren. Die SQL-Unterstützung für die Pipeline-Entwicklung baut auf den Grundlagen von Spark SQL auf und ergänzt Unterstützung für Structured-Streaming-Funktionalität.

Nutzer, die mit PySpark-DataFrames vertraut sind, bevorzugen unter Umständen die Pipeline-Entwicklung mit Python: Python unterstützt umfangreichere Tests und Operationen, die mit SQL schwer umzusetzen sind, etwa Metaprogrammierung.

SQL-Code, der Pipeline-Datasets erzeugt, verwendet die `CREATE OR REFRESH`-Syntax, um Materialized Views und Streaming Tables gegen Abfrageergebnisse zu definieren.

Das Schlüsselwort `STREAM` gibt an, ob die in einer `SELECT`-Klausel referenzierte Datenquelle mit Streaming-Semantik gelesen werden soll.

Lese- und Schreibvorgänge verwenden standardmäßig den in der Pipeline-Konfiguration angegebenen Katalog und Schema.

Pipeline-Quellcode unterscheidet sich grundlegend von SQL-Skripten: Lakeflow Declarative Pipelines werten alle Dataset-Definitionen über alle in einer Pipeline konfigurierten Quellcodedateien hinweg aus und bauen daraus einen Dataflow-Graphen, bevor irgendeine Abfrage ausgeführt wird. Die Reihenfolge der Abfragen in den Quelldateien bestimmt die Reihenfolge der Code-Auswertung, nicht die Reihenfolge der Abfrageausführung.

---

## <a id="mv-erstellen">2. Materialized View mit SQL erstellen</a>

Grundlegende Syntax zum Erstellen einer Materialized View mit SQL:

```sql
CREATE OR REFRESH MATERIALIZED VIEW basic_mv
AS SELECT * FROM samples.nyctaxi.trips;
```

---

## <a id="st-erstellen">3. Streaming Table mit SQL erstellen</a>

Grundlegende Syntax zum Erstellen einer Streaming Table mit SQL. Beim Lesen einer Quelle für eine Streaming Table zeigt das Schlüsselwort `STREAM` an, dass für die Quelle Streaming-Semantik verwendet werden soll. Das `STREAM`-Schlüsselwort wird beim Erstellen einer Materialized View nicht verwendet:

```sql
CREATE OR REFRESH STREAMING TABLE basic_st
AS SELECT * FROM STREAM samples.nyctaxi.trips;
```

Das `STREAM`-Schlüsselwort liest die Quelle mit Streaming-Semantik. Trifft der Lesevorgang auf eine Änderung oder Löschung eines bestehenden Datensatzes, wird ein Fehler ausgelöst. Am sichersten ist das Lesen aus statischen oder nur anfügenden (append-only) Quellen. Um Daten mit Änderungscommits einzulesen, lässt sich die Option `skipChangeCommits` verwenden, um Fehler zu behandeln:

```sql
CREATE OR REFRESH STREAMING TABLE basic_st
AS SELECT * FROM STREAM samples.nyctaxi.trips WITH (SKIPCHANGECOMMITS);
```

---

## <a id="object-storage">4. Daten aus Object Storage laden</a>

Pipelines unterstützen das Laden von Daten in allen von Databricks unterstützten Formaten.

Databricks empfiehlt, für inkrementelle Ingestion-Workloads gegen in Cloud Object Storage abgelegte Daten Auto Loader und Streaming Tables zu verwenden.

SQL verwendet die Funktion `read_files`, um die Auto-Loader-Funktionalität aufzurufen. Für einen Streaming-Read mit `read_files` muss zusätzlich das Schlüsselwort `STREAM` verwendet werden.

Syntax für `read_files` in SQL:

```
CREATE OR REFRESH STREAMING TABLE table_name
AS SELECT *
  FROM STREAM read_files(
    "<file-path>",
    [<option-key> => <option_value>, ...]
  )
```

Optionen für Auto Loader werden als Schlüssel-Wert-Paare angegeben.

Beispiel — Streaming Table aus JSON-Dateien mit Auto Loader:

```sql
CREATE OR REFRESH STREAMING TABLE ingestion_st
AS SELECT *
FROM STREAM read_files(
  "/databricks-datasets/retail-org/sales_orders",
  format => "json");
```

Die Funktion `read_files` unterstützt auch Batch-Semantik zum Erstellen von Materialized Views. Beispiel — Materialized View mit Batch-Semantik aus einem JSON-Verzeichnis:

```sql
CREATE OR REFRESH MATERIALIZED VIEW batch_mv
AS SELECT *
FROM read_files(
  "/databricks-datasets/retail-org/sales_orders",
  format => "json");
```

---

## <a id="expectations">5. Datenqualität mit Expectations prüfen</a>

Expectations dienen dazu, Datenqualitätsbeschränkungen festzulegen und durchzusetzen.

Der folgende Code definiert eine Expectation namens `valid_data`, die bei der Dateneinspeisung Datensätze mit `NULL`-Wert verwirft:

```sql
CREATE OR REFRESH STREAMING TABLE orders_valid(
  CONSTRAINT valid_date
  EXPECT (order_datetime IS NOT NULL AND length(order_datetime) > 0)
  ON VIOLATION DROP ROW
)
AS SELECT * FROM STREAM read_files("/databricks-datasets/retail-org/sales_orders");
```

---

## <a id="abfragen">6. Materialized Views und Streaming Tables der eigenen Pipeline abfragen</a>

Das folgende Beispiel definiert vier Datasets:

- eine Streaming Table `orders`, die JSON-Daten lädt;
- eine Materialized View `customers`, die CSV-Daten lädt;
- eine Materialized View `customer_orders`, die Datensätze aus `orders` und `customers` verbindet, den Bestell-Zeitstempel in ein Datum umwandelt und die Felder `customer_id`, `order_number`, `state` und `order_date` auswählt;
- eine Materialized View `daily_orders_by_state`, die die tägliche Anzahl der Bestellungen je Bundesstaat aggregiert.

Beim Abfragen von Views oder Tabellen der eigenen Pipeline lassen sich Katalog und Schema entweder direkt angeben, oder es werden die in der Pipeline konfigurierten Standardwerte verwendet. Im folgenden Beispiel werden `orders`, `customers` und `customer_orders` aus dem für die Pipeline konfigurierten Standardkatalog und -schema geschrieben und gelesen.

Der Legacy-Publishing-Modus verwendet das `LIVE`-Schema, um andere Materialized Views und Streaming Tables der eigenen Pipeline abzufragen. In neuen Pipelines wird die `LIVE`-Schema-Syntax stillschweigend ignoriert.

```sql
CREATE OR REFRESH STREAMING TABLE orders(
  CONSTRAINT valid_date
  EXPECT (order_datetime IS NOT NULL AND length(order_datetime) > 0)
  ON VIOLATION DROP ROW
)
AS SELECT * FROM STREAM read_files("/databricks-datasets/retail-org/sales_orders");

CREATE OR REFRESH MATERIALIZED VIEW customers
AS SELECT * FROM read_files("/databricks-datasets/retail-org/customers");

CREATE OR REFRESH MATERIALIZED VIEW customer_orders
AS SELECT
  c.customer_id,
  o.order_number,
  c.state,
  date(timestamp(int(o.order_datetime))) order_date
FROM orders o
INNER JOIN customers c
ON o.customer_id = c.customer_id;

CREATE OR REFRESH MATERIALIZED VIEW daily_orders_by_state
AS SELECT state, order_date, count(*) order_count
FROM customer_orders
GROUP BY state, order_date;
```

---

## <a id="private-tabelle">7. Private Tabelle definieren</a>

Die Klausel `PRIVATE` lässt sich beim Erstellen einer Materialized View oder einer Streaming Table verwenden. Beim Erstellen einer privaten Tabelle wird die Tabelle selbst angelegt, jedoch keine Metadaten für die Tabelle erzeugt. Die `PRIVATE`-Klausel weist die Pipeline an, eine Tabelle zu erstellen, die innerhalb der Pipeline verfügbar ist, aber nicht außerhalb der Pipeline zugegriffen werden sollte. Um die Verarbeitungszeit zu reduzieren, besteht eine private Tabelle für die Lebensdauer der sie erstellenden Pipeline fort, nicht nur für ein einzelnes Update.

Private Tabellen können denselben Namen wie Tabellen im Katalog tragen. Wird innerhalb einer Pipeline ein nicht qualifizierter Tabellenname angegeben und existieren sowohl eine private Tabelle als auch eine Katalogtabelle mit diesem Namen, wird die private Tabelle verwendet.

Private Tabellen wurden früher als temporäre Tabellen (`TEMPORARY`) bezeichnet.

---

## <a id="loeschen">8. Datensätze dauerhaft aus einer Materialized View oder Streaming Table löschen</a>

Um Datensätze dauerhaft aus einer Streaming Table mit aktivierten Deletion Vectors zu löschen — etwa zur DSGVO-Konformität —, müssen zusätzliche Operationen auf den zugrunde liegenden Delta-Tabellen des Objekts durchgeführt werden.

Materialized Views spiegeln bei jedem Refresh stets die Daten der zugrunde liegenden Tabellen wider. Um Daten in einer Materialized View zu löschen, müssen die Daten aus der Quelle gelöscht und die Materialized View anschließend aktualisiert werden.

---

## <a id="parametrisieren">9. Werte beim Deklarieren von Tabellen oder Views parametrisieren</a>

Mit `SET` lässt sich ein Konfigurationswert in einer Abfrage festlegen, die eine Tabelle oder View deklariert — einschließlich Spark-Konfigurationen. Jede Tabelle oder View, die in einer Quelldatei nach dem `SET`-Statement definiert wird, hat Zugriff auf den definierten Wert. Über `SET` angegebene Spark-Konfigurationen werden bei der Ausführung der Spark-Abfrage für jede nach dem `SET`-Statement folgende Tabelle oder View verwendet. Um einen Konfigurationswert in einer Abfrage zu lesen, wird die String-Interpolationssyntax `${}` verwendet. Das folgende Beispiel setzt einen Spark-Konfigurationswert namens `startDate` und verwendet diesen Wert in einer Abfrage:

```
SET startDate='2025-01-01';

CREATE OR REFRESH MATERIALIZED VIEW filtered
AS SELECT * FROM src
WHERE date > ${startDate}
```

Um mehrere Konfigurationswerte anzugeben, wird für jeden Wert ein eigenes `SET`-Statement verwendet.

---

## <a id="einschraenkungen">10. Einschränkungen</a>

Die `PIVOT`-Klausel wird nicht unterstützt. Die `pivot`-Operation in Spark erfordert das vorzeitige (eager) Laden der Eingabedaten, um das Ausgabeschema zu berechnen — diese Fähigkeit wird in Pipelines nicht unterstützt.

Die `CREATE OR REFRESH LIVE TABLE`-Syntax zum Erstellen einer Materialized View ist veraltet (deprecated). Stattdessen ist `CREATE OR REFRESH MATERIALIZED VIEW` zu verwenden.

---

## <a id="quellen">11. Quellen</a>

- Develop Lakeflow pipelines code with SQL (Grundlagen der SQL-Entwicklung für Pipelines, `CREATE OR REFRESH`-Syntax, `STREAM`-Schlüsselwort, `read_files`/Auto Loader, Expectations, private Tabellen, Parametrisierung mit `SET`, Einschränkungen): https://docs.databricks.com/aws/en/ldp/developer/sql-dev

**Stand:** 2026-08-19.
