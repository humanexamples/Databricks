# Compute-Auswahl: Empfehlungen je Workload

> Quelle: <https://docs.databricks.com/aws/en/compute/choose-compute> (Stand der Seite: 11.09.2026)

Diese Seite erklärt, welcher Compute-Typ zu welchem Workload passt. Welche Compute-Ressourcen du auswählen oder anlegen darfst, hängt von deinen Berechtigungen ab.

Hinweise zur Konfiguration von Classic Compute: [Classic compute configuration best practices](https://docs.databricks.com/aws/en/compute/cluster-config-best-practices).

> Die Originalseite enthält **keine Codebeispiele**, nur die vier Entscheidungstabellen unten.

---

## Compute für interaktive Notebooks

| Compute-Typ | Wann verwenden |
|---|---|
| **Serverless Compute** | **Generell empfohlen.** Schnellerer Start, automatische Skalierung, geringere Kosten. |
| **Serverless SQL Warehouse** | Für SQL-basierte Analysen und Reporting. Optimiert auf SQL-Query-Performance. |
| **Classic All-Purpose Compute** | Wenn RDD-APIs oder R benötigt werden. |

Mehr dazu: [Notebook compute resources](https://docs.databricks.com/aws/en/notebooks/notebook-compute) · [01 Serverless Compute/02 Notebooks.md](01%20Serverless%20Compute/02%20Notebooks.md)

---

## Compute für Jobs

Beim Konfigurieren eines Jobs wird **für jeden Task** eine Compute-Ressource gewählt.

| Compute-Typ | Wann verwenden |
|---|---|
| **Serverless Compute** | **Empfohlen für die meisten automatisierten Workloads.** Weniger Einstellungen, schnellerer Start, automatische Skalierung, geringere Kosten. Je nach Latenz- und Kostenanforderung **Performance-optimized** oder **Standard Performance Mode** wählen. |
| **SQL Warehouse** | Für SQL-Tasks. Einen Warehouse-Typ wählen, der zu Latenz- und Kostenanforderung passt. |
| **Classic Jobs Compute** | Für Nicht-SQL-Jobs, die eigene Cluster-Einstellungen brauchen, die Serverless nicht bietet. |
| **Classic All-Purpose Compute** | **Generell vermeiden.** Nicht für automatisierte Workloads optimiert. |

Empfohlener Compute-Typ je Task-Typ: [Recommended compute for each task](https://docs.databricks.com/aws/en/jobs/compute#compute-recommendations).

### Compute für Pipelines

Für eine Pipeline wird entweder Serverless Compute oder eine Classic Pipeline verwendet.

| Compute-Typ | Wann verwenden |
|---|---|
| **Serverless Compute** | **Empfohlen für die meisten automatisierten Workloads.** Weniger Einstellungen, schnellerer Start, automatische Skalierung, geringere Kosten. Je nach Latenz- und Kostenanforderung **Performance-optimized** oder **Standard Performance Mode** wählen. |
| **Classic Pipeline Compute** | Wenn ein Feature benötigt wird, das Serverless nicht unterstützt, oder wenn mit dem **Legacy-Hive-Metastore** gearbeitet wird. |

---

## SQL-Warehouse-Typ für SQL-Workloads

Es gibt drei SQL-Warehouse-Typen:

| Warehouse-Typ | Wann verwenden |
|---|---|
| **Serverless SQL Warehouse** | **Empfohlen für BI, ETL und explorative Analysen.** Start typischerweise in **2–6 Sekunden**, skaliert schnell. |
| **Pro SQL Warehouse** | Wenn Serverless nicht verfügbar ist oder eigenes Networking nötig ist (z. B. Federation oder Hybrid). |
| **Classic SQL Warehouse** | Einstiegs-Performance. Für einfache interaktive Exploration, wenn Serverless oder Pro nicht in Frage kommen. |

Weitere Kriterien: [SQL warehouse types](https://docs.databricks.com/aws/en/compute/sql-warehouse/warehouse-types).

---

## Kurzfassung

| Workload | Erste Wahl | Classic nur, wenn … |
|---|---|---|
| Interaktive Notebooks | Serverless Compute | RDD-APIs oder R nötig |
| SQL-Analysen / BI | Serverless SQL Warehouse | Serverless nicht verfügbar oder eigenes Networking (→ Pro) |
| Jobs | Serverless Compute (SQL-Tasks: SQL Warehouse) | eigene Cluster-Einstellungen nötig (→ Classic Jobs Compute, **nicht** All-Purpose) |
| Pipelines | Serverless Compute | Feature fehlt in Serverless oder Legacy-Hive-Metastore |

## Verwandte Themen

- [01 Serverless Compute/01 Uebersicht.md](01%20Serverless%20Compute/01%20Uebersicht.md)
- [01 Serverless Compute/09 Einschraenkungen.md](01%20Serverless%20Compute/09%20Einschraenkungen.md) (was Serverless nicht kann → Gründe für Classic)
- [01 Serverless Compute/06 Migration von Classic zu Serverless.md](01%20Serverless%20Compute/06%20Migration%20von%20Classic%20zu%20Serverless.md)
