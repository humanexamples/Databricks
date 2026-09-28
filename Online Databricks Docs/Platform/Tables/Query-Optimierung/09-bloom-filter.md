# Bloom-Filter-Indizes (veraltet)

**Wichtig:** Verwenden Sie keine Bloom-Filter-Indizes mehr. Databricks hat diese Funktion als veraltet markiert und empfiehlt, bestehende Bloom-Filter-Indizes von Ihren Tabellen zu entfernen.

Bloom-Filter-Indizes sind ein älterer Data-Skipping-Mechanismus. Databricks empfiehlt sie für keinen Workload mehr. Sie erhöhen den Schreib-Overhead, sind schwer zu tunen und wurden durch wirksamere Alternativen abgelöst.

## Empfohlene Alternativen

Nutzen Sie stattdessen folgende Funktionen:

- **Predictive I/O:** Auf Photon-fähigem Compute ab Databricks Runtime 12.2 führt Predictive I/O automatisch Data Skipping auf allen Spalten durch. Es ersetzt Bloom-Filter-Indizes vollständig. Bloom-Filter-Indizes verursachen bei aktiviertem Photon nur noch zusätzlichen Schreib-Overhead.
- **Liquid Clustering:** Ab Databricks Runtime 13.3 verbessert Liquid Clustering das Data Skipping, indem es Daten anhand häufig gefilterter Spalten organisiert.

## Bestehende Bloom-Filter-Indizes entfernen

Haben Sie noch Bloom-Filter-Indizes auf Ihren Tabellen, entfernen Sie diese, um unnötigen Schreib-Overhead zu vermeiden:

```sql
%sql
DROP BLOOMFILTER INDEX ON TABLE table_name
```

Nach dem Entfernen aller Bloom-Filter-Indizes führen Sie `VACUUM` aus. Das räumt die zugrunde liegenden Indexdateien im Verzeichnis `_delta_index` auf.

---
**Quelle:** https://docs.databricks.com/aws/en/optimizations/bloom-filters  
**Stand:** 2026-08-06
