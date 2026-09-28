# `create_auto_cdc_from_snapshot_flow` (`apply_changes_from_snapshot`) — Python-Referenz

## Abschnittsübersicht

1. [Zweck](#zweck)
2. [Vollständige Signatur](#signatur)
3. [Parameter](#parameter)
4. [Die Snapshot-Lambda-Funktion](#lambda)
5. [Codebeispiel](#beispiel)
6. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck</a>

`create_auto_cdc_from_snapshot_flow()` ist eine Python-exklusive Funktion (siehe [SQL vs Python.md](../SQL%20vs%20Python.md) Abschnitt 5), die Änderungen zwischen aufeinanderfolgenden Snapshots derselben Quelle automatisch erkennt (Inserts/Updates/Deletes) und auf eine Zieltabelle anwendet — in diesem Projekt bereits in `_fileIngestionScenarios.md` (Ordner "Working with Files", Abschnitt zu wachsenden/vollständig überschriebenen Dateien) als Lösungsweg für vollständige Snapshot-Quellen referenziert.

---

## <a id="signatur">2. Vollständige Signatur</a>

```python
from pyspark import pipelines as dp

dp.create_auto_cdc_from_snapshot_flow(
  target = "<target-table>",
  source = Any,
  keys = ["key1", "key2", "keyN"],
  stored_as_scd_type = "1",
  track_history_column_list = None,
  track_history_except_column_list = None)
```

---

## <a id="parameter">3. Parameter</a>

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| `target` | `str` | — | Erforderlich. Name der zu aktualisierenden Tabelle, angelegt über `create_streaming_table()`. |
| `source` | `str` oder Lambda-Funktion | — | Erforderlich. Tabellen-/View-Name oder eine Python-Lambda-Funktion, die eine Snapshot-DataFrame und eine Version zurückgibt. |
| `keys` | `list` | — | Erforderlich. Spalte(n), die eine Zeile eindeutig identifizieren; akzeptiert Strings oder unqualifizierte Spark-`col()`-Funktionen. |
| `stored_as_scd_type` | `str` oder `int` | `"1"` | SCD-Speichertyp: `"1"` (Default) oder `"2"`. |
| `track_history_column_list` | `list` | `None` | Optional zu verfolgende Spalten für die Historiennachverfolgung; Strings oder `col()`-Funktionen. Standardmäßig alle Spalten. |
| `track_history_except_column_list` | `list` | `None` | Alternative Ausschlussliste für die Historiennachverfolgung. |

---

## <a id="lambda">4. Die Snapshot-Lambda-Funktion</a>

Wird `source` als Lambda-Funktion übergeben, hat sie folgende Signatur:

```python
lambda Any => Optional[(DataFrame, Any)]
```

Die Pipeline-Laufzeit ruft diese Funktion wiederholt auf und lädt Snapshots samt zugehöriger Version, bis `None` zurückgegeben wird.

Beispielhafte Implementierung:

```python
def next_snapshot_and_version(latest_snapshot_version: Optional[int]) -> Tuple[DataFrame, Optional[int]]:
  if latest_snapshot_version is None:
    return (spark.read.load("filename.csv"), 1)
  else:
    return None

create_auto_cdc_from_snapshot_flow(
  # ...
  source = next_snapshot_and_version,
  # ...)
```

---

## <a id="beispiel">5. Codebeispiel</a>

Anwendung des in diesem Projekt bereits über `_fileIngestionScenarios.md` referenzierten Musters (dort für eine wachsende CSV-Log-Datei):

```python
from pyspark import pipelines as dp

@dp.view(name="source")
def source():
  return spark.read.format("csv").option("header", True).load("/Volumes/main/landing/growing_log.csv")

dp.create_streaming_table("target")
dp.create_auto_cdc_from_snapshot_flow(
  target = "target",
  source = "source",
  keys = ["log_id"],
  stored_as_scd_type = 1)
```

**Abweichung zum in `_fileIngestionScenarios.md` verwendeten Beispiel:** Dieses in `_fileIngestionScenarios.md` verwendete Beispiel dekoriert die Quellfunktion mit `@dp.view(name="source")`. Die für dieses Projekt verifizierte Referenzseite zum View-Dekorator ([view.md](view.md)) dokumentiert unter der URL `ldp-python-ref-view` jedoch ausschließlich `@dp.temporary_view` (bzw. `@dp.temporary_view()`) als aktuellen Dekoratornamen im `pyspark.pipelines`-Modul; ein Dekorator namens `dp.view` wird auf dieser Referenzseite nicht dokumentiert — laut Doku existierte `@view` nur im älteren `dlt`-Modul (`@dlt.view` bzw. importiert als `view`), das laut Doku durch `pyspark.pipelines`/`@dp.temporary_view` abgelöst wurde. Diese Diskrepanz wird hier nur benannt, nicht korrigiert (siehe Abschlussbericht).

Ebenso übergibt `stored_as_scd_type = 1` in diesem Beispiel einen `int`-Literalwert, während die offizielle Signatur oben den Default `"1"` als String zeigt — laut Parametertabelle ist sowohl `str` als auch `int` als Typ zulässig.

---

## <a id="quellen">6. Quellen</a>

- create_auto_cdc_from_snapshot_flow (apply_changes_from_snapshot) (vollständige Signatur, Parametertabelle, Lambda-Signatur, Codebeispiel): https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-apply-changes-from-snapshot
- Cross-Referenz-Quelle innerhalb dieses Projekts (verwendetes `@dp.view`/`stored_as_scd_type`-Beispiel): `Lakeflow Connect/Lakeflow Connect Standard Connectors/Working with Files/_fileIngestionScenarios.md`

**Stand:** 2026-08-19.
