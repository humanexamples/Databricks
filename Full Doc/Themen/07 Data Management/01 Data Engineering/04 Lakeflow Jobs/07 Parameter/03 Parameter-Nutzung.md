# Parameterwerte in einem Task abrufen

Wie sich Parameterwerte im Code eines Tasks (Notebook, Python-Skript, SQL-Datei) lesen lassen — Parameter umfassen nutzerdefinierte Werte, Ausgaben vorgelagerter Tasks und job-generierte Metadaten.

## Vier gängige Methoden

1. Databricks-Utilities-Widgets (`dbutils.widgets`)
2. SQL-Named-Parameter-Syntax
3. Dynamische Wertreferenzen
4. Code-Argumente

Der Zugriff erfolgt über den Schlüssel (Parameternamen).

## `dbutils` im Notebook

```python
# Retrieve a job-level parameter
year_value = dbutils.widgets.get("year_param")
# Use the value in your code
display(babynames.filter(babynames.Year == year_value))
```

**Wichtig:** Teilen sich Job- und Task-Parameter denselben Schlüssel, hat der **Job-Parameter** Vorrang.

Für eigenständiges Testen außerhalb eines Jobs Standardwert setzen:

```python
# Set a default (for when not running in a job)
dbutils.widgets.text("year_param", "2012", "Year Parameter")
# Retrieve a job-level parameter (will use default if it doesn't exist)
year_value = dbutils.widgets.get("year_param")
display(babynames.filter(babynames.Year == year_value))
```

## Named Parameters in SQL

```sql
SELECT *
FROM baby_names_prepared
WHERE Year_Of_Birth = :year_param
GROUP BY First_Name
```

## Code-Argumente

Task-Typen mit Argument-Übergabe: Python Script, Python Wheel, JAR, Spark Submit. Bei dbt-Tasks erfolgt die Übergabe über dbt-Kommandos.

## Dynamische Wertreferenzen

Syntax `{{job.parameters.<name>}}` in der Task-Konfiguration, z. B. ein Parameterwert `Year_{{job.parameters.year_param}}`. Weitere zugängliche dynamische Werte, z. B. `{{job.id}}`.

## Übersicht je Task-Typ

| Task-Typ | Konfiguration | Code |
|---|---|---|
| Notebooks | dynamische Wertreferenzen in der UI; überschreibbar via „Run a job with different settings" | Named SQL Parameters oder `dbutils.widgets` |
| Python script | Parameter als Argumente übergeben; dynamische Wertreferenzen im Parameters-Feld | Positionale Argumente oder `argparse` |
| Python wheel | dynamische Wertreferenzen in Parameterwerten | Keyword-Argumente |
| SQL | dynamische Wertreferenzen in der Konfiguration | Named Parameters |
| Pipeline (Beta) | dynamische Wertreferenzen im Parameters-Feld | Named Parameters |
| Dashboard | Dashboard-Filter mit URL-Identifiern passend zu Parameter-Keys | — |
| Power BI | nicht unterstützt | nicht unterstützt |
| dbt | dynamische Wertreferenzen als dbt-Kommandos | dbt-Kommandos |
| JAR | dynamische Wertreferenzen im Parameters-Feld | Argumente an die Main-Methode |
| Spark Submit | dynamische Wertreferenzen im Parameters-Feld | Argumente an die Main-Methode |
| Run Job | dynamische Wertreferenzen für Job-Parameter | — |
| If/else condition | dynamische Wertreferenzen in der Condition | — |
| For each | dynamische Wertreferenzen in Inputs | abhängig vom verschachtelten Task-Typ |
| Clean room notebook | dynamische Wertreferenzen in der UI | Named SQL Parameters oder `dbutils.widgets` |

## Quelle

- https://docs.databricks.com/aws/en/jobs/parameter-use
