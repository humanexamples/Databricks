# Disk Cache

Beschleunigt wiederholte Lesevorgänge, indem Kopien remote gespeicherter Parquet-Dateien (inklusive Delta-Lake-Tabellen) im lokalen Storage des Compute-Knotens abgelegt werden — ein Standardbestandteil der automatischen Runtime-Optimierungen (siehe [Grundlagen der Query-Performance.md](02%20Grundlagen%20der%20Query-Performance.md), Abschnitt 8).

## Abschnittsübersicht

1. [Funktionsweise](#funktionsweise)
2. [Namenshistorie: Delta Cache → Disk Cache](#namenshistorie)
3. [Disk Cache vs. Spark Cache](#vs-spark-cache)
4. [Cache-Konsistenz](#konsistenz)
5. [Instance-Auswahl für Disk Caching](#instance-auswahl)
6. [Konfiguration](#konfiguration)
7. [Aktivieren, Deaktivieren und Status prüfen](#aktivieren-deaktivieren)
8. [Zusammenfassung](#zusammenfassung)

---

## <a id="funktionsweise">1. Funktionsweise</a>

Der Disk Cache nutzt ein schnelles internes Zwischenformat für zwischengespeicherte Daten. Daten werden automatisch gecacht, sobald sie von einem entfernten Speicherort (z. B. S3, ABFS) gelesen werden — nachfolgende Lesevorgänge erfolgen dann lokal und damit deutlich schneller. Betroffen sind alle Parquet-Datendateien, einschließlich Delta-Lake-Tabellen.

**Hinweis zu `CACHE SELECT`:** In SQL-Warehouses sowie ab Databricks Runtime 14.2 wird der SQL-Befehl `CACHE SELECT` ignoriert — der (verbesserte) Disk Cache übernimmt diese Funktion automatisch, ein manuelles Cachen einzelner Selects ist nicht mehr nötig bzw. wirkungslos.

### Quelle

- https://docs.databricks.com/aws/en/optimizations/disk-cache

---

## <a id="namenshistorie">2. Namenshistorie: Delta Cache → Disk Cache</a>

Das Feature hieß früher **„Delta Cache"** bzw. **„DBIO Cache"**. Die Umbenennung in „Disk Cache" stellt klar, dass es sich **nicht** um einen Bestandteil des Delta-Lake-Protokolls handelt, sondern um ein proprietäres Databricks-Feature (funktioniert dementsprechend auch für nicht-Delta-Parquet-Dateien).

### Quelle

- https://docs.databricks.com/aws/en/optimizations/disk-cache

---

## <a id="vs-spark-cache">3. Disk Cache vs. Spark Cache</a>

| Aspekt | Disk Cache | Spark Cache |
|---|---|---|
| Speicherort | lokale Dateien auf einem Worker-Knoten | In-Memory-Blöcke (abhängig vom Storage Level) |
| Gilt für | Parquet-Tabellen auf S3, ABFS und anderen Dateisystemen | jedes DataFrame oder RDD |
| Auslösung | automatisch beim ersten Lesen (falls aktiviert) | manuell, erfordert Code-Änderungen (`.cache()`/`.persist()`) |
| Auswertung | lazy | lazy |
| Verfügbarkeit | konfigurierbar, bei bestimmten Node-Typen standardmäßig aktiviert | immer verfügbar |
| Eviction | automatisch (LRU oder bei Dateiänderung); manuell bei Cluster-Neustart | automatisch (LRU); manuell via `unpersist` |

Databricks empfiehlt, das automatische Disk Caching gegenüber manuellem Spark Caching zu bevorzugen.

**Spark Cache im Detail (offizielle Apache-Spark-Doku):** Spark SQL cacht Tabellen in einem spaltenbasierten In-Memory-Format über `spark.catalog.cacheTable("tableName")` bzw. `dataFrame.cache()`. Danach scannt Spark SQL nur noch die tatsächlich benötigten Spalten und wählt automatisch eine Kompression, um Speicherverbrauch und GC-Druck zu minimieren. Zum Entfernen aus dem Speicher: `spark.catalog.uncacheTable("tableName")` bzw. `dataFrame.unpersist()`. Über `spark.catalog.listCachedTables()` lassen sich benannte gecachte Relationen auflisten — Einträge, die nur über `Dataset.cache()` ohne Namen gecacht wurden, erscheinen dort **nicht**.

| Parameter | Standard | Bedeutung |
|---|---|---|
| `spark.sql.inMemoryColumnarStorage.compressed` | `true` | wählt automatisch einen Kompressions-Codec je Spalte basierend auf Datenstatistiken |
| `spark.sql.inMemoryColumnarStorage.batchSize` | `10000` | Batch-Größe für das spaltenbasierte Caching — größere Werte verbessern Speicherausnutzung und Kompression, riskieren aber OOMs beim Cachen |

### Quelle

- https://docs.databricks.com/aws/en/optimizations/disk-cache
- https://spark.apache.org/docs/latest/sql-performance-tuning.html#caching-data-in-memory

---

## <a id="konsistenz">4. Cache-Konsistenz</a>

Der Disk Cache erkennt automatisch, wenn zugrunde liegende Dateien erstellt, gelöscht, geändert oder überschrieben werden, und aktualisiert den Cache-Inhalt entsprechend. Eine explizite Cache-Invalidierung bei Schreib-/Änderungs-/Löschoperationen ist **nicht** nötig — veraltete Einträge werden automatisch erkannt und aus dem Cache entfernt.

### Quelle

- https://docs.databricks.com/aws/en/optimizations/disk-cache

---

## <a id="instance-auswahl">5. Instance-Auswahl für Disk Caching</a>

Empfohlener Ansatz: bei der Cluster-Konfiguration Worker-Instance-Typen mit lokalen SSD-Volumes wählen — für solche Worker ist Disk Caching bereits aktiviert und optimal vorkonfiguriert. Der Disk Cache ist standardmäßig so konfiguriert, dass er **höchstens die Hälfte** des auf den lokalen SSDs verfügbaren Speicherplatzes nutzt.

### Quelle

- https://docs.databricks.com/aws/en/optimizations/disk-cache

---

## <a id="konfiguration">6. Konfiguration</a>

Databricks empfiehlt, Cache-optimierte Worker-Instance-Typen zu nutzen, da diese automatisch optimal konfiguriert sind — manuelle Konfiguration ist meist nicht nötig.

**Autoscaling-Falle:** Ist Autoscaling aktiviert und werden Worker abgebaut, geht der auf diesen Workern zwischengespeicherte Spark-Cache-Inhalt verloren — betroffene Daten müssen bei Bedarf erneut aus der Quelle gelesen werden.

**Konfigurationsparameter** (Beispielwerte laut Doku):

| Parameter | Bedeutung | Beispielwert |
|---|---|---|
| `spark.databricks.io.cache.maxDiskUsage` | pro Knoten für gecachte Daten reservierter Plattenplatz (in Bytes) | `50g` |
| `spark.databricks.io.cache.maxMetaDataCache` | pro Knoten für gecachte Metadaten reservierter Plattenplatz (in Bytes) | `1g` |
| `spark.databricks.io.cache.compression.enabled` | ob gecachte Daten komprimiert gespeichert werden | `false` |

**Ungeklärt:** Ob es sich bei den genannten Werten (`50g`, `1g`, `false`) um dokumentierte Standardwerte oder lediglich um Beispielwerte zur Syntax-Illustration handelt, ließ sich aus der geprüften Quelle nicht eindeutig klären.

### Quelle

- https://docs.databricks.com/aws/en/optimizations/disk-cache

---

## <a id="aktivieren-deaktivieren">7. Aktivieren, Deaktivieren und Status prüfen</a>

**Status prüfen:**

```python
spark.conf.get("spark.databricks.io.cache.enabled")
```

**Aktivieren/Deaktivieren:**

```python
spark.conf.set("spark.databricks.io.cache.enabled", "[true | false]")
```

**Wichtig:** Das Deaktivieren löscht bereits gecachte Daten **nicht** — es verhindert lediglich, dass neue Daten zum Cache hinzugefügt oder bestehende Cache-Inhalte gelesen werden.

**Anwendungsfall Benchmarking** (aus einer privaten Kursnotiz): Für Benchmarks, bei denen der Effekt anderer Optimierungen isoliert sichtbar werden soll, lässt sich das Disk Caching gezielt abschalten — dann werden Dateien bei jeder Query erneut aus dem Cloud Storage gelesen statt aus der lokalen Kopie:

```python
spark.conf.set('spark.databricks.io.cache.enabled', False)
```

**Hinweis:** Funktioniert nicht auf Serverless Compute (dort schlägt der Befehl mit einem Fehler fehl) — nur auf Classic Compute nutzbar.

### Quellen

- https://docs.databricks.com/aws/en/optimizations/disk-cache
- Private Kursnotiz

---

## <a id="zusammenfassung">8. Zusammenfassung</a>

- Der **Disk Cache** (früher „Delta Cache"/„DBIO Cache") ist ein proprietäres, nicht an das Delta-Lake-Protokoll gebundenes Databricks-Feature, das Kopien remote gelesener Parquet-Dateien lokal auf dem Worker-Knoten ablegt.
- Er unterscheidet sich vom **Spark Cache** durch automatische Auslösung, lokale Festplattenspeicherung statt In-Memory und automatische statt manuelle Verwaltung.
- **Konsistenz** wird automatisch sichergestellt — Änderungen an den Quelldateien invalidieren betroffene Cache-Einträge ohne manuelles Eingreifen.
- Am besten geeignet sind **Worker-Instance-Typen mit lokalen SSDs**, für die Disk Caching automatisch optimal konfiguriert ist (Standard: höchstens die Hälfte des SSD-Speicherplatzes).
- Konfigurierbar über `spark.databricks.io.cache.maxDiskUsage`, `spark.databricks.io.cache.maxMetaDataCache` und `spark.databricks.io.cache.compression.enabled`; Aktivierung/Deaktivierung über `spark.databricks.io.cache.enabled` — Deaktivieren löscht bestehende Cache-Daten nicht, verhindert aber deren weitere Nutzung. Auf **Serverless Compute** lässt sich der Cache nicht per Config deaktivieren.
- Der SQL-Befehl `CACHE SELECT` wird in SQL-Warehouses und ab Databricks Runtime 14.2 ignoriert, da der Disk Cache dessen Funktion automatisch übernimmt.

### Quelle

- https://docs.databricks.com/aws/en/optimizations/disk-cache
