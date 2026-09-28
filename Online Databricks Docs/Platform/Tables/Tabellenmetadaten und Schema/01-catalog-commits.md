# Catalog Commits

Catalog Commits verlagern die Commit-Koordination vom Dateisystem in den Unity Catalog. Der Catalog wird damit zur alleinigen Quelle der Wahrheit für den Zustand von Delta-Lake- und Apache-Iceberg-Tabellen. Das ermöglicht Transaktionen über mehrere Tabellen hinweg, schnellere Query-Planung und kontrollierten Zugriff bei allen Tabellenoperationen.

Klassische Delta-Lake-Transaktionen koordinieren Commits auf Ebene einzelner Tabellen. Jede Tabelle verwaltet ihr eigenes Transaktionslog und ihre Konflikterkennung unabhängig. Durch die Verlagerung der Commit-Koordination auf die Catalog-Ebene können Organisationen den gesamten Zugriff auf das Lakehouse konsistent über Unity Catalog steuern. Außerdem kann Unity Catalog dadurch Commits über mehrere Tabellen hinweg innerhalb einer Transaktionsgrenze orchestrieren, ohne die ACID-Garantien von Delta Lake zu verlieren.

## Vorteile

Catalog Commits bieten folgende Möglichkeiten:

- **Transaktionen über mehrere Tabellen**: Mehrere SQL-Anweisungen über mehrere Tabellen hinweg als einen einzigen atomaren Commit ausführen. Alle Änderungen gelingen zusammen oder scheitern zusammen.
- **Kontrollierter Zugriff**: Lese- und Schreibzugriffe werden über Unity Catalog koordiniert. Engines sehen dadurch immer den zuletzt committeten Zustand, und Governance-Richtlinien werden angewendet.
- **Schnellere Query-Planung und Schreibvorgänge**: Unity Catalog liefert einem Delta-Client die Tabellen-Metadaten direkt beim Zugriff auf eine Tabelle. Der Umweg über den Cloud Storage entfällt, eine wichtige Quelle für Metadaten-Latenz fällt weg.
- **Erzwingbare Constraints**: Unity Catalog validiert oder verwirft Schema- und Constraint-Änderungen. Das verhindert inkompatible Updates, die die Datenintegrität oder nachgelagerte Workloads gefährden könnten.
- **Externer Zugriff**: Sicheres Schreiben in Unity-Catalog-Managed-Tables von externen Engines aus. Unity Catalog koordiniert Commits, um Korruption und Nebenläufigkeitskonflikte zu verhindern.

**PREVIEW:** Transaktionen, die in Unity-Catalog-Managed-Iceberg-Tabellen schreiben, befinden sich in der Private Preview. Für die Teilnahme muss man das Anmeldeformular für die Managed-Iceberg-Tables-Preview ausfüllen.

**BETA:** Dieses Feature befindet sich in der Beta-Phase. Workspace-Administratoren können den Zugriff auf dieses Feature über die Seite Previews steuern.

## Voraussetzungen

- Die Tabellen müssen Unity-Catalog-Managed-Tables sein (Delta oder Iceberg).
- Databricks Runtime 16.4 oder höher wird benötigt, um Tabellen mit aktivierten Catalog Commits zu lesen, zu schreiben oder zu erstellen.
- Databricks Runtime 18.0 oder höher wird benötigt, um Catalog Commits bei bestehenden Tabellen zu aktivieren oder zu deaktivieren.

## Catalog Commits aktivieren

Man kann Catalog Commits bei neuen und bei bestehenden Tabellen aktivieren.

### Catalog Commits für neue Tabellen aktivieren

Beim Erstellen einer Tabelle nutzt man die Tabelleneigenschaft `delta.feature.catalogManaged`:

```sql
%sql
CREATE TABLE sales_data (
  sale_id BIGINT,
  amount DECIMAL(10,2),
  sale_date DATE)
TBLPROPERTIES ('delta.feature.catalogManaged' = 'supported');
```

### Catalog Commits für bestehende Tabellen aktivieren

Mit `ALTER TABLE` fügt man Catalog Commits zu einer bestehenden Tabelle hinzu:

```sql
%sql
ALTER TABLE sales_data SET TBLPROPERTIES ('delta.feature.catalogManaged' = 'supported');
```

**WICHTIG:** Das Aktivieren von Catalog Commits bei einer bestehenden Tabelle synchronisiert den Tabellenzustand mit dem Catalog. Bei Tabellen mit hohem Schreibvolumen kann dieser Vorgang mehrere Minuten dauern.

## Prüfen, ob Catalog Commits aktiviert sind

So prüft man, ob bei einer Tabelle Catalog Commits aktiviert sind:

```sql
%sql
DESCRIBE DETAIL sales_data;
```

Ist die Funktion aktiviert, erscheint `catalogManaged` in der Spalte `tableFeatures`.

## Catalog Commits deaktivieren

Man kann Catalog Commits ab Databricks Runtime 18.0 deaktivieren. Siehe „Ein Delta-Lake-Tablefeature entfernen und das Tabellenprotokoll zurückstufen".

**WARNUNG:** Man sollte Upgrade- oder Downgrade-Vorgänge während der Ausführung von `ALTER`- oder `DROP`-Anweisungen nicht abbrechen. Eine Unterbrechung kann die Tabelle in einem teilweise hoch- oder heruntergestuften Zustand belassen und sie für alle künftigen Lese- und Schreibvorgänge sperren. Um das rückgängig zu machen, führt man den passenden Befehl erneut aus, statt ihn abzubrechen. Bei einer gesperrten Tabelle sollte man den Databricks-Support kontaktieren.

## Einschränkungen

- Man kann Catalog Commits bei bestehenden Tabellen nicht mit `CREATE OR REPLACE TABLE` oder `REPLACE TABLE` aktivieren oder deaktivieren. Beim Erstellen einer Tabelle nutzt man `CREATE TABLE` mit der Eigenschaft `delta.feature.catalogManaged`. Bei einer bestehenden Tabelle nutzt man `ALTER TABLE`, um die Funktion zu aktivieren oder zu deaktivieren.
- Um Catalog Commits bei Streaming Tables zu nutzen, muss man das Databricks-Account-Team kontaktieren und Zugang zur Public Preview beantragen.
- Catalog Commits sind nicht mit externem Datenzugriff bei Streaming Tables kompatibel. Um Catalog Commits zu nutzen, muss man den externen Zugriff zuerst deaktivieren.
- Tabellen mit aktivierten Catalog Commits werden über OpenSharing mit vorsignierten URLs statt mit Cloud-Tokens geteilt.
- Materialized Views können keine Catalog Commits aktiviert haben.
- Single-User-Cluster können nicht auf Streaming Tables mit aktivierten Catalog Commits zugreifen.

## Weiterführende Ressourcen

- Transaktionen
- Transaktionsmodi
- Referenz zu Tabelleneigenschaften

---
**Quelle:** https://docs.databricks.com/aws/en/tables/features/catalog-commits  
**Stand:** 2026-08-06
