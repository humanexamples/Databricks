[← Übersicht](../00%20Uebersicht.md)

# CDF über Delta Sharing teilen (Anbieter / Provider)

> Quellen: [ALTER SHARE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-share) · [Create and manage shares](https://docs.databricks.com/aws/en/opensharing/create-share) · [Manage egress costs](https://docs.databricks.com/aws/en/opensharing/manage-egress) · [CREATE SHARE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-share) · [SHOW ALL IN SHARE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-all-in-share) · [Sharing SQL reference](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-sharing) · [Use change data feed on Databricks](https://docs.databricks.com/aws/en/tables/features/change-data-feed)

> Delta Sharing heißt in der aktuellen Databricks-Doku **OpenSharing**. Beide Namen meinen dasselbe Protokoll.

## Die Grundregel

Damit Empfänger den CDF einer geteilten Tabelle lesen können, braucht es **zwei** Dinge:

1. **CDF auf der Quelltabelle** (bei Legacy CDF: `delta.enableChangeDataFeed = true`), und zwar **bevor** sie geteilt wird.
2. Die Tabelle wird **`WITH HISTORY`** geteilt.

> Aus der Doku: *„If, in addition to doing time travel queries and streaming reads, you want your customers to be able to query a table's change data feed (CDF) using the table_changes() function, you must enable CDF on the table before you share it `WITH HISTORY`.“*

**Automatic CDF** funktioniert laut CDF-Doku auch mit **Databricks-to-Databricks OpenSharing**.

---

## `ALTER SHARE`: Tabelle mit Historie hinzufügen

### Syntax (Auszug)

```text
alter_add_table
  { { ALTER | ADD } [ TABLE ] table_name [ COMMENT comment ]
        [ PARTITION clause ] [ AS table_share_name ]
        [ WITH HISTORY | WITHOUT HISTORY ] }
```

| Klausel | Bedeutung |
|---|---|
| `WITH HISTORY` | teilt die Tabelle mit **vollständiger Historie**: Empfänger können Time Travel (`VERSION AS OF`, `TIMESTAMP AS OF`), Streaming-Reads und Transaktionen ausführen und, bei aktivem CDF, `table_changes()` nutzen |
| `WITHOUT HISTORY` | nur der aktuelle Stand |

### Default und Versionen

| Umgebung | Default beim Hinzufügen einer Tabelle |
|---|---|
| Databricks SQL und **DBR 16.2+** | `WITH HISTORY` |
| DBR 16.1 und älter | `WITHOUT HISTORY` |
| ganzes **Schema** teilen | immer `WITH HISTORY`, unabhängig von der Runtime |

- `WITH HISTORY` / `WITHOUT HISTORY` gibt es ab **DBR 12.2 LTS**.
- In DBR 11.1 bis 12.0 musste stattdessen `WITH CHANGE DATA FEED [ START VERSION version ]` angegeben werden. **`WITH CHANGE DATA FEED` ist deprecated.**
- Für Databricks-to-Databricks-Shares teilt `WITH HISTORY` zusätzlich das **Delta-Log** der Tabelle, um die Leseperformance zu verbessern.

### Beispiele

```sql
ALTER SHARE <share-name> ADD TABLE <catalog-name>.<schema-name>.<table-name>  [COMMENT "<comment>"]
   [PARTITION(<clause>)] [AS <alias>]
   [WITH HISTORY | WITHOUT HISTORY];
```

```sql
-- Share a table with history
> ALTER SHARE share ADD TABLE table1 WITH HISTORY;
> ALTER SHARE share ADD TABLE table2 WITHOUT HISTORY;
> SHOW ALL IN SHARE share;
  Name    type   ... history_sharing  ...
  ------  ------ ... ----------------
  Table1  TABLE  ... ENABLED          ...
  Table2  TABLE  ... DISABLED         ...
```

`SHOW ALL IN SHARE` zeigt in der Spalte `history_sharing`, ob die Historie (und damit ein möglicher CDF) geteilt wird.

### Kompletter Ablauf für einen CDF-Share

Aus den Einzelbeispielen der Doku zusammengesetzt:

```sql
-- 1. CDF auf der Quelltabelle einschalten (Legacy CDF), BEVOR geteilt wird
ALTER TABLE myDeltaTable
  SET TBLPROPERTIES (delta.enableChangeDataFeed = true)

-- 2. Share anlegen
> CREATE SHARE some_share;

-- 3. Tabelle mit Historie hinzufügen
> ALTER SHARE share ADD TABLE table1 WITH HISTORY;
```

### Per UI (Catalog Explorer)

Catalog → Zahnrad → **OpenSharing** → Tab *Shared by me* → Share wählen → **Manage assets > Edit assets** → Tabelle auswählen → Option **History** aktivieren → **Save**.

---

## Einsatzfall: inkrementelle Replikation und Egress-Kosten

Wird eine Tabelle mit ihrem CDF geteilt, kann der Empfänger die Änderungen lesen und in eine **lokale Kopie mergen**, auf der seine Nutzer dann abfragen. So überqueren Nutzerabfragen keine Regionsgrenzen, und **Egress** entsteht nur für das Aktualisieren der Kopie. Ein Databricks-Empfänger kann dafür einen Lakeflow Job verwenden.

> Voraussetzung laut Doku: CDF auf der Tabelle aktivieren **und** `WITH HISTORY` teilen.

---

## Was sich nicht mit CDF teilen lässt

| Objekt | CDF für Empfänger? |
|---|---|
| **Streaming Tables** an Databricks-to-**Open**-Empfänger | **nein**: nur der aktuelle Snapshot. Für CDF stattdessen eine reguläre Delta-Tabelle mit CDF teilen. |
| **Managed Iceberg Tables** | **nein**: CDF wird für Managed Iceberg Tables beim Teilen nicht unterstützt |
| Tabellen mit **Type Widening** | ja, Empfänger müssen aber `responseFormat = delta` setzen und dürfen nicht über die Typänderung hinweg lesen → [02 Empfänger](02%20CDF%20lesen%20%28Empfaenger%29.md) |

> **Sicherheitshinweis (Cloud-Token-Zugriff):** Bei Tabellen, die `WITH HISTORY` ohne Partitionsfilter geteilt werden, erhalten Empfänger Credentials auf das **Wurzelverzeichnis** der Tabelle. Das umfasst Datendateien **und** Delta-Log, inklusive Commit-Historie und **gelöschter, noch nicht per `VACUUM` entfernter Daten**.

---
[← Übersicht](../00%20Uebersicht.md) · [Nächste Datei →](02%20CDF%20lesen%20%28Empfaenger%29.md)
