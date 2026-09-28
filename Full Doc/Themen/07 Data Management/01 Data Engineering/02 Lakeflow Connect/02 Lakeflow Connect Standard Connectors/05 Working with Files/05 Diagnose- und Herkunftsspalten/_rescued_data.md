# Rescued Data Column — Referenz

Dieses Dokument fasst die Rescued-Data-Column (`_rescued_data`) werkzeugübergreifend zusammen — für `read_files`, `spark.read` und Auto Loader. Ein Teil der Fakten war bereits in `_read_files.md` (Abschnitt 13), `_spark_read.md` (Abschnitt 9) und `../06 Auto Loader/01 Schema-Inferenz und -Evolution.md` (Abschnitt Rescued-Data-Column) verifizert und wird hier themenzentriert neu zusammengeführt; die darüber hinausgehenden Details (Extraktions-Syntax, JSON-Struktur, Mindest-Runtime) wurden für dieses Dokument zusätzlich per `WebFetch` gegen die offizielle Databricks-Dokumentation verifiziert (teils zweifach, AWS- und Azure-Spiegelseite).

## Abschnittsübersicht

1. [Grundzweck](#grundzweck)
2. [Wann wird eine Spalte gerettet?](#wann-gerettet)
3. [Aktivierung und Standardverhalten je Werkzeug](#aktivierung)
4. [Struktur des Inhalts](#struktur)
5. [Werte aus der Rescued-Data-Spalte extrahieren](#extraktion)
6. [Zusammenspiel mit den Parser-Modi](#parser-modi)
7. [Abgrenzung zu `_corrupt_record`/`badRecordsPath`](#abgrenzung)
8. [Groß-/Kleinschreibung (nur Auto Loader)](#case-sensitivity)
9. [Eigenes Beispiel aus Kursmaterial](#eigenes-beispiel)
10. [Quellen](#quellen)

---

## <a id="grundzweck">1. Grundzweck</a>

Die Rescued-Data-Spalte stellt sicher, dass beim Einlesen keine Daten stillschweigend verloren gehen: Statt Datensätze zu verwerfen, deren Inhalt nicht zum (inferierten oder explizit angegebenen) Schema passt, werden die betroffenen Werte in einer separaten Spalte "gerettet" und bleiben so für spätere Inspektion oder Nachbearbeitung erhalten. Verfügbar seit **Databricks Runtime 8.3** (für `spark.read`/CSV dokumentiert; identischer Mechanismus bei `read_files` und Auto Loader).

---

## <a id="wann-gerettet">2. Wann wird eine Spalte gerettet?</a>

Ein Feld eines Datensatzes landet in der Rescued-Data-Spalte, wenn eines der folgenden drei, wörtlich dokumentierten Kriterien zutrifft:

- Die Spalte fehlt im angegebenen Schema
- Der Wert entspricht nicht dem im Schema angegebenen Datentyp
- Der Feldname weicht in der Groß-/Kleinschreibung vom Schema ab

Diese drei Kriterien sind für CSV explizit dokumentiert und gelten inhaltlich identisch für die anderen unterstützten Formate (JSON u. a.), da derselbe Mechanismus zugrunde liegt.

---

## <a id="aktivierung">3. Aktivierung und Standardverhalten je Werkzeug</a>

Das Standardverhalten unterscheidet sich deutlich zwischen den drei Werkzeugen — das ist der wichtigste werkzeugübergreifende Unterschied bei diesem Thema:

| Werkzeug | `rescuedDataColumn` standardmäßig aktiv? |
|---|---|
| `read_files` | **Ja**, sofern Schema-Inferenz aktiv ist (kein explizites Schema bzw. Schema-Evolution zugelassen) — deaktivierbar über `schemaEvolutionMode => 'none'`. |
| Auto Loader (`cloudFiles`, direkt oder über `STREAM read_files`) | **Ja, automatisch** — beim Inferieren des Schemas fügt Auto Loader die Spalte automatisch als `_rescued_data` hinzu. |
| `spark.read` (`DataFrameReader`) | **Nein** — muss explizit über `.option("rescuedDataColumn", "_rescued_data")` aktiviert werden. In allen geprüften Optionstabellen (CSV, JSON, Parquet, Avro, XML) ist der Standardwert durchgängig `None`. |

```sql
-- read_files (SQL): standardmäßig aktiv bei Schema-Inferenz
SELECT * FROM read_files('s3://bucket/path', format => 'json');

-- read_files (SQL): gezielt deaktivieren
SELECT * FROM read_files('s3://bucket/path', format => 'json', schemaEvolutionMode => 'none');
```

```python
# Auto Loader: automatisch aktiv, Spaltenname bei Bedarf explizit umbenennen
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaHints", "_corrupt_record string")
  .option("columnNameOfCorruptRecord", "_corrupt_record")
  .load("/Volumes/analytics/bronze/events"))
```

```python
# spark.read: muss explizit gesetzt werden
df = (spark.read
      .option("rescuedDataColumn", "_rescued_data")
      .format("csv")
      .load("/Volumes/<catalog>/<schema>/<volume>/reviews_csv"))
```

```sql
-- read_files (SQL): explizites Schema + rescuedDataColumn
SELECT * FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>/reviews_csv',
  format => 'csv',
  header => true,
  rescuedDataColumn => '_rescued_data'
)
```

**Praktische Konsequenz:** Da `rescuedDataColumn` bei `spark.read` standardmäßig **aus** ist, ist dort das Risiko stiller Typ-Fehlparsierungen bzw. unerwarteter `FAILFAST`-Abbrüche bei Typkonflikten höher als bei `read_files`/Auto Loader, sofern die Option nicht bewusst gesetzt wird.

---

## <a id="struktur">4. Struktur des Inhalts</a>

Wörtlich bestätigt: *"The rescued data column is returned as a JSON document containing the columns that were rescued, and the source file path of the record."* Die Spalte enthält also pro Zeile ein JSON-Dokument mit zwei Bestandteilen:

- den geretteten Spalten/Werten selbst (Feldname → Wert), und
- dem Quelldateipfad des Datensatzes.

Der Quelldateipfad lässt sich bei Bedarf aus dem JSON-Dokument entfernen:

```python
spark.conf.set("spark.databricks.sql.rescuedDataColumn.filePath.enabled", "false")
```

Hat ein Datensatz keine Schema-Abweichung, ist die Rescued-Data-Spalte für diese Zeile `NULL`.

---

## <a id="extraktion">5. Werte aus der Rescued-Data-Spalte extrahieren</a>

Da die Spalte ein JSON-String ist, lassen sich einzelne Felder über den Doppelpunkt-Operator (`:`) extrahieren — laut Sprachreferenz *"Extracts content from a JSON string using a JSON path expression"*, anwendbar auf `VARIANT`- und `STRING`-Ausdrücke mit gültigem JSON-Inhalt:

```sql
-- Allgemeine Syntax des Doppelpunkt-Operators
SELECT c1:price FROM VALUES('{ "price": 5 }') AS T(c1);
-- Ergebnis: 5
```

Angewendet auf `_rescued_data`, um ein einzelnes Feld (hier `_c0`, die erste positionsbasierte CSV-Spalte) gezielt zu extrahieren und in einen numerischen Typ zu casten:

```sql
SELECT
  cast(_rescued_data:_c0 AS BIGINT) AS order_id,
  *
FROM read_files(
  '/Volumes/analytics/landing/malformed_example.csv',
  format => 'csv',
  sep => '|',
  header => true
)
```

Ist der Wert kein gültiges JSON oder passt der Pfadausdruck nicht zum JSON-Wert, liefert der Doppelpunkt-Operator laut Doku `NULL` statt eines Fehlers.

---

## <a id="parser-modi">6. Zusammenspiel mit den Parser-Modi</a>

Der CSV-/JSON-Parser unterstützt drei Modi (`PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`). In Kombination mit aktiver `rescuedDataColumn` gilt wörtlich: *"data type mismatches do not cause records to be dropped in `DROPMALFORMED` mode or throw an error in `FAILFAST` mode. Only corrupt records — that is, incomplete or malformed CSV — are dropped or throw errors."*

Konkret für den `PERMISSIVE`-Modus mit aktiver `rescuedDataColumn` gelten laut Doku folgende Regeln für korrupte Datensätze:

- Die erste Zeile der Datei (Header- oder erste Datenzeile) legt die erwartete Zeilenlänge fest.
- Eine Zeile mit abweichender Spaltenanzahl gilt als *unvollständig*.
- Typkonflikte gelten **nicht** als korrupt.
- Nur unvollständige und fehlerhaft formatierte CSV-Datensätze gelten als korrupt und werden in `_corrupt_record` bzw. `badRecordsPath` erfasst.

| Konfliktart | Verhalten bei aktiver `rescuedDataColumn` |
|---|---|
| Typkonflikt (z. B. Text statt Zahl) | Landet in `_rescued_data`, wird **nicht** verworfen — auch nicht in `DROPMALFORMED`/`FAILFAST` |
| Wirklich korrupter/unvollständiger Datensatz (defektes JSON/CSV, falsche Spaltenanzahl) | Landet in `_corrupt_record`/`badRecordsPath`, oder löst in `FAILFAST` einen Fehler aus |

---

## <a id="abgrenzung">7. Abgrenzung zu `_corrupt_record`/`badRecordsPath`</a>

`_rescued_data` und `_corrupt_record`/`badRecordsPath` adressieren unterschiedliche Fehlerarten und schließen sich nicht gegenseitig aus, haben aber eine dokumentierte Rangfolge: *"The `badRecordsPath` option takes precedence over `_corrupt_record`, meaning that malformed rows written to the provided path do not appear in the resultant DataFrame."* Zudem gilt ausdrücklich: *"Default behavior for malformed records changes when using the rescued data column."*

| Spalte/Option | Zuständig für |
|---|---|
| `_rescued_data` | Typkonflikte, fehlende Schema-Spalten, Case-Mismatches — Daten bleiben im Ergebnis-DataFrame erhalten |
| `_corrupt_record` (Schema-Spalte) | Wirklich korrupte/unvollständige Datensätze, im Ergebnis-DataFrame sichtbar |
| `badRecordsPath` (Option) | Wirklich korrupte/unvollständige Datensätze, **nicht** im Ergebnis-DataFrame — landen stattdessen an einem separaten Pfad; hat Vorrang vor `_corrupt_record` |

Databricks empfiehlt laut `../06 Auto Loader/01 Schema-Inferenz und -Evolution.md` (Abschnitt Rescued-Data-Column) `columnNameOfCorruptRecord` gegenüber `badRecordsPath`, um mögliche Race Conditions zu vermeiden, die beschädigte Datensätze übersehen können.

---

## <a id="case-sensitivity">8. Groß-/Kleinschreibung (nur Auto Loader)</a>

Ohne aktivierte Case-Sensitivity behandelt Auto Loader die Spalten `abc`, `Abc` und `ABC` für Zwecke der Schema-Inferenz als dieselbe Spalte; welche Schreibweise tatsächlich verwendet wird, wählt Auto Loader arbiträr anhand der Stichprobendaten. Ist die Rescued-Data-Spalte aktiv, lädt Auto Loader Felder, deren Schreibweise von der des Schemas abweicht, in `_rescued_data`. Über `readerCaseSensitive => false` lässt sich dieses Verhalten ändern, sodass Auto Loader case-insensitiv liest. *(Quelle: `../06 Auto Loader/01 Schema-Inferenz und -Evolution.md`, Abschnitt Rescued-Data-Column — für `read_files`/`spark.read` wurde keine gesonderte, vom allgemeinen Case-Mismatch-Kriterium aus Abschnitt 2 abweichende Case-Sensitivity-Option dokumentiert gefunden.)*

---

## <a id="eigenes-beispiel">9. Eigenes Beispiel aus Kursmaterial</a>

Das folgende, aus einer privaten Kursnotiz (`_Code Beispiele/Data Ingestion/Rescuing Malformed Rows.md`) übernommene und gegen die offizielle Doku geprüfte Beispiel liest eine CSV-Datei mit explizitem Schema und aktivierter `rescuedDataColumn`. Zeilen, die nicht zum Schema passen (z. B. ein nicht-numerischer Wert in einer als `BIGINT` deklarierten Spalte), erscheinen dadurch nicht als Fehler, sondern landen nachvollziehbar in `_rescued_data`:

```sql
SELECT *
FROM read_files(
  '/Volumes/analytics/landing/malformed_example_1_data.csv',
  format => 'csv',
  sep => '|',
  header => true,
  schema => '
    order_id INT,
    email STRING,
    transactions_timestamp BIGINT',
  rescuedDataColumn => '_rescued_data'
);
```

Ein Datensatz, dessen `order_id`-Wert nicht als `INT` interpretierbar ist, wird dadurch nicht verworfen — der komplette Original-Datensatz landet stattdessen als JSON in `_rescued_data` und kann wie in Abschnitt 5 gezeigt (`_rescued_data:_c0`) inspiziert oder nachträglich bereinigt werden.

**Hinweis aus dem Kursmaterial, mit Abschnitt 1 vereinbar:** Ein explizit angegebenes Schema überspringt bei `read_files` den Inferenz-Lesedurchlauf und beschleunigt dadurch das Laden — besonders relevant bei großen oder wiederholt gelesenen Datenmengen (siehe `_read_files.md` Abschnitt 2 für die dort bereits verifizierte Begründung).

---

## <a id="quellen">10. Quellen</a>

- Read and write CSV files (Rescued-Data-Column: Aktivierung, JSON-Struktur, Mindest-Runtime 8.3, `filePath.enabled`-Konfiguration, Zusammenspiel mit Parser-Modi — AWS- und Azure-Spiegelseite zweifach abgerufen): https://docs.databricks.com/aws/en/query/formats/csv
- Configure schema inference and evolution in Auto Loader (automatische Aktivierung bei Auto Loader, Case-Sensitivity, `readerCaseSensitive`): https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema
- `:` (Doppelpunkt-Operator, JSON-Pfad-Extraktion): https://docs.databricks.com/aws/en/sql/language-manual/functions/colonsign
- Details zu `read_files`-Standardverhalten (aktiv bei Inferenz, Deaktivierung über `schemaEvolutionMode`): `_read_files.md` Abschnitt 13 (dieser Ordner)
- Details zu Auto-Loader-Verhalten, Case-Sensitivity, `columnNameOfCorruptRecord`: `../06 Auto Loader/01 Schema-Inferenz und -Evolution.md` (Abschnitt Rescued-Data-Column)
- Details zu `spark.read`-Standardverhalten (standardmäßig inaktiv, zweifach bestätigt): `_spark_read.md` Abschnitt 9 (dieser Ordner)
- Nicht-Databricks-Quelle (privates Kursmaterial, Anstoß für Abschnitt 9): `_Zusammenfassung/_Code Beispiele/Data Ingestion/Rescuing Malformed Rows.md`

**Stand:** 2026-08-18.
