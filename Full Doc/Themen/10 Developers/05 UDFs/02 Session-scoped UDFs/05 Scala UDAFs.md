# Scala User-Defined Aggregate Functions (UDAFs)

Referenz zu session-scoped Scala-UDAFs über die `UserDefinedAggregateFunction`-API: eigene Aggregatfunktionen implementieren, in Spark SQL registrieren und über SQL oder die DataFrame-API aufrufen.

## Abschnittsübersicht

1. [Voraussetzungen](#voraussetzungen)
2. [Eine `UserDefinedAggregateFunction` implementieren](#implementieren)
3. [Die UDAF bei Spark SQL registrieren](#registrieren)
4. [Die UDAF verwenden](#verwenden)
5. [Quellen](#quellen)

---

## <a id="voraussetzungen">1. Voraussetzungen</a>

- Databricks Runtime 13.3 LTS und höher
- Klassisches Compute mit Dedicated Access Mode

---

## <a id="implementieren">2. Eine `UserDefinedAggregateFunction` implementieren</a>

Beispiel: geometrisches Mittel als UDAF.


Die Klasse implementiert dabei folgende Bestandteile:

- `inputSchema`: die Eingabefelder der Aggregatfunktion.
- `bufferSchema`: die internen Felder, die für die Berechnung des Aggregats gehalten werden.
- `dataType`: der Ausgabetyp der Aggregatfunktion.
- `initialize`: der Startwert für das Buffer-Schema.
- `update`: wie das Buffer-Schema anhand einer Eingabe aktualisiert wird.
- `merge`: wie zwei Objekte vom Buffer-Schema-Typ zusammengeführt werden.
- `evaluate`: gibt den finalen Wert anhand des finalen Werts des Buffer-Schemas zurück.

---

## <a id="registrieren">3. Die UDAF bei Spark SQL registrieren</a>


---

## <a id="verwenden">4. Die UDAF verwenden</a>

Test-DataFrame und Spark-SQL-Tabelle anlegen:


Aufruf über eine `GROUP BY`-Anweisung in SQL:

```sql
-- Use a group_by statement and call the UDAF.
select group_id, gm(id) from simple group by group_id
```

Aufruf über die DataFrame-API:


---

## <a id="quellen">5. Quellen</a>

- Scala user-defined aggregate functions (UDAFs): https://docs.databricks.com/aws/en/udf/aggregate-scala

**Stand:** 2026-08-22.
