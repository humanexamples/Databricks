# Quiz

1. **Ein Data-Engineering-Team baut eine Pipeline, die Transaktionsdaten aus drei regionalen Bereichen ingestiert: Division Alpha (CSV), Division Beta (CSV) und Division Gamma (JSON). Jeder Bereich liefert täglich Dateien in separate Cloud-Speicher-Volumes. Das Team möchte alle Transaktionen für eine einheitliche nachgelagerte Verarbeitung in einer einzigen Bronze-Streaming-Table zusammenführen.**

**Was ist der beste Ansatz, um dies in Spark Declarative Pipelines umzusetzen?**

   - Eine Materialized View verwenden, um die drei separaten Bronze-Tabellen zusammenzuführen
   - UNION ALL verwenden, um drei separate Streaming Tables zu einer Bronze-Tabelle zu kombinieren
   - Drei explizite CREATE-FLOW-Definitionen erstellen, die jeweils per INSERT INTO ... BY NAME in dieselbe Bronze-Zieltabelle schreiben ✅
   - Einen einzigen Flow erstellen, der mit Wildcard-Pfaden aus allen drei Volumes liest

2. **Warum wird im Quarantäne-Muster inverse Logik (z. B. `NOT(alle Regeln erfüllt)`) verwendet, statt `DROP ROW` auf die Tracking-Tabelle anzuwenden?**

   - Inverse Logik ist erforderlich, um VARIANT-Spalten zu verarbeiten
   - Inverse Logik verbessert die Abfrage-Performance während der Ingestion
   - Inverse Logik stellt sicher, dass alle Datensätze geschrieben und markiert werden, sodass nachgelagerte Views gültige und ungültige Datensätze sicher weiterleiten können ✅
   - Inverse Logik korrigiert Formatierungsfehler in den Daten automatisch

3. **Welchen Zweck hat in einer Multiplex-Streaming-Pipeline der „Fan-out“-Schritt nach der Bronze-Tabelle?**

   - Unterschiedliche Event-Typen filtern und in separate, domänenspezifische Silber-Tabellen leiten ✅
   - Alle Datensätze über mehrere geografische Regionen duplizieren
   - Die Daten für eine effiziente Speicherung komprimieren
   - Alle Event-Typen in einer einzigen denormalisierten Tabelle zusammenführen

4. **Ein Team baut eine Multiplex-Pipeline, die rohe Telemetrie-Events aus einer einzigen Parquet-Quelle mit Web-, Mobile- und API-Events ingestiert. Die Bronze-Tabelle verwendet `PARSE_JSON`, um den Payload als VARIANT-Spalte zu speichern.**

**Beim Erstellen der Bronze-Tabelle erhalten sie einen Fehler, dass der Typ VARIANT nicht unterstützt wird. Was ist die wahrscheinlichste Ursache?**

   - Der Typ VARIANT wird nur in Gold-Materialized-Views unterstützt
   - PARSE_JSON kann nur mit JSON-Dateien verwendet werden, nicht mit Parquet
   - In der Tabelle fehlt die TBLPROPERTIES-Einstellung `'delta.feature.variantType-preview' = 'supported'` ✅
   - VARIANT-Spalten können in Streaming Tables nicht verwendet werden

5. **Eine Streaming-Pipeline verwendet in der Silber-Schicht `TRY_CAST(transaction_value AS DOUBLE)`. In den eingehenden Daten hat ein Datensatz `transaction_value = "N/A"`.**

**Was enthält die Silber-Tabelle für diesen Datensatz in der Spalte `transaction_value`?**

   - Die Pipeline löst eine Laufzeitausnahme aus und schlägt fehl
   - Sie enthält den String "N/A"
   - Sie enthält den Wert 0.0
   - Sie enthält einen NULL-Wert ✅

6. **Eine Pipeline verwendet für einen kritischen Constraint den Verletzungsmodus FAIL UPDATE: `CONSTRAINT valid_user EXPECT (user_id IS NOT NULL) ON VIOLATION FAIL UPDATE`.**

**Es trifft eine Datei mit 1.000.000 gültigen Datensätzen und genau 1 Datensatz ohne `user_id` ein. Was ist das Ergebnis des Pipeline-Laufs?**

   - Das gesamte Pipeline-Update schlägt fehl, und es werden null Datensätze in die Tabelle geschrieben ✅
   - 999.999 Datensätze werden geschrieben und 1 Datensatz wird verworfen
   - 999.999 Datensätze werden geschrieben und 1 Datensatz wird in Quarantäne gestellt
   - Alle 1.000.000 Datensätze werden geschrieben, aber die Pipeline protokolliert eine Warnung

7. **Was ist in einer mehrschichtigen Pipeline die Hauptaufgabe von Unity-Catalog-Tags (z. B. `ALTER TABLE SET TAGS ('domain' = 'finance')`)?**

   - Sie liefern semantische Metadaten für Organisation, Auffindbarkeit und Governance von Pipeline-Objekten ✅
   - Sie verbessern die Geschwindigkeit der Abfrageausführung, indem sie als Sekundärindizes dienen
   - Sie erzwingen automatisch Sicherheit auf Zeilenebene
   - Sie lösen automatisch erneute Pipeline-Läufe aus, wenn sich Daten ändern

8. **Was verhindert die TBLPROPERTIES-Einstellung `'pipelines.reset.allowed' = 'false'` bei einer Bronze-Streaming-Table?**

   - Sie verhindert Full Table Refreshes, die Daten leeren und Checkpoints entfernen würden ✅
   - Sie verhindert, dass neue Flows in die Tabelle schreiben
   - Sie verhindert, dass nachgelagerte Systeme die Tabelle abfragen
   - Sie verhindert automatische Schema Evolution

9. **Welchen Zweck hat die Klausel `SEQUENCE BY` in einem AUTO-CDC-INTO-Flow?**

   - Sie legt fest, welche Spalten in die Ausgabe aufgenommen werden
   - Sie stellt sicher, dass CDC-Events anhand der angegebenen Spalte in chronologischer Reihenfolge angewendet werden ✅
   - Sie erzeugt eine automatisch hochzählende ID für die Tabelle
   - Sie gibt den Primärschlüssel der Zieltabelle an

10. **Eine Silber-Streaming-Table verarbeitet Lagerbestandsdaten und wendet den folgenden Constraint an:**

```sql
    CONSTRAINT valid_stock EXPECT (stock_level >= 0) ON VIOLATION DROP ROW
    ```

**Während eines Pipeline-Laufs werden 500 Datensätze verarbeitet. Die Pipeline-UI zeigt, dass 12 Datensätze den Constraint `valid_stock` verletzt haben. Die Silber-Tabelle enthält 488 Datensätze.**

**Was ist mit den 12 ungültigen Datensätzen passiert?**

- Sie haben ein FAIL UPDATE ausgelöst und die Pipeline gestoppt
- Sie wurden dauerhaft gelöscht und können nicht wiederhergestellt werden ✅
- Sie wurden in der Silber-Tabelle mit `is_quarantined = TRUE` markiert
- Sie wurden automatisch in eine separate Quarantäne-Tabelle geschrieben

11. **Warum können Iceberg-Lesezugriffe nicht direkt auf von der Pipeline verwalteten Streaming Tables oder Materialized Views aktiviert werden?**

- Materialized Views verwenden nicht das Delta-Lake-Format
- Streaming Tables unterstützen keine spaltenorientierte Speicherung
- Für von der Pipeline verwaltete Tabellen kann die erforderliche Eigenschaft `delta.universalFormat.enabledFormats` nicht direkt gesetzt werden ✅
- Iceberg unterstützt keine Streaming-Ingestion

12. **Welchen Zweck hat es, `_metadata.file_name` beim Ingestieren von Rohdateien in eine Bronze-Streaming-Table aufzunehmen?**

- Es legt die Verarbeitungsreihenfolge der Dateien fest
- Es partitioniert die Tabelle automatisch nach Datei
- Es liefert den Namen der Quelldatei für Data Lineage und Debugging ✅
- Es speichert die Dateigröße für die Kostenverfolgung

13. **Eine Pipeline verarbeitet 10.000 JSON-Datensätze in eine Bronze-Tabelle. 50 Datensätze enthalten eine fehlerhafte JSON-Struktur, die nicht in die definierten Schemaspalten geparst werden kann. Der Data Engineer hat die Spalte `_rescued_data` in die Tabellendefinition aufgenommen.**

**Wie sieht die Bronze-Tabelle nach dem Lauf aus?**

- 10.000 Datensätze werden geschrieben; bei den 50 fehlerhaften Datensätzen werden die Roh-Strings in der Spalte `_rescued_data` erfasst ✅
- 10.000 Datensätze werden geschrieben, aber die 50 fehlerhaften Datensätze enthalten in allen Spalten nur NULL-Werte
- Die Pipeline schlägt fehl, da JSON-Parsing-Fehler standardmäßig fatal sind
- 9.950 Datensätze werden geschrieben; die 50 fehlerhaften Datensätze werden dauerhaft verworfen

14. **Ein Business-Analyst führt die folgende Abfrage auf einer SCD-Type-2-CDC-Tabelle aus:**

```sql
    SELECT * FROM users_silver WHERE __END_AT IS NULL
    ```

**Was genau ruft der Analyst ab?**

- Die aktuell aktive Version aller Benutzer ✅
- Alle Benutzer, die dauerhaft gelöscht wurden
- Benutzer, denen aufgrund von Datenfehlern ein Ablaufdatum fehlt
- Das vollständige historische Protokoll aller Benutzeränderungen

15. **Ein Team setzt das Quarantäne-Muster mit einer Tracking-Tabelle (`tx_silver_dq`) mit reinen WARN-Constraints und einer Spalte `is_quarantined` um, die über inverse Logik definiert ist:**

```sql
    NOT(item_count >= 0 AND transaction_value >= 0) AS is_quarantined
    ```

**Nach der Verarbeitung von 217 Datensätzen enthält eine nachgelagerte View `valid_records` 208 Datensätze und eine View `quarantined_records` 9 Datensätze. Was ist der Hauptvorteil dieses Musters gegenüber `DROP ROW`?**

- Es verbessert die Abfrage-Performance durch Partitionierung der Daten
- Es bewahrt alle ungültigen Datensätze mit detaillierter Fehlerverfolgung für Audit und Korrektur auf ✅
- Es senkt die Speicherkosten durch Komprimierung ungültiger Datensätze
- Es behebt Datenqualitätsprobleme automatisch

16. **Eine Multi-Flow-Pipeline führt Daten aus drei verschiedenen Quellen zusammen. Der Data Engineer definiert Datenqualitäts-Constraints direkt in den drei einzelnen `CREATE FLOW`-Anweisungen statt auf der Bronze-Ziel-Streaming-Table.**

**Welche Konsequenz hat dieses Design?**

- Es verbessert die Ausführungsgeschwindigkeit der Pipeline
- Es aktiviert Liquid Clustering auf den einzelnen Flows
- Es erstellt automatisch drei separate Quarantäne-Tabellen
- Es ist ungültige Syntax; Constraints müssen zentral auf der Zieltabelle definiert werden ✅

17. **Eine CDC-Pipeline verwendet AUTO CDC INTO, um Änderungen an Benutzerprofilen mit SCD-Type-2-Speicherung zu verarbeiten. Nach der Verarbeitung von zwei Dateien enthält die Silber-Tabelle die folgenden Datensätze für `user_id = 98765`:**

| user_id | name | email | __START_AT | __END_AT |
|---|---|---|---|---|
| 98765 | Jane Doe | jane@email.com | 2026-01-01 10:00 | 2026-01-02 14:30 |
| 98765 | Jane Doe | j.doe@newemail.com | 2026-01-02 14:30 | NULL |

**Welche Art von CDC-Operation hat zur Erstellung des zweiten Datensatzes geführt?**

- DELETE
- MERGE
- INSERT
- UPDATE ✅

18. **Was ist der Hauptzweck expliziter `CREATE FLOW`-Definitionen gegenüber den standardmäßigen Single-Flow-Anweisungen `AS SELECT` in Spark Declarative Pipelines?**

- Explizite Flows aktivieren automatisch Liquid Clustering
- Explizite Flows ermöglichen es mehreren Quellabfragen, unabhängig voneinander in eine einzige Zieltabelle zu schreiben ✅
- Explizite Flows benötigen keine Checkpoint-Verwaltung
- Explizite Flows werden schneller ausgeführt als Default Flows

19. **Eine Bronze-Schicht ist darauf ausgelegt, Schema Evolution für Versanddaten zu behandeln, die in künftigen Dateilieferungen neue Spalten erhalten werden:**

```sql
    FROM STREAM read_files(
      '${source}',
      format => 'csv',
      schemaHints => 'delivery_status STRING, insurance_cost STRING'
    )
    ```

**Die erste Dateilieferung (`batch_1.csv`) enthält die Spalten `delivery_status` und `insurance_cost` NICHT. Die zweite Dateilieferung (`batch_2.csv`) enthält BEIDE neuen Spalten.**

**Was passiert, wenn beide Dateien verarbeitet werden?**

- Die Einstellung schemaHints lehnt batch_1.csv ab, bis sie alle deklarierten Spalten enthält
- Beide neuen Spalten werden für batch_1.csv in `_rescued_data` erfasst
- Zeilen aus batch_1.csv haben NULL in den neuen Spalten; Zeilen aus batch_2.csv haben tatsächliche Werte ✅
- Die Pipeline schlägt bei der Verarbeitung von batch_1.csv wegen fehlender Spalten fehl

20. **Wofür stehen die Metadatenspalten `__START_AT` und `__END_AT` in einer SCD-Type-2-Tabelle?**

- Den Zeitpunkt, zu dem eine Datei im Cloud-Speicher eingetroffen ist, und den Zeitpunkt ihrer Ingestion
- Die Checkpoint-Zeitstempel für die Streaming-Verarbeitung
- Den Gültigkeitszeitraum, in dem eine bestimmte Version eines Datensatzes aktiv war ✅
- Start- und Endzeit der Pipeline-Ausführung
