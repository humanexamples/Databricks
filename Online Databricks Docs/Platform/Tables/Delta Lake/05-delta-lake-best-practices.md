# Best Practices: Delta Lake

Diese Seite beschreibt bewährte Vorgehensweisen für den Einsatz von Delta Lake.

## Überblick über die Best Practices

Folgende allgemeine Empfehlungen gelten für die meisten Delta-Lake-Workloads:

- Nutzen Sie von Unity Catalog verwaltete Tabellen.
- Nutzen Sie Predictive Optimization.
- Nutzen Sie Liquid Clustering.
- Löschen und erstellen Sie eine Tabelle am selben Ort neu, verwenden Sie immer eine `CREATE OR REPLACE TABLE`-Anweisung.

## Veraltete Delta-Konfigurationen entfernen

Databricks empfiehlt, die meisten expliziten Legacy-Delta-Konfigurationen aus Spark-Konfigurationen und Tabelleneigenschaften zu entfernen, wenn Sie auf eine neue Databricks-Runtime-Version aktualisieren. Legacy-Konfigurationen können verhindern, dass neue Optimierungen und Standardwerte von Databricks bei migrierten Workloads greifen.

## Dateien kompaktieren

Predictive Optimization führt automatisch `OPTIMIZE`- und `VACUUM`-Befehle auf von Unity Catalog verwalteten Tabellen aus.

Databricks empfiehlt, den Befehl `OPTIMIZE` häufig auszuführen, um kleine Dateien zu kompaktieren.

Diese Operation entfernt die alten Dateien nicht. Um sie zu entfernen, führen Sie den Befehl `VACUUM` aus.

## Kein Spark-Caching mit Delta Lake verwenden

Databricks empfiehlt, kein Spark-Caching mit Delta Lake zu verwenden, aus folgenden Gründen:

- Sie verlieren das Data Skipping, das durch zusätzliche Filter auf dem gecachten `DataFrame` entstehen würde.
- Die gecachten Daten werden möglicherweise nicht aktualisiert, wenn auf die Tabelle über einen anderen Bezeichner zugegriffen wird.

## Unterschiede zwischen Delta Lake und Parquet auf Apache Spark

Delta Lake übernimmt folgende Operationen automatisch. Führen Sie diese Operationen niemals manuell aus:

- **`REFRESH TABLE`:** Delta-Lake-Tabellen liefern immer den aktuellsten Stand. Nach Änderungen müssen Sie `REFRESH TABLE` nicht manuell aufrufen.
- **Partitionen hinzufügen und entfernen:** Delta Lake verfolgt automatisch, welche Partitionen in einer Tabelle vorhanden sind, und aktualisiert die Liste beim Hinzufügen oder Entfernen von Daten. Sie müssen daher `ALTER TABLE [ADD|DROP] PARTITION` oder `MSCK` nicht ausführen.
- **Eine einzelne Partition laden:** Partitionen direkt zu lesen ist nicht nötig. Sie müssen zum Beispiel nicht `spark.read.format("parquet").load("/data/date=2017-01-01")` ausführen. Nutzen Sie stattdessen eine `WHERE`-Klausel für Data Skipping, etwa `spark.read.table("<table-name>").where("date = '2017-01-01'")`.
- **Datendateien nicht manuell ändern:** Delta Lake nutzt das Transaktionslog, um Änderungen an der Tabelle atomar zu committen. Ändern, ergänzen oder löschen Sie Parquet-Datendateien einer Delta-Lake-Tabelle niemals direkt. Das kann zu Datenverlust oder Tabellenkorruption führen.

## Performance von Delta-Lake-Merge verbessern

Mit folgenden Ansätzen reduzieren Sie die Zeit für einen Merge:

- **Suchraum für Treffer reduzieren:** Standardmäßig durchsucht die `merge`-Operation die gesamte Delta-Lake-Tabelle nach Treffern in der Quelltabelle. Eine Möglichkeit, `merge` zu beschleunigen, ist es, den Suchraum durch bekannte Einschränkungen in der Match-Bedingung zu reduzieren. Nehmen wir an, eine Tabelle ist nach `country` und `date` partitioniert. Sie wollen mit `merge` Informationen für den letzten Tag und ein bestimmtes Land aktualisieren. Folgende Bedingung macht die Abfrage schneller, weil nur in den relevanten Partitionen nach Treffern gesucht wird:

```sql
%sql
events.date = current_date() AND events.country = 'USA'
```

Diese Abfrage reduziert außerdem die Wahrscheinlichkeit von Konflikten mit anderen gleichzeitigen Operationen.

- **Dateien kompaktieren:** Liegen die Daten in vielen kleinen Dateien, kann das Lesen zur Trefferermittlung langsam werden. Kompaktieren Sie kleine Dateien zu größeren, um den Lesedurchsatz zu verbessern.
- **Shuffle-Partitionen für Schreibvorgänge steuern:** Die `merge`-Operation shuffelt Daten mehrfach, um die aktualisierten Daten zu berechnen und zu schreiben. Die Anzahl der Tasks beim Shuffling steuert die Spark-Session-Konfiguration `spark.sql.shuffle.partitions`. Dieser Parameter bestimmt nicht nur die Parallelität, sondern auch die Anzahl der Ausgabedateien. Ein höherer Wert erhöht die Parallelität, erzeugt aber auch mehr kleinere Dateien.
- **Optimierte Schreibvorgänge aktivieren:** Bei partitionierten Tabellen kann `merge` deutlich mehr kleine Dateien erzeugen als es Shuffle-Partitionen gibt. Jeder Shuffle-Task kann nämlich mehrere Dateien in mehreren Partitionen schreiben, was zum Flaschenhals werden kann. Optimierte Schreibvorgänge reduzieren die Anzahl der Dateien.
- **Dateigrößen der Tabelle anpassen:** Databricks passt Dateigrößen automatisch an die Tabellengröße an. Kleinere Tabellen erhalten kleinere Dateien, größere Tabellen größere Dateien.
- **Low Shuffle Merge:** Low Shuffle Merge ist eine optimierte Implementierung von `MERGE`. Sie liefert bei den meisten gängigen Workloads eine bessere Performance. Zusätzlich erhält sie bestehende Layout-Optimierungen wie Liquid Clustering bei unveränderten Daten.

---
**Quelle:** https://docs.databricks.com/aws/en/delta/best-practices  
**Stand:** 2026-08-06
