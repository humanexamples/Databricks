# API-Ingestion in Pipelines — Referenz

Dieses Dokument beschreibt, wie Daten aus einer HTTP-/REST-API in Lakeflow-Declarative-Pipelines (LDP) eingelesen werden. Es vertieft den in `Daten laden.md` Abschnitt 8 verlinkten Fall "Beliebige HTTP-/REST-API ohne Managed Connector". Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/api-ingestion`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte; die AWS-Fassung (`docs.databricks.com/aws/en/ldp/api-ingestion`) wurde ergänzend geprüft und deckt sich inhaltlich (Pattern-Tabelle, Codebeispiele identisch).

## Abschnittsübersicht

1. [Grundprinzip: Warum es keine generische API-Quelle gibt](#grundprinzip)
2. [Voraussetzungen](#voraussetzungen)
3. [Muster wählen](#muster-waehlen)
4. [Muster 1: Periodische Abrufe als Materialized View](#muster-1)
5. [Muster 2: Python Data Source API für hochvolumige/streamende APIs](#muster-2)
6. [Muster 3: Entkoppelte Ingestion über Scheduled Job + Auto Loader](#muster-3)
7. [Best Practices](#best-practices)
8. [Quellen](#quellen)

---

## <a id="grundprinzip">1. Grundprinzip: Warum es keine generische API-Quelle gibt</a>

Ingestion aus einer API bedeutet, Daten per HTTP von einem Webservice abzurufen — meist als paginiertes JSON — statt aus einer Datei oder Datenbank zu lesen. Im Unterschied zu Dateien oder einem Message Bus gibt es **keine eingebaute generische API-Quelle**: Authentifizierung, Pagination und Rate Limits müssen selbst gehandhabt werden. Lakeflow-Pipelines unterstützen dafür drei Muster; welches passt, hängt von Datenvolumen und Aktualisierungsbedarf ab.

**Wichtiger Hinweis vor Eigenentwicklung:** Bevor eigener API-Ingestion-Code geschrieben wird, sollte geprüft werden, ob bereits ein Managed Connector existiert. Lakeflow Connect liefert eingebaute Connectoren für viele verbreitete SaaS-APIs (z. B. Salesforce, Workday, ServiceNow, Google Analytics) sowie eine wachsende Zahl an Partner-Connectoren. Ein passender Connector übernimmt Authentifizierung, Pagination und inkrementelle Extraktion automatisch und ist fast immer weniger Aufwand als eine handgeschriebene Ingestion. Die folgenden Muster sind nur für Fälle gedacht, für die kein Connector passt.

## <a id="voraussetzungen">2. Voraussetzungen</a>

- Eine Pipeline.
- API-Credentials (Token oder Key), gespeichert als Databricks Secret — Credentials dürfen nie im Pipeline-Quellcode hartkodiert werden.
- Netzwerkzugriff vom Pipeline-Compute zum API-Endpunkt.
- Vertrautheit mit Streaming Tables und Materialized Views, den von diesen Mustern erzeugten Dataset-Typen.

## <a id="muster-waehlen">3. Muster wählen</a>

Da es keine native generische REST-API-Quelle in Pipelines gibt, wird eines der drei folgenden Muster anhand von Datenvolumen und Ingestion-Frequenz gewählt:

| Muster | Einsatz wenn |
|---|---|
| Periodische Abrufe als Materialized View | Kleine bis mittlere Payloads, einmaliger Abruf pro Pipeline-Lauf (z. B. Referenzdaten, tägliche FX-Kurse, begrenzt-paginierte APIs). |
| Python Data Source API | Hochvolumige oder streamende APIs, die inkrementell mit Checkpoint-Fortschritt abgefragt werden müssen, sodass ein Neustart nicht alles erneut liest. |
| Entkoppelte Ingestion mit Auto Loader | API-spezifische Eigenheiten sollen von der Transformationslogik isoliert werden; zusätzlich wird Exactly-once-Datei-Tracking gewünscht. |

## <a id="muster-1">4. Muster 1: Periodische Abrufe als Materialized View</a>

Für kleine bis mittlere Payloads, die einmal pro Pipeline-Lauf abgerufen werden, wird eine Python-Funktion geschrieben, die die API aufruft und einen Spark-DataFrame zurückgibt. Da das Dataset eine Materialized View ist, führt die Pipeline die Funktion bei jedem Update vollständig und idempotent erneut aus.

**Schritt 1 — API-Token als Secret hinterlegen** und als Spark-Konfigurationsproperty im `spark_conf`-Block der Cluster-Konfiguration der Pipeline-Einstellungen abbilden:

```json
{
  "clusters": [
    {
      "spark_conf": {
        "api.token": "{{secrets/<scope-name>/<secret-name>}}"
      }
    }
  ]
}
```

Der Code liest diesen Wert anschließend über `spark.conf.get("api.token")`.

**Schritt 2 — Materialized View definieren**, die die API aufruft und die Antwort als DataFrame zurückgibt:

```python
import requests
from pyspark import pipelines as dp
from pyspark.sql import Row

@dp.materialized_view(
    name="exchange_rates_bronze",
    comment="Daily FX rates pulled from a public REST API",
)
def exchange_rates_bronze():
    resp = requests.get(
        "https://api.example.com/v1/rates",
        params={"base": "USD"},
        headers={"Authorization": f"Bearer {spark.conf.get('api.token')}"},
        timeout=30,
    )
    resp.raise_for_status()
    rates = resp.json()["rates"]
    rows = [Row(currency=k, rate=float(v), as_of_date=resp.json()["date"]) for k, v in rates.items()]
    return spark.createDataFrame(rows)
```

**Schritt 3 — Pagination innerhalb der Funktion behandeln**, durch Schleifen über Seiten und Zusammenführen der Ergebnisse vor der Rückgabe:

```python
import requests
from pyspark import pipelines as dp
from pyspark.sql import Row

@dp.materialized_view(
    name="customers_bronze",
    comment="Customers pulled from a paginated REST API",
)
def customers_bronze():
    token = spark.conf.get("api.token")
    rows = []
    url = "https://api.example.com/v1/customers"
    while url:  # follow the API's next-page cursor until exhausted
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()
        rows.extend(Row(**record) for record in payload["data"])
        url = payload.get("next")  # None on the last page
    return spark.createDataFrame(rows)
```

Retry- und Backoff-Logik um den Request herum wird für Robustheit empfohlen.

Dieses Muster liest bei jedem Pipeline-Update die vollständige API-Antwort erneut — es eignet sich daher nur, wenn die Payload-Größe begrenzt ist. Für inkrementelle Reads dient Muster 2.

## <a id="muster-2">5. Muster 2: Python Data Source API für hochvolumige/streamende APIs</a>

Für APIs, die inkrementell mit Offset-Tracking abgefragt werden müssen, wird eine Custom Data Source über die Python-Data-Source-API implementiert. Das liefert echte Streaming-Semantik inklusive Checkpoint-Fortschritt und inkrementellen Reads, sodass ein Neustart beim letzten Offset fortsetzt statt die gesamte API erneut abzufragen.

1. `DataSource`- und `DataSourceStreamReader`-Klassen implementieren, die die API aufrufen und den Lese-Offset tracken.
2. Die Data Source registrieren, damit die Pipeline sie über den Formatnamen referenzieren kann:

```python
spark.dataSource.register(MyApiDataSource)
```

3. Aus der registrierten Quelle in einer Streaming Table lesen:

```python
from pyspark import pipelines as dp

@dp.table(name="events_bronze")
def events_bronze():
    return spark.readStream.format("my_api_source").load()
```

## <a id="muster-3">6. Muster 3: Entkoppelte Ingestion über Scheduled Job + Auto Loader</a>

Ein verbreitetes Produktionsmuster trennt den API-Aufruf von der Pipeline: Ein geplanter Job landet die rohen API-Antworten als Dateien in einem Unity-Catalog-Volume, die Pipeline holt sie anschließend über Auto Loader ab. Das isoliert API-spezifische Eigenheiten wie Pagination und Rate Limits von der deklarativen Transformationslogik und liefert Auto Loaders Exactly-once-Datei-Tracking kostenlos mit.

**Schritt 1 — Notebook/Skript**, das die API aufruft und die rohen JSON-Antworten in ein Unity-Catalog-Volume schreibt:

```python
import requests, json, time

token = dbutils.secrets.get(scope="<scope-name>", key="<secret-name>")
volume_path = "/Volumes/main/raw/landing/api_events"

resp = requests.get(
    "https://api.example.com/v1/events",
    headers={"Authorization": f"Bearer {token}"},
    timeout=30,
)
resp.raise_for_status()
# One file per run; the pipeline's Auto Loader tracks which files it has ingested.
with open(f"{volume_path}/events_{int(time.time())}.json", "w") as f:
    json.dump(resp.json()["data"], f)
```

**Schritt 2:** Notebook/Skript per Lakeflow Jobs eigenständig planen.

**Schritt 3 — In der Pipeline** eine Streaming Table definieren, die die gelandeten Dateien via Auto Loader liest:

```python
from pyspark import pipelines as dp

@dp.table(name="api_events_bronze")
def api_events_bronze():
    return (
        spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "json")
            .load("/Volumes/main/raw/landing/api_events")
    )
```

Für verlässliche File-Ingestion mit Auto Loader siehe außerdem den Ordner `Lakeflow Connect/Lakeflow Connect Standard Connectors/Working with Files/06 Auto Loader/` in diesem Projekt (vertiefte Referenz).

## <a id="best-practices">7. Best Practices</a>

- **Secrets aus dem Quellcode heraushalten:** API-Tokens und -Keys in Databricks-Secret-Scopes speichern und zur Laufzeit auslesen.
- **Antworten früh validieren:** [Expectations](../14%20Developer%20Reference/Python-Referenz/apply_changes.md) auf den eingelesenen Zeilen ergänzen, um fehlerhafte API-Antworten frühzeitig zu erkennen.
- **Pagination und Rate Limits handhaben:** Über Seiten iterieren und Retry mit Backoff ergänzen, damit ein transienter Fehler nicht das gesamte Update scheitern lässt.

---

## <a id="quellen">8. Quellen</a>

- Ingest data from an API in pipelines (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/ldp/api-ingestion
- Ingest data from an API in pipelines (AWS): https://docs.databricks.com/aws/en/ldp/api-ingestion

**Stand:** 2026-08-19.
