# Low Shuffle Merge

Low Shuffle Merge ist eine optimierte Implementierung des `MERGE`-Befehls in Databricks. Sie reduziert Shuffle-Operationen und verbessert dadurch die Performance vieler typischer Workloads spürbar.

## Vorteile

### Bessere Performance

Low Shuffle Merge verarbeitet unveränderte Zeilen getrennt von geänderten Zeilen. Unveränderte Zeilen durchlaufen dabei keine Shuffle-Schritte, keine aufwendige Verarbeitung und keinen zusätzlichen Overhead. Früher liefen unveränderte Zeilen durch dieselbe teure Pipeline wie geänderte Zeilen, inklusive mehrerer Shuffle-Stufen.

### Erhaltenes Datenlayout

Low Shuffle Merge erhält nach bestem Bemühen das bestehende Datenlayout unveränderter Datensätze, einschließlich des Liquid-Clustering-Layouts. Das reduziert den Bedarf, nach einem Merge `OPTIMIZE` auszuführen. Es verhindert außerdem eine Verschlechterung der Performance bei nachfolgenden Operationen.

## Verfügbarkeit

- Allgemein verfügbar (GA) ab Databricks Runtime 10.4 LTS.
- Public Preview in Databricks Runtime 9.1 LTS.
- Ab Runtime 10.4 standardmäßig aktiviert.
- In früheren Runtime-Versionen aktivieren Sie die Funktion über das Konfigurations-Flag `spark.databricks.delta.merge.enableLowShuffle`, gesetzt auf `true`.

## Wichtige Hinweise

Auch bei Tabellen mit Liquid Clustering kann es weiterhin nötig sein, `OPTIMIZE` auszuführen. Neu eingefügte oder geänderte Daten haben nach dem Merge möglicherweise noch kein optimales Layout.

Bei Tabellen mit dem älteren Z-Ordering gilt Ähnliches: Low Shuffle Merge versucht, das bestehende Z-Order-Layout zu erhalten. Databricks empfiehlt für neue Tabellen jedoch Liquid Clustering statt des Legacy-Z-Ordering.

---
**Quelle:** https://docs.databricks.com/aws/en/optimizations/low-shuffle-merge  
**Stand:** 2026-08-06
