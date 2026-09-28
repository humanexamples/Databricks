# 13 Demo - Continuous Integration and Continuous Deployment with DABs/Full Project/src/Final Visualization.py

*(Databricks-Notebook, konvertiert nach Markdown)*

# Finale Visualisierung

Den Job-Parameter abrufen und in der Variablen **my_catalog** speichern.

```python
my_catalog = dbutils.widgets.get('catalog_name')
target = dbutils.widgets.get('target')
print(f'Accessing the {target} pipeline')
```

Die Visualisierung für **chol_age_agg** erstellen.

```python
def create_pandas_df(catalog, schema, table):
    df_spark = spark.sql(f"SELECT * FROM {catalog}.default.{table}")
    df_pandas = df_spark.toPandas()
    return df_pandas

df_pandas = create_pandas_df(catalog = my_catalog, schema = 'default', table = 'chol_age_agg')
df_pandas.head()
```

```python
def create_stacked_bar_chart(pandas_df):
    import pandas as pd
    import matplotlib.pyplot as plt


    # Den DataFrame pivotieren
    df_pivot = pandas_df.pivot_table(index='Age_Group', columns='HighCholest_Group', values='Total', aggfunc='sum', fill_value=0)

    # Das gestapelte Balkendiagramm zeichnen
    ax = df_pivot.plot(kind='bar', stacked=True, figsize=(10, 6))

    # Titel und Beschriftungen
    plt.title('Cholesterol Group Distribution by Age Group', fontsize=14)
    plt.xlabel('Age Group', fontsize=12)
    plt.ylabel('Total Count', fontsize=12)

    # Das Diagramm anzeigen
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

create_stacked_bar_chart(df_pandas)
```
