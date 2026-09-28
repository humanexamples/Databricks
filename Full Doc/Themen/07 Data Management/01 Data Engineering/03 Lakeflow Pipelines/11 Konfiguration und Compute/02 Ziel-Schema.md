# Ziel-Catalog und -Schema festlegen

Dieses Dokument fasst die Databricks-Referenzseite "Set the target catalog and schema" zusammen. Verifiziert per `WebFetch` gegen die AWS-Seite (`docs.databricks.com/aws/en/ldp/target-schema`) und wörtlich vollständig extrahiert von der inhaltlich übereinstimmenden Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/target-schema`).

## Abschnittsübersicht

1. [Default Location for Data Assets](#default-location)
2. [Ein Dataset in einem anderen Catalog oder Schema ansprechen](#anderes-schema)
3. [USE CATALOG / USE SCHEMA](#use-catalog-schema)
4. [Verhalten bei nicht existierenden Datasets](#nicht-existierend)
5. [Quellen](#quellen)

---

## <a id="default-location">1. Default Location for Data Assets</a>

Der Abschnitt **Default location for data assets** der Pipeline-Konfigurations-UI legt den Standard-Catalog und das Standard-Schema für eine Pipeline fest. Dieser Standard-Catalog und dieses Standard-Schema werden für alle Dataset-Definitionen und Tabellen-Lesevorgänge verwendet, sofern nicht innerhalb der Query überschrieben.

**Hinweis aus der Doku:** Der Legacy-Publishing-Modus verwendet das virtuelle `LIVE`-Schema, um ein ähnliches Verhalten zu erreichen. Im Standard-Publishing-Modus (verwendet von allen neuen Pipelines) wird das `LIVE`-Schlüsselwort ignoriert.

## <a id="anderes-schema">2. Ein Dataset in einem anderen Catalog oder Schema ansprechen</a>

Lakeflow-Pipelines unterstützen die dreistufige Identifier-Resolution-Semantik (Three-Tier Identifier Resolution). Databricks empfiehlt, für Queries und Anweisungen, die andere Datasets als die für die Pipeline konfigurierten Standardwerte ansprechen, vollständig qualifizierte Identifier zu verwenden.

Beispiel aus der Doku: Um eine Materialized View namens `regional_sales` im Catalog `main` und Schema `stores` zu erstellen — die nicht den Pipeline-Standardwerten entsprechen — wird der Name vollständig qualifiziert als `main.stores.regional_sales` angegeben:

```python
from pyspark import pipelines as dp

@dp.materialized_view(name="main.stores.regional_sales")
def func():
  return spark.read.table("partners");
```

```sql
CREATE OR REPLACE MATERIALIZED VIEW main.stores.regional_sales
  AS SELECT *
  FROM partners;
```

## <a id="use-catalog-schema">3. USE CATALOG / USE SCHEMA</a>

Pipelines unterstützen die SQL-Befehle `USE CATALOG catalog_name` und `USE SCHEMA schema_name`. Diese Befehle setzen den aktuellen Catalog und das aktuelle Schema, gültig nur für die Datei bzw. das Notebook, das diese Befehle enthält. Operationen, die im Quellcode nach diesen Befehlen folgen und unqualifizierte oder teilweise qualifizierte Identifier verwenden, lösen sich gegen den aktuellen Catalog und das aktuelle Schema auf — statt gegen die in der Pipeline-Konfiguration gesetzten Standardwerte.

## <a id="nicht-existierend">4. Verhalten bei nicht existierenden Datasets</a>

Wörtlich übernommene Verhaltenstabelle aus der Doku:

| Operation | Ergebnis |
|---|---|
| Read | Existiert für den angegebenen Identifier keine Tabelle, Materialized View, Streaming Table oder View, schlägt das Update fehl. |
| Write | Existiert für den angegebenen Identifier keine Materialized View, Streaming Table, View oder kein Sink, versucht das Update, das Dataset zu erstellen. Falls nötig, erstellt das Update auch das angegebene Schema. |

**Wichtiger Hinweis aus der Doku:** Es kann eine Fehlermeldung erscheinen, dass ein Dataset nicht existiert, obwohl tatsächlich nur unzureichende Berechtigungen zum Einsehen des Datasets vorliegen. Ausreichende Berechtigungen zum Lesen, Schreiben und Erstellen von Datasets mit Lakeflow-Pipelines sind erforderlich.

---

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/target-schema
- https://learn.microsoft.com/en-us/azure/databricks/ldp/target-schema (wörtliche Vollzitat-Quelle, inhaltlich mit AWS-Seite abgeglichen)
