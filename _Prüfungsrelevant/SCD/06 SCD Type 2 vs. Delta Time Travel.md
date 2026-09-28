[← Übersicht](00%20Uebersicht.md)

# SCD Type 2 vs. Delta Time Travel

**Kombination:** SCD 2 · Delta Time Travel · `VACUUM` · Change Data Feed

Eine häufige Frage (auch in Prüfungen): *Delta Lake speichert doch alle Versionen einer Tabelle. Wozu dann SCD 2?*

Die Antwort: Time Travel ist eine **technische** Historie (Stand der **Tabelle** nach Commit X), SCD 2 ist eine **fachliche** Historie (Stand eines **Kunden** ab Zeitpunkt Y).

---

## Time Travel

```sql
-- Tabelle, wie sie in Version 12 aussah
SELECT * FROM catalog.silver.dim_customer VERSION AS OF 12;

-- Tabelle, wie sie zu einem Zeitpunkt aussah
SELECT * FROM catalog.silver.dim_customer TIMESTAMP AS OF '2026-09-15 00:00:00';

-- Welche Versionen gibt es?
DESCRIBE HISTORY catalog.silver.dim_customer;

-- Versehentliches Update rückgängig machen
RESTORE TABLE catalog.silver.dim_customer TO VERSION AS OF 12;
```

## SCD 2

```sql
-- Kunde 42, wie er fachlich am 15.09. war
SELECT * FROM catalog.silver.dim_customer_history
WHERE customer_id = 42
  AND __START_AT <= TIMESTAMP'2026-09-15'
  AND (__END_AT > TIMESTAMP'2026-09-15' OR __END_AT IS NULL);
```

---

## Der Unterschied

| | Delta Time Travel | SCD Type 2 |
|---|---|---|
| Art der Historie | technisch: Zustand der **Tabelle** pro Commit | fachlich: Zustand eines **Datensatzes** über die Zeit |
| Zeitachse | **Commit-Zeit** (wann wurde geschrieben?) | **Fachliche Zeit** aus `SEQUENCE BY` (wann hat sich der Kunde geändert?) |
| Lebensdauer | begrenzt: `VACUUM` löscht alte Dateien (Default-Retention 7 Tage) | dauerhaft, solange die Zeilen nicht gelöscht werden |
| Verspätete Daten | Eine Änderung vom 01.09., die erst am 20.09. geladen wird, erscheint in der Version vom 20.09. | wird korrekt zum 01.09. einsortiert |
| Abfrage über viele Zeitpunkte | eine Abfrage pro Version nötig | ein normaler Join (Point-in-Time) |
| Join mit Fakten | nicht praktikabel | Standard im Star-Schema → [04](04%20SCD%20im%20Star-Schema.md) |
| Zweck | Fehler rückgängig machen, Audit von Schreibvorgängen, Reproduzierbarkeit (ML) | Reporting, Stichtagsauswertung, Regulatorik |

---

## Warum Time Travel **kein** Ersatz für SCD 2 ist

1. **`VACUUM` begrenzt die Reichweite.** Nach Ablauf der Retention sind alte Versionen weg. Die Retention massiv zu erhöhen (`delta.deletedFileRetentionDuration`) lässt Speicherkosten und Metadaten wachsen und ist nicht als Langzeitarchiv gedacht.
2. **Commit-Zeit ≠ fachliche Zeit.** Wird ein Tagesexport erst drei Tage später geladen, zeigt Time Travel die Änderung drei Tage zu spät.
3. **Point-in-Time-Joins sind unmöglich.** „Jede Bestellung mit dem Kundenstand zum Bestellzeitpunkt“ bräuchte für jede Bestellung eine eigene Time-Travel-Abfrage.

## Wie beide zusammenspielen

- **Time Travel schützt die SCD-Tabelle selbst:** Läuft ein fehlerhaftes `MERGE` über `dim_customer_history`, stellt `RESTORE TABLE … TO VERSION AS OF …` den vorherigen Stand wieder her.
- **CDF liegt dazwischen:** Er zeigt Änderungen **pro Commit** und ist damit ebenfalls technisch. Er eignet sich, um Änderungen weiterzureichen, aber nicht als dauerhafte fachliche Historie → [../CDC/04](../CDC/04%20Change%20Data%20Feed%20-%20Aenderungen%20weiterreichen.md).
- **DSGVO betrifft beide:** Personenbezogene Daten stehen sowohl in alten SCD-Versionen als auch in alten Delta-Dateien → `DELETE` **und** `VACUUM` → [05, Abschnitt D](05%20SCD%20mit%20Governance%2C%20Data%20Quality%20und%20Performance.md).

**Merksatz:** Time Travel beantwortet „Wie sah die **Tabelle** aus?“, SCD 2 beantwortet „Wie sah der **Kunde** aus?“.

---
[← Vorherige Datei](05%20SCD%20mit%20Governance%2C%20Data%20Quality%20und%20Performance.md) · [Übersicht](00%20Uebersicht.md) · [Nächste Datei →](07%20SCD%20in%20Lakeflow%20Connect.md)

## Quellen

- [Work with Delta Lake table history](https://docs.databricks.com/aws/en/delta/history)
- [Remove unused data files with vacuum](https://docs.databricks.com/aws/en/delta/vacuum)
