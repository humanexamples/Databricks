# Wo ist DLT geblieben?

Referenz zur Umbenennung von Delta Live Tables (DLT) zu Lakeflow-Pipelines, basierend auf `https://docs.databricks.com/aws/en/ldp/concepts/where-is-dlt` (wörtlich per Azure/Microsoft-Learn-Spiegelseite gegengeprüft).

## Abschnittsübersicht

1. [Umbenennung ohne Migrationszwang](#umbenennung)
2. [Python-API-Namensänderungen](#python-api)
3. [SQL-Syntax: keine Umbenennung durch diese Migration](#sql-syntax)
4. [Verbleibende DLT-Referenzen](#verbleibende-referenzen)
5. [Quellen](#quellen)

---

## <a id="umbenennung">1. Umbenennung ohne Migrationszwang</a>

Das Produkt, das früher als Delta Live Tables (DLT) bekannt war, wurde zu Lakeflow-Pipelines aktualisiert. Wer zuvor DLT verwendet hat, muss für die Nutzung von Lakeflow-Pipelines **nicht migrieren** — bestehender Code funktioniert weiterhin unverändert.

Es gibt jedoch Änderungen, die vorgenommen werden können, um Lakeflow-Pipelines besser zu nutzen — sowohl aktuell als auch zukünftig — und um Kompatibilität mit Apache Spark™ Declarative Pipelines herzustellen (ab Apache Spark 4.1).

## <a id="python-api">2. Python-API-Namensänderungen</a>

Im Python-Code kann `import dlt` durch `from pyspark import pipelines as dp` ersetzt werden. Dies erfordert zusätzlich folgende Änderungen:

- `@dlt` wird durch `@dp` ersetzt.
- Der Decorator `@table` wird nun verwendet, um Streaming Tables zu erstellen; der neue Decorator `@materialized_view` wird verwendet, um Materialized Views zu erstellen.
- `@view` heißt nun `@temporary_view`.

Für weitere Details zu den Python-API-Namensänderungen und den Unterschieden zwischen Lakeflow-Pipelines und Apache Spark Declarative Pipelines verweist die Doku auf die Seite "Was ist aus `@dlt` geworden?" in der Python-Referenz für Pipelines.

## <a id="sql-syntax">3. SQL-Syntax: veraltete `LIVE`-Keywords vs. moderne SQL-Syntax</a>

**Korrektur/Klarstellung gegenüber einer möglichen Erwartung:** Die Quellseite dieser Datei sowie die von ihr verlinkte Vergleichstabelle dokumentieren ausschließlich Namensänderungen in der **Python**-API. Eine SQL-seitige Umbenennungstabelle (etwa `CREATE STREAMING LIVE TABLE` → `CREATE STREAMING TABLE` o. Ä.) wird auf keiner der geprüften aktuellen Doku-Seiten (dieser Seite, der verlinkten Python-Referenzseite mit Vergleichstabelle, sowie den einzelnen SQL-Referenzseiten zu `CREATE STREAMING TABLE`, `CREATE MATERIALIZED VIEW` und `CREATE VIEW`) genannt.

Stattdessen zeigt die Vergleichstabelle "Differences between DLT, Lakeflow pipelines, and Apache Spark Declarative Pipelines" (Python-Referenzseite) für die SQL-Zeilen **identische** Syntax in der Spalte "DLT syntax" und der Spalte "SDP Syntax (Lakeflow and Apache, where applicable)" — die SQL-Anweisungen wurden durch die DLT→Lakeflow-Pipelines-Umbenennung laut aktueller Doku also **nicht** verändert:

| Bereich | DLT-Syntax | SDP-Syntax (Lakeflow und Apache, wo zutreffend) | In Apache Spark verfügbar |
|---|---|---|---|
| SQL – Streaming Table | `CREATE STREAMING TABLE ...` | `CREATE STREAMING TABLE ...` | Ja |
| SQL – Materialized View | `CREATE MATERIALIZED VIEW ...` | `CREATE MATERIALIZED VIEW ...` | Ja |
| SQL – Flow | `CREATE FLOW ...` | `CREATE FLOW ...` | Ja |

**Klärung der zuvor offenen historischen Randnotiz:** Es gibt sehr wohl noch ältere, veraltete SQL-Syntax mit `LIVE` im Namen, die auf modernere Äquivalente ohne `LIVE` abbildet:

| Veraltet (DLT) | Modern (SDP) |
|---|---|
| `CREATE OR REFRESH STREAMING LIVE TABLE` | `CREATE OR REFRESH STREAMING TABLE` |
| `CREATE OR REFRESH LIVE TABLE` | `CREATE OR REFRESH MATERIALIZED VIEW` |
| `CREATE LIVE VIEW` / `CREATE TEMPORARY LIVE VIEW` | `CREATE VIEW` / `CREATE TEMPORARY VIEW` |

Dies passt zum einzigen noch auffindbaren Hinweis auf der Python-Referenzseite zu `create_streaming_table()`: *"The `create_target_table()` and `create_streaming_live_table()` functions are deprecated. Databricks recommends updating existing code to use the `create_streaming_table()` function."* — dort betrifft es zwei veraltete **Python**-Funktionsnamen, das obige `LIVE`-Muster zieht sich aber parallel durch die SQL-Syntax. Eine explizite, aktuell von Databricks selbst so tabellarisch dokumentierte SQL-Umbenennungstabelle für `LIVE`-Schlüsselwörter ließ sich auf den ursprünglich geprüften Seiten nicht finden; die obige Zuordnung ergänzt daher die Doku-Recherche um extern bestätigte Praxis-Information.

## <a id="verbleibende-referenzen">4. Verbleibende DLT-Referenzen</a>

Es gibt weiterhin einige Referenzen auf den Namen DLT in Databricks:

- Die klassischen SKUs für Lakeflow-Pipelines beginnen weiterhin mit `DLT`.
- Event-Log-Schemas mit `dlt` im Namen wurden nicht geändert.
- Python-APIs, die `dlt` im Namen verwenden, können weiterhin genutzt werden — Databricks empfiehlt jedoch, zu den neuen Namen zu wechseln.

## <a id="quellen">5. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/concepts/where-is-dlt
- https://learn.microsoft.com/en-us/azure/databricks/ldp/concepts/where-is-dlt (Gegenprüfung, wörtlich)
- Lakeflow pipelines Python language reference, Abschnitt "What happened to `@dlt`?" (Vergleichstabelle DLT/SDP/Apache Spark): https://learn.microsoft.com/en-us/azure/databricks/ldp/developer/python-ref
- create_streaming_table() Python-Referenz (Hinweis zu deprecateten Funktionsnamen `create_target_table()`/`create_streaming_live_table()`): https://learn.microsoft.com/en-us/azure/databricks/ldp/developer/ldp-python-ref-streaming-table
- Pipeline SQL language reference, CREATE STREAMING TABLE / CREATE MATERIALIZED VIEW / CREATE VIEW (geprüft, keine Umbenennungshinweise gefunden): https://docs.databricks.com/aws/en/ldp/developer/sql-ref

**Stand:** 2026-08-22.
