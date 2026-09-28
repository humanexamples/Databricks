[← Übersicht](../00%20Uebersicht.md)

# CDF von AUTO-CDC-Zielen und Materialized Views lesen

> Quellen: [Advanced AUTO CDC topics](https://docs.databricks.com/aws/en/ldp/cdc-advanced) · [Change data capture and snapshots](https://docs.databricks.com/aws/en/data-engineering/what-is-cdc) · [Materialized views (DBSQL)](https://docs.databricks.com/aws/en/ldp/dbsql/materialized) · [Lakeflow Pipelines Release Notes 2024.33](https://docs.databricks.com/aws/en/release-notes/dlt/2024/33/) · [Release Notes August 2026](https://docs.databricks.com/aws/en/release-notes/product/2026/august) · [The AUTO CDC APIs](https://docs.databricks.com/aws/en/ldp/cdc)

Pipeline-Tabellen sind selbst Delta-Tabellen und können deshalb ihrerseits einen CDF liefern. So lassen sich Änderungen **über mehrere Pipelines hinweg** weiterreichen.

```
Quelle ──AUTO CDC──► Streaming Table (SCD 1/2) ──CDF──► nächste Pipeline / Replikation
Tabellen ──────────► Materialized View ────────────CDF (Beta)──► externe Ziele / Audit
```

---

## A – CDF aus einem AUTO-CDC-Ziel lesen

Ab **Databricks Runtime 15.2** kann man den CDF einer Streaming Table lesen, die **Ziel von `AUTO CDC` oder `AUTO CDC FROM SNAPSHOT`** ist, genauso wie bei jeder anderen Delta-Tabelle.

**Voraussetzungen:**

- Die Ziel-Streaming-Table ist in **Unity Catalog veröffentlicht**.
- Lesen mit **DBR 15.2** oder höher. Liest eine **andere Pipeline** den Feed, muss sie ebenfalls DBR 15.2+ verwenden.
- Historisch (Release Notes Lakeflow Pipelines 2024.33): Beim Einführen musste die lesende Pipeline den **Preview-Channel** nutzen.

Gelesen wird mit denselben Mitteln wie immer (`table_changes()`, `readChangeFeed`) → [02 Lesen](../02%20Lesen/01%20Batch%20-%20table_changes%20und%20readChangeFeed.md).

### Besonderheit: `_change_type` bei geändertem Primärschlüssel

- Normalerweise erzeugt ein Update `update_preimage` und `update_postimage`.
- **Ändert sich ein Primärschlüsselwert**, lauten die Events stattdessen **`insert` und `delete`**. Das passiert bei manuellen `UPDATE`/`MERGE` auf Key-Spalten oder bei **SCD 2**, wenn sich `__START_AT` auf einen früheren Sequenzwert ändert.

**Welcher Primärschlüssel gilt?**

| SCD-Typ | Primärschlüssel |
|---|---|
| SCD Typ 1 (und Python-Schnittstelle) | der Parameter `keys` in `create_auto_cdc_flow()` bzw. die `KEYS`-Klausel in `AUTO CDC ... INTO` |
| SCD Typ 2 | `keys`/`KEYS` **plus** `coalesce(__START_AT, __END_AT)`: `__START_AT`, falls vorhanden, sonst `__END_AT` (z. B. beim ersten Datensatz) |

### Warum das wichtig ist

- Laut AUTO-CDC-Limitations streamt man aus dem Ziel eines AUTO-CDC-Prozesses **über dessen Change Feed**, nicht direkt aus der Tabelle.
- Das Ziel von `AUTO CDC FROM SNAPSHOT` liefert einen CDF (SCD 1 oder SCD 2) für nachgelagerte Abfragen. So erhalten auch Snapshot-Quellen die Vorteile von CDC, etwa **inkrementelle Verarbeitung** nachgelagerter Materialized Views und **stabile Surrogate Keys**.
- Bei SCD 1 sieht die Zieltabelle genau wie der neueste Snapshot aus. Der Unterschied: Nachgelagerte Abfragen können über den Change Feed **nur die geänderten Datensätze** verarbeiten.

---

## B – CDF aus einer Materialized View lesen (Beta)

Seit August 2026 kann man den CDF einer Materialized View lesen, die in einer **Lakeflow Pipeline** oder in **Databricks SQL** erstellt wurde. Zweck: MV-Änderungen an Ziele **außerhalb von Databricks** replizieren oder eine Historie der MV-Änderungen für Audit und Reporting führen.

Materialized Views nutzen **Automatic CDF**. Man schaltet den CDF also nicht selbst ein, sondern erfüllt pro MV die Voraussetzungen:

1. **Databricks Runtime 18 LTS** oder höher, auf Classic, Serverless oder Databricks SQL.
2. Die MV, die erzeugende oder die lesende Pipeline nutzt den **`PREVIEW`-Channel**.
3. Die MV hat **Row Tracking** aktiviert (auf Serverless standardmäßig an). Prüfen mit:

```sql
SHOW TBLPROPERTIES my_mv ('delta.enableRowTracking');
```

4. Das **External-Metadata-Flag** ist auf der Pipeline bzw. der MV aktiviert.

Gelesen wird wie bei anderen Delta-Tabellen: `table_changes()`, Streaming-Read oder Option `readChangeFeed`. Aus einer MV oder Streaming Table in Databricks SQL heraus:

```sql
CREATE OR REFRESH STREAMING TABLE sales
  AS SELECT * FROM STREAM my_mv WITH (readChangeFeed=true)
```

### Einschränkungen (zusätzlich zu denen von Automatic CDF)

- Wird die MV **komplett neu geschrieben**, enthält der Feed auch **unveränderte Zeilen**. Mehrere Updates derselben Zeile werden **nicht** zu einem Event zusammengefasst. Zum Herausfiltern: den Feed über **alle Spalten gruppieren**, um Inserts und Deletes mit identischen Werten zu finden.
- **Nur Databricks** kann den CDF einer MV abfragen, keine externen Delta- oder Iceberg-Clients.
- Innerhalb von Lakeflow Pipelines nur aus einer **anderen** Pipeline lesbar (ebenfalls `PREVIEW`-Channel), **nicht** aus der Pipeline, die die MV erzeugt.
- Aus einer MV lässt sich kein Vector-Search-Index erstellen.

> Auf der MV-Seite von Databricks SQL steht deshalb unter Limitations: CDF einer MV ist nur lesbar, wenn man ihn **pro MV** über diese Voraussetzungen aktiviert. **Time Travel** auf MVs wird nicht unterstützt.

---

## C – Umgekehrt: CDF als Beschleuniger für Materialized Views

Materialized Views werden inkrementell oder vollständig aktualisiert. Für **inkrementelles Refresh** sollten die Quelldaten in Delta-Tabellen **mit Row Tracking** liegen; **CDF auf den Quellen wird für bessere Performance empfohlen**. Konfiguration → [01/03 Tabelleneigenschaften](../01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md).

---
[← Vorherige Datei](02%20CDF%20und%20AUTO%20CDC.md) · [Übersicht](../00%20Uebersicht.md) · [Nächste Datei →](04%20Change%20Feeds%20bei%20Datei-Ingestion.md)
