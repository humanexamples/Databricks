# cloudFiles.schemaEvolutionMode

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `addNewColumns`, wenn kein Schema angegeben ist; `none`, wenn ein Schema angegeben ist |
| **Gültige Werte** | `addNewColumns`, `addNewColumnsWithTypeWidening`, `rescue`, `failOnNewColumns`, `none` |
| **`read_files`-Parameter** | `schemaEvolutionMode` |
| **Seit** | alle Versionen; `addNewColumnsWithTypeWidening` ab Databricks Runtime 16.4 |

## Beschreibung

> „The mode for evolving the schema as new columns are discovered in the data."

Steuert, wie Auto Loader auf neu auftauchende Spalten reagiert.

| Modus | Verhalten |
|---|---|
| `addNewColumns` | Stream schlägt mit `UnknownFieldException` fehl, nachdem die neuen Spalten ins Schema aufgenommen wurden; Neustart setzt fort. |
| `addNewColumnsWithTypeWidening` | Wie `addNewColumns`, erweitert zusätzlich kompatible Typen (z. B. `int`→`long`). |
| `rescue` | Schema entwickelt sich nie weiter; kein Fehlschlag; neue Spalten landen in `_rescued_data`. |
| `failOnNewColumns` | Stream schlägt fehl und startet nicht neu, bis Schema aktualisiert oder Datei entfernt. |
| `none` | Keine Evolution, neue Spalten ignoriert, keine Rettung (außer `rescuedDataColumn` gesetzt). |

`addNewColumns` ist nicht erlaubt bei explizitem `schema`, funktioniert aber mit `schemaHints`.

## Beispiel

```python
.option("cloudFiles.schemaEvolutionMode", "rescue")
```

## Siehe auch

- [../01 Schema-Inferenz und -Evolution.md](../01%20Schema-Inferenz%20und%20-Evolution.md)
- [../02 Automatisches Type Widening.md](../02%20Automatisches%20Type%20Widening.md)
