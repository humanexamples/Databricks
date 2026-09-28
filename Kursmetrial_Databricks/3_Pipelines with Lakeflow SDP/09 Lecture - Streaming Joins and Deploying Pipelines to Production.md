Die Grundlagen von Streaming Joins in Apache Spark™ Declarative Pipelines

## Streaming Joins

Wenn Sie in Declarative Pipelines Joins mit Streaming Tables durchführen, ist es wichtig, die verschiedenen Join-Typen und ihr Verhalten zu verstehen.

- Streaming Joins unterstützen verschiedene Muster: Stream-Snapshot-Joins zur Anreicherung über Lookups, Joins von Streaming Tables über Materialized Views sowie Stream-Stream-Joins mit Windowing und Watermarking.
- Die Wahl des richtigen Join-Typs hängt davon ab, ob die Quellen statisch oder Streaming sind und ob der Workflow eine Anreicherung oder eine Synchronisation benötigt.

1. **Stream-Snapshot Join**: Streaming Table mit einer statischen Tabelle verknüpft

   Ziel ist es, **neue Daten** aus einer Streaming Table **inkrementell** mit einer **statischen Lookup-Tabelle** zu verknüpfen, um eine weitere Streaming Table zu erstellen.

   Das ist nützlich, wenn Sie Ihre Streaming-Daten mit Referenzinformationen anreichern möchten, die sich selten ändern.



2. **Streaming über Materialized View**: Zwei Streaming Tables, verknüpft in einer Materialized View

   Ziel ist es, **alle Zeilen aus zwei Streaming Tables** zu nehmen und sie bei jedem Pipeline-Lauf miteinander zu verknüpfen.

   Da beide Seiten Streaming sind, ist eine Materialized View erforderlich, um diesen Join effizient zu verarbeiten und die Ergebnisse aktuell zu halten.

   Die Materialized View verarbeitet alle neuen Zeilen aus beiden Tabellen und wird – abhängig von Pipeline-Konfiguration und Compute-Modus – inkrementell aktualisiert.



3. **Stream-Stream Join**: Inkrementeller Join zweier Live-Streams (fortgeschritten)

   Ziel ist es, neue Daten aus zwei Tabellen **inkrementell** zu verknüpfen; **vergangene Daten werden nicht verwendet**

   Diese Joins sind nützlich, um Beziehungen zwischen Ereignissen zu erkennen, die zeitlich nah beieinander auftreten, etwa beim Verknüpfen von Clickstream-Daten mit Echtzeit-Werbeeinblendungen.

   Da Stream-Stream-Joins jedoch häufig Windowing-Logik, Watermarking und andere fortgeschrittene Streaming-Konzepte erfordern, liegen sie außerhalb des Umfangs dieses Kurses.





## E. Die Join-Typen im Vergleich

Die folgende Tabelle fasst alle drei Join-Muster auf einen Blick zusammen. Nutzen Sie sie als Kurzreferenz, wenn Sie entscheiden, welcher Join-Typ zu den Anforderungen Ihrer Pipeline passt.

**Alle drei Join-Typen – auf einen Blick**

| Join-Typ | Quellen | Ausgabetyp | Verarbeitete Daten | Im Kursumfang? |
| --- | --- | --- | --- | --- |
| **Stream-Snapshot** | Streaming + statisch | Streaming Table | Nur neue Zeilen | Ja |
| **MV Join** | Streaming + Streaming | Materialized View | Alle Zeilen bei jedem Lauf | Ja |
| **Stream-Stream** | Streaming + Streaming | Streaming Table | Nur neue Zeilen (gefenstert) | Nur fortgeschritten |





