# `AUTO CDC ... INTO` (Pipelines) — Referenz

## Abschnittsübersicht

1. [Grundzweck](#grundzweck)
2. [Formale Syntax](#syntax)
3. [Parameter](#parameter)
4. [Doku-eigenes Beispiel](#doku-beispiel)
5. [Quellen](#quellen)

---

## <a id="grundzweck">1. Grundzweck</a>

Das Statement `AUTO CDC ... INTO` erstellt einen Flow, der die Change-Data-Capture-Funktionalität (CDC) von Lakeflow Declarative Pipelines nutzt. Es liest Änderungen aus einer CDC-Quelle und wendet sie auf eine Streaming-Ziel-Tabelle an.

Wichtig: Es muss eine Ziel-Streaming-Tabelle deklariert werden, in die die Änderungen angewendet werden. Das Schema der Zieltabelle kann optional angegeben werden. Für SCD-Type-2-Tabellen müssen bei Angabe des Zielschemas zusätzlich die Spalten `__START_AT` und `__END_AT` mit demselben Datentyp wie das `SEQUENCE BY`-Feld enthalten sein.

Datenqualitätsbeschränkungen für das Ziel werden über dieselbe `CONSTRAINT`-Klausel definiert wie bei anderen Pipeline-Abfragen.

---

## <a id="syntax">2. Formale Syntax</a>

```
CREATE OR REFRESH STREAMING TABLE table_name;

CREATE FLOW flow_name AS AUTO CDC [ONCE] INTO table_name
FROM source
KEYS (keys)
[IGNORE NULL UPDATES [ON {columnList | * EXCEPT (exceptColumnList)}]]
[APPLY AS DELETE WHEN condition]
[APPLY AS TRUNCATE WHEN condition]
SEQUENCE BY orderByColumn
[SYSTEM SEQUENCE BY systemOrderByColumn]
[COLUMNS {columnList | * EXCEPT (exceptColumnList)}]
[STORED AS {SCD TYPE 1 | SCD TYPE 2 | BITEMPORAL}]
[TRACK HISTORY ON {columnList | * EXCEPT (exceptColumnList)}]
[COLUMNS TO UPDATE columnName]
```

Das Standardverhalten für `INSERT`- und `UPDATE`-Ereignisse ist ein *Upsert* der CDC-Ereignisse aus der Quelle: Zeilen in der Zieltabelle, die dem angegebenen Schlüssel (bzw. den Schlüsseln) entsprechen, werden aktualisiert, oder es wird eine neue Zeile eingefügt, wenn kein passender Datensatz im Ziel existiert. Das Verhalten für `DELETE`-Ereignisse lässt sich über die Bedingung `APPLY AS DELETE WHEN` festlegen.

### Reales Beispiel mit möglichst vielen Bausteinen der formalen Syntax

Mehrere Klauseln schließen sich gegenseitig aus: `COLUMNS TO UPDATE` ist nicht mit `IGNORE NULL UPDATES` kombinierbar; `APPLY AS TRUNCATE WHEN` ist nur für `STORED AS SCD TYPE 1` zulässig; `SYSTEM SEQUENCE BY` und `STORED AS BITEMPORAL` gehören zusammen und schließen `STORED AS SCD TYPE 2` aus. Das folgende, aus den einzeln verifizierten Bausteinen dieses Dokuments zusammengesetzte Beispiel (kein wörtliches Einzelzitat einer Doku-Seite) kombiniert daher die größtmögliche gemeinsam nutzbare Untermenge — SCD Type 2 mit `IGNORE NULL UPDATES ON`, `APPLY AS DELETE WHEN`, `SEQUENCE BY`, `COLUMNS ... EXCEPT` und `TRACK HISTORY ON`:

```sql
CREATE OR REFRESH STREAMING TABLE main.sales.users_cdc_target;

CREATE FLOW users_cdc_flow AS AUTO CDC INTO main.sales.users_cdc_target
FROM stream(cdc_data.users)
KEYS (userId)
IGNORE NULL UPDATES ON (email, phone)
APPLY AS DELETE WHEN operation = "DELETE"
SEQUENCE BY sequenceNum
COLUMNS * EXCEPT (operation, sequenceNum)
STORED AS SCD TYPE 2
TRACK HISTORY ON * EXCEPT (city);
```

Die separat zu betrachtenden, sich gegenseitig ausschließenden Varianten:

- **`ONCE`** — für einen einmaligen Insert bzw. Backfill in die Zieltabelle: `AUTO CDC ONCE INTO table_name ...`. Wird der Flow bei einer Pipeline-Aktualisierung nicht per vollständigem Refresh erneut ausgeführt, läuft er kein zweites Mal.
- **`APPLY AS TRUNCATE WHEN`** — nur zulässig in Kombination mit `STORED AS SCD TYPE 1`, nicht mit SCD Type 2 oder bitemporal:

  ```sql
  APPLY AS TRUNCATE WHEN operation = "TRUNCATE"
  STORED AS SCD TYPE 1
  ```
- **`SYSTEM SEQUENCE BY` mit `STORED AS BITEMPORAL`** (Beta) — verfolgt Änderungen sowohl über Business-Zeit (`SEQUENCE BY`) als auch über System-Zeit:

  ```sql
  SEQUENCE BY sequenceNum
  SYSTEM SEQUENCE BY _commit_timestamp
  STORED AS BITEMPORAL
  ```
- **`COLUMNS TO UPDATE`** — für partielle Updates, bei denen jeder Änderungsdatensatz eine andere Spaltenmenge aktualisiert und explizite `NULL`-Werte angewendet werden sollen; nicht kombinierbar mit `IGNORE NULL UPDATES` und nicht für bitemporale Tabellen unterstützt:

  ```sql
  COLUMNS TO UPDATE changedColumnsArray
  ```

---

## <a id="parameter">3. Parameter</a>

- **`ONCE`** — optional. Bewirkt einen einmaligen Insert bzw. Backfill in die Zieltabelle. Wird bei einer Pipeline-Aktualisierung nicht erneut ausgeführt, außer bei einem vollständigen Refresh.
- **`flow_name`** — der Name des zu erstellenden Flows.
- **`source`** — die Quelle für die Daten. Die Quelle muss eine **Streaming**-Quelle sein. Das Schlüsselwort `STREAM` liest die Quelle mit Streaming-Semantik. Trifft der Lesevorgang auf eine Änderung oder Löschung eines bestehenden Datensatzes, wird ein Fehler ausgelöst — am sichersten ist das Lesen aus statischen oder nur anfügenden Quellen. Um Daten mit Änderungscommits einzulesen, kann in Python die Option `skipChangeCommits` zur Fehlerbehandlung verwendet werden.
- **`KEYS`** (erforderlich) — die Spalte oder Kombination von Spalten, die eine Zeile in den Quelldaten eindeutig identifiziert. Die Werte dieser Spalten bestimmen, welche CDC-Ereignisse auf welche Datensätze der Zieltabelle angewendet werden. Für eine Kombination von Spalten wird eine kommagetrennte Liste verwendet.
- **`IGNORE NULL UPDATES`** — optional. Erlaubt das Einspielen von Updates, die nur eine Teilmenge der Zielspalten enthalten. Trifft ein CDC-Ereignis auf eine bestehende Zeile und ist `IGNORE NULL UPDATES` angegeben, behalten Spalten mit `null`-Wert ihren bestehenden Wert im Ziel — dies gilt auch für geschachtelte Spalten mit `null`-Wert. Für partielle Updates lässt sich eine `ON`-Klausel ergänzen:
  - `IGNORE NULL UPDATES ON columnList`: nur die gelisteten Spalten behalten ihren bestehenden Wert, wenn der eingehende Wert `null` ist. Alle übrigen Spalten wenden explizite `null`-Werte an.
  - `IGNORE NULL UPDATES ON * EXCEPT (exceptColumnList)`: alle Spalten außer den gelisteten behalten ihren bestehenden Wert bei `null`. Die gelisteten Spalten wenden explizite `null`-Werte an.

  Standard ist das Überschreiben bestehender Spalten mit `null`-Werten.
- **`APPLY AS DELETE WHEN`** — optional. Legt fest, wann ein CDC-Ereignis als `DELETE` statt als Upsert behandelt werden soll. Für SCD-Type-2-Quellen wird die gelöschte Zeile zur Behandlung nicht-chronologisch eintreffender Daten vorübergehend als Tombstone in der zugrunde liegenden Delta-Tabelle beibehalten; eine View im Metastore filtert diese Tombstones heraus. Das Aufbewahrungsintervall lässt sich über die Tabelleneigenschaft `pipelines.cdc.tombstoneGCThresholdInSeconds` konfigurieren.
- **`APPLY AS TRUNCATE WHEN`** — optional. Legt fest, wann ein CDC-Ereignis als vollständiges `TRUNCATE` der Tabelle behandelt werden soll. Da diese Klausel ein vollständiges Truncate der Zieltabelle auslöst, sollte sie nur für spezifische Anwendungsfälle verwendet werden, die diese Funktionalität benötigen. Nur für SCD Type 1 unterstützt — SCD Type 2 unterstützt die Truncate-Operation nicht.
- **`SEQUENCE BY`** (erforderlich) — der Spaltenname, der die logische Reihenfolge der CDC-Ereignisse in den Quelldaten angibt. Die Pipeline-Verarbeitung nutzt diese Sequenzierung, um nicht-chronologisch eintreffende Änderungsereignisse zu behandeln. Werden mehrere Spalten zur Sequenzierung benötigt, wird ein `STRUCT`-Ausdruck verwendet: Er ordnet zunächst nach dem ersten Struct-Feld, bei Gleichstand nach dem zweiten Feld, und so weiter. Die angegebenen Spalten müssen sortierbare Datentypen besitzen.
- **`SYSTEM SEQUENCE BY`** (Beta, optional, nur für bitemporale Tabellen) — der Spaltenname, der die Systemzeit angibt, zu der jedes CDC-Ereignis dem System bekannt wurde. Wird zusammen mit `STORED AS BITEMPORAL` verwendet, um Änderungen sowohl über Business-Zeit (`SEQUENCE BY`) als auch über Systemzeit nachzuverfolgen. Die angegebenen Spalten müssen sortierbare Datentypen besitzen.
- **`COLUMNS`** — optional. Legt eine Teilmenge der in die Zieltabelle aufzunehmenden Spalten fest — entweder als vollständige Liste (`COLUMNS (userId, name, city)`) oder als Ausschlussliste (`COLUMNS * EXCEPT (operation, sequenceNum)`). Standard ist die Aufnahme aller Spalten, wenn `COLUMNS` nicht angegeben ist.
- **`STORED AS`** — optional. Legt fest, ob Datensätze als SCD Type 1, SCD Type 2 oder bitemporal gespeichert werden. `BITEMPORAL` erfordert `SYSTEM SEQUENCE BY` und befindet sich in Beta. Standard ist SCD Type 1.
- **`TRACK HISTORY ON`** — optional. Legt eine Teilmenge der Ausgabespalten fest, für die bei Änderungen History-Datensätze erzeugt werden — entweder als vollständige Liste (`COLUMNS (userId, name, city)`) oder als Ausschlussliste (`COLUMNS * EXCEPT (operation, sequenceNum)`). Standard ist das Tracking der History für alle Ausgabespalten bei jeder Änderung, äquivalent zu `TRACK HISTORY ON *`.
- **`COLUMNS TO UPDATE`** — optional. Gibt den Namen einer Quellspalte an, die für jeden Änderungsdatensatz die Menge der zu aktualisierenden Spalten als Array von Spaltennamen-Strings (`array<string>`) enthält. Nicht im Array enthaltene Spalten behalten ihren bestehenden Zielwert, gelistete Spalten werden aus der Quelle geschrieben — einschließlich expliziter `null`-Werte. Dient partiellen Updates, bei denen jeder Änderungsdatensatz eine andere Spaltenmenge aktualisiert und explizite `null`-Werte angewendet werden sollen. Nicht kombinierbar mit `IGNORE NULL UPDATES`, nicht unterstützt für bitemporale Tabellen.

---

## <a id="doku-beispiel">4. Doku-eigenes Beispiel</a>

```sql
-- Create a streaming table, then use AUTO CDC to populate it:
CREATE OR REFRESH STREAMING TABLE target;

CREATE FLOW flow
AS AUTO CDC INTO
  target
FROM stream(cdc_data.users)
  KEYS (userId)
  APPLY AS DELETE WHEN operation = "DELETE"
  SEQUENCE BY sequenceNum
  COLUMNS * EXCEPT (operation, sequenceNum)
  STORED AS SCD TYPE 2
  TRACK HISTORY ON * EXCEPT (city);
```

---

## <a id="quellen">5. Quellen</a>

- AUTO CDC INTO (pipelines) — SQL-Sprachreferenz (formale Syntax, alle Parameter, Doku-Beispiel, Hinweis zu `__START_AT`/`__END_AT`): https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-apply-changes-into

**Stand:** 2026-08-19.
