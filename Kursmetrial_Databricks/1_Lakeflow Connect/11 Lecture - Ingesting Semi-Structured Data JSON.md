# Semistrukturierte Daten ingestieren: JSON

**Datentyp STRING**
Eine Technik für die Arbeit mit einer JSON-formatierten String-Spalte besteht darin, direkt auf Werte in der Spalte vom Datentyp STRING zuzugreifen.

- Eine Spalte kann JSON-Daten einfach als normalen STRING speichern
- Da sie als String gespeichert wird, kann die Spalte jeden beliebigen JSON-String ohne Einschränkungen aufnehmen
- Dieser Ansatz ist jedoch weniger performant als typisierte Ansätze wie STRUCT
Um auf Unterfelder in JSON-formatierten String-Spalten zuzugreifen, können Sie die Doppelpunkt-Syntax (:) verwenden.
Wenn Ihre Spalte beispielsweise json_column heißt und Sie auf das Unterfeld "name" zugreifen möchten, geben Sie an: json_column:name
Mit dieser Syntax können Sie bestimmte Felder direkt aus dem in der Spalte gespeicherten JSON-String extrahieren.

**Datentyp STRUCT**
Eine weitere Methode für die Arbeit mit einer JSON-formatierten String-Spalte besteht darin, die Spalte in den Datentyp STRUCT zu konvertieren.

- Sie können JSON-Daten durch Definition eines Schemas in einen STRUCT-Typ parsen
- Der STRUCT erzwingt das JSON-Schema und stellt sicher, dass Datentypen und Struktur konsistent sind
- Das Abfragen eines STRUCT ist effizienter als die Arbeit mit einem rohen JSON-formatierten STRING.

**Datentyp VARIANT**
Der Datentyp VARIANT ist der neueste Ansatz für die Arbeit mit JSON-Daten in Databricks.
Stand Q2 2025 befindet sich VARIANT in der **Public Preview**. Die wichtigsten Vorteile:

- Kann **jede Art von Daten** speichern, einschließlich JSON, und ist daher ideal für semistrukturierte Daten
- **Sehr flexibel**, passt sich unterschiedlichen Datenformen ohne starre Schemas an
- Bietet eine **bessere Performance** als bestehende Methoden (STRING und STRUCT)
Achten Sie auf die Veröffentlichung als General Availability (GA).

## C. JSON-formatierte Strings in STRUCTs konvertieren
##### Klicken Sie auf einen Schritt, um die relevanten JSON- und STRUCT-Abschnitte hervorzuheben.

JSON-formatierter String

```json
{
 "name": "John Doe",
 "age": 35,
 "address": {
 "city": "Anytown",
 "state": "CA"
 },
 "children": [
 {
 "name": "Owen",
 "age": 10
 },
 {
 "name": "Eva",
 "age": 8
 }
 ]
}
```

Schritt 1: Das Schema des JSON-formatierten Strings definieren

Schritt 2: Den Datentyp STRUCT angeben, der den JSON-formatierten String aufnimmt

Schritt 3: Die Datentypen STRING und INT für die Schlüssel name und age angeben

Schritt 4: Der Schlüssel address enthält einen STRUCT-Datentyp mit den Schlüsseln city und state

Schritt 5: Der Schlüssel children enthält ein ARRAY von STRUCTs

**STRUCT-Schema**

```structured text
STRUCT<
 name: STRING,
 age: INT,
 address: STRUCT<city: STRING, state: STRING>,
 children: ARRAY<STRUCT<name: STRING, age: INT>>
>
```

### Schritt 1: Das Schema mit `schema_of_json` ableiten

Anstatt das Schema manuell zu definieren, können Sie die eingebaute Funktion `schema_of_json` verwenden, um das Schema automatisch aus einem Beispiel-JSON-String abzuleiten.

Übergeben Sie der Funktion einfach einen Beispiel-JSON-String als Argument, und sie gibt das abgeleitete Schema (die Struktur) zurück.

```json
{
  "name": "John Doe",
  "age": 35,
  "address": {
    "city": "Anytown",
    "state": "CA"
  },
  "children": [
    { "name": "Owen", "age": 10 },
    { "name": "Eva", "age": 8 }
  ]
}
```

```sql
SELECT schema_of_json('sample-json-string')
```

Die Funktion gibt die **Struktur** des JSON-formatierten Strings zurück

```structured text
STRUCT<
  name: STRING,
  age: INT,
  address: STRUCT<city: STRING, state: STRING>,
  children: ARRAY<STRUCT<name: STRING, age: INT>
>
```

### D2. Schritt 2: JSON mit `from_json` parsen

Sobald Sie die Struktur des JSON-formatierten Strings kennen, können Sie die Spark-Funktion **`from_json`** verwenden. Diese Funktion nimmt den JSON-String und das im vorherigen Schritt ermittelte Schema entgegen und gibt eine STRUCT-Spalte zurück.

Mit `from_json` wird eine neue Spalte vom Datentyp STRUCT erstellt, die die gemäß dem definierten Schema geparsten JSON-Daten enthält.

```structured text
STRUCT<
  name: STRING, 
  age: INT,
  address: STRUCT<city: STRING, state: STRING>,
  children: ARRAY<STRUCT<name: STRING, age: INT>>
>
```

```sql
-- Das Schema mit from_json anwenden
-- Die Funktion `from_json` gibt eine **STRUCT-Spalte** zurück,
-- basierend auf dem JSON-String und dem angegebenen Schema
SELECT from_json(json_col, 'json-struct-schema') AS struct_column
FROM table
```



## E. Fazit

In dieser Lektion haben Sie gelernt, wie Sie in Databricks mit semistrukturierten JSON-Daten arbeiten:

- **JSON-Struktur**: Objekte in geschweiften Klammern enthalten Schlüssel-Wert-Paare. Werte können Strings, Zahlen, Booleans, Arrays oder verschachtelte Objekte sein.
- **Drei Ansätze** für die Arbeit mit JSON-formatierten Spalten:
  - **STRING**: Einfach, aber weniger performant. JSON wird als Rohtext gespeichert.
  - **STRUCT**: JSON mit einem definierten Schema parsen. Erzwingt die Struktur und ist effizienter bei Abfragen.
  - **VARIANT**: Der neueste Ansatz (Public Preview). Sehr flexibel mit verbesserter Performance.
- Die **Konvertierung von JSON in STRUCT** erfordert die Zuordnung von JSON-Typen zu Databricks-SQL-Typen (STRING, INT, BOOLEAN, STRUCT<>, ARRAY<>).
- Verwenden Sie **`schema_of_json`**, um das Schema automatisch aus einem Beispiel-JSON-String abzuleiten.
- Verwenden Sie **`from_json`**, um eine JSON-String-Spalte mithilfe des abgeleiteten Schemas in eine STRUCT-Spalte zu parsen.

### Nächste Schritte

Im nächsten Abschnitt arbeiten Sie praktisch mit JSON-Daten und parsen und transformieren JSON-formatierte Spalten mit diesen Techniken.

© 2026 Databricks, Inc. Alle Rechte vorbehalten.
Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) |
[Nutzungsbedingungen](https://databricks.com/terms-of-use) |
[Support](https://help.databricks.com/)
