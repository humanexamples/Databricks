# Sinks, externer Zugriff und GDPR in Lakeflow Declarative Pipelines

## 1. Was ist ein Sink?

- Standard: Flows schreiben in UC-verwaltete Delta-Tabellen (Streaming Table/MV). **Sinks** = alternatives Ziel **außerhalb** verwalteten Speichers (Event-Streaming-Dienste, benutzerdefinierte Speicher).
- Genutzt mit Append- oder Update-Flows: Sink via Sink-API definieren, dann als `target` in `append_flow`/`update_flow` referenzieren.

### 1.1 Managed Table vs. Sink

| | Managed Table (Standard) | Sink |
|---|---|---|
| Speicherort | Unity Catalog | beliebiges externes System |
| Lineage | vollständig | keine |
| Expectations / CDC | unterstützt | nicht unterstützt |
| Schreibmodus | je nach Flow-Typ | nur `append_flow` oder `update`-Mode (`update_flow`) |
| Typische Ziele | Streaming Table, MV | Delta außerhalb Pipeline, Kafka, Event Hubs, Custom |

### 1.2 Wann Sinks verwenden?

- Operative Low-Latency-Fälle (Fraud Detection, Echtzeit-Analysen, Empfehlungen) — Daten an Message-Bus statt Cloud-Speicher. Für Millisekunden-Latenz zusätzlich *Real-Time Mode*.
- Schreiben in Tabellen einer externen Delta-Instanz (UC-Managed + External).
- Reverse ETL (z. B. zurück nach Kafka für Nutzung außerhalb Databricks).
- Schreiben in nicht nativ unterstütztes Format via benutzerdefinierter Python-Datenquelle.

### 1.3 Sink-Typen

| Sink-Typ | Beschreibung |
|---|---|
| **Delta-Table-Sinks** | UC-Managed/External-Delta; Dateipfad oder vollqualifizierter Name |
| **Apache-Kafka-Sinks** | Kafka-Topics über Pipeline-Runtime-Connector |
| **Azure-Event-Hubs-Sinks** | via Kafka-Schnittstelle, gleiche Optionen wie Kafka |
| **Python-Custom-Sinks** | beliebiger Speicher via `spark.dataSource.register`-Datenquelle |
| **ForEachBatch-Sinks** | benutzerdefinierte Python-Logik je Micro-Batch; mehrere Ziele, Upserts, Ziele ohne natives Streaming |

### 1.4 Sink-APIs

- **`create_sink()`:** benannter Sink (Delta, Kafka, Azure Event Hubs, Python-Custom). Nur Python.
- **`foreach_batch_sink()`:** dekoriert Python-Funktion, ausgeführt je Micro-Batch.
- Per `create_sink()` erzeugter Sink wird als `target` eines `append_flow`/`update_flow` referenziert.

**Vollständige Signatur von `create_sink()` (alle Parameter):**

```python
from pyspark import pipelines as dp

dp.create_sink(
  name = <sink_name>,   # Pflicht: eindeutiger Bezeichner des Sinks, eindeutig über die gesamte Pipeline (alle Quelldateien)
  format = <format>,    # Pflicht: "kafka" oder "delta" -- legt das Zielsystem fest
  options = <options>   # optional: dict mit Schlüssel-Wert-Paaren zur Konfiguration (Bootstrap-Server/Topic bei Kafka, Pfad/Tabellenname bei Delta -- Codebeispiele: Abschnitt 2)
)
```

Die konkreten Ausprägungen von `format`/`options` je Zielsystem stehen in Abschnitt 2. Vollständige Signatur von `foreach_batch_sink()`: Abschnitt 2.4.

## 2. Sink erstellen

### 2.1 Delta-Sinks

Per Dateipfad:

```python
dp.create_sink(
  name = "delta_sink",
  format = "delta",
  options = {"path": "/Volumes/catalog_name/schema_name/volume_name/path/to/data"}
)
```

Per vollqualifiziertem Tabellennamen:

```python
dp.create_sink(
  name = "delta_sink",
  format = "delta",
  options = { "tableName": "catalog_name.schema_name.table_name" }
)
```

### 2.2 Kafka- und Azure-Event-Hubs-Sinks

Derselbe Code funktioniert für beide (`credential_name` referenziert ein UC-Service-Credential):

```python
credential_name = "<service-credential>"
eh_namespace_name = "dp-eventhub"
bootstrap_servers = f"{eh_namespace_name}.servicebus.windows.net:9093"
topic_name = "dp-sink"

dp.create_sink(
name = "eh_sink",
format = "kafka",
options = {
    "databricks.serviceCredential": credential_name,
    "kafka.bootstrap.servers": bootstrap_servers,
    "topic": topic_name
  }
)
```

### 2.3 Python Custom Data Sources

```python
from pyspark import pipelines as dp

# Annahme: my_custom_datasource ist eine registrierte Python-Custom-Streaming-Datenquelle
dp.create_sink(
    name="custom_sink",
    format="my_custom_datasource",
    options={
        # <options-needed-for-custom-datasource>
    }
)

@dp.append_flow(name="flow_to_custom_sink", target="custom_sink")
def flow_to_custom_sink():
    return read_stream("my_source_data")
```

### 2.4 ForEachBatch-Sink erstellen

Anders als `create_sink()` (Abschnitt 2.1–2.3) wird hier keine benannte Sink-Konfiguration erzeugt — stattdessen wird eine Python-Funktion direkt als Sink dekoriert. Diese Funktion (der **Batch-Handler**) wird für jeden Micro-Batch des Streams aufgerufen:

```python
from pyspark import pipelines as dp

@dp.foreach_batch_sink(name = "my_batch_sink")
# name: optional -- eindeutiger Sink-Name innerhalb der Pipeline; ohne Angabe Default = Name der dekorierten Funktion (hier "batch_handler")
def batch_handler(df, batch_id):
    # df: Spark-DataFrame mit den Zeilen dieses Micro-Batches -- wird von Spark automatisch übergeben, kein eigener Parameter der Dekorator-API
    # batch_id: fortlaufende Ganzzahl-ID des Micro-Batches -- steigt bei jedem Trigger-Intervall, ebenfalls automatisch übergeben
    df.write.format("some-target-system").save("...")   # eigene Schreib-/Transformationslogik
    # df.sparkSession liefert Zugriff auf die SparkSession innerhalb des Handlers
```

**`batch_id == 0`:** markiert entweder den Stream-Start oder den Beginn eines Full Refresh. Der Handler sollte diesen Fall für nachgelagerte Ziele korrekt behandeln (z. B. Ziel vorher leeren) — sonst können nach einem Full Refresh Daten doppelt im externen System landen (vgl. Full-Refresh-Gotcha in Abschnitt 4).

Als Flow-Ziel referenziert wie ein per `create_sink()` erzeugter Sink:

```python
@dp.append_flow(target = "my_batch_sink")
def flow_to_batch_sink():
  return spark.readStream.table("source_table")
```

## 3. Mit einem Append Flow in einen Sink schreiben

- **UC-Managed-/External-Tables:** Format `delta`, Pfad/Tabellenname; Pipeline muss UC-konfiguriert sein.
- **Kafka-Topics:** Format `kafka`, Topic-Name, Verbindungsinfo — gleiche Options wie Spark-Structured-Streaming-Kafka-Sink.
- **Azure Event Hubs:** Format `kafka`, analog via Kafka-Schnittstelle.

```python
@dp.append_flow(name = "delta_sink_flow", target="delta_sink")
def delta_sink_flow():
  return (
    spark.readStream.table("spark_referrers")
    .selectExpr("current_page_id", "referrer", "current_page_title", "click_count")
  )
```

```python
@dp.append_flow(name = "kafka_sink_flow", target = "eh_sink")
def kafka_sink_flow():
  return (
    spark.readStream.table("spark_referrers")
    .selectExpr("cast(current_page_id as string) as key", "to_json(struct(referrer, current_page_title, click_count)) AS value")
  )
```

- **Gotcha:** `value` ist für Azure-Event-Hubs-Sink zwingend; `key`, `partition`, `headers`, `topic` optional.

## 4. Limitierungen von Sinks

- Nur **Python-API** — SQL nicht unterstützt.
- Nur **Streaming-Queries** — keine Batch-Queries.
- Nur `append_flow`/`update_flow` schreiben in Sinks; andere Flows (z. B. `create_auto_cdc_flow`) nicht unterstützt; ein Sink kann nicht in Pipeline-Dataset-Definition (`@table`) gelesen werden:

  ```python
  # Nicht unterstützt:
  @table("from_sink_table")
  def fromSink():
    return read_stream("my_sink")
  ```
- Delta-Sinks: Tabellenname muss vollständig qualifiziert sein (`<catalog>.<schema>.<table>` UC; `<schema>.<table>` Hive-Metastore).
- **Gotcha:** Full Refresh räumt zuvor in Sinks geschriebene Daten **nicht** auf — erneut verarbeitete Daten angehängt, bestehende bleiben.
- Keine Pipeline-Expectations für Sinks.
- Serverless Egress Control unterstützt nur Kafka- und Delta-Lake-Sink-Connectors.

## 5. Architekturmuster mit Sinks

(Details siehe Kapitel Flows, Fan-in/Fan-out.)

- **Fan-out auf mehrere Sinks:** `foreach_batch_sink` schreibt aus einem Flow in mehrere Ziele (z. B. Delta-Tabelle + JSON-Pfad).
- **Fan-in in einen gemeinsamen Sink:** mehrere `append_flow`-Quellen (Kafka-Topics, APIs, Verzeichnisse) laufen in einen `foreach_batch_sink` zusammen, teilen einen Checkpoint statt vieler.
- Innerhalb `foreach_batch_sink`: voller Spark-Batch-Funktionsumfang, auch `MERGE INTO` gegen externe Delta-Tabelle (mit reinem Streaming-Write nicht möglich).

---

## 6. Externer Zugriff auf Materialized Views und Streaming Tables

- Standard: MVs/Streaming Tables **nicht** von externen Systemen zugreifbar. Zwei Mechanismen: **External Data Access** und **Compatibility Mode**.

### 6.1 External Data Access

- Veröffentlicht extern zugängliche Metadaten für Pipeline-verwaltete + eigenständige MVs/Streaming Tables — Clients nutzen UC- oder Iceberg-REST-APIs, ohne vollständige Datenkopie oder separaten Refresh-Zeitplan.
- Clients müssen Catalog-REST-APIs nutzen + Delta Lake 4.0.0+ oder Iceberg-V3 unterstützen.

### 6.2 Compatibility Mode (Public Preview)

- Erzeugt schreibgeschützte Datenkopie an gewähltem Speicherort, muss bei Tabellen-Update aktualisiert werden.
- Enthält v1-Metadaten für Delta Lake **und** Iceberg + Datenkopie — breitere Client-Palette, auf Kosten von Aktualisierungsverzögerung + Kopierkosten.

### 6.3 Empfehlung und Vergleich

| Eigenschaft | External Data Access | Compatibility Mode |
|---|---|---|
| Datenkopie | keine | erforderlich |
| Konsistenz | Read-after-write | nach Zeitplan (Standard stündlich, verzögert um Kopierzeit) |
| Zugriff | Delta 4.0.0+ oder Iceberg v3 (inkl. Deletion Vectors) | jeder Delta-Lake-/Iceberg-Client |
| Tabellenobjekt | erscheint als Managed Table, gleicher Name | neue Tabelle, neuer Speicherort |
| Unterstützte Typen | MV/Streaming Table (Pipeline- oder standalone) | dasselbe + jede andere UC-verwaltete Tabelle |
| Kosten | Teil der Refresh-Kosten, < 1 % zusätzlich | größtenteils Übertragungskosten |

- Unterstützen externe Clients REST-APIs → External Data Access. Für breitere/ältere Clients oder andere UC-Tabellen → Compatibility Mode.

### 6.4 Delta UniForm als zugrunde liegender Mechanismus (Vertiefung)

- Delta UniForm (Universal Format): Delta-Tabelle gleichzeitig als Iceberg-Tabelle lesbar, ohne Parquet-Duplikation. UniForm generiert nach jedem Delta-Commit asynchron zusätzliche Iceberg-Metadaten für dieselben Parquet-Dateien: **ein Datensatz, zwei Sichten**.

Vier Tabelleneigenschaften (vor erstem Schreibzugriff):

| Property | Zweck |
|---|---|
| `delta.enableDeletionVectors = false` | Iceberg v2 kennt keine Soft-Delete-Marker — alle Deletes müssen Hard Deletes sein |
| `delta.columnMapping.mode = name` | hält Spaltenidentifikatoren konsistent. **Dauerhaft** — nicht mehr entfernbar |
| `delta.enableIcebergCompatV2 = true` | Delta-Schreibprotokoll-Kompatibilität mit Iceberg v2 |
| `delta.universalFormat.enabledFormats = iceberg` | löst asynchrone Iceberg-Metadatengenerierung aus |

- **Gotcha:** Pipeline-verwaltete Streaming Tables/MVs können `delta.universalFormat.enabledFormats` **nicht direkt** setzen — UniForm nur auf **plain external Delta-Tabelle** (z. B. Delta-Sink-Ziel). Ablauf: Append-/Update-Flow schreibt in per `create_sink()` angelegten Delta-Sink; die vier Properties einmalig auf der resultierenden plain-Delta-Zieltabelle setzen. Iceberg-Clients nur Lesezugriff, UC übernimmt Iceberg-REST-Catalog-Rolle.
- **Einordnung ggü. External Data Access:** External Data Access deckt denselben Fall direkt für Pipeline-verwaltete MVs/Streaming Tables ab, ohne Delta-Sink-Umweg und ohne manuelle UniForm-Properties. Für **plain Delta-Tabellen außerhalb einer Pipeline** (z. B. Sink-Ziele) bleibt manuelle UniForm-Konfiguration relevant.

---

## 7. GDPR / Right to be Forgotten in Lakeflow Pipelines

### 7.1 Rechtlicher Hintergrund

GDPR/CCPA verpflichten zur dauerhaften, vollständigen Löschung von PII auf Kundenanfrage ("Right to be Forgotten") innerhalb festgelegter Frist (z. B. ein Kalendermonat).

### 7.2 Point Deletes mit Delta Lake

- Delta Lake beschleunigt Point Deletes via ACID-Transaktionen; PII lokalisierbar/entfernbar für GDPR/CCPA-Anfragen.
- Delta behält Tabellenhistorie für Time Travel/Rollbacks; `VACUUM` entfernt nicht mehr referenzierte, über Retention-Schwelle liegende Dateien dauerhaft.

### 7.3 Löschung bei aktivierten Deletion Vectors

- **Gotcha:** nach Löschen zusätzlich `REORG TABLE ... APPLY (PURGE)` nötig, um zugrunde liegende Datensätze dauerhaft zu löschen — gilt für Delta-Tabellen, MVs, Streaming Tables gleichermaßen.

### 7.4 Löschung in vorgelagerten Quellen

GDPR/CCPA gelten auch außerhalb Delta Lake (Kafka, Dateien, DBs) — zusätzlich zu Databricks müssen vorgelagerte Quellen (Queues, Cloud-Speicher) bereinigt werden.

### 7.5 Vollständige Löschung statt Verschleierung

Löschen vs. Verschleiern (Pseudonymisierung, Masking) — vollständige Löschung ist sicherste Option, da Reidentifizierungsrisiko oft nur so vollständig beseitigt wird.

### 7.6 Reihenfolge: Bronze zuerst, dann Silver/Gold

Empfohlen: zuerst Bronze-Löschung (geplanter Job liest Löschanfragen-Tabelle), Änderungen dann an Silver/Gold weitergeben.

### 7.7 Regelmäßige Tabellenpflege

- Delta behält Historie (inkl. gelöschter Datensätze) standardmäßig **30 Tage** für Time Travel — Daten bleiben im Cloud-Speicher, auch wenn ältere Versionen "entfernt" scheinen.
- Mit **Predictive Optimization:** Lakeflow-Pipelines pflegen Streaming Tables/MVs nutzungsbasiert.
- Ohne Predictive Optimization: automatische Pflege innerhalb 24 h nach Tabellenaktualisierung.
- Ohne beides: manuelles `VACUUM` — reduziert Time-Travel-Fähigkeit auf **7 Tage** (konfigurierbar), entfernt historische Versionen dauerhaft.

### 7.8 PII-Löschung in der Bronze-Schicht

- PII/Nicht-PII-Verknüpfung ggf. trennbar (z. B. `user_id` statt E-Mail als Schlüssel) → PII löschbar, Nicht-PII bleibt.

Einzelner Datensatz:

```python
spark.sql("DELETE FROM bronze.users WHERE user_id = 5")
```

Für viele Datensätze: `MERGE`, gesteuert über `gdpr_control_table` (`user_id`-Spalte je RTBF-Antragsteller):

```python
spark.sql("""
  MERGE INTO target
  USING (
    SELECT user_id
    FROM gdpr_control_table
  ) AS source
  ON target.user_id = source.user_id
  WHEN MATCHED THEN DELETE
""")
```

Nach erfolgreichem `MERGE`: Kontrolltabelle zur Bestätigung aktualisieren.

### 7.9 Propagation von Bronze nach Silver/Gold

- **Materialized Views:** behandeln Quell-Löschungen **automatisch** — MV nutzt inkrementelle Berechnung nur wenn günstiger, nie auf Kosten der Korrektheit; Quell-Löschung kann Full Recompute auslösen, liefert aber immer korrektes Ergebnis.
- **Streaming Tables:** verarbeiten aus Delta-Quellen nur Append-only — **Gotcha:** Update/Delete in Streaming-Quelle **nicht unterstützt**, unterbricht Stream. Robuster: aus **Change Feed** streamen, Updates/Deletes im eigenen Code behandeln.

Empfohlen für Streaming Tables: (1) Quell-Delta-Tabellen per DML löschen; (2) Streaming Table per DML löschen; (3) Streaming-Lesen auf `skipChangeCommits` umstellen (überspringt alles außer Inserts).

- Alternative: Quelle löschen, dann Streaming Table per Full Refresh aktualisieren — State gelöscht, alle Daten neu verarbeitet; Quelle außerhalb Retention (z. B. Kafka 7 Tage) wird nicht erneut verarbeitet → Datenverlust möglich. Nur sinnvoll, wenn historische Daten verfügbar und Re-Processing günstig ist.

### 7.10 Vollständiges Beispiel: E-Commerce-Pipeline

Medaillon-Architektur: `source_users` (PII `email`), `source_clicks` (PII `ip_address`); `gdpr_requests` (Kontrolltabelle); Bronze `users_bronze`/`clicks_bronze`; Silver `clicks_silver`/`users_silver`/`user_clicks_silver` (Join Streaming `clicks_silver` + Snapshot `users_silver`); Gold `user_behavior_gold`/`marketing_insights_gold`.

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col, count, countDistinct, when

catalog = "users"
schema = "name"

# Bronze Layer
@dp.table(name=f"{catalog}.{schema}.users_bronze", comment='Raw users data loaded from source')
def users_bronze():
   return spark.readStream.table(f"{catalog}.{schema}.source_users")

@dp.table(name=f"{catalog}.{schema}.clicks_bronze", comment='Raw clicks data loaded from source')
def clicks_bronze():
   return spark.readStream.table(f"{catalog}.{schema}.source_clicks")

# Silver Layer
@dp.create_streaming_table(name=f"{catalog}.{schema}.users_silver", comment='Cleaned and standardized users data')

@dp.view
@dp.expect_or_drop('valid_email', "email IS NOT NULL")
def users_bronze_view():
   return (
       spark.readStream
           .table(f"{catalog}.{schema}.users_bronze")
           .withColumn('registration_date', col('registration_date').cast('timestamp'))
           .dropDuplicates(['user_id', 'registration_date'])
           .select('user_id', 'username', 'email', 'registration_date', 'user_preferences')
   )

@dp.create_auto_cdc_flow(
   target=f"{catalog}.{schema}.users_silver",
   source="users_bronze_view",
   keys=["user_id"],
   sequence_by="registration_date",
)

@dp.table(name=f"{catalog}.{schema}.clicks_silver", comment='Cleaned and standardized clicks data')
@dp.expect_or_drop('valid_click_timestamp', "click_timestamp IS NOT NULL")
def clicks_silver():
   return (
       spark.readStream
           .table(f"{catalog}.{schema}.clicks_bronze")
           .withColumn('click_timestamp', col('click_timestamp').cast('timestamp'))
           .withWatermark('click_timestamp', '10 minutes')
           .dropDuplicates(['click_id'])
           .select('click_id', 'user_id', 'url_clicked', 'click_timestamp', 'device_type', 'ip_address')
   )

@dp.table(name=f"{catalog}.{schema}.user_clicks_silver", comment='Joined users and clicks data on user_id')
def user_clicks_silver():
   users = spark.read.table(f"{catalog}.{schema}.users_silver")  # statischer Snapshot je Refresh
   clicks = spark.readStream.table('clicks_silver')
   return clicks.join(users, on='user_id', how='inner')

# Gold Layer
@dp.materialized_view(name=f"{catalog}.{schema}.user_behavior_gold", comment='Aggregated user behavior metrics')
def user_behavior_gold():
   df = spark.read.table(f"{catalog}.{schema}.user_clicks_silver")
   return df.groupBy('user_id').agg(
       count('click_id').alias('total_clicks'),
       countDistinct('url_clicked').alias('unique_urls')
   )

@dp.materialized_view(name=f"{catalog}.{schema}.marketing_insights_gold", comment='User segments for marketing insights')
def marketing_insights_gold():
   df = spark.read.table(f"{catalog}.{schema}.user_behavior_gold")
   return df.withColumn(
       'engagement_segment',
       when(col('total_clicks') >= 100, 'High Engagement')
       .when((col('total_clicks') >= 50) & (col('total_clicks') < 100), 'Medium Engagement')
       .otherwise('Low Engagement')
   )
```

Löschung in Quelltabellen:

```python
def apply_gdpr_delete(user_id):
 tables_with_pii = ["clicks_bronze", "users_bronze", "clicks_silver", "users_silver", "user_clicks_silver"]
 for table in tables_with_pii:
   spark.sql(f"""
     DELETE FROM {catalog}.{schema}.{table}
     WHERE user_id = {user_id}
   """)
```

`skipChangeCommits` bei betroffenen Streaming-Table-Definitionen ergänzen (`users_bronze`, `users_silver`, `clicks_bronze`, `clicks_silver`, `user_clicks_silver`) — **MV-Definitionen brauchen keine Anpassung** (behandeln Updates/Deletes automatisch):

```python
def users_bronze():
   return spark.readStream.option('skipChangeCommits', 'true').table(f"{catalog}.{schema}.source_users")
```

Ergebnis: bei erneutem Pipeline-Lauf ist das Update erfolgreich.

**Stand:** 2026-09-14.
