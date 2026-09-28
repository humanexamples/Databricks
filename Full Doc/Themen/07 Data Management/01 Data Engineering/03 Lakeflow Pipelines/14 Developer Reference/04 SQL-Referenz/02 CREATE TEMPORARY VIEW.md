# `CREATE TEMPORARY VIEW` (Pipelines) — Referenz

## Abschnittsübersicht

1. [Grundzweck](#grundzweck)
2. [Formale Syntax](#syntax)
3. [Parameter](#parameter)
4. [Einschränkungen](#einschraenkungen)
5. [Doku-eigenes Beispiel](#doku-beispiel)
6. [Quellen](#quellen)

---

## <a id="grundzweck">1. Grundzweck</a>

Das Statement `CREATE TEMPORARY VIEW` erstellt temporäre Views in einer Pipeline.

---

## <a id="syntax">2. Formale Syntax</a>

```
CREATE TEMPORARY VIEW view_name
  [(
    [ col_name [ COMMENT col_comment ] [, ...] ]
    [ column_constraint ] [, ...]
  )]
  [ COMMENT view_comment ]
  [ TBLPROPERTIES ]
  AS query
```

### Reales Beispiel mit allen Bausteinen der formalen Syntax

Das folgende, aus den einzeln verifizierten Bausteinen dieses Dokuments zusammengesetzte Beispiel (kein wörtliches Einzelzitat einer Doku-Seite) kombiniert jeden optionalen Bestandteil der formalen Syntax gleichzeitig — Spaltenliste mit `COMMENT`, `column_constraint` als Datenqualitäts-Expectation, `COMMENT view_comment` und `TBLPROPERTIES`:

```sql
CREATE TEMPORARY VIEW valid_sales_by_rep (
  sale_day COMMENT 'Verkaufsdatum',
  total_sales COMMENT 'Tagesumsatz',
  sales_rep COMMENT 'Erster Vertriebsmitarbeiter des Tages',
  CONSTRAINT valid_total_sales EXPECT (total_sales > 0) ON VIOLATION DROP ROW
)
COMMENT 'Bereinigte, nach Verkaufstag aggregierte Umsätze'
TBLPROPERTIES ('quality' = 'silver')
AS SELECT date(sales_date) AS sale_day, SUM(sales) AS total_sales, FIRST(sales_rep)
FROM sales GROUP BY date(sales_date), sales_rep;
```

---

## <a id="parameter">3. Parameter</a>

- **`view_name`** — der Name der View.
- **`col_name`** — optional lassen sich Spalten für die resultierende View angeben. `col_name` ist ein Name für die Spalte.
- **`col_comment`** — bei Angabe von Spalten lässt sich optional eine Beschreibung für die Spalte angeben.
- **`column_constraint`**:
  - **`CONSTRAINT expectation_name EXPECT (expectation_expr) [ ON VIOLATION { FAIL UPDATE | DROP ROW } ]`** — fügt der View Datenqualitäts-Expectations hinzu, die über die Zeit nachverfolgt und über das Event-Log der Pipeline eingesehen werden können. Eine `FAIL UPDATE`-Expectation lässt die Verarbeitung sowohl beim Erstellen der View als auch beim Aktualisieren der Pipeline fehlschlagen. Eine `DROP ROW`-Expectation verwirft die gesamte Zeile, wenn die Expectation nicht erfüllt ist. `expectation_expr` darf aus Literalen, Spaltenbezeichnern innerhalb der View sowie deterministischen, eingebauten SQL-Funktionen oder Operatoren bestehen — mit Ausnahme von Aggregatfunktionen (einschließlich analytischer Window-Funktionen und Ranking-Window-Funktionen) sowie tabellenwertigen Generatorfunktionen; außerdem darf `expr` keine Subquery enthalten.
- **`view_comment`** — optionale Beschreibung für die View.
- **`TBLPROPERTIES`** — optionale Liste von Tabelleneigenschaften für die View.
- **`query`** — befüllt die View mit den Daten einer Abfrage. Werden eine Abfrage und eine Spaltenliste gemeinsam angegeben, muss die Spaltenliste alle von der Abfrage zurückgegebenen Spalten enthalten, sonst tritt ein Fehler auf. Angegebene, aber von `query` nicht zurückgegebene Spalten liefern beim Abfragen `null`-Werte.

---

## <a id="einschraenkungen">4. Einschränkungen</a>

- Temporäre Views bestehen nur über die Lebensdauer der Pipeline fort.
- Sie sind privat für die definierende Pipeline.
- Sie werden nicht dem Katalog hinzugefügt und können denselben Namen wie eine View im Katalog tragen. Haben innerhalb der Pipeline eine temporäre View und eine View oder Tabelle im Katalog denselben Namen, lösen Referenzen auf den Namen zur temporären View auf.

---

## <a id="doku-beispiel">5. Doku-eigenes Beispiel</a>

```sql
-- Create a temporary view, and use it
CREATE TEMPORARY VIEW my_view (sales_day, total_sales, sales_rep)
  AS SELECT date(sales_date) AS sale_day, SUM(sales) AS total_sales, FIRST(sales_rep) FROM sales GROUP BY date(sales_date), sales_rep;

CREATE OR REFRESH MATERIALIZED VIEW sales_by_date
  AS SELECT * FROM my_view;

-- Create a temporary view with a data quality expectation
CREATE TEMPORARY VIEW valid_sales (
  CONSTRAINT valid_total_sales EXPECT (total_sales > 0) ON VIOLATION DROP ROW
)
  AS SELECT date(sales_date) AS sales_day, SUM(sales) AS total_sales FROM sales GROUP BY date(sales_date);
```

---

## <a id="quellen">6. Quellen</a>

- CREATE TEMPORARY VIEW (pipelines) — SQL-Sprachreferenz (formale Syntax, alle Parameter, Einschränkungen, zwei Doku-Beispiele): https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-temporary-view

**Stand:** 2026-08-19.
