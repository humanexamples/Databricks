# Automatische Upgrades

Databricks aktualisiert Unity Catalog Managed Tables automatisch mit neuen, allgemein verfügbaren Funktionen. Das geschieht ohne Code-Änderungen und ohne manuelle `ALTER TABLE`-Befehle.

## Vorteile

- Weniger Verwaltungsaufwand, weil Kompatibilitätsprüfungen nicht mehr manuell pro Tabelle und Funktion nötig sind. Das hilft besonders bei Katalogen mit tausenden Tabellen.
- Neue Performance- und Zuverlässigkeitsverbesserungen kommen automatisch bei Managed Tables an.
- Upgrades erfolgen sicher. Funktionen werden erst aktiviert, nachdem die Kompatibilität der Workloads geprüft wurde.

## Funktionsweise

Automatische Upgrades beobachten die Zugriffsmuster auf Managed Tables. Sie nutzen ein Beobachtungsfenster, um Kompatibilität zu prüfen, bevor eine Funktion aktiviert wird. Das Beobachtungsfenster beträgt 50 Tage für Funktionen in der Public Preview und 100 Tage für allgemein verfügbare Funktionen.

Automatische Upgrades laufen im Hintergrund über Serverless Compute. Dafür entstehen keine zusätzlichen Kosten.

## Verhalten nach Schema- und Tabellentyp

| Schema | Tabelle | Verhalten |
| --- | --- | --- |
| Neu | Neu | Automatische Upgrades setzen Schema-Standardwerte bereits bei der Erstellung. Neue Tabellen erben dadurch sofort alle unterstützten Funktionen. |
| Bestehend | Neu | Eine Funktion wird nur aktiviert, wenn alle Tabellen im Schema während des vorherigen Beobachtungsfensters ausschließlich von verifizierten Workloads genutzt wurden. Gab es auch nur einen nicht verifizierten Zugriff auf eine Tabelle im Schema, wird die neue Tabelle ignoriert. |
| Bestehend | Bestehend | Eine Funktion wird aktiviert, wenn alle folgenden Bedingungen erfüllt sind: Nur verifizierte Workloads haben im Beobachtungsfenster auf die Tabelle zugegriffen. Der erste erfasste Zugriff liegt vor Beginn des Beobachtungsfensters. Die Tabelle wurde innerhalb der letzten 30 Tage genutzt. Inaktive Tabellen werden übersprungen. |

## Verifizierte Workloads

Ein Workload gilt für eine bestimmte Funktion als verifiziert, wenn er von einem Databricks-Cluster mit einer Databricks-Runtime-Version zugegriffen hat, die mindestens der geforderten Mindestversion entspricht.

Als nicht verifiziert gelten:

- Externe Clients und Drittanbieter-Dienste wie Flink oder Presto
- Databricks-Dienste mit direktem Tabellenzugriff, etwa Zerobus, die den normalen Databricks-Runtime-Zugriff umgehen

Wurde eine Tabelle im Schema innerhalb des Beobachtungsfensters von einer zu alten Runtime-Version oder einem externen Client genutzt, aktivieren automatische Upgrades die betroffene Funktion für keine Tabelle in diesem Schema.

## Unterstützte Funktionen

Automatische Upgrades gelten für eine Teilmenge der allgemein verfügbaren Funktionen. Die Verfügbarkeit kann je nach Region variieren.

Wichtiger Hinweis: Automatisches Liquid Clustering gilt nur für neue Tabellen. Es wird bei der Erstellung standardmäßig hinzugefügt und niemals nachträglich auf bestehende Tabellen angewendet.

### Allgemein verfügbare Funktionen

| Funktion | Tabellentypen | Minimale Runtime-Version | Wirkung | Veröffentlichung |
| --- | --- | --- | --- | --- |
| Automatisches Liquid Clustering | Alle neuen Tabellen | 15.4 LTS | Organisiert Tabellendaten automatisch anhand häufig abgefragter Spalten, um die Abfrageleistung ohne manuelle Partitionierung zu verbessern. Gilt nicht für bestehende Tabellen. | 22. Mai 2026 |
| Checkpoint V2 | Alle neuen Tabellen; bestehende Tabellen | 13.3 LTS | Unterstützt mehr gleichzeitige Schreibvorgänge und reduziert Schreibkonflikte bei großen oder häufig aktualisierten Tabellen. | 19. Mai 2026 für neue Tabellen in neuen Schemas; 13. Juli 2026 für alle Tabellen in bestehenden Schemas |
| Row Tracking | Alle neuen Tabellen; bestehende Tabellen | 14.1 | Verwaltet versteckte Row-IDs für inkrementelle Verarbeitung. Bei aktiviertem Row Tracking steht automatisch ein Change Data Feed zur Verfügung. | 25. Juli 2026 für neue Tabellen in neuen Schemas; 13. Juli 2026 für alle Tabellen in bestehenden Schemas |
| Catalog Commits | Neue Tabellen in neuen Schemas | 16.4 LTS | Zentralisiert Commits in Unity Catalog. Ermöglicht Multi-Table-Transaktionen, verbessert Interoperabilität für externe Schreibvorgänge und erlaubt Governance-Richtlinien über mehrere Engines hinweg. | 13. Juli 2026 |
| Parquet v2 | Neue Tabellen in neuen Schemas | 18.1 | Nutzt fortgeschrittene Parquet-Kodierungen, Data-Page-Header und INT64-Zeitstempel, um Abfrageleistung zu verbessern und Speicherbedarf bei Delta-Lake-Tabellen zu reduzieren. | 25. Juni 2026 |

### Funktionen in der Public Preview

Für die Teilnahme an Public-Preview-Funktionen ist ein Formular mit der Account-ID auszufüllen. Nach der Anmeldung sind keine Code-Änderungen oder zusätzliche Konfiguration nötig.

| Funktion | Tabellentypen | Minimale Runtime-Version | Wirkung |
| --- | --- | --- | --- |
| Catalog Commits | Alle Tabellen in bestehenden Schemas | 16.4 LTS | Zentralisiert Commits in Unity Catalog für Multi-Table-Transaktionen und bessere Interoperabilität. |
| Column Mapping | Alle Tabellen | 15.4 LTS | Ermöglicht das Umbenennen und Löschen von Spalten, ohne Daten neu zu schreiben. |
| Parquet v2 | Alle Tabellen in bestehenden Schemas | 18.1 | Nutzt fortgeschrittene Parquet-Kodierungen zur Verbesserung von Leistung und Speicherbedarf. |

## Voraussetzungen

- Serverless Compute muss in der Region verfügbar sein.
- Die Tabellen müssen Unity Catalog Managed Tables im Format Delta Lake oder Apache Iceberg sein.

## Aktivierte Funktionen beobachten

Um zu prüfen, ob automatische Upgrades eine Funktion aktiviert haben, suchen Sie nach einer `SET TBLPROPERTIES`-Operation im Tab History im Catalog Explorer. Alternativ nutzen Sie `DESCRIBE HISTORY <table_name>`. Wenn automatische Upgrades die Operation durchgeführt haben, zeigt das Feld für den Benutzernamen einen Hash-Wert statt eines Benutzernamens, zum Beispiel `4d137f29-62`.

Nachdem automatische Upgrades Funktionen für Tabellen in einem neuen Schema aktiviert haben, lassen sich die Schema-Standardwerte im Tab Properties im Catalog Explorer einsehen. Ein Schema mit aktiviertem Row Tracking zeigt zum Beispiel die Eigenschaft `catalog.schema.enableRowTracking: "true"`. Bestehende Schemas zeigen diese Beobachtungs-Eigenschaften nicht.

Für eine kontoweite Übersicht lässt sich die Systemtabelle für automatische Upgrades abfragen. Sie erfasst, welche Funktion wann für welche Tabelle hinzugefügt wurde.

## Empfohlene Funktionen verwalten

Administratoren können Änderungen eines Upgrades rückgängig machen oder Funktionen für einzelne Tabellen deaktivieren.

### Änderungen rückgängig machen

Mit `RESTORE` lässt sich eine Tabelle auf eine Version vor der Aktivierung der Funktion zurücksetzen:

```sql
%sql
RESTORE TABLE <table_name> TO VERSION AS OF <version>;
RESTORE TABLE <table_name> TO TIMESTAMP AS OF <timestamp>;
```

### Funktionen für Tabellen deaktivieren

Um eine Funktion für eine einzelne Tabelle abzuschalten:

```sql
%sql
ALTER TABLE <table_name> DROP FEATURE <feature_name>
```

Nach dem manuellen Abschalten aktivieren automatische Upgrades diese Funktion für die Tabelle nicht erneut.

## Einschränkungen

- Tabellen, die über Delta Sharing freigegeben sind (sowohl Databricks-zu-Open als auch Databricks-zu-Databricks), sind von automatischen Upgrades ausgeschlossen.
- Es gibt keinen Batch-Rollback-Mechanismus, um eine Funktion kontoweit für alle Tabellen zu deaktivieren.
- Materialized Views und Streaming Tables werden nicht unterstützt.
- Workloads, die Unity Catalog umgehen und Tabellen direkt über den Pfad ansprechen, werden nicht erfasst. Bei pfadbasiertem Zugriff sollte das Account-Team kontaktiert werden.
- External Tables sind von automatischen Upgrades ausgeschlossen. Sie werden typischerweise per Dateipfad angesprochen, wodurch Unity Catalog umgangen wird. Dadurch lassen sich Zugriffsmuster nicht zuverlässig verfolgen.

## Häufig gestellte Fragen

**Ändern automatische Upgrades meine Tabellen automatisch?**

Ja. Sobald eine Funktion für eine Tabelle als sicher eingestuft ist, wendet Databricks sie über einen leichtgewichtigen Hintergrundjob an. Funktionen lassen sich weiterhin für einzelne Tabellen deaktivieren.

**Kann eine deaktivierte Funktion später wieder aktiviert werden?**

Nein. Nachdem eine von automatischen Upgrades hinzugefügte Funktion manuell deaktiviert wurde, aktivieren automatische Upgrades diese Funktion für diese Tabelle nicht erneut.

**Ändern automatische Upgrades auch bestehende Tabellen?**

Ja, aber erst, nachdem das Beobachtungsfenster bestätigt hat, dass jeder zugreifende Client die Funktion unterstützt. Ausnahme ist automatisches Liquid Clustering: Es gilt nur für neu erstellte Tabellen, nie für bestehende, weil es sonst das bestehende Datenlayout verändern würde.

**Wie unterscheiden sich automatische Upgrades von Predictive Optimization?**

Predictive Optimization pflegt das Datenlayout durch Operationen wie Kompaktierung und Vacuum, optional mit automatischem Liquid Clustering. Automatische Upgrades aktivieren neue Tabellenfunktionen wie Row Tracking oder Checkpoint V2. Beide ergänzen sich: Eines hält Tabellen gepflegt, das andere hält sie aktuell. Automatisches Liquid Clustering wird über automatische Upgrades auf neue Tabellen angewendet.

**Wie wird geprüft, ob eine Tabelle sicher aktualisiert werden kann?**

Automatische Upgrades aktivieren nur allgemein verfügbare Funktionen, die die Leistung nicht wesentlich verschlechtern oder die Kosten erhöhen. Sie warten das Beobachtungsfenster ab, verlangen Kompatibilität aller zugreifenden Clients, überspringen nicht vollständig verifizierbare Tabellen und erlauben es, jede Funktion jederzeit für eine Tabelle zu deaktivieren.

**Woran erkenne ich, dass eine Änderung von automatischen Upgrades stammt?**

Jede Änderung erscheint in der Ausgabe von `DESCRIBE HISTORY` der Tabelle und im Tab History im Catalog Explorer, deutlich von eigenen Änderungen unterschieden. Für eine kontoweite Übersicht lässt sich `system.storage.table_auto_upgrade_operations_history` abfragen.

**Werden Tabellen kaputt gemacht, die von externen oder Open-Source-Tools gelesen werden?**

Nein. Tabellen, auf die externe oder Open-Source-Clients zugreifen, sind ausgenommen. Automatische Upgrades greifen nur dann ein, wenn sicher feststeht, dass jeder zugreifende Client die Funktion unterstützt.

**Wie lange dauert es, bis meine Tabellen aktualisiert werden?**

Das Beobachtungsfenster soll auch seltene Workloads erfassen, etwa monatliche Batch-Jobs oder Quartalsberichte. Nach erfolgreicher Verifizierung wird die Funktion kurz danach über einen Hintergrundjob angewendet. Da der Rollout neuer Funktionen schrittweise über Kunden und Tabellen erfolgt, kann es bis zu sechs Monate dauern, bis kompatible Workloads erreicht werden.

**Was muss ich tun, um automatische Upgrades zu aktivieren?**

Nichts. Automatische Upgrades bewerten und aktualisieren geeignete Tabellen ohne zusätzliche Konfiguration.

**Lassen sich automatische Upgrades kontoweit abschalten?**

Automatische Upgrades lassen sich nicht vollständig abschalten. Es lässt sich aber jederzeit jede einzelne Funktion für eine Tabelle deaktivieren. Danach wird diese Funktion für diese Tabelle nicht erneut aktiviert.

**Kostet der automatische Upgrade-Prozess etwas?**

Für den Hintergrundprozess (die `ALTER TABLE`-Operationen) entstehen keine Kosten.

**Kosten die aktivierten Funktionen selbst etwas?**

Funktionen, die die Kosten wesentlich erhöhen würden, sind grundsätzlich ausgeschlossen. Mehrere aktivierte Funktionen, etwa Deletion Vectors und Parquet v2, senken sogar Speicher- und Rechenkosten. Row Tracking verursacht bei sehr großen Tabellen einmalig geringe Zusatzkosten, weil jede Zeile eine eindeutige Kennung erhält. Gleichzeitig ermöglicht es inkrementelle Aktualisierungen von Materialized Views statt vollständiger Neuberechnung.

**Wie behalte ich künftige Funktionen im Blick?**

Der Abschnitt zu unterstützten Funktionen zeigt, welche Funktionen sich in der Public Preview befinden und welche demnächst für alle Kunden ausgerollt werden. Ein RSS-Feed auf der Databricks-Release-Notes-Seite informiert über Neuerungen.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/automatic-upgrades  
**Stand:** 2026-08-06
