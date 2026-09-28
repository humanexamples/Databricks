# 14L Bonus - Adding ML to Engineering Workflows with DABs/Solution - Lab DABs Workflow/src/Inference.py

*(Databricks-Notebook, konvertiert nach Markdown)*

# Inferenz auf der Silber-Tabelle

Zweck dieses Notebooks ist es, eine Inferenz auf der im Katalog `dev` gespeicherten Streaming Table durchzuführen. Das hier verwendete Modell wurde im Classroom-Setup-Skript des zugehörigen Labs erstellt. 

## Schritte:
1. Die Streaming Table einlesen und einige Datentransformationen durchführen, um sie als Eingabe für unser Modell vorzubereiten. 
1. Ein vortrainiertes Modell aus Unity Catalog laden. Es befindet sich im Staging-Katalog. 
1. Auf den ersten 2 Zeilen der transformierten Streaming Table eine Vorhersage treffen, um unsere Silber-Schicht für das ML-Team zu validieren.

## Das Notebook für unseren Workflow parametrisieren und Variablen übergeben

```python
base_model_name = dbutils.widgets.get("base_model_name") # In der Parametrisierung des Notebooks im Workflow auf "diabetes_model_dev" gesetzt 
silver_table_name = dbutils.widgets.get('silver_table_name')# Auf "<username>_1_dev.default.health_silver" gesetzt
catalog_name = dbutils.widgets.get('catalog_name')# Auf "<username>_1_dev.default.diabetes_model_dev" gesetzt
print(base_model_name)
print(silver_table_name)
print(catalog_name)
```

```sql
SELECT current_catalog(), current_schema()
```

## Schritt 1: Die Streaming Table der Silber-Schicht lesen und transformieren.

```python
from mlflow.tracking import MlflowClient
import mlflow 

from pyspark.sql.functions import col, log, pow
from pyspark.ml.feature import VectorAssembler
from pyspark.sql.streaming import StreamingQueryListener
from pyspark.sql import DataFrame

# Eine Funktion erstellen, die Spalten für die Inferenz auf Streaming-Daten transformiert
def create_streaming_features(silver_table: str) -> DataFrame:
    # Read streaming data
    stream_df = (
        spark.read
        .table(silver_table)  # Setzt voraus, dass eine Streaming Table in Unity Catalog registriert ist
    )

    # Die Daten transformieren, sodass die benötigten berechneten Features enthalten sind
    transformed_stream_df = (
        stream_df
        .withColumn("log_BMI", log(col("BMI") + 1))
        .withColumn("log_Age", log(col("Age") + 1))
        .withColumn("BMI_squared", pow(col("BMI"), 2))
        .drop("PII", "date")
        .na.drop()
    )

    # Sicherstellen, dass die Features wie beim Training transformiert werden
    assembler = VectorAssembler(
        inputCols=["HighCholest", "HighBP", "BMI", "Age", "Education", "income", "log_BMI", "log_Age", "BMI_squared"], 
        outputCol="features"
    )
    stream_features = assembler.transform(transformed_stream_df)
    print("Silver table successfully transformed!")
    return stream_features
```

## Schritt 2: Das vortrainierte Modell laden.

```python
from pyspark.ml import PipelineModel

def load_ml_model(env: str) -> PipelineModel:
    model_base_name = base_model_name
    full_model_name = f"{catalog_name}.default.{model_base_name}"

    # Die neueste Version des Modells abrufen
    client = MlflowClient()
    model_version_infos = client.search_model_versions(f"name = '{full_model_name}'")

    if model_version_infos:
        latest_version = max([int(info.version) for info in model_version_infos])
        model_uri = f"models:/{full_model_name}/{latest_version}"
        print(f"Found model {full_model_name} in {env}")
        print(f"Loading model version {latest_version} from MLflow...")
        return mlflow.spark.load_model(model_uri)  # Ensure correct model loading
    else:
        raise ValueError(f"No registered versions of {full_model_name} found.")
```

## Schritt 3: Auf der transformierten Streaming Table eine Vorhersage treffen und die Ergebnisse ausgeben.

```python
from pyspark.ml import PipelineModel



def make_prediction(sample_df: DataFrame, loaded_model: PipelineModel):
    """
    Applies feature transformation and runs inference using the loaded model.
    """
    feature_cols = [
        "HighCholest",  
        "HighBP",
        "BMI",
        "Age",
        "Education",
        "income",
        "log_BMI",
        "log_Age",
        "BMI_squared"
    ]

    # Sicherstellen, dass alle benötigten Spalten existieren
    missing_cols = [col for col in feature_cols if col not in sample_df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in input DataFrame: {missing_cols}")

    # Check if 'features' column already exists
    if "features" not in sample_df.columns:
        assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
        sample_df = assembler.transform(sample_df)

    print("Inferenceing sample silver table data...")
    # Perform inference
    predictions = loaded_model.transform(sample_df)
    
    return predictions.select("prediction")  # Return only predictions
```

```python
silver_df = create_streaming_features(f'{catalog_name}.default.{silver_table_name}')
loaded_model = load_ml_model('dev')
sample_prediction = make_prediction(silver_df, loaded_model)
display(sample_prediction)
```
