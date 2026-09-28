# Tabellenlayout und Performance

Die Themen Liquid Clustering, Data Skipping, Dateigröße und Partitionierung sind bereits ausführlich im Ordner `Performance Optimization/Foundation Design` dokuverifiziert behandelt worden. Dieses Dokument dient als kompakter Verweis-Hub aus Sicht der Tabellenverwaltung und ergänzt einen bisher noch nicht behandelten Aspekt: die Überwachung der Tabellengröße. Basierend auf offiziellen Databricks-Doku-Seiten (jeweils am Ende jedes Abschnitts referenziert).

## Abschnittsübersicht

1. [Liquid Clustering](#clustering)
2. [Data Skipping](#data-skipping)
3. [Dateigröße steuern](#tune-file-size)
4. [Partitionierung](#partitions)
5. [Tabellengröße überwachen](#size)
6. [Zusammenfassung](#zusammenfassung)

---

## <a id="clustering">1. Liquid Clustering</a>

Liquid Clustering ist Databricks' moderner Ersatz für Hive-Style-Partitioning und Z-Ordering — vollständig behandelt in [Liquid Clustering.md](../../Performance%20Optimization/Foundation%20Design/Liquid%20Clustering.md), inklusive `CLUSTER BY`-Syntax, Automatic Liquid Clustering, Row-Level Concurrency, Isolation Levels und Predictive Optimization.

### Quelle

- https://docs.databricks.com/aws/en/tables/clustering

---

## <a id="data-skipping">2. Data Skipping</a>

Data Skipping vermeidet das Lesen irrelevanter Dateien anhand von Datei-Statistiken — vollständig behandelt in [Data Skipping und Tabellenstatistiken.md](../../Performance%20Optimization/Foundation%20Design/Data%20Skipping%20und%20Tabellenstatistiken.md), inklusive Statistik-Konfiguration, Predictive I/O, Bloom-Filter-Ablösung, Dynamic File Pruning, Range Join Optimization, Full-Text-Search-Indexes und Cost-Based Optimizer.

### Quelle

- https://docs.databricks.com/aws/en/tables/data-skipping

---

## <a id="tune-file-size">3. Dateigröße steuern</a>

Auto Compaction, Optimized Writes und automatische Ziel-Dateigröße nach Tabellengröße — vollständig behandelt in [Grundlagen der Query-Performance.md](../../Performance%20Optimization/Foundation%20Design/Grundlagen%20der%20Query-Performance.md), Abschnitte 4–6.

### Quelle

- https://docs.databricks.com/aws/en/tables/tune-file-size

---

## <a id="partitions">4. Partitionierung</a>

Wann Partitionierung sinnvoll ist, Über-Partitionierung, Ingestion Time Clustering als automatische Alternative — vollständig behandelt in [Partitioning.md](../../Performance%20Optimization/Foundation%20Design/Partitioning.md).

### Quelle

- https://docs.databricks.com/aws/en/tables/partitions

---

## <a id="size">5. Tabellengröße überwachen</a>

### 5.1 `ANALYZE TABLE ... COMPUTE STORAGE METRICS`

Der zentrale Befehl zur Überwachung des Tabellen-Storage, verfügbar ab Databricks Runtime 18.0 und **ausschließlich für Unity-Catalog-Managed-Tables**. Er „zeigt eine detaillierte Aufschlüsselung der Storage-Allokation" und liefert umfassende Metriken:

- **Total Storage Size** — vollständiger Speicher-Fußabdruck inklusive aller Daten, Metadaten und Logs.
- **Active Data** — Größe der aktuellen Tabellenversion.
- **Vacuumable Data** — Speicherplatz, der zurückgewonnen werden kann (siehe [DROP, OPTIMIZE, VACUUM und Auto-TTL.md](Tabellenoperationen/DROP%2C%20OPTIMIZE%2C%20VACUUM%20und%20Auto-TTL.md), Abschnitt 3).
- **Time Travel Data** — historische Daten für Rollbacks.

```sql
ANALYZE TABLE table_name COMPUTE STORAGE METRICS;
```

**Typische Anwendungsfälle:** Identifikation von Kostenoptimierungspotenzial, Analyse des Time-Travel-Overheads, Nachverfolgung des Storage-Wachstums über wiederholte Läufe, Audit über den gesamten Datenbestand hinweg.

**Bezug zu Deletion Vectors:** Bei Tabellen mit regelmäßigen `DELETE`/`UPDATE`-Operationen können Deletion Vectors sowohl Queries beschleunigen als auch die Gesamtgröße der Datendateien reduzieren (siehe [Liquid Clustering.md](../../09%20Performance%20Optimization/01%20Foundation%20Design/05%20Liquid%20Clustering.md), Abschnitt 9.2).

Databricks empfiehlt Unity-Catalog-Managed-Tables mit aktivierter Predictive Optimization, da diese automatisch `OPTIMIZE` und `VACUUM` ausführt und so unnötigen Datei-Aufbau verhindert, ohne die Time-Travel-Fähigkeit zu beeinträchtigen.

### 5.2 `DESCRIBE`-Befehl

Über Databricks-UIs und `DESCRIBE`-Befehle gemeldete Tabellengrößen zeigen die Gesamtgröße der Datendateien im Storage für Dateien, die in der aktuellen Tabellenversion referenziert werden.

### 5.3 Wichtiges Konzept: gemeldete vs. tatsächliche Größe

Die gemeldete Tabellengröße unterscheidet sich von der tatsächlichen Verzeichnisgröße im Cloud-Storage, da Delta Lake und Apache Iceberg frühere Versionen von Datendateien für die Time-Travel-Funktionalität aufbewahren.

### 5.4 Verwandte Wartungsbefehle

- **`VACUUM`:** entfernt ungenutzte Datendateien nach Ablauf der Retention-Frist. Meldet dabei Dateianzahl und -größe der entfernten Dateien — die entfernte Größe übersteigt häufig die Größe der aktuellen Tabellenversion, da mehrere historische Versionen gleichzeitig aufgeräumt werden.
- **`OPTIMIZE`:** fasst Datensätze bestehender Dateien zu neuen, kompaktierten Dateien zusammen, ohne den Dateninhalt zu verändern — die alten Dateien bleiben bis zum nächsten `VACUUM`-Lauf parallel bestehen, was die Gesamt-Verzeichnisgröße vorübergehend erhöht, während die *gemeldete* Tabellengröße (Abschnitt 5.2) durch weniger referenzierte Dateien sinkt.
- **`REORG TABLE` und `DROP FEATURE`:** folgen demselben Muster wie `OPTIMIZE` — beide erfordern das Neuschreiben von Datendateien und erhöhen dadurch vorübergehend die Verzeichnisgröße, bis ein nachfolgender `VACUUM`-Lauf die nicht mehr referenzierten Dateien entfernt.

### Quelle

- https://docs.databricks.com/aws/en/tables/size

---

## <a id="zusammenfassung">6. Zusammenfassung</a>

- Die Kern-Layout-Optimierungen (Liquid Clustering, Data Skipping, Dateigröße, Partitionierung) sind vollständig im Ordner [Performance Optimization/Foundation Design](../../Performance%20Optimization/Foundation%20Design/) dokumentiert.
- **`ANALYZE TABLE ... COMPUTE STORAGE METRICS`** (ab Runtime 18.0, nur Unity-Catalog-Managed-Tables) liefert eine detaillierte Aufschlüsselung von Active Data, Vacuumable Data und Time Travel Data.
- Die im UI oder über `DESCRIBE` gemeldete Tabellengröße entspricht **nicht** der tatsächlichen Cloud-Storage-Verzeichnisgröße, da Time-Travel-Versionen zusätzlichen Speicherplatz belegen, bis `VACUUM` läuft.

---

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### CREATE BLOOMFILTER INDEX (deprecated)

Die Seite zu `CREATE BLOOMFILTER INDEX` enthält keine SQL-Syntax mehr — sie besteht nur noch aus einem Deprecation-Hinweis: „Bloom filter indexes are deprecated. Do not create new Bloom filter indexes. Use predictive I/O or liquid clustering instead." Bloom-Filter-Indizes wurden durch Predictive I/O und Data Skipping (siehe [Data Skipping und Tabellenstatistiken.md](../../Performance%20Optimization/Foundation%20Design/Data%20Skipping%20und%20Tabellenstatistiken.md)) sowie Liquid Clustering abgelöst.

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/delta-create-bloomfilter-index

### DROP BLOOMFILTER INDEX

Für bestehende Bloom-Filter-Indizes auf älteren Tabellen empfiehlt Databricks ausdrücklich deren Entfernung:

```sql
DROP BLOOMFILTER INDEX ON [TABLE] table_name [FOR COLUMNS(columnName1 [, ...])]
```

„Bloom filter indexes are deprecated. Databricks recommends dropping all existing Bloom filter indexes." Sobald eine Tabelle keine Bloom-Filter mehr besitzt, werden die zugehörigen Index-Dateien beim nächsten `VACUUM`-Lauf entfernt (siehe [Tabellenoperationen/DROP, OPTIMIZE, VACUUM und Auto-TTL.md](Tabellenoperationen/DROP%2C%20OPTIMIZE%2C%20VACUUM%20und%20Auto-TTL.md), Abschnitt 3).

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/delta-drop-bloomfilter-index
