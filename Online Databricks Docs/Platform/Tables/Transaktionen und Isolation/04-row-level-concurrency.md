# Row-Level Concurrency

Row-Level Concurrency reduziert Konflikte zwischen gleichzeitigen Schreiboperationen. Die Funktion erkennt Änderungen auf Zeilenebene. Sie löst Konflikte automatisch auf, wenn gleichzeitige Schreibvorgänge unterschiedliche Zeilen derselben Datendatei ändern.

## Voraussetzungen für Row-Level Concurrency

Row-Level Concurrency wird automatisch aktiviert, wenn alle folgenden Bedingungen erfüllt sind:

- Databricks Runtime 14.3 LTS oder höher wird verwendet.
- Die Quelltabelle nutzt keine Partitionen.
- Die Quelltabelle hat Deletion Vectors aktiviert.

Partitionierte Tabellen erlauben kein Row-Level Concurrency. Sind aber Deletion Vectors aktiviert, können partitionierte Tabellen trotzdem Konflikte zwischen `OPTIMIZE` und Schreiboperationen vermeiden. Details dazu finden Sie im Abschnitt „Einschränkungen für Row-Level Concurrency".

## Konfliktmatrix mit Row-Level Concurrency

Für Quelltabellen mit Row-Level Concurrency zeigt folgende Tabelle, welche Paare von Schreiboperationen in welcher Isolationsstufe konfligieren können:

| Operation | INSERT (1) | UPDATE, DELETE, MERGE INTO | OPTIMIZE |
| --- | --- | --- | --- |
| INSERT | Kein Konflikt möglich. | Kein Konflikt in WriteSerializable. Konflikt möglich in Serializable, bei Änderung derselben Zeile. | Konflikt möglich, bei Änderung derselben Zeile. |
| UPDATE, DELETE, MERGE INTO | Kein Konflikt in WriteSerializable. Konflikt möglich in Serializable, bei Änderung derselben Zeile. | Kein Konflikt in WriteSerializable. Konflikt möglich in Serializable, bei Änderung derselben Zeile. | Konflikt möglich bei Verwendung von `ZORDER BY`. Sonst kein Konflikt. |
| OPTIMIZE | Konflikt möglich, bei Änderung derselben Zeile. | Konflikt möglich bei Verwendung von `ZORDER BY`. Sonst kein Konflikt. | Konflikt möglich bei Verwendung von `ZORDER BY`. Sonst kein Konflikt. |

(1) Alle `INSERT`-Operationen in dieser Tabelle bezeichnen Append-Operationen ohne Subqueries, die Daten aus derselben Tabelle lesen. `INSERT`-Operationen mit Subqueries, die aus derselben Tabelle lesen, unterstützen dieselbe Nebenläufigkeit wie `MERGE`.

- Tabellen mit Identity-Spalten unterstützen keine gleichzeitigen Transaktionen.
- `REORG`-Operationen haben bei der Neuschreibung von Datendateien dieselbe Isolationssemantik wie `OPTIMIZE`. Nutzen Sie `REORG`, um ein Upgrade anzuwenden, ändern sich die Tabellenprotokolle. Das konfligiert dann mit allen laufenden Operationen.

## Schreibkonflikte ohne Row-Level Concurrency

Für Quelltabellen ohne Row-Level Concurrency zeigt folgende Tabelle, welche Paare von Schreiboperationen in welcher Isolationsstufe konfligieren können:

| Operation | INSERT (1) | UPDATE, DELETE, MERGE INTO | OPTIMIZE |
| --- | --- | --- | --- |
| INSERT | Kein Konflikt möglich. | Kein Konflikt in WriteSerializable. Konflikt möglich in Serializable. Siehe „Konflikte durch Partitionierung vermeiden". | Konflikt möglich in Serializable und WriteSerializable. Siehe „Konflikte durch Partitionierung vermeiden". |
| UPDATE, DELETE, MERGE INTO | Kein Konflikt in WriteSerializable. Konflikt möglich in Serializable. Siehe „Konflikte durch Partitionierung vermeiden". | Kein Konflikt in WriteSerializable. Konflikt möglich in Serializable. Siehe „Konflikte durch Partitionierung vermeiden". | Kein Konflikt bei Tabellen mit aktivierten Deletion Vectors, außer bei Verwendung von `ZORDER BY`. Sonst Konflikt möglich. |
| OPTIMIZE | Konflikt möglich in Serializable und WriteSerializable. Siehe „Konflikte durch Partitionierung vermeiden". | Kein Konflikt bei Tabellen mit aktivierten Deletion Vectors, außer bei Verwendung von `ZORDER BY`. Sonst Konflikt möglich. | Kein Konflikt bei Tabellen mit aktivierten Deletion Vectors, außer bei Verwendung von `ZORDER BY`. Sonst Konflikt möglich. |

(1) Alle `INSERT`-Operationen in dieser Tabelle bezeichnen Append-Operationen ohne Subqueries, die Daten aus derselben Tabelle lesen. `INSERT`-Operationen mit Subqueries, die aus derselben Tabelle lesen, unterstützen dieselbe Nebenläufigkeit wie `MERGE`.

- Tabellen mit Identity-Spalten unterstützen keine gleichzeitigen Transaktionen.
- `REORG`-Operationen haben bei der Neuschreibung von Datendateien dieselbe Isolationssemantik wie `OPTIMIZE`. Nutzen Sie `REORG`, um ein Upgrade anzuwenden, ändern sich die Tabellenprotokolle und konfligieren mit allen laufenden Operationen.

## Einschränkungen für Row-Level Concurrency

Für Row-Level Concurrency gelten Einschränkungen. Bei folgenden Operationen erfolgt die Konfliktlösung nach dem normalen Verhalten ohne Row-Level Concurrency, wie oben im Abschnitt „Schreibkonflikte ohne Row-Level Concurrency" beschrieben:

| Einschränkung | Beschreibung |
| --- | --- |
| Komplexe Bedingungsklauseln | Bedingungen auf komplexen Datentypen (Structs, Arrays, Maps), nicht-deterministische Ausdrücke, Subqueries und korrelierte Subqueries. |
| Anforderung an MERGE-Prädikat | In Databricks Runtime 14.2 müssen `MERGE`-Befehle ein explizites Prädikat auf der Zieltabelle verwenden, um passende Zeilen der Quelltabelle zu filtern. |
| Performance-Kompromiss | Die Konflikterkennung auf Zeilenebene kann die Gesamtausführungszeit erhöhen. Bei vielen gleichzeitigen Transaktionen priorisiert der Writer Latenz vor Konfliktlösung. |

Alle Einschränkungen von Deletion Vectors gelten ebenfalls.

## Konflikte durch Partitionierung vermeiden

In allen Fällen, die in den Konfliktmatrizen als „Konflikt möglich" markiert sind, entsteht ein Konflikt nur, wenn beide Operationen dieselben Dateien betreffen. Um die Dateimengen disjunkt zu machen, partitionieren Sie die Tabelle nach denselben Spalten, die in den Operationsbedingungen verwendet werden.

Beispiel:

Die Befehle `UPDATE table WHERE date > '2010-01-01' ...` und `DELETE table WHERE date < '2010-01-01'` konfligieren, wenn die Tabelle nicht nach `date` partitioniert ist. Beide könnten dann versuchen, dieselben Dateien zu ändern. Eine Partitionierung nach `date` vermeidet den Konflikt.

Partitioniert man eine Tabelle nach einer Spalte mit hoher Kardinalität, kann das wegen der vielen Unterverzeichnisse zu Performance-Problemen führen.

## Konflikte mit expliziten Partitionsfiltern vermeiden

Diese Ausnahme tritt oft bei gleichzeitigen `DELETE`-, `UPDATE`- oder `MERGE`-Operationen auf, die dieselbe Partition lesen könnten, auch wenn sie unterschiedliche Partitionen aktualisieren. Machen Sie die Trennung in der Operationsbedingung explizit.

## Konflikt-Exceptions

Bei einem Transaktionskonflikt tritt eine der folgenden Exceptions auf:

### ConcurrentAppendException

Diese Exception tritt auf, wenn eine gleichzeitige Operation Dateien in derselben Partition hinzufügt (oder irgendwo in einer nicht partitionierten Tabelle), die Ihre Operation liest. Die Dateihinzufügungen können durch `INSERT`, `DELETE`, `UPDATE` oder `MERGE` verursacht werden.

Mit der Standard-Isolationsstufe WriteSerializable konfligieren Dateien, die durch `INSERT`-Operationen ohne vorheriges Lesen angehängt werden, mit keiner Operation. Bei der Isolationsstufe Serializable können Anhänge dagegen konfligieren.

`INSERT`-Operationen können im WriteSerializable-Modus konfligieren, wenn mehrere gleichzeitige `DELETE`-, `UPDATE`- oder `MERGE`-Operationen sich möglicherweise auf die vom `INSERT` angehängten Werte beziehen. Um das zu vermeiden:

- Stellen Sie sicher, dass gleichzeitige `DELETE`-, `UPDATE`- oder `MERGE`-Operationen die angehängten Daten nicht lesen.
- Lassen Sie höchstens eine `DELETE`-, `UPDATE`- oder `MERGE`-Operation zu, die die angehängten Daten lesen kann.

### ConcurrentDeleteReadException

Diese Exception tritt auf, wenn eine gleichzeitige Operation eine Datei löscht, die Ihre Operation gelesen hat. Häufige Ursachen sind `DELETE`-, `UPDATE`- oder `MERGE`-Operationen, die Dateien neu schreiben.

### ConcurrentDeleteDeleteException

Diese Exception tritt auf, wenn eine gleichzeitige Operation eine Datei löscht, die Ihre Operation ebenfalls löscht. Das kann zum Beispiel durch zwei gleichzeitige Kompaktierungsoperationen verursacht werden, die dieselben Dateien neu schreiben.

### MetadataChangedException

Diese Exception tritt auf, wenn eine gleichzeitige Transaktion die Metadaten einer Delta-Tabelle aktualisiert. Häufige Ursachen sind `ALTER TABLE`-Operationen oder Schreibvorgänge, die das Tabellenschema ändern.

### ConcurrentTransactionException

Diese Exception tritt auf, wenn eine Streaming-Query mit demselben Checkpoint-Verzeichnis mehrfach gleichzeitig gestartet wird und versucht, gleichzeitig in die Delta-Tabelle zu schreiben. Führen Sie niemals zwei Streaming-Queries mit demselben Checkpoint-Verzeichnis gleichzeitig aus.

### ProtocolChangedException

Diese Exception kann auftreten, wenn:

- Ihre Delta-Lake-Tabelle auf eine neue Protokollversion aktualisiert wurde (unter Umständen müssen Sie dann Ihre Databricks Runtime aktualisieren),
- mehrere Writer gleichzeitig eine Tabelle erstellen oder ersetzen,
- mehrere Writer gleichzeitig in einen leeren Pfad schreiben.

## Legacy-Verhalten von Row-Level Concurrency

In Databricks Runtime 13.3 LTS nutzt Row-Level Concurrency ein Legacy-Verhalten:

- Es erfordert Deletion Vectors.
- Tabellen mit Liquid Clustering aktivieren Row-Level Concurrency automatisch.

## Weiterführende Informationen

- Isolationsstufen (WriteSerializable und Serializable)
- Transaktionen
- Deletion Vectors in Databricks
- Delta-Lake-Feature-Kompatibilität und -Protokolle

---
**Quelle:** https://docs.databricks.com/aws/en/optimizations/isolation/row-level-concurrency  
**Stand:** 2026-08-06
