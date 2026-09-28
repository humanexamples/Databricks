

Demo: Wie Sie PII-Datensicherheit mit **Pseudonymisierung und Anonymisierung** handhaben

1. **Pseudonymisierungs**

   - Ersetzt den ursprünglichen Datenpunkt durch ein Pseudonym zur späteren Re-Identifizierung
   - Nur autorisierte Benutzer haben Zugriff auf Schlüssel/Hash/Tabelle zur Re-Identifizierung
   - Schützt Datensätze auf Datensatzebene für maschinelles Lernen
   - Ein Pseudonym gilt gemäß der DSGVO weiterhin als personenbezogene Daten
     Zwei Hauptmethoden der Pseudonymisierung: Hashing und Tokenisierung

   Techniken:

   - Hashing; Ziele:
     - Wenden Sie SHA oder andere Hashes auf alle PII an.
     - Fügen Sie den Werten vor dem Hashing eine zufällige Zeichenfolge ("Salt") hinzu.
     - Databricks Secrets können genutzt werden, um den Salt-Wert zu verschleiern.
     - Dies führt zu einer leichten Zunahme der Datengröße.
     - Einige Operationen können weniger effizient sein.

   - Tokenisierung; Ziele:
     - Wandelt alle PII in Schlüssel um.
       - Werte werden in einer sicheren Lookup-Tabelle gespeichert.
       - Langsam beim Schreiben, aber schnell beim Lesen.
       - Deidentifizierte Daten werden in weniger Bytes gespeichert.

2. **Anonymisierung**; Ziele:
   - Schützt den gesamten Datensatz (Tabellen, Datenbanken oder ganze Datenkataloge), hauptsächlich für Business Intelligence
   - Personenbezogene Daten werden so unwiderruflich verändert, dass eine betroffene Person nicht mehr direkt oder indirekt identifiziert werden kann
   - In der Praxis wird meist eine Kombination mehrerer Techniken verwendet
   - Zwei Hauptmethoden der Anonymisierung: Datenunterdrückung und Generalisierung

Führen Sie die folgende Zelle aus, um Ihre Spark Declarative Pipeline mithilfe der bereitgestellten Konfigurationswerte automatisch zu generieren.

**HINWEIS:** Die Klasse `DeclarativePipelineCreator` ist eine benutzerdefinierte Klasse, die wir zum Einrichten der Spark Declarative Pipeline verwenden. Die Klasse basiert auf dem Databricks SDK und REST-API-Aufrufen.

```python
demo_pipeline = DeclarativePipelineCreator(
    pipeline_name=f"1.2_PII_Data_Security_{DA.catalog_name}", 
    catalog_name=DA.catalog_name,
    schema_name="pii_data",
    root_path_folder_name='Pipeline',
    source_folder_names=[
        'DP 1.2.1 - Pseudonymized PII Lookup Table',
        'DP 1.2.2 - Anonymized Users Age'
    ],
    configuration={
        'user_reg_source':f'/Volumes/{DA.catalog_name}/pii_data/pii/stream_source/user_reg',
        'daily_user_events_source':f"/Volumes/{DA.catalog_name}/pii_data/pii/stream_source/daily",
        'lookup_catalog': DA.catalog_name
        },
    serverless=True,
    channel='CURRENT',
    delete_pipeine_if_exists = True
)

demo_pipeline.create_pipeline()

demo_pipeline.start_pipeline()
```

![ddemo01_2_full_pipeline.png](https://files.training.databricks.com/binder/prod_main/databricks-data-privacy-en_us-2.1.2/images/20260819T030319Z/Databricks Data Privacy/Includes/images/demo01_2_full_pipeline.png)

## C. Pseudonymisierung im DAG

Die Tabelle **registered_users** ist unsere Quelle für die aufgenommenen Benutzer, auf die wir *Pseudonymisierung* und *Anonymisierung* anwenden werden.

![demo01_2_pii_data_security_pseudo_dag.png](https://files.training.databricks.com/binder/prod_main/databricks-data-privacy-en_us-2.1.2/images/20260819T030319Z/Databricks Data Privacy/Includes/images/demo01_2_pii_data_security_pseudo_dag.png)

Der Code in **DP 1.2.1 - Pseudonymized PII Lookup Table.ipynb**:

```python
from pyspark import pipelines as dp
import pyspark.sql.functions as F

user_reg_source = spark.conf.get("user_reg_source")

# Funktion zur Pseudonymisierung mit gesalzenem Hashing definieren 
salt = "BEANS"     
def salted_hash(id):
    return F.sha2(F.concat(id, F.lit(salt)), 256)
```

```python
# Daten mit Auto Loader inkrementell in die Tabelle registered_users ingestieren
@dp.table
def registered_users():
    return (
        spark.readStream
            .format("cloudFiles")
            .schema("""device_id LONG, 
                       mac_address STRING, 
                       registration_timestamp DOUBLE, 
                       user_id LONG""")
            .option("cloudFiles.format", "json")
            .load(f"{user_reg_source}")
        )
    
# Create pseudonymized user lookup table
# Method: Hashing
# Die untenstehende Logik erstellt die Tabelle user_lookup. Im nächsten Notebook 
# werden wir diese Pseudo-ID als einzige Verbindung zu den personenbezogenen Daten 
# (PII) der Benutzer verwenden. Indem wir den Zugriff auf die Verknüpfung zwischen 
# unserer alt_id und anderen natürlichen Schlüsseln kontrollieren, können wir 
# verhindern, dass PII mit anderen Benutzerdaten in unserem gesamten System verknüpft 
# werden.
@dp.table
def user_lookup_hashed():
    return (dp
            .read_stream("registered_users")
            .select(
                  salted_hash(F.col("user_id")).alias("alt_id"),
                  "device_id", 
                  "mac_address", 
                  "user_id")
           )

# Erstellen wir zunächst eine Tabelle, die die Token für unsere Benutzer in der Tabelle 
# 'registered_token' speichert.
@dp.table
def registered_users_tokens():
    return (dp
            .readStream("registered_users")
            .select("user_id")
            .distinct()
            .withColumn("token", F.expr("uuid()"))
        )

# Create pseudonymized user lookup table
# Method: Tokenization
# Erstellen wir nun die Tabelle 'user_lookup_tokenized' unter Verwendung der 
# 'registered_users_tokens' und führen einen Join durch, um die neue tokenisierte 
# Spalte als alt_id einzubinden.
@dp.table
def user_lookup_tokenized():
    return (dp
            .read_stream("registered_users")
            .join(dp.read("registered_users_tokens"), "user_id", "left")
            .drop("user_id")
            .withColumnRenamed("token", "alt_id")
           )
```



## D. Anonymisierung im DAG

![demo01_2_anonymization_dag.png](https://files.training.databricks.com/binder/prod_main/databricks-data-privacy-en_us-2.1.2/images/20260819T030319Z/Databricks Data Privacy/Includes/images/demo01_2_anonymization_dag.png)

```python
from pyspark import pipelines as dp
import pyspark.sql.functions as F

# Den Quellpfad für die täglichen Benutzer-Events aus der Spark-Konfiguration abrufen
daily_user_events_source = spark.conf.get("daily_user_events_source")

# Den Katalognamen für Lookup-Tabellen aus der Spark-Konfiguration abrufen
lookup_catalog = spark.conf.get("lookup_catalog")


def age_bins(dob_col):
    age_col = F.floor(F.months_between(F.current_date(), dob_col) / 12).alias("age")
    return (
        F.when((age_col < 18), "under 18")
        .when((age_col >= 18) & (age_col < 25), "18-25")
        .when((age_col >= 25) & (age_col < 35), "25-35")
        .when((age_col >= 35) & (age_col < 45), "35-45")
        .when((age_col >= 45) & (age_col < 55), "45-55")
        .when((age_col >= 55) & (age_col < 65), "55-65")
        .when((age_col >= 65) & (age_col < 75), "65-75")
        .when((age_col >= 75) & (age_col < 85), "75-85")
        .when((age_col >= 85) & (age_col < 95), "85-95")
        .when((age_col >= 95), "95+")
        .otherwise("invalid age")
        .alias("age")
    )
```

```sql
# Die Tabelle 'date_lookup' wird für die Zuordnung von 'date' und 'week_part' verwendet 
# und dient dazu, mit den 'user_events_raw' Daten verknüpft zu werden, um zu ermitteln, 
# zu welchem 'week_part' das Date of Birth(DOB) gehört. Z.B.: 2020-07-02 = 2020-27. 
@dp.table
def date_lookup():
    # Die rohe Datums-Lookup-Tabelle aus dem angegebenen Katalog lesen
    return (spark
            .read
            .table(f"{lookup_catalog}.pii_data.date_lookup_raw")
            .select("date", "week_part")
        )



# Die Tabelle 'user_events_raw' stellt die eingelesenen Benutzerereignisdaten im 
# JSON-Format dar, die anschließend entpackt und gefiltert werden, um ausschließlich 
# Benutzerinformationen abzurufen. 
@dp.table(
    partition_cols=["topic", "week_part"],
    table_properties={"quality": "bronze"}
)
def user_events_raw():
    # Die Streaming-Daten der Benutzer-Events aus der angegebenen Quelle lesen
    return (
      spark.readStream
        .format("cloudFiles")
        .schema("key BINARY, value BINARY, topic STRING, partition LONG, offset LONG, timestamp LONG")
        .option("cloudFiles.format", "json")
        .load(f"{daily_user_events_source}")
        .join(
          # Mit der Datums-Lookup-Tabelle verknüpfen, um den Wochenteil zu erhalten
          F.broadcast(dp.read("date_lookup")),  # Broadcast verteilt die Lookup-Tabelle an alle Executors
          F.to_date((F.col("timestamp")/1000).cast("timestamp")) == F.col("date"), "left") 
    )

        
users_schema = "user_id LONG, update_type STRING, timestamp FLOAT, dob STRING, sex STRING, gender STRING, first_name STRING, last_name STRING, address STRUCT<street_address: STRING, city: STRING, state: STRING, zip: INT>"    



# users_bronze: ist unser Schwerpunkt und wird unsere Quelle für die eingelesenen 
# Benutzerinformationen sein, auf die wir die Binning-Anonymisierung auf das 
# 'Date of Birth (dob)' anwenden werden.
@dp.table(
    table_properties={"quality": "bronze"}
)
def users_bronze():
    # Den rohen Stream der Benutzer-Events lesen und nach Aktualisierungen der Benutzerinfos filtern
    return (
        dp.read_stream("user_events_raw") # Reads from user_events_raw
          .filter("topic = 'user_info'")  # Filters topic with user_info
          # Unpacks the JSON
          .select(F.from_json(F.col("value").cast("string"), users_schema).alias("v")) 
          .select("v.*") # Alle Felder auswählen
          .select(
              # Die benötigten Spalten auswählen und transformieren
              F.col("user_id"),
              F.col("timestamp").cast("timestamp").alias("updated"),
              F.to_date("dob", "MM/dd/yyyy").alias("dob"),
              "sex", 
              "gender", 
              "first_name", 
              "last_name", 
              "address.*", 
              "update_type"
            )
    )


@dp.table
def user_age_bins():
    return (
        dp.read("users_bronze")
        .select(
            "user_id", 
            age_bins(F.col("dob")), 
            "gender", 
            "city", 
            "state")
    )
```
