# Range-Join-Optimierung

Ein *Range Join* liegt vor, wenn zwei Relationen über eine „Punkt in Intervall"-Bedingung oder eine Intervall-Überlappung verbunden werden. Die Range-Join-Optimierung in Databricks Runtime kann die Performance solcher Abfragen deutlich verbessern.

In Databricks SQL optimiert Databricks Range Joins automatisch, ohne manuelle Konfiguration. Bei allen Compute-Typen können Sie Range Joins zusätzlich manuell über Join-Hints oder Session-Konfiguration anpassen.

## Punkt-in-Intervall Range Join

Ein *Punkt-in-Intervall Range Join* ist ein Join, dessen Bedingung festlegt, dass ein Wert aus einer Relation zwischen zwei Werten aus der anderen Relation liegt. Beispiele:

```sql
%sql
-- using BETWEEN expressions
SELECT *
FROM points JOIN ranges ON points.p BETWEEN ranges.start and ranges.end;

-- using inequality expressions
SELECT *
FROM points JOIN ranges ON points.p >= ranges.start AND points.p < ranges.end;

-- with fixed length interval
SELECT *
FROM points JOIN ranges ON points.p >= ranges.start AND points.p < ranges.start + 100;

-- join two sets of point values within a fixed distance from each other
SELECT *
FROM points1 p1 JOIN points2 p2 ON p1.p >= p2.p - 10 AND p1.p <= p2.p + 10;

-- a range condition together with other join conditions
SELECT *
FROM points, ranges
WHERE points.symbol = ranges.symbol
AND points.p >= ranges.start
AND points.p < ranges.end;
```

## Intervall-Überlappungs-Range-Join

Ein *Intervall-Überlappungs-Range-Join* ist ein Join, dessen Bedingung eine Überlappung von Intervallen zwischen zwei Werten aus jeder Relation festlegt. Beispiele:

```sql
%sql
-- overlap of [r1.start, r1.end] with [r2.start, r2.end]
SELECT *
FROM r1 JOIN r2 ON r1.start < r2.end AND r2.start < r1.end;

-- overlap of fixed length intervals
SELECT *
FROM r1 JOIN r2 ON r1.start < r2.start + 100 AND r2.start < r1.start + 100;

-- a range condition together with other join conditions
SELECT *
FROM r1 JOIN r2 ON r1.symbol = r2.symbol
AND r1.start <= r2.end
AND r1.end >= r2.start;
```

## Voraussetzungen für die Range-Join-Optimierung

Die Range-Join-Optimierung wird für Joins durchgeführt, die:

- eine Bedingung haben, die sich als Punkt-in-Intervall- oder Intervall-Überlappungs-Range-Join interpretieren lässt,
- bei denen alle Werte in der Range-Join-Bedingung von einem numerischen Typ sind (Integer, Fließkomma, Dezimal), oder vom Typ `DATE` oder `TIMESTAMP`,
- bei denen alle Werte in der Range-Join-Bedingung vom gleichen Typ sind. Beim Dezimaltyp müssen die Werte zusätzlich dieselbe Skalierung und Genauigkeit haben,
- ein `INNER JOIN` sind, oder bei einem Punkt-in-Intervall-Range-Join ein `LEFT OUTER JOIN` mit dem Punktwert auf der linken Seite, beziehungsweise ein `RIGHT OUTER JOIN` mit dem Punktwert auf der rechten Seite,
- eine Bin-Größe haben, entweder automatisch abgeleitet oder manuell festgelegt.

## Joins mit numerischer Gleichheits- und Range-Bedingung

Enthält eine Join-Bedingung sowohl eine Gleichheitsbedingung auf einer numerischen Spalte als auch eine Range-Bedingung, kann der Optimizer auch die Gleichheitsspalte in Bins einteilen. Sie erfüllt schließlich die Typanforderungen der Range-Join-Optimierung. Das kann dazu führen, dass die Gleichheitsspalte Bins zugeordnet oder von der Optimierung ausgeschlossen wird, was die Performance verschlechtert.

Um sicherzustellen, dass die Range-Join-Optimierung nur auf die gewünschte Range-Bedingung angewendet wird, casten Sie die numerischen Gleichheitsspalten auf `STRING`. Damit werden sie von der Betrachtung als Range-Bedingungsspalten ausgeschlossen.

```sql
%sql
SELECT /*+ RANGE_JOIN(reference, 3306084) */
    reference.*, position.*
FROM position
INNER JOIN reference
    ON CAST(position.parent_index AS STRING) = CAST(reference.parent_index AS STRING)
    AND position.child_index BETWEEN reference.min_child_index AND reference.max_child_index;
```

Dasselbe Muster gilt für andere numerische Spalten, die als Gleichheitsschlüssel dienen, etwa `DATE`-Spalten, Integer-IDs oder geclusterte Partitionsspalten.

## Bin-Größe

Die *Bin-Größe* ist ein numerischer Tuning-Parameter. Er teilt den Wertebereich der Range-Bedingung in mehrere gleich große *Bins* auf. Bei einer Bin-Größe von 10 teilt die Optimierung den Wertebereich zum Beispiel in Intervalle der Länge 10 auf. Bei einer Punkt-in-Intervall-Bedingung `p BETWEEN start AND end`, mit `start` gleich 8 und `end` gleich 22, überlappt dieses Wertintervall drei Bins der Länge 10: das erste Bin von 0 bis 10, das zweite von 10 bis 20 und das dritte von 20 bis 30. Nur Punkte in diesen drei Bins müssen als mögliche Join-Treffer für dieses Intervall geprüft werden. Liegt `p` zum Beispiel bei 32, kann es als Treffer für `start` gleich 8 und `end` gleich 22 ausgeschlossen werden, weil es im Bin von 30 bis 40 liegt.

- Bei `DATE`-Werten wird die Bin-Größe als Anzahl Tage interpretiert. Ein Wert von 7 entspricht zum Beispiel einer Woche.
- Bei `TIMESTAMP`-Werten wird die Bin-Größe als Sekunden interpretiert. Für Werte unterhalb einer Sekunde können Sie Nachkommawerte verwenden. Ein Wert von 60 entspricht einer Minute, ein Wert von 0.1 entspricht 100 Millisekunden.

Sie können die Bin-Größe über einen Range-Join-Hint in der Abfrage oder über einen Session-Konfigurationsparameter festlegen. In Databricks SQL wird die Bin-Größe automatisch abgeleitet, wenn die automatische Range-Join-Optimierung aktiviert ist.

## Automatische Range-Join-Optimierung

In Databricks SQL erkennt Databricks passende Range Joins automatisch. Es leitet die optimale Bin-Größe ab, indem es die Intervalltabelle stichprobenartig untersucht. Dadurch entfällt die Notwendigkeit, die Bin-Größe manuell per Hint oder Session-Konfiguration festzulegen.

Die automatische Range-Join-Optimierung ist in Databricks SQL standardmäßig aktiviert. Deaktivieren Sie sie mit folgender Konfiguration:

```sql
%sql
SET spark.databricks.optimizer.autoRangeJoin.enabled = false;
```

Legen Sie eine Bin-Größe über einen Range-Join-Hint oder eine Session-Konfiguration fest, überschreibt dieser Wert die automatisch abgeleitete Bin-Größe.

## Range Join über einen Range-Join-Hint aktivieren

Um die Range-Join-Optimierung in einer SQL-Abfrage zu aktivieren, verwenden Sie einen *Range-Join-Hint*, um die Bin-Größe festzulegen. Der Hint muss den Relationsnamen einer der verbundenen Relationen und den numerischen Bin-Größenparameter enthalten. Der Relationsname kann eine Tabelle, eine View oder eine Subquery sein.

```sql
%sql
SELECT /*+ RANGE_JOIN(points, 10) */ *
FROM points JOIN ranges ON points.p >= ranges.start AND points.p < ranges.end;

SELECT /*+ RANGE_JOIN(r1, 0.1) */ *
FROM (SELECT * FROM ranges WHERE ranges.amount < 100) r1, ranges r2
WHERE r1.start < r2.start + 100 AND r2.start < r1.start + 100;

SELECT /*+ RANGE_JOIN(c, 500) */ *
FROM a
JOIN b ON (a.b_key = b.id)
JOIN c ON (a.ts BETWEEN c.start_time AND c.end_time)
```

Im dritten Beispiel **müssen** Sie den Hint bei `c` setzen. Joins sind linksassoziativ, die Abfrage wird also als `(a JOIN b) JOIN c` interpretiert. Ein Hint bei `a` gilt für den Join von `a` mit `b`, nicht für den Join mit `c`.

Alternativ können Sie einen Range-Join-Hint direkt auf einen der zu verbindenden DataFrames setzen. In diesem Fall enthält der Hint nur den numerischen Bin-Größenparameter.

```python
#create minute table
minutes = spark.createDataFrame(
    [(0, 60), (60, 120)],
    "minute_start: int, minute_end: int")

#create events table
events = spark.createDataFrame(
    [(12, 33), (0, 120), (33, 72), (65, 178)],
    "event_start: int, event_end: int")

#Range_Join with "hint" on the from table
(events.hint("range_join", 60)
  .join(minutes,
    on=[events.event_start < minutes.minute_end,
    minutes.minute_start < events.event_end])
  .orderBy(events.event_start,
    events.event_end,
    minutes.minute_start)
  .show())
```

```python
#Range_Join with "hint" on the join table
(events.join(minutes.hint("range_join", 60),
  on=[events.event_start < minutes.minute_end,
    minutes.minute_start < events.event_end])
  .orderBy(events.event_start,
    events.event_end,
    minutes.minute_start)
  .show())
```

## Range Join über Session-Konfiguration aktivieren

Wenn Sie die Abfrage nicht ändern möchten, legen Sie die Bin-Größe als Konfigurationsparameter fest.

```sql
%sql
SET spark.databricks.optimizer.rangeJoin.binSize=5
```

Dieser Konfigurationsparameter gilt für jeden Join mit einer Range-Bedingung. Eine abweichende Bin-Größe, die per Range-Join-Hint gesetzt wird, überschreibt aber immer den über den Parameter gesetzten Wert.

## Bin-Größe wählen

Wie wirksam die Range-Join-Optimierung ist, hängt von der passenden Wahl der Bin-Größe ab.

Eine kleine Bin-Größe führt zu mehr Bins. Das hilft, mögliche Treffer effizienter zu filtern. Ist die Bin-Größe jedoch deutlich kleiner als die vorkommenden Wertintervalle, wird es ineffizient: Die Wertintervalle überlappen dann mehrere Bin-Intervalle. Bei der Bedingung `p BETWEEN start AND end`, mit `start` gleich 1.000.000 und `end` gleich 1.999.999, und einer Bin-Größe von 10, überlappt das Wertintervall 100.000 Bins.

Ist die Intervalllänge einigermaßen gleichmäßig und bekannt, empfiehlt sich, die Bin-Größe auf die typische erwartete Intervalllänge zu setzen. Variiert die Intervalllänge dagegen stark und ist schief verteilt, braucht es eine Balance: Die Bin-Größe muss kurze Intervalle effizient filtern, darf aber nicht dazu führen, dass lange Intervalle zu viele Bins überlappen. Angenommen, eine Tabelle `ranges` hat Intervalle zwischen den Spalten `start` und `end`. Mit folgender Abfrage bestimmen Sie verschiedene Perzentile der schief verteilten Intervalllänge:

```sql
%sql
SELECT
  map_from_arrays(
    ARRAY(0.5, 0.9, 0.99, 0.999, 0.9999),
    APPROX_PERCENTILE(
      end::DOUBLE - start::DOUBLE,
      ARRAY(0.5, 0.9, 0.99, 0.999, 0.9999)
    )
  ) AS bin_sizes
FROM
  ranges;
```

Casten Sie jede Spalte vor der Subtraktion auf `DOUBLE`. So funktioniert die Abfrage unabhängig davon, ob die Spalten numerisch sind oder vom Typ `DATE` oder `TIMESTAMP`.

Eine empfohlene Bin-Größe ist das Maximum aus: dem Wert des 90. Perzentils, dem Wert des 99. Perzentils geteilt durch 10, dem Wert des 99,9. Perzentils geteilt durch 100, und so weiter. Die Begründung:

- Ist der Wert des 90. Perzentils die Bin-Größe, sind nur 10 % der Intervalllängen länger als das Bin-Intervall und erstrecken sich über mehr als 2 benachbarte Bin-Intervalle.
- Ist der Wert des 99. Perzentils die Bin-Größe, erstrecken sich nur 1 % der Intervalllängen über mehr als 11 benachbarte Bin-Intervalle.
- Ist der Wert des 99,9. Perzentils die Bin-Größe, erstrecken sich nur 0,1 % der Intervalllängen über mehr als 101 benachbarte Bin-Intervalle.
- Das lässt sich für das 99,99. Perzentil, das 99,999. Perzentil und so weiter fortsetzen, falls nötig.

Diese Methode begrenzt, wie viele schief verteilte, lange Wertintervalle mehrere Bin-Intervalle überlappen. Die so ermittelte Bin-Größe ist nur ein Startpunkt für die Feinabstimmung. Die tatsächlichen Ergebnisse hängen vom konkreten Workload ab.

---
**Quelle:** https://docs.databricks.com/aws/en/optimizations/range-join  
**Stand:** 2026-08-06
