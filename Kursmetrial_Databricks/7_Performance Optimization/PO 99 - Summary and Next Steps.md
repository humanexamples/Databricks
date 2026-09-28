

  ![Databricks Learning](https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png)

# Zusammenfassung und nächste Schritte

  Das Toolkit zur Performance-Optimierung

**Daten-Layout**

Partitionierungsstrategie
Dateigrößen
ZORDER
Liquid Clustering

  ➔

**Query-Ausführung**

Shuffle & Broadcast Joins
Join-Reihenfolge & Spill
ANALYZE TABLE & CBO
UDF-Optimierung

  ➔

**Diagnostizieren & Optimieren**

Nutzen Sie das Spark UI, um Engpässe zu identifizieren, Verbesserungen zu messen und Optimierungen zu validieren

**MESSEN & VERBESSERN**

**Ihr Weg durch den Kurs**

| Schritt | Was Sie getan haben | Wichtigste Erkenntnis |  |
| --- | --- | --- | --- |
| 1 | Over-Partitioning und das Problem kleiner Dateien untersucht | Lassen Sie Spark das Datei-Layout übernehmen; vermeiden Sie unnötiges Partitionieren | ✓ |
| 2 | ZORDER und Liquid Clustering für Data Skipping verglichen | Liquid Clustering ist flexibel und unterstützt mehrere Spalten ohne Leistungseinbußen | ✓ |
| 3 | Shuffle bei Joins identifiziert und Broadcast Joins angewendet | Broadcast Joins eliminieren teure Datenbewegungen bei Joins mit kleinen Tabellen | ✓ |
| 4 | Explodierende Joins und Spill diagnostiziert und Join-Strategien optimiert | Join-Reihenfolge, Shuffle-Partitionen und ANALYZE TABLE können Spill und Laufzeit drastisch reduzieren | ✓ |
| 5 | Python-UDFs und SQL-UDFs hinsichtlich Performance verglichen | Bevorzugen Sie native Spark-/SQL-Funktionen; partitionieren Sie neu, wenn UDFs erforderlich sind | ✓ |

**Performance-Optimierung ist keine einmalige Aufgabe.**
  Die leistungsstärksten Workloads werden durch kontinuierliches Monitoring aufrechterhalten. Nutzen Sie das Spark UI, um Engpässe zu diagnostizieren, gezielte Optimierungen anzuwenden, Verbesserungen anhand von Metriken zu validieren und den Prozess zu wiederholen, sobald sich Datenmengen und Abfragemuster weiterentwickeln.

##### Zusätzliche Hinweise
#### Das vollständige Optimierungs-Toolkit

Diese Abbildung zeigt die drei Säulen der Performance-Optimierung, die Sie in allen Demos und Labs kennengelernt haben. Jede baut auf der anderen auf, um schnelle, effiziente Workloads zu liefern.

#### Daten-Layout

Wie Ihre Daten physisch auf der Festplatte organisiert sind, wirkt sich direkt auf die Abfragegeschwindigkeit aus. Sie haben gelernt, dass:

- **Over-Partitioning** Tausende kleiner Dateien erzeugt, was zu übermäßigen Cloud-Storage-Anfragen und langsamen Abfragen führt. Wenn Sie Spark das Datei-Layout überlassen, vermeiden Sie dieses Problem vollständig.
- **ZORDER** platziert zusammengehörige Daten in denselben Dateien und ermöglicht so Data Skipping für gefilterte Abfragen — allerdings nur für die Z-geordnete Spalte.
- **Liquid Clustering** ersetzt sowohl Partitionierung als auch ZORDER durch einen flexiblen Multi-Column-Ansatz. Es ermöglicht das Neudefinieren von Clustering-Keys, ohne Daten neu zu schreiben, und bietet ein starkes File Pruning über mehrere Abfragemuster hinweg.

#### Query-Ausführung

Selbst bei gutem Daten-Layout ist die Strategie der Query-Ausführung entscheidend:

- **Shuffle Joins** verteilen Daten über Nodes neu, was bei großen Tabellen teuer ist. **Broadcast Joins** senden kleine Tabellen an alle Nodes und vermeiden so den Shuffle vollständig.
- **Explodierende Joins**, verursacht durch doppelte Keys, können die Zeilenanzahl um das 100-Fache erhöhen und massiven Spill auf die Festplatte verursachen. Das Umsortieren von Joins (kleinere zuerst) und die Verwendung von `ANALYZE TABLE` zur Aktivierung des kostenbasierten Optimizers können Spill eliminieren.
- **Python-UDFs** umgehen den Optimizer von Spark und verarbeiten Daten standardmäßig seriell. SQL-UDFs werden durch Catalyst und Photon optimiert. Wenn Python-UDFs erforderlich sind, ermöglicht Repartitionierung eine parallele Ausführung.

#### Diagnostizieren & Optimieren

Das Spark UI ist Ihr wichtigstes Diagnose-Tool. Im Verlauf dieses Kurses haben Sie gelernt, Folgendes zu lesen:

- **Cloud-Storage-Anfragen** und **Antwortgrößen**, um die I/O-Effizienz zu verstehen
- **Gelesene Dateien** und **ausgeschlossene Dateien (pruned)**, um die Wirksamkeit von Data Skipping zu überprüfen
- **Shuffle-Read-/Write-Größen**, um teure Datenbewegungen zu identifizieren
- **Disk-Spill-Metriken**, um Speicherdruck zu erkennen
- **Query-Pläne (DAGs)**, um den vollständigen Ausführungspfad nachzuvollziehen und die Auswirkungen von Optimierungen zu überprüfen

## Predictive Optimization

**Lassen Sie Databricks automatisch für Sie optimieren**

Nachdem Sie nun die Grundlagen der Performance-Optimierung verstehen — vom Daten-Layout über Clustering bis hin zu Join-Strategien und UDF-Tuning — erkunden Sie **Predictive Optimization**, um viele dieser Aufgaben zu automatisieren.

Predictive Optimization identifiziert automatisch Tabellen, die von Wartungsoperationen profitieren würden, und führt diese für Sie aus. Es übernimmt `OPTIMIZE`, `VACUUM` und `ANALYZE TABLE` basierend auf den Nutzungsmustern Ihrer Tabelle, sodass keine manuelle Wartungsplanung mehr erforderlich ist.

[AWS →](https://docs.databricks.com/aws/en/optimizations/predictive-optimization)
[Azure →](https://learn.microsoft.com/en-us/azure/databricks/optimizations/predictive-optimization)
[GCP →](https://docs.databricks.com/gcp/en/optimizations/predictive-optimization)

## A. Weitere Ressourcen

Nutzen Sie die folgenden Ressourcen, um mehr über die Performance-Optimierung in Databricks zu erfahren und über die neuesten Plattform-Updates auf dem Laufenden zu bleiben.

### A1. Dokumentation

- Optimierungsempfehlungen für Databricks:
[AWS](https://docs.databricks.com/aws/en/optimizations/) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/optimizations/) |
[GCP](https://docs.databricks.com/gcp/en/optimizations/)

- Partitionierungsempfehlungen – Wann und wie Partitionierung verwendet werden sollte:
[AWS](https://docs.databricks.com/aws/en/tables/partitions) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/tables/partitions) |
[GCP](https://docs.databricks.com/gcp/en/tables/partitions)

- Liquid Clustering für Tabellen verwenden – Ersetzt Tabellenpartitionierung und ZORDER:
[AWS](https://docs.databricks.com/aws/en/delta/clustering) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/delta/clustering) |
[GCP](https://docs.databricks.com/gcp/en/delta/clustering)

- Data Skipping mit Z-Order-Indizes für Delta Lake:
[AWS](https://docs.databricks.com/aws/en/delta/data-skipping) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/delta/data-skipping) |
[GCP](https://docs.databricks.com/gcp/en/delta/data-skipping)

- Performance mit Caching in Databricks optimieren:
[AWS](https://docs.databricks.com/aws/en/optimizations/disk-cache) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/optimizations/disk-cache) |
[GCP](https://docs.databricks.com/gcp/en/optimizations/disk-cache)

### A2. Blog und Ankündigungen

- [Announcing Automatic Liquid Clustering: Optimized data layout for up to 10x faster queries](https://www.databricks.com/blog/announcing-automatic-liquid-clustering) - Automatic Liquid Clustering macht die manuelle Auswahl von Clustering-Keys überflüssig, indem es Abfragemuster analysiert und das Daten-Layout automatisch optimiert.

- [Arrow-optimized Python UDFs in Apache Spark 3.5](https://www.databricks.com/blog/arrow-optimized-python-udfs-apache-sparktm-35) - Wie Arrow-optimierte UDFs die Effizienz des Datenaustauschs zwischen der Spark-Runtime und dem UDF-Prozess verbessern.

- [Top 5 Performance Tips](https://www.databricks.com/blog/2022/03/10/top-5-databricks-performance-tips.html) - Praktische Tipps zur Optimierung von Spark-Workloads in Databricks.

- [Accelerate Feature Engineering With Photon](https://www.databricks.com/blog/accelerate-feature-engineering-photon) - Erfahren Sie, wie die Photon Engine in der Databricks Machine Learning Runtime Spark-Jobs und Feature-Engineering-Workloads um das 2-Fache oder mehr beschleunigt.

### A3. Weitere Funktionen außerhalb des Umfangs dieses Kurses

- Predictive Optimization für von Unity Catalog verwaltete Tabellen:
[AWS](https://docs.databricks.com/aws/en/optimizations/predictive-optimization) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/optimizations/predictive-optimization) |
[GCP](https://docs.databricks.com/gcp/en/optimizations/predictive-optimization)

- Adaptive Query Execution:
[Apache Spark AQE Documentation](https://spark.apache.org/docs/latest/sql-performance-tuning.html#adaptive-query-execution)

- ANALYZE TABLE für Statistiken:
[AWS](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-analyze-table) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/sql-ref-syntax-aux-analyze-table) |
[GCP](https://docs.databricks.com/gcp/en/sql/language-manual/sql-ref-syntax-aux-analyze-table)

- Photon-Runtime:
[AWS](https://docs.databricks.com/aws/en/compute/photon) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/compute/photon) |
[GCP](https://docs.databricks.com/gcp/en/compute/photon)

## B. Nächste Schritte

Bauen Sie Ihre Databricks-Kenntnisse mit weiteren Schulungs- und Zertifizierungsressourcen weiter aus.

### B1. Setzen Sie Ihr Lernen fort

Erweitern Sie Ihr Daten- und KI-Wissen durch selbstgesteuerte und von Trainern geleitete Databricks-Schulungen. Diese Kurse helfen Ihnen, Ihre technischen Fähigkeiten zu vertiefen und praktische Erfahrung mit der Databricks-Plattform zu sammeln.

Besuchen Sie [Databricks Training and Certification](https://www.databricks.com/learn/training/home)

- [Advanced Data Engineering with Databricks](https://www.databricks.com/training/catalog/advanced-data-engineering-with-databricks-971) - Erstellen Sie produktionsreife Datenpipelines im großen Maßstab mit Delta Lake und Structured Streaming.

- [Data Engineering with Databricks](https://www.databricks.com/learn/partners/partner-courses-and-public-schedule/data-engineering-databricks) - Lernen Sie die Grundlagen des Data Engineering auf der Databricks Lakehouse Platform.

- [Apache Spark Programming with Databricks](https://www.databricks.com/training/catalog/apache-spark-programming-with-databricks-134) - Entwickeln Sie Kompetenz in der Nutzung von Apache Spark auf der Databricks-Plattform.

### B2. Erwerben Sie eine Zertifizierung

Bestätigen Sie Ihre Databricks-Expertise durch den Erwerb eines offiziellen Zertifikats. Zertifizierungen belegen Ihre Fähigkeit, Databricks-Technologien in realen Daten- und KI-Workloads anzuwenden.

Besuchen Sie [Databricks Certification and Badging](https://www.databricks.com/learn/training/certification)

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
