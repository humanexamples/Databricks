# Tutorial: Geodaten-Pipelines

Referenz zum Tutorial für geografische (räumliche) Datenpipelines, basierend auf `https://docs.databricks.com/aws/en/ldp/tutorial-spatial-pipelines`.

## Abschnittsübersicht

1. [Was baut man in diesem Tutorial?](#einleitung)
2. [Voraussetzungen](#voraussetzungen)
3. [Schritt 1: Pipeline erstellen](#schritt1)
4. [Schritt 2: GPS- und Geofence-Beispieldaten erzeugen](#schritt2)
5. [Schritt 3: GPS-Daten in Bronze-Streaming-Table einlesen](#schritt3)
6. [Schritt 4: Silver-Streaming-Table mit Geometrie-Punkten](#schritt4)
7. [Schritt 5: Warehouse-Geofences-Gold-Tabelle erstellen](#schritt5)
8. [Schritt 6: Warehouse-Arrivals-Tabelle mit räumlichem Join](#schritt6)
9. [Verifikation des räumlichen Joins](#verifikation)
10. [Schritt 7: Pipeline zeitplanen (optional)](#schritt7)
11. [Quellen](#quellen)

---

## <a id="einleitung">1. Was baut man in diesem Tutorial?</a>

Es wird eine Pipeline erstellt und bereitgestellt, die GPS-Daten einliest, Koordinaten in native räumliche Typen umwandelt und sie gegen Lager-Geofences abgleicht, um Ankünfte (Arrivals) nachzuverfolgen.

Konkret wird gelernt:

- Eine Pipeline zu erstellen und Beispiel-GPS- sowie Geofence-Daten in einem Unity-Catalog-Volume zu erzeugen.
- Rohe GPS-Pings inkrementell mit Auto Loader in eine Bronze-Streaming-Table einzulesen.
- Eine Silver-Streaming-Table zu bauen, die Längen- und Breitengrad in einen nativen `GEOMETRY`-Punkt umwandelt.
- Eine Materialized View der Lager-Geofences aus WKT-Polygonen (Well-Known Text) zu erstellen.
- Einen räumlichen Join durchzuführen, um eine Tabelle mit Lager-Ankünften zu erzeugen.

## <a id="voraussetzungen">2. Voraussetzungen</a>

- In einem Databricks-Workspace angemeldet sein, mit aktiviertem Unity Catalog.
- Serverless Compute im Workspace verfügbar, sofern Serverless-Lakeflow-Pipelines genutzt werden sollen.
- Berechtigung, eine Compute-Ressource zu erstellen, oder Zugriff auf eine bestehende.
- Berechtigungen, ein neues Schema in einem Katalog zu erstellen.
- Berechtigungen, ein neues Volume in einem bestehenden Schema zu erstellen.
- Eine Runtime verwenden, die native räumliche Typen und räumliche Funktionen unterstützt.
- Für die vollständigen Rechte zum Erstellen, Ausführen, Aktualisieren und Einsehen von Pipelines und deren Ausgabe verweist die Doku auf die Berechtigungsverwaltung für Pipelines.

**Ungeklärt:** Ab welcher konkreten Databricks-Runtime-Version native räumliche Typen (`GEOMETRY`) und räumliche Funktionen (`ST_Point`, `ST_GeomFromWKT`, `ST_Contains`) genau verfügbar sind, wurde auf dieser Seite nicht mit einer expliziten Versionsnummer benannt — die Doku fordert nur allgemein "eine Runtime, die native räumliche Typen und räumliche Funktionen unterstützt".

## <a id="schritt1">3. Schritt 1: Pipeline erstellen</a>

1. Im Workspace in der Seitenleiste auf **New** klicken, dann **ETL Pipeline** auswählen.
2. Einen beschreibenden Namen eingeben.
3. Rechts neben dem Namen Katalog- und Schema-Standardwerte wählen.
4. Optional **Python** oder **SQL** als Sprache wählen.
5. **Use sample code** klicken.

## <a id="schritt2">4. Schritt 2: GPS- und Geofence-Beispieldaten erzeugen</a>

Zunächst werden 5000 simulierte GPS-Pings sowie zwei Geofence-Polygone (als WKT-Strings) erzeugt und als JSON in ein Unity-Catalog-Volume geschrieben:

```python
from pyspark.sql import functions as F

catalog = "<catalog>"
schema = "<schema>"
spark.sql(f"USE CATALOG `{catalog}`")
spark.sql(f"USE SCHEMA `{schema}`")
spark.sql(f"CREATE VOLUME IF NOT EXISTS `{catalog}`.`{schema}`.`raw_data`")
volume_base = f"/Volumes/{catalog}/{schema}/raw_data"

gps_path = f"{volume_base}/gps"
df_gps = (
    spark.range(0, 5000)
    .repartition(10)
    .select(
        F.format_string("device_%d", F.col("id").cast("long")).alias("device_id"),
        F.current_timestamp().alias("timestamp"),
        (-118.3 + F.rand() * 0.2).alias("longitude"),
        (34.0 + F.rand() * 0.2).alias("latitude"),
    ))
df_gps.write.format("json").mode("overwrite").save(gps_path)

geofences_path = f"{volume_base}/geofences"
geofences_data = [
    ("Warehouse_A", "POLYGON ((-118.35 34.02, -118.25 34.02, -118.25 34.08, -118.35 34.08, -118.35 34.02))"),
    ("Warehouse_B", "POLYGON ((-118.20 34.05, -118.12 34.05, -118.12 34.12, -118.20 34.12, -118.20 34.05))"),
]
df_geo = spark.createDataFrame(geofences_data, ["warehouse_name", "boundary_wkt"])
df_geo.write.format("json").mode("overwrite").save(geofences_path)
```

## <a id="schritt3">5. Schritt 3: GPS-Daten in Bronze-Streaming-Table einlesen</a>

Die rohen GPS-Pings werden per Auto Loader inkrementell aus dem Volume in eine Bronze-Streaming-Table eingelesen.

```sql
CREATE OR REFRESH STREAMING TABLE gps_bronze
COMMENT "Raw GPS pings ingested from volume using Auto Loader";

CREATE FLOW gps_bronze_ingest_flow AS
INSERT INTO gps_bronze BY NAME
SELECT *
FROM STREAM read_files(
  "/Volumes/<catalog>/<schema>/raw_data/gps",
  format => "json",
  inferColumnTypes => "true")
```

```python
from pyspark import pipelines as dp

path = "/Volumes/<catalog>/<schema>/raw_data/gps"

dp.create_streaming_table(
  name="gps_bronze",
  comment="Raw GPS pings ingested from volume using Auto Loader",
)

@dp.append_flow(target="gps_bronze", name="gps_bronze_ingest_flow")
def gps_bronze_ingest_flow():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(path)
    )
```

## <a id="schritt4">6. Schritt 4: Silver-Streaming-Table mit Geometrie-Punkten</a>

In dieser Stufe werden Längen- und Breitengrad über die Funktion `ST_Point` in einen nativen `GEOMETRY`-Punkt (`point_geom`) umgewandelt, der für den räumlichen Join in Schritt 6 benötigt wird.

```sql
CREATE OR REFRESH STREAMING TABLE raw_gps_silver
COMMENT "GPS pings with native geometry point for spatial joins";

CREATE FLOW raw_gps_silver_flow AS
INSERT INTO raw_gps_silver BY NAME
SELECT
  device_id,
  timestamp,
  longitude,
  latitude,
  ST_Point(longitude, latitude) AS point_geom
FROM STREAM(gps_bronze)
```

```python
from pyspark import pipelines as dp
from pyspark.sql import functions as F

dp.create_streaming_table(
  name="raw_gps_silver",
  comment="GPS pings with native geometry point for spatial joins",
)

@dp.append_flow(target="raw_gps_silver", name="raw_gps_silver_flow")
def raw_gps_silver_flow():
    return (
        spark.readStream.table("gps_bronze")
        .select(
            "device_id",
            "timestamp",
            "longitude",
            "latitude",
            F.expr("ST_Point(longitude, latitude)").alias("point_geom"),
        )
    )
```

## <a id="schritt5">7. Schritt 5: Warehouse-Geofences-Gold-Tabelle erstellen</a>

Die Geofence-Polygone (als WKT-Text abgelegt) werden über `ST_GeomFromWKT` in native Geometrie-Objekte umgewandelt und als Materialized View bereitgestellt.

```sql
CREATE OR REPLACE MATERIALIZED VIEW warehouse_geofences_gold AS
SELECT
  warehouse_name,
  ST_GeomFromWKT(boundary_wkt) AS boundary_geom
FROM read_files(
  "/Volumes/<catalog>/<schema>/raw_data/geofences",
  format => "json")
```

```python
from pyspark import pipelines as dp
from pyspark.sql import functions as F

path = "/Volumes/<catalog>/<schema>/raw_data/geofences"

@dp.table(name="warehouse_geofences_gold", comment="Warehouse geofence polygons as geometry")
def warehouse_geofences_gold():
    return (
        spark.read.format("json").load(path).select(
            "warehouse_name",
            F.expr("ST_GeomFromWKT(boundary_wkt)").alias("boundary_geom"),
        )
    )
```

## <a id="schritt6">8. Schritt 6: Warehouse-Arrivals-Tabelle mit räumlichem Join</a>

Über die Funktion `ST_Contains` wird geprüft, ob ein GPS-Punkt innerhalb eines Geofence-Polygons liegt. Das Ergebnis ist eine Tabelle, die jedes Gerät mit dem Lager verknüpft, dessen Geofence es betreten hat.

```sql
CREATE OR REPLACE MATERIALIZED VIEW warehouse_arrivals AS
SELECT
  g.device_id,
  g.timestamp,
  w.warehouse_name
FROM raw_gps_silver g
JOIN warehouse_geofences_gold w
  ON ST_Contains(w.boundary_geom, g.point_geom)
```

```python
from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(name="warehouse_arrivals", comment="Devices that have entered a warehouse geofence")
def warehouse_arrivals():
    g = spark.read.table("raw_gps_silver")
    w = spark.read.table("warehouse_geofences_gold")
    return (
        g.alias("g")
        .join(w.alias("w"), F.expr("ST_Contains(w.boundary_geom, g.point_geom)"))
        .select(
            F.col("g.device_id").alias("device_id"),
            F.col("g.timestamp").alias("timestamp"),
            F.col("w.warehouse_name").alias("warehouse_name"),
        )
    )
```

## <a id="verifikation">9. Verifikation des räumlichen Joins</a>

Zur Kontrolle des Ergebnisses stellt das Tutorial folgende Abfragen bereit:

```sql
-- Anzahl der Ankünfte je Lager
SELECT warehouse_name, COUNT(*) AS arrival_count
FROM warehouse_arrivals
GROUP BY warehouse_name
ORDER BY warehouse_name;
```

```sql
-- Stichprobe der jüngsten Datensätze
SELECT device_id, timestamp, warehouse_name
FROM warehouse_arrivals
ORDER BY timestamp DESC
LIMIT 10;
```

```python
display(spark.table("warehouse_arrivals").groupBy("warehouse_name").count().orderBy("warehouse_name"))
display(spark.table("warehouse_arrivals").orderBy("timestamp", ascending=False).limit(10))
```

## <a id="schritt7">10. Schritt 7: Pipeline zeitplanen (optional)</a>

1. Oben im Editor wird der Button **Schedule** gewählt.
2. Erscheint der Dialog **Schedules**, wird **Add schedule** gewählt.
3. Optional wird ein Name für den Job vergeben.
4. Standardmäßig läuft der Zeitplan einmal täglich; dieser Wert kann übernommen oder angepasst werden.
5. Mit **Create** wird der Zeitplan angelegt.

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/tutorial-spatial-pipelines
