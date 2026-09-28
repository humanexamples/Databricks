# Isolationsstufen (WriteSerializable und Serializable)

Delta Lake unterstützt in Databricks zwei Isolationsstufen. Sie bestimmen, wie gleichzeitige Operationen auf einer Tabelle miteinander interagieren.

| Isolationsstufe | Beschreibung |
| --- | --- |
| **Serializable** | Die stärkste Isolationsstufe. Sie stellt sicher, dass committete Schreiboperationen und alle Lesevorgänge serialisierbar sind. Operationen sind erlaubt, solange eine serielle Abfolge existiert, die bei sequenzieller Ausführung dasselbe Ergebnis liefert wie in der Tabelle sichtbar. Bei Schreiboperationen entspricht diese serielle Abfolge der Reihenfolge in der Tabellenhistorie. |
| **WriteSerializable** (Standard) | Eine schwächere Isolationsstufe als Serializable. Sie stellt sicher, dass nur Schreiboperationen (nicht Lesevorgänge) serialisierbar sind. Das ist immer noch stärker als Snapshot-Isolation. Diese Stufe bietet für die meisten gängigen Operationen eine gute Balance zwischen Datenkonsistenz und Verfügbarkeit. |

## Wie Isolationsstufen Lesevorgänge beeinflussen

Lesevorgänge nutzen immer Snapshot-Isolation. Die Schreib-Isolationsstufe bestimmt, ob ein Reader einen Tabellenzustand sehen kann, der laut Historie „nie existiert hat".

- **Serializable:** Ein Reader sieht immer nur Tabellenzustände, die der Historie entsprechen.
- **WriteSerializable:** Ein Reader kann einen Tabellenzustand sehen, der so nicht im Delta-Log existiert.

## Beispiel: Gleichzeitiges Löschen und Einfügen

Stellen Sie sich vor, eine lange laufende Delete-Transaktion und eine Insert-Transaktion starten gleichzeitig und lesen beide Version `v0`. Die Insert-Transaktion committet zuerst und erzeugt Version `v1`. Danach versucht die Delete-Transaktion, `v2` zu committen:

```
t0: deleteTxn_START
t1: insertTxn_START
t2: insertTxn_COMMIT(v1)
t3: deleteTxn_COMMIT(v2)
```

In diesem Szenario hat `deleteTxn` die von `insertTxn` eingefügten Daten nicht gesehen und daher nicht gelöscht:

- **Serializable:** `deleteTxn` darf nicht committen, es entsteht ein Konflikt.
- **WriteSerializable:** `deleteTxn` darf committen, weil sich die Transaktionen ordnen lassen. Der resultierende Tabellenzustand ist so, als hätte `insertTxn` nach `deleteTxn` stattgefunden. Die eingefügten Zeilen bleiben also Teil der Tabelle. Die Delta-Historie zeigt aber weiterhin die physische Commit-Reihenfolge: `insertTxn` bei v1 vor `deleteTxn` bei v2.

## Isolationsstufe festlegen

Sie legen die Isolationsstufe mit dem Befehl `ALTER TABLE` fest:

```sql
%sql
ALTER TABLE <table-name> SET TBLPROPERTIES ('delta.isolationLevel' = <level-name>)
```

Dabei ist `<level-name>` entweder `Serializable` oder `WriteSerializable`.

Beispiel:

```sql
%sql
-- Change from default WriteSerializable to Serializable
ALTER TABLE my_table SET TBLPROPERTIES ('delta.isolationLevel' = 'Serializable')
```

## Wann committet Delta Lake ohne die Tabelle zu lesen?

Delta-Lake-`INSERT`- oder Append-Operationen lesen den Tabellenzustand vor dem Commit nicht, wenn folgende Bedingungen erfüllt sind:

1. Die Logik wird über `INSERT`-SQL-Anweisungen oder im Append-Modus ausgedrückt.
2. Die Logik enthält keine Subqueries oder Bedingungen, die sich auf die Zieltabelle des Schreibvorgangs beziehen.

Wie bei anderen Commits nutzt Delta Lake Metadaten aus dem Transaktionslog, um Tabellenversionen beim Commit zu validieren und aufzulösen. Es wird jedoch keine Version der Tabelle tatsächlich gelesen.

Viele gängige Muster nutzen `MERGE`-Operationen, um Daten abhängig von Tabellenbedingungen einzufügen. Auch wenn sich diese Logik theoretisch mit `INSERT`-Anweisungen umschreiben lässt: Verweist ein bedingter Ausdruck auf eine Spalte der Zieltabelle, gelten dieselben Nebenläufigkeitseinschränkungen wie bei `MERGE`.

## Weiterführende Informationen

- Row-Level Concurrency
- Transaktionen
- Isolationsstufen und Schreibkonflikte

---
**Quelle:** https://docs.databricks.com/aws/en/optimizations/isolation/isolation-levels  
**Stand:** 2026-08-06
