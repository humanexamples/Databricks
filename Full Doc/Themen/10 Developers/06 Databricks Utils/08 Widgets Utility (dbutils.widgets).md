# Widgets Utility (`dbutils.widgets`)

Befehle zur Parametrisierung von Notebooks über interaktive Eingabeelemente. Teil der [Databricks Utils](00%20Uebersicht.md)-Reihe.

## Verfügbarkeit

Alle Befehle in Python, R, Scala und SQL nutzbar, sofern nicht anders angegeben. Python nutzt `snake_case` für Keyword-Argumente (z. B. `default_value` statt `defaultValue`). Widget-Werte werden stets als String zurückgegeben.

## Eingabewidgets erstellen

| Befehl | Signatur | Auswahltyp | Eingabemethode |
|---|---|---|---|
| `text` | `text(name: String, defaultValue: String, label: String): void` | — | freie Texteingabe |
| `dropdown` | `dropdown(name: String, defaultValue: String, choices: Seq, label: String): void` | einfach | vordefinierte Liste |
| `combobox` | `combobox(name: String, defaultValue: String, choices: Seq, label: String): void` | einfach | vordefinierte Liste + Textsuche |
| `multiselect` | `multiselect(name: String, defaultValue: String, choices: Seq, label: String): void` | mehrfach | vordefinierte Liste (Checkboxen) |

```python
dbutils.widgets.text(
  name='your_name_text',
  defaultValue='Enter your name',
  label='Your name')

dbutils.widgets.dropdown(
  name='toys_dropdown',
  defaultValue='basketball',
  choices=['alphabet blocks', 'basketball', 'cape', 'doll'],
  label='Toys')

dbutils.widgets.combobox(
  name='fruits_combobox',
  defaultValue='banana',
  choices=['apple', 'banana', 'coconut', 'dragon fruit'],
  label='Fruits')

dbutils.widgets.multiselect(
  name='days_multiselect',
  defaultValue='Tuesday',
  choices=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
  label='Days of the Week')
```

## Werte lesen

| Befehl | Signatur | Beschreibung |
|---|---|---|
| `get` | `get(name: String): String` | liefert den aktuellen Wert eines Widgets — dient auch dem Abruf von an einen Notebook-Task übergebenen Parametern |
| `getAll` | `getAll: map` | liefert ein Dictionary aller Widget-Namen samt aktuellem Wert — ab Databricks Runtime 13.3 LTS, **nur Python und Scala** |
| `getArgument` (deprecated) | `getArgument(name: String, optional: String): String` | wie `get`, mit optionalem Fallback-Text, falls das Widget fehlt — durch `get()` ersetzt |

```python
dbutils.widgets.get('fruits_combobox')
# Rückgabe: banana

# getAll() eignet sich, um mehrere Widget-Werte gebündelt an eine Spark-SQL-Query zu übergeben:
df = spark.sql("SELECT * FROM table where col1 = :param",
               dbutils.widgets.getAll())
```

## Widgets entfernen

| Befehl | Signatur | Beschreibung |
|---|---|---|
| `remove` | `remove(name: String): void` | löscht ein einzelnes Widget anhand seines Namens |
| `removeAll` | `removeAll: void` | löscht alle Widgets des Notebooks gleichzeitig |

```python
dbutils.widgets.remove('fruits_combobox')
dbutils.widgets.removeAll()
```

**Wichtig:** Nach einem Remove-Befehl kann in derselben Zelle **kein** neues Widget erstellt werden.

## Hilfe

```python
dbutils.widgets.help()
dbutils.widgets.help("combobox")
```

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/databricks-utils#widgets-utility-dbutilswidgets

**Stand:** 2026-08-26.
