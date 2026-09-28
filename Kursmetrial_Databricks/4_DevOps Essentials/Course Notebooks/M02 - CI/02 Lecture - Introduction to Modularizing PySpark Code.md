# Vorlesung – Einführung in die Modularisierung von PySpark-Code

## (Vorher)

### Probleme

- **Alles steckt in einem Block** – Dadurch wird es schwieriger, bestimmte Teile zu ändern oder zu testen, etwa das Laden von Daten oder das Hinzufügen neuer Spalten.
- **Code-Duplizierung** – Kann auftreten, wenn dieselben Operationen an anderer Stelle im Projekt benötigt werden.

**Nicht modularisierter Code (Vorher)**

```python
# Load data
df = (spark
      .read
      .csv("health.csv",
           header=True,
           inferSchema=True))

# Create column
df = (df
      .withColumn("NewColumn",
          when(col("Column") == 0, 'Normal')
          .otherwise('Unknown')))
```

## (Nachher)

Vorteile der Modularisierung:

1. **Einfachere Wartung** – Aktualisieren Sie nur bestimmte Funktionen, ohne das gesamte Skript zu ändern.
2. **Wiederverwendung** – Verwenden Sie Funktionen in verschiedenen Projekten wieder.
3. **Testen** – Testen Sie einzelne Funktionen mit Unit-Tests, um die Zuverlässigkeit des Codes sicherzustellen.

**Nicht modularisierter Code**

```python
def load_data(file_path):
    return (spark
            .read
            .csv(file_path,
                 header=True,
                 inferSchema=True))


def add_new_col(df, new, s_col):
    return (df
            .withColumn(new,
                when(col(s_col) == 0, 'Normal')
                .otherwise('Unknown')))
```

- **`load_data()`** – Verwandelt den Code zum Einlesen der CSV-Datei in eine wiederverwendbare Funktion.
- **`add_new_col()`** – Strukturiert die Logik zur Spaltenerstellung in eine wiederverwendbare Funktion um
