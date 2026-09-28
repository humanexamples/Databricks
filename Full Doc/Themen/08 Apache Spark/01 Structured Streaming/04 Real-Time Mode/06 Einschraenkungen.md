# Real-Time-Mode-Einschränkungen — Referenz

Dieses Dokument beschreibt bekannte Einschränkungen von Real-Time Mode in Structured Streaming — für Quellen, den Union-Operator, `mapPartitions` und `transformWithStateInPandas`. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/limitations`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte.

## Abschnittsübersicht

1. [Quellen-Einschränkungen](#quellen-einschraenkungen)
2. [Union-Einschränkungen](#union-einschraenkungen)
3. [`mapPartitions`-Einschränkung](#mappartitions)
4. [`transformWithStateInPandas` nicht unterstützt](#transformwithstateinpandas)
5. [Quellen](#quellen)

---

## <a id="quellen-einschraenkungen">1. Quellen-Einschränkungen</a>

Für Kinesis empfiehlt Databricks den Enhanced-Fan-Out-(EFO)-Modus für die niedrigste Latenz. Zudem können häufige Repartitionierungen die Latenz negativ beeinflussen.

## <a id="union-einschraenkungen">2. Union-Einschränkungen</a>

Der Union-Operator hat folgende Einschränkungen:

- Self-Union wird nicht unterstützt:
    - Bei Kafka kann nicht dasselbe Quell-DataFrame-Objekt verwendet und daraus abgeleitete DataFrames per Union verbunden werden. Als Workaround können unterschiedliche DataFrames verwendet werden, die von derselben Quelle lesen.
    - Bei Kinesis können keine DataFrames per Union verbunden werden, die von derselben Kinesis-Quelle mit derselben Konfiguration abgeleitet sind. Als Workaround kann statt unterschiedlicher DataFrames jedem DataFrame eine andere `consumerName`-Option zugewiesen werden.
- Zustandsbehaftete Operatoren (z. B. `aggregate`, `deduplicate`, `transformWithState`) dürfen nicht vor dem Union definiert werden.
- Union mit Batch-Quellen wird nicht unterstützt.

## <a id="mappartitions">3. `mapPartitions`-Einschränkung</a>

`mapPartitions` in Scala und ähnliche Python-APIs (`mapInPandas`, `mapInArrow`) nehmen einen Iterator über die gesamte Eingabe-Partition entgegen und erzeugen einen Iterator über die gesamte Ausgabe mit beliebiger Zuordnung zwischen Eingabe und Ausgabe. Diese APIs können in Real-Time Mode Performance-Probleme verursachen, da sie die gesamte Ausgabe blockieren, was die Latenz erhöht. Die Semantik dieser APIs unterstützt die Watermark-Weitergabe nicht gut.

Stattdessen sollten skalare UDFs in Kombination mit "Transform complex data types" oder `filter` verwendet werden, um ähnliche Funktionalität zu erreichen.

## <a id="transformwithstateinpandas">4. `transformWithStateInPandas` nicht unterstützt</a>

Der Operator `transformWithStateInPandas` wird in Real-Time Mode nicht unterstützt. Wird benutzerdefinierte zustandsbehaftete Verarbeitung in Python mit Real-Time Mode benötigt, sollte stattdessen die zeilenbasierte `transformWithState`-API verwendet werden. Die zeilenbasierte API bietet dieselben Fähigkeiten zur zustandsbehafteten Verarbeitung, verwendet dabei jedoch `Row`-Objekte anstelle von Pandas-DataFrames.

Details zum Verhalten von `transformWithState` in Real-Time Mode finden sich im entsprechenden Abschnitt der Datei `Referenz.md`, ein funktionierendes Python-Beispiel mit der zeilenbasierten API in der Datei `Beispiele.md`.

---

## <a id="quellen">5. Quellen</a>

- Real-time mode limitations (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/real-time/limitations
- Real-time mode limitations (Mirror, Azure, verifiziert/vollständig abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/limitations
- Real-time mode limitations (AWS): https://docs.databricks.com/aws/en/structured-streaming/real-time/limitations

**Stand:** 2026-08-22.
