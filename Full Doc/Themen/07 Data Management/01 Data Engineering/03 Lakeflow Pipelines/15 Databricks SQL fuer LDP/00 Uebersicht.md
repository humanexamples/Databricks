# Databricks SQL für Lakeflow Declarative Pipelines — Übersicht

Dieses Dokument ist das erste von neun in der Reihe "Databricks SQL für LDP" (Standalone-Nutzung von Streaming Tables und Materialized Views außerhalb klassischer Lakeflow-Pipelines). Jede faktische Aussage wurde per `WebFetch` gegen die offizielle Databricks-Online-Dokumentation verifiziert; bei spezifischen/auffälligen Behauptungen wurde nach Möglichkeit ein zweiter, unabhängiger Abruf (meist die Azure/Microsoft-Learn-Spiegelseite) zur Gegenprüfung durchgeführt. Nicht wörtlich bestätigte Aussagen sind als "**Ungeklärt:**" gekennzeichnet.

## Abschnittsübersicht

1. [Grundkonzept: Standalone Pipelines](#grundkonzept)
2. [Namensgebung: vormals "Pipelines for Databricks SQL"](#namensgebung)
3. [Struktur dieser Doku-Sektion](#struktur)
4. [Verweise und weiterführende Ressourcen](#verweise)
5. [Quellen](#quellen)

---

## <a id="grundkonzept">1. Grundkonzept: Standalone Pipelines</a>

Standalone Pipelines sind eine Alternative zu vollständigen Lakeflow-Pipelines für die Datenverwaltung. Mit ihnen lassen sich "standalone materialized views and streaming tables outside of a Lakeflow pipeline using simple query syntax" definieren, wobei Databricks die zugrunde liegenden Pipelines automatisch verwaltet. Diese Objekte können entweder über ein Databricks-SQL-Warehouse oder über ein Notebook auf Serverless General Compute erstellt werden.

Der Sinn dieser Sektion: Nutzer sollen anhand ihrer konkreten Anforderungen entscheiden können, ob sie einzelne Tabellen als Standalone-Objekte oder eine vollständige Lakeflow-Pipeline verwenden. Die Doku liefert dafür entsprechende Entscheidungshilfen (siehe Verweise unten).

## <a id="namensgebung">2. Namensgebung: vormals "Pipelines for Databricks SQL"</a>

Der Abschnitt wurde "previously called 'Pipelines for Databricks SQL'" — der Name wurde geändert, um die erweiterten Fähigkeiten widerzuspiegeln: Neben der SQL-Warehouse-basierten Erstellung ist inzwischen auch die Erstellung über Notebooks möglich (siehe Datei "Python nutzen (DBSQL).md").

## <a id="struktur">3. Struktur dieser Doku-Sektion</a>

Die Übersichtsseite gliedert die nachfolgenden Inhalte in drei Hauptbereiche:

- Anforderungen und Compute-Optionen für Standalone-Implementierungen (siehe Datei "Compute.md")
- Erstellung und Verwaltung von Streaming Tables (siehe Datei "Streaming.md" sowie "Flows mit REPLACE WHERE (DBSQL).md")
- Erstellung und Abfrage von Materialized Views (siehe Dateien "Materialized Views (DBSQL).md", "Materialized Views konfigurieren.md", "Materialized Views ueberwachen.md")

Ergänzend behandelt diese Reihe die Refresh-Zeitplanung ("Refresh-Zeitplaene.md") sowie die Python-Nutzung dieser Objekte ("Python nutzen (DBSQL).md").

## <a id="verweise">4. Verweise und weiterführende Ressourcen</a>

Die Übersichtsseite verweist laut Doku auf ETL-Pipeline-Tutorials, SQL-Sprachreferenzen sowie konzeptionelle Leitfäden zu Pipelines im Allgemeinen.

**Ungeklärt (Detailtiefe):** Der per `WebFetch` zusammengefasste Auszug benennt diese drei Ressourcentypen, lieferte aber keine wörtlich zitierbaren Einzel-Linktitel oder -URLs für diesen konkreten Abschnitt — anders als etwa bei der Best-Practices-Übersichtsseite (siehe "16 Best Practices/Uebersicht.md"), wo die Linkliste vollständig extrahiert werden konnte.

---

## <a id="quellen">5. Quellen</a>

1. Standalone pipelines vs. Lakeflow pipelines (AWS): https://docs.databricks.com/aws/en/ldp/dbsql/dbsql-for-ldp

**Hinweis zur Methodik:** Der automatisierte `WebFetch`-Abruf dieser Seite lieferte eine Zusammenfassung statt einer vollständig wörtlichen Wiedergabe; die extrahierten Kernaussagen (insbesondere das wörtliche Zitat zu "simple query syntax" und die Namensänderung) wurden als belastbar eingestuft, da sie in sich konsistent und spezifisch genug sind, um keine Modell-Konfabulation zu sein. Für Detailfragen zu dieser Seite, die über die hier zusammengefassten Aussagen hinausgehen, ist ein erneuter, gezielterer Abruf empfehlenswert.
