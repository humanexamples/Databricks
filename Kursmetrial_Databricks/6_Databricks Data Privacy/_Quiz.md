# Quiz

1. **Ein Data-Privacy-Architekt evaluiert, ob für eine neue PII-Pipeline Hashing oder Tokenisierung verwendet werden soll. Der nachgelagerte Use Case erfordert häufige Lookups über den anonymisierten Identifier, und der Datensatz enthält Milliarden von Datensätzen. Welche Technik ist besser geeignet und warum?**

   - Hashing, weil es keine Lookup-Tabelle benötigt und eine deterministische Ausgabe erzeugt, die schnell zu berechnen und abzufragen ist.

   - Beide sind gleich gut geeignet; die Wahl hängt nur von regulatorischen Anforderungen ab.

   - Tokenisierung, weil sie Werte in einer sicheren Lookup-Tabelle speichert, die schnell zu lesen ist, und weil die de-identifizierten Daten in weniger Bytes gespeichert werden – beides Vorteile bei Milliarden von Datensätzen. ✅

   - Keine von beiden; bei Milliarden von Datensätzen ist Data Suppression die einzig praktikable Technik.

2. **Eine Streaming-Query verwendet `.trigger(availableNow=True)`, um Löschanfragen in eine Tabelle zu schreiben. Ein Entwickler führt dieselbe Zelle später erneut aus. Was bestimmt, ob der Stream erneut Daten verarbeitet oder sofort beendet wird?**

   - Der Stream verarbeitet bei einem erneuten Lauf immer alle Quelldaten neu, unabhängig vom Checkpoint-Status.

   - Der Modus `trigger(availableNow=True)` verarbeitet immer genau einen Micro-Batch pro Aufruf.

   - Der Stream läuft nur erneut, wenn die Zieltabelle seit dem letzten Lauf gedroppt und neu erstellt wurde.

   - Der Checkpoint-Speicherort bestimmt, was bereits verarbeitet wurde; wenn der Checkpoint intakt ist und seit dem letzten Lauf keine neuen Daten eingetroffen sind, beendet sich der Stream sofort, nachdem er null Datensätze verarbeitet hat. ✅

3. **Ein Team möchte Account-Nutzern Zugriff auf `customers_gold_view` im Schema `pii_data` gewähren. Es führt aus: `GRANT SELECT ON VIEW pii_data.customers_gold_view TO \`account users\`.` Ein Nutzer versucht, die View abzufragen, und erhält einen Fehler. Was ist der wahrscheinlichste fehlende Grant?**

   - GRANT READ VOLUME ON SCHEMA pii_data TO `account users`

   - GRANT MODIFY ON VIEW pii_data.customers_gold_view TO `account users`

   - GRANT EXECUTE ON VIEW pii_data.customers_gold_view TO `account users`

   - GRANT USE SCHEMA ON SCHEMA pii_data TO `account users` ✅

4. **Was ist ein Vorteil der Tokenisierung in Bezug auf die Datengröße?**

   - De-identifizierte Daten benötigen weniger Bytes ✅

   - Verdoppelt den Speicherbedarf

   - Erhöht die Datengröße erheblich

   - Hat keine Auswirkung auf die Speichergröße

5. **Ein Compliance-Engineer muss nachweisen, dass die Daten eines bestimmten Nutzers innerhalb der 30-Tage-SLA aus `gold_users` gelöscht wurden. Die Löschung wurde über die Streaming-Funktion `process_deletes` verarbeitet. Welche Kombination von Artefakten liefert den stärksten Audit-Trail?**

   - DESCRIBE HISTORY gold_users (zeigt den Timestamp der MERGE-Operation) + die Tabelle `delete_requests` (zeigt status='deleted' und request_date) + die userMetadata-Commit-Message in der Historie. ✅

   - Die CDF-Ausgabe von `silver_users`, die den Delete-Datensatz für die mrn des Nutzers zeigt.

   - Der Inhalt des Checkpoint-Verzeichnisses, der zeigt, dass die Streaming-Query den relevanten Micro-Batch verarbeitet hat.

   - Ein Screenshot des Databricks-Notebooks, der zeigt, dass die DELETE-Zelle ausgeführt wurde.

6. **Ein Entwickler aktiviert CDF global mit `spark.conf.set('spark.databricks.delta.properties.defaults.enableChangeDataFeed', True)`. Anschließend erstellt er eine neue Tabelle mit CREATE TABLE AS SELECT. Hat die neue Tabelle CDF aktiviert, und werden Tabellen, die vor dem Setzen dieser Einstellung erstellt wurden, ebenfalls CDF aktiviert haben?**

   - Ja für neue Tabellen; bestehende Tabellen werden bei ihrer nächsten Schreiboperation automatisch auf CDF migriert.

   - Nein für beide: Die globale Einstellung betrifft nur die aktuelle Session und wird nicht in die Tabelleneigenschaften übernommen.

   - Ja für beide: Die globale Einstellung aktiviert CDF rückwirkend für alle bestehenden Tabellen.

   - Ja für neue Tabellen, die nach dem Setzen der Einstellung erstellt werden; nein für Tabellen, die vorher existierten – sie benötigen ein explizites ALTER TABLE, um CDF zu aktivieren. ✅

7. **Ein Team möchte Unity Catalog Lineage nutzen, um vor dem Droppen der Tabelle `customers_silver` eine Impact-Analyse durchzuführen. Was zeigt die Downstream-Ansicht im Lineage-Tab, und warum ist dies vor dem Droppen der Tabelle entscheidend?**

   - Downstream zeigt alle Objekte (Views, Tabellen, Notebooks, Dashboards), die auf `customers_silver` verweisen oder daraus abgeleitet sind; dies ist entscheidend, weil das Droppen der Tabelle alle nachgelagerten Consumer brechen würde. ✅

   - Downstream zeigt den Speicherort der Datendateien von `customers_silver`; dies ist entscheidend für die Rückgewinnung von Speicherplatz.

   - Downstream zeigt die Quelldateien, die `customers_silver` befüllt haben; dies ist entscheidend, um die Datenherkunft zu verstehen.

   - Downstream zeigt die Query-Historie für `customers_silver`; dies ist entscheidend für das Auditing, wer auf die Daten zugegriffen hat.

8. **Ein Data Engineer wendet auf derselben Tabelle einen Column Mask auf `customer_id` und einen Row Filter auf `loyalty_segment` an. Ein nachgelagertes BI-Tool fragt die Tabelle mit `SELECT customer_id, loyalty_segment FROM table WHERE customer_id = 12345` ab. Was erhält das BI-Tool tatsächlich?**

   - Die Zeile, die `customer_id = 12345` entspricht, mit `customer_id = 9999999`, unabhängig vom Ergebnis des Row Filters.

   - Die Zeile, die `customer_id = 12345` entspricht, mit dem echten `customer_id`-Wert, weil die WHERE-Klausel vor dem Mask ausgewertet wird.

   - Entweder keine Zeilen (wenn die Zeile durch den Row Filter herausgefiltert wird) oder eine Zeile mit `customer_id = 9999999` (wenn die Zeile den Row Filter passiert), weil Policies vor den Nutzer-Prädikaten injiziert werden. ✅

   - Einen Fehler, weil das Filtern auf einer maskierten Spalte nicht erlaubt ist.

9. **Ein Unity-Catalog-Tag mit dem Key `compliance` und dem Wert `GDPR` wird auf die Spalte `customer_id` angewendet. Welche INFORMATION_SCHEMA-View würdest du abfragen, um dieses Tag programmatisch abzurufen?**

   - INFORMATION_SCHEMA.CATALOG_TAGS

   - INFORMATION_SCHEMA.TABLE_TAGS

   - INFORMATION_SCHEMA.SCHEMA_TAGS

   - INFORMATION_SCHEMA.COLUMN_TAGS ✅

10. **Eine Apache Spark™ Declarative Pipeline verarbeitet `registered_users` parallel über einen Hashing- und einen Tokenisierungs-Pfad. Wenn die Pipeline mitten im Tokenisierungs-Pfad fehlschlägt, welche Garantien gibt das Declarative-Pipeline-Framework für den Zustand der Tabellen des Hashing-Pfads?**

- Die Tabellen des Hashing-Pfads werden als beschädigt markiert und müssen manuell neu aufgebaut werden.

- Die Tabellen des Hashing-Pfads werden auf ihren vorherigen Zustand zurückgerollt, um die Konsistenz über alle Pipeline-Ausgaben hinweg zu wahren.

- Die Tabellen des Hashing-Pfads behalten den Zustand, den sie vor dem Fehler erreicht haben; das Pipeline-Framework verfolgt den Zustand jeder Tabelle unabhängig und setzt beim nächsten Lauf am letzten erfolgreichen Checkpoint fort. ✅

- Alle Pipeline-Ausgaben werden atomar zurückgerollt, weil Spark Declarative Pipelines eine Alles-oder-nichts-Ausführung garantieren.

11. **Ein Data Engineer entwirft eine CDF-basierte Delete-Propagation-Pipeline für GDPR-Compliance. Die Pipeline muss Deletes von einer zentralen Tabelle `silver_users` an 10 nachgelagerte Gold-Tabellen propagieren. Was ist der wesentliche Vorteil der Verwendung von CDF mit `foreachBatch` und `MERGE INTO` gegenüber 10 separaten DELETE-Anweisungen?**

- CDF mit `foreachBatch` aktiviert CDF automatisch für alle 10 nachgelagerten Gold-Tabellen.

- CDF mit `foreachBatch` ist schneller, weil es vektorisierte Ausführung nutzt.

- DELETE-Anweisungen unterstützen keine Subquery-Filter, was sie für die Multi-Table-Propagierung ungeeignet macht.

- CDF mit `foreachBatch` ermöglicht es, mit einem einzigen inkrementellen Read der Änderungen von `silver_users` Updates für alle 10 nachgelagerten Tabellen atomar innerhalb jedes Micro-Batches anzustoßen. Das sichert Konsistenz und ermöglicht es der Pipeline, bei einem Fehler mitten in der Propagierung von Checkpoints aus fortzusetzen. ✅

12. **Ein Nutzer, der Owner einer Dynamic View ist, fragt sie ab, ist aber KEIN Mitglied der Gruppe `supervisors`, die in `is_account_group_member()` referenziert wird. Welche Daten sieht der Nutzer?**

- Alle Zeilen, aber nur mit geschwärzten Spalten, weil Ownership einen Row-Level-Bypass gewährt, aber keinen Column-Level-Bypass.

- Geschwärzte Spalten und gefilterte Zeilen wie in der View-Logik definiert, weil `is_account_group_member()` die Gruppenmitgliedschaft des abfragenden Nutzers zur Laufzeit auswertet – unabhängig von der Ownership. ✅

- Alle Zeilen und ungeschwärzte Spalten, weil Ownership alle View-Level-Filter umgeht.

- Einen Fehler, weil Owner ihre eigenen Dynamic Views nicht abfragen können.

13. **Ein View-Owner hat SELECT auf der zugrunde liegenden Tabelle `customers_silver` durch Ownership. Einem Nicht-Owner-Nutzer wird SELECT auf `customers_gold_view` (die `customers_silver` abfragt) gewährt, er hat aber keine direkten Privileges auf `customers_silver`. Kann der Nicht-Owner-Nutzer die View erfolgreich abfragen?**

- Nein, weil SELECT auf einer View nicht transitiv Zugriff auf ihre Quelltabellen gewährt.

- Ja, weil Unity Catalog den Zugriff auf die zugrunde liegende Tabelle der View mit den Privileges des View-Owners auswertet, nicht mit denen des abfragenden Nutzers. ✅

- Ja, aber nur, wenn die View eine Materialized View statt einer Standard-View ist.

- Nein, weil der Nutzer mindestens READ-Privilege auf allen von der View referenzierten Tabellen haben muss.

14. **Ein Team entwirft eine Data-Privacy-Architektur. Es muss aggregierte Verkaufsdaten für Analysten bereitstellen, ohne einzelne Kundenidentitäten offenzulegen, gleichzeitig aber Data Scientists den Zugriff auf den vollständigen Datensatz für das Modelltraining ermöglichen. Welches Unity-Catalog-Design-Pattern erfüllt beide Anforderungen gleichzeitig am besten?**

- Zwei separate Kataloge erstellen: einen für Analysten mit anonymisierten Daten, einen für Data Scientists mit vollständigen Daten.

- Eine Dynamic View oder einen Row Filter/Column Mask auf die Quelltabelle anwenden, Analysten Zugriff auf die View/Tabelle gewähren und Data Scientists direkten Zugriff auf die Quelltabelle mit den passenden Privileges. ✅

- Die Quelltabelle in zwei physische Kopien duplizieren: eine maskierte für Analysten und eine unmaskierte für Data Scientists.

- Eine einzige View ohne Zugriffskontrollen verwenden und sich darauf verlassen, dass Data Scientists ihren Zugriff selbst regulieren.

15. **Eine Column-Mask-UDF wird in Python definiert und auf eine Tabellenspalte angewendet. Unter welcher Bedingung wird dies in Unity Catalog unterstützt?**

- Python-UDFs werden als Column Masks nur unterstützt, wenn die Tabelle an einer External Location gespeichert ist.

- Python-UDFs können unter keinen Umständen als Column Masks verwendet werden; nur SQL-UDFs sind erlaubt.

- Python-UDFs werden nativ als Column Masks unterstützt, ohne zusätzliches Wrapping.

- Python-UDFs werden als Column Masks nur unterstützt, wenn sie in eine SQL-UDF eingebettet (gewrappt) sind. ✅

16. **Eine Streaming-Pipeline schreibt mit `.outputMode('append')` in `bronze_users`, und eine zweite Pipeline liest aus `bronze_users` und merged mit `foreachBatch` in `silver_users`. Wenn der Bronze-Stream gestoppt und mit einem neuen Checkpoint-Speicherort neu gestartet wird, welche Konsequenz hat das für die Silver-Tabelle?**

- Die Silver-Tabelle wird automatisch auf den Startpunkt des neuen Bronze-Streams zurückgesetzt.

- Die `foreachBatch`-Funktion wirft einen Fehler, weil sich der Checkpoint-Status der Quelltabelle geändert hat.

- Der Bronze-Stream verarbeitet alle Quelldateien von Anfang an neu (da der Checkpoint neu ist), wodurch potenziell doppelte Datensätze erneut an `bronze_users` angehängt werden, die das Silver-MERGE dann zu upserten versucht – das führt aufgrund der MERGE-Idempotenz zu keinem Datenverlust, verursacht aber potenziell unnötige Neuverarbeitung. ✅

- Keine Konsequenz; die Silver-Tabelle behält alle zuvor gemergten Daten, und der neue Bronze-Stream hängt nur neue Dateien an.

17. **Ein Entwickler möchte `table_changes('silver_users', 2, 3)` verwenden, um CDF für einen bestimmten Versionsbereich zu lesen. Was passiert, wenn Version 3 zum Zeitpunkt der Query noch nicht existiert?**

- Die Query wirft einen Out-of-Range-Fehler, weil die angegebene End-Version standardmäßig nicht die zuletzt committete Version der Tabelle überschreiten darf. ✅

- Die Query blockiert, bis Version 3 committet wird.

- Die Query gibt alle Änderungen von Version 2 bis zur zuletzt verfügbaren Version zurück.

- Die Query gibt ein leeres Ergebnis zurück.

18. **Auf eine Tabelle wurde über `ALTER TABLE ... SET ROW FILTER` ein Row Filter angewendet. Ein Data Engineer führt dann `ALTER TABLE ... DROP ROW FILTER` aus. Was passiert mit der zugrunde liegenden UDF, die den Filter implementiert hat?**

- Die UDF bleibt im Schema und muss separat gedroppt werden, falls sie nicht mehr benötigt wird. ✅

- Die UDF wird deaktiviert, aber nicht gedroppt, und kann mit ALTER TABLE wieder aktiviert werden.

- Die UDF wird zu Audit-Zwecken in ein System-Schema verschoben.

- Die UDF wird zusammen mit dem Row Filter automatisch gedroppt.

19. **Ein Entwickler versucht, einer Tabelle, die bereits einen Row Filter hat, einen zweiten Row Filter hinzuzufügen. Was ist das Ergebnis?**

- Der zweite Row Filter ersetzt den ersten stillschweigend.

- Ein Fehler wird geworfen, weil jede Tabelle nur einen Row Filter haben kann. Der bestehende Filter muss gedroppt werden, bevor ein neuer angewendet werden kann. ✅

- Der zweite Row Filter wird in eine Warteschlange gestellt und angewendet, nachdem die Ergebnisse des ersten Filters zurückgegeben wurden.

- Der zweite Row Filter wird hinzugefügt, und beide Filter werden zur Query-Zeit konjunktiv (UND-Logik) angewendet.

20. **Ein Entwickler setzt auf Notebook-Ebene `spark.databricks.delta.commitInfo.userMetadata = 'Deletes committed'` und schreibt dann eine Streaming Table mit `.option('userMetadata', 'Requests processed interactively')`. Welcher userMetadata-Wert erscheint im STREAMING-UPDATE-Eintrag der Tabellenhistorie?**

- 'Requests processed interactively', weil userMetadata-Optionen auf Schreibebene die Konfiguration auf Session-Ebene für diese bestimmte Schreiboperation überschreiben. ✅

- Beide Werte werden verkettet: 'Deletes committed; Requests processed interactively'.

- Kein Wert erscheint; userMetadata wird nur für Batch-Writes aufgezeichnet, nicht für Streaming-Writes.

- 'Deletes committed', weil die Einstellung auf Notebook-Ebene Vorrang vor Optionen auf Schreibebene hat.
