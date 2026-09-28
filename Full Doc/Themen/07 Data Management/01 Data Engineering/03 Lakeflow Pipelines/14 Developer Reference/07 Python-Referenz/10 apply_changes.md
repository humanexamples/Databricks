# `create_auto_cdc_flow` (`apply_changes`) — Python-Referenz

## Abschnittsübersicht

1. [Zweck und Vorgänger-Funktion](#zweck)
2. [Vollständige Signatur](#signatur)
3. [Parameter](#parameter)
4. [Rückgabewert](#rueckgabe)
5. [Voraussetzung: Zieltabelle](#zieltabelle)
6. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck und Vorgänger-Funktion</a>

`create_auto_cdc_flow()` erzeugt einen Flow, der Quelldaten aus Change-Data-Feeds (CDF) mittels CDC-Funktionalität (Change Data Capture) verarbeitet. Die Doku stellt klar: *"This function replaces the previous function `apply_changes()`"* — mit identischer Signatur. `apply_changes()` ist also die ältere Bezeichnung derselben Funktion.

---

## <a id="signatur">2. Vollständige Signatur</a>

```python
from pyspark import pipelines as dp

dp.create_auto_cdc_flow(
  target = "<target-table>",
  source = "<data-source>",
  keys = ["key1", "key2", "keyN"],
  sequence_by = "<sequence-column>",
  system_sequence_by = None,
  ignore_null_updates = False,
  ignore_null_updates_column_list = None,
  ignore_null_updates_except_column_list = None,
  columns_to_update = None,
  apply_as_deletes = None,
  apply_as_truncates = None,
  column_list = None,
  except_column_list = None,
  stored_as_scd_type = "1",
  track_history_column_list = None,
  track_history_except_column_list = None,
  name = None,
  once = False
)
```

---

## <a id="parameter">3. Parameter</a>

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| `target` | `str` | — | Erforderlich. Name der zu aktualisierenden Tabelle. Über `create_streaming_table()` lässt sich die Zieltabelle vor Aufruf von `create_auto_cdc_flow()` anlegen. |
| `source` | `str` | — | Erforderlich. Die CDC-Datenquelle (Datenquelle, die die CDC-Datensätze enthält). |
| `keys` | `list` | — | Erforderlich. Spalte(n), die eine Zeile in den Quelldaten eindeutig identifizieren. Akzeptiert Listen von Strings oder Spark-SQL-`col()`-Funktionen. |
| `sequence_by` | `str`, `col()` oder `struct()` | — | Erforderlich. Spaltenname(n), die die logische Reihenfolge der CDC-Ereignisse in den Quelldaten festlegen. Muss ein sortierbarer Datentyp sein. |
| `system_sequence_by` | `str` oder `col()` | `None` | Spalte, die den Systemzeitpunkt angibt, zu dem jedes CDC-Ereignis dem System bekannt wurde. Wird zusammen mit `stored_as_scd_type="bitemporal"` verwendet. |
| `ignore_null_updates` | `bool` | `False` | Steuert, wie Nullwerte in eingehenden CDC-Updates behandelt werden. |
| `ignore_null_updates_column_list` | `list` | `None` | Teilmenge von Spalten, für die Nullwerte in einem eingehenden Change-Datensatz ignoriert werden. |
| `ignore_null_updates_except_column_list` | `list` | `None` | Teilmenge von Spalten, die explizite Nullwerte anwenden. Alle übrigen Spalten ignorieren Nullwerte. |
| `columns_to_update` | `str` oder `col()` | `None` | Name einer Quellspalte, die pro Change-Datensatz die zu aktualisierende Spaltenmenge als Array von Spaltennamen-Strings enthält. |
| `apply_as_deletes` | `str` oder `expr()` | `None` | Legt fest, wann ein CDC-Ereignis als DELETE statt als Upsert behandelt werden soll. |
| `apply_as_truncates` | `str` oder `expr()` | `None` | Legt fest, wann ein CDC-Ereignis als vollständiges TRUNCATE der Tabelle behandelt werden soll. |
| `column_list` | `list` | `None` | Teilmenge der in die Zieltabelle zu übernehmenden Spalten. |
| `except_column_list` | `list` | `None` | Von der Zieltabelle auszuschließende Spalten. |
| `stored_as_scd_type` | `str` oder `int` | `"1"` | Ob Datensätze als SCD Type 1, SCD Type 2 oder bitemporal gespeichert werden. Standard: SCD Type 1. |
| `track_history_column_list` | `list` | `None` | Teilmenge der Ausgabespalten, deren Historie in der Zieltabelle nachverfolgt werden soll. |
| `track_history_except_column_list` | `list` | `None` | Von der Historiennachverfolgung auszuschließende Spalten. |
| `name` | `str` | Wert von `target` | Der Flow-Name. Wenn nicht angegeben, entspricht er standardmäßig dem Wert von `target`. |
| `once` | `bool` | `False` | Definiert den Flow optional als einmaligen Flow, z. B. für einen Backfill. |

**Hinweis zu `column_list`/`except_column_list` sowie `track_history_column_list`/`track_history_except_column_list`:** Jeweils nur einer der beiden Parameter eines Paares wird gleichzeitig angegeben (Einschluss- vs. Ausschlussliste).

---

## <a id="rueckgabe">4. Rückgabewert</a>

Streaming-DataFrame (bzw. Batch-DataFrame, wenn `once=True`).

---

## <a id="zieltabelle">5. Voraussetzung: Zieltabelle</a>

Vor dem Aufruf von `create_auto_cdc_flow()` muss die Zieltabelle typischerweise über `create_streaming_table()` angelegt werden (siehe [streaming_table.md](streaming_table.md)) — ein Muster, das auch in `_fileIngestionScenarios.md` dieses Projekts (Abschnitt zu wachsenden Dateien) für die verwandte Funktion `create_auto_cdc_from_snapshot_flow()` verwendet wird.

**Ungeklärt:** Die per WebFetch abgerufene Doku-Zusammenfassung enthielt keine vollständigen, eigenständigen Codebeispiele für SCD Type 1 vs. SCD Type 2 auf dieser Seite — laut zweitem Abruf liefert die Doku hierzu nur ein einziges Syntaxbeispiel mit allen verfügbaren Parametern und deren Defaults, keine ausgearbeiteten SCD-1-/SCD-2-Einzelbeispiele.

---

## <a id="quellen">6. Quellen</a>

- create_auto_cdc_flow (apply_changes) (vollständige Signatur, Parametertabelle, Hinweis auf Vorgänger-Funktion `apply_changes()`): https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-apply-changes

**Stand:** 2026-08-19.
