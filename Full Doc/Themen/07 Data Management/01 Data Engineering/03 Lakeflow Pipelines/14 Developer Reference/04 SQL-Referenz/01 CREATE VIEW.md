# `CREATE VIEW` (Pipelines) — Referenz

## Abschnittsübersicht

1. [Grundzweck](#grundzweck)
2. [Formale Syntax](#syntax)
3. [Parameter](#parameter)
4. [Notwendige Berechtigungen](#berechtigungen)
5. [Einschränkungen](#einschraenkungen)
6. [Doku-eigene Beispiele](#doku-beispiele)
7. [Quellen](#quellen)

---

## <a id="grundzweck">1. Grundzweck</a>

Das Statement `CREATE VIEW` konstruiert in einer Pipeline eine virtuelle Tabelle ohne physische Daten, basierend auf dem Ergebnis einer SQL-Abfrage.

---

## <a id="syntax">2. Formale Syntax</a>

```
CREATE VIEW view_name
  [ COMMENT view_comment ]
  [ TBLPROPERTIES ]
  AS query
```

### Reales Beispiel mit allen Bausteinen der formalen Syntax

Das folgende, aus den einzeln verifizierten Bausteinen dieses Dokuments zusammengesetzte Beispiel (kein wörtliches Einzelzitat einer Doku-Seite) kombiniert jeden optionalen Bestandteil der formalen Syntax gleichzeitig — `COMMENT` und `TBLPROPERTIES`:

```sql
CREATE VIEW main.sales.taxi_silver
COMMENT 'Gefilterte Taxifahrten mit positiver Distanz'
TBLPROPERTIES ('quality' = 'silver')
AS SELECT * FROM main.sales.taxi_raw
WHERE distance > 0.0;
```

---

## <a id="parameter">3. Parameter</a>

- **`view_name`** — der Name der View. Der Name muss innerhalb des von der Pipeline anvisierten Katalogs und Schemas eindeutig sein.
- **`view_comment`** — optionale Beschreibung für die View.
- **`TBLPROPERTIES`** — optionale Liste von Tabelleneigenschaften für die Tabelle.
- **`query`** — eine Abfrage, die die View aus Basistabellen oder anderen Views konstruiert.

---

## <a id="berechtigungen">4. Notwendige Berechtigungen</a>

Der Run-as-Nutzer der Pipeline benötigt folgende Berechtigungen, um eine View erstellen zu können:

- `SELECT`-Privileg auf die von der View referenzierten Basistabellen.
- `USE CATALOG`-Privileg auf den übergeordneten Katalog und `USE SCHEMA`-Privileg auf das übergeordnete Schema.
- `CREATE TABLE`-Privileg auf das Schema für die View.

Um die View innerhalb der Pipeline aktualisieren zu können, sind erforderlich:

- `USE CATALOG`-Privileg auf den übergeordneten Katalog und `USE SCHEMA`-Privileg auf das übergeordnete Schema.
- `MANAGE`-Berechtigung für die View.
- `SELECT`-Privilegien auf die von der View referenzierten Basistabellen.

Um die resultierende View abfragen zu können, sind erforderlich:

- `USE CATALOG`-Privileg auf den übergeordneten Katalog und `USE SCHEMA`-Privileg auf das übergeordnete Schema.
- `SELECT`-Privileg auf die View.

---

## <a id="einschraenkungen">5. Einschränkungen</a>

- `CREATE VIEW` ist nur in Pipelines verfügbar, die den Standard-Publishing-Modus unterstützen. Pipelines, die das `LIVE`-Schema (Legacy) verwenden, werden nicht unterstützt.
- Die Pipeline muss eine Unity-Catalog-Pipeline sein.
- Expectations in Form von `CONSTRAINT`-Klauseln werden nicht unterstützt.
- Views dürfen keine Streaming-Abfragen enthalten und nicht als Streaming-Quelle verwendet werden.
- Kommentare werden für in einer Pipeline erstellte Views nicht unterstützt.

---

## <a id="doku-beispiele">6. Doku-eigene Beispiele</a>

```sql
-- Create a view from an external data source
CREATE VIEW taxi_raw AS SELECT *
  FROM read_files("/databricks-datasets/nyctaxi/sample/json/");

-- Use a view to create a filtered view:
CREATE VIEW taxi_silver AS SELECT *
  FROM taxi_raw
  WHERE distance > 0.0;
```

---

## <a id="quellen">7. Quellen</a>

- CREATE VIEW (pipelines) — SQL-Sprachreferenz (formale Syntax, alle Parameter, notwendige Berechtigungen, Einschränkungen, zwei Doku-Beispiele): https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-view

**Stand:** 2026-08-19.
