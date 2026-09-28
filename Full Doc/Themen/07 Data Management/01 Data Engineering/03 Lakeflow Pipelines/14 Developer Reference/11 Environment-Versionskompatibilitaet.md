# Environment-Versionskompatibilität

## Abschnittsübersicht

1. [Einschränkungen unter Spark Connect](#einschraenkungen)
2. [Verhaltensänderungen](#verhaltensaenderungen)
3. [Kompatibilitäts-Scan](#scan)
4. [Migrations-Ablauf](#migration)
5. [Kategorien betroffener Probleme](#kategorien)
6. [Quellen](#quellen)

---

## <a id="einschraenkungen">1. Einschränkungen unter Spark Connect</a>

Environment-Versionen laufen über Spark Connect und unterliegen dadurch Einschränkungen. Pipelines schlagen fehl, wenn Python-Code

- "den Spark-Session-Zustand innerhalb einer mit einem Pipelines-Dekorator versehenen Funktion mutiert" (*"Mutates Spark session state inside a function decorated with a pipelines decorator"*), oder
- unter Spark Connect nicht verfügbare PySpark-APIs wie `SparkContext`, `RDD`, `SQLContext` oder Py4J verwendet.

---

## <a id="verhaltensaenderungen">2. Verhaltensänderungen</a>

Zwei zentrale Verhaltensunterschiede treten bei Environment-Versionen auf:

**Verschachtelte DataFrame-Konstruktion und Session-Mutation:** DataFrames verhalten sich unterschiedlich, je nachdem, wann relativ zu ihrer Erzeugung Änderungen am Session-Zustand erfolgen.

**Veränderlicher UDF-Zustand:** *"When a UDF references a Python global variable whose value changes after the UDF is defined"* — verweist eine UDF auf eine globale Python-Variable, deren Wert sich nach der UDF-Definition ändert, verwendet die UDF unter Environment-Versionen den Wert zum Definitionszeitpunkt (nicht den zum Aufrufzeitpunkt).

---

## <a id="scan">3. Kompatibilitäts-Scan</a>

Aktivierung über den Konfigurationsschlüssel `pipelines.environmentVersion.enableCompatibilityScan`, gesetzt auf `true`. Dieser Scan:

- gibt pro erkanntem Muster ein `BehaviorChangeInSparkConnect`-`WARN`-Ereignis im Pipeline-Event-Log aus (*"Emits one `BehaviorChangeInSparkConnect` `WARN` event in the pipeline event log per detected pattern"*),
- blockiert die Aktivierung der Environment-Version, bis die Warnungen behoben sind.

---

## <a id="migration">4. Migrations-Ablauf</a>

1. Kompatibilitäts-Scan aktivieren.
2. Lauf auslösen und `BehaviorChangeInSparkConnect`-Ereignisse prüfen.
3. Code anpassen, um erkannte Muster zu beheben.
4. Environment-Version nach Behebung der Probleme aktivieren.
5. Erfolgreiche Migration verifizieren.

---

## <a id="kategorien">5. Kategorien betroffener Probleme</a>

Die Doku listet Problem-Codes in folgenden Kategorien, jeweils mit konkreten Beispielen und Lösungsvorschlägen in der vollständigen Referenztabelle:

- Datenbank- und Katalog-Mutationen,
- Spark-Konfigurations-Mutationen,
- Ersetzen temporärer Sichten,
- UDF- und UDTF-Mutationen,
- Eager-Ausführung innerhalb von Flow-Funktionen.

**Ungeklärt:** Die einzelnen konkreten Problem-Codes samt zugehöriger Beispiele und Fix-Vorschläge aus der vollständigen Referenztabelle wurden per WebFetch nicht vollständig wörtlich wiedergegeben — nur die fünf übergeordneten Kategorien sind hier belegt.

---

## <a id="quellen">6. Quellen</a>

- Environment version compatibility (Spark-Connect-Einschränkungen, Verhaltensänderungen, Kompatibilitäts-Scan-Konfiguration, Migrations-Ablauf, Problem-Kategorien): https://docs.databricks.com/aws/en/ldp/developer/environment-version-compatibility

**Stand:** 2026-08-19.
