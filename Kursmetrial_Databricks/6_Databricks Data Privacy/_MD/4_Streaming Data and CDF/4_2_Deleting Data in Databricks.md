## 4_2_Daten in Databricks löschen

In dieser Lektion befassen wir uns mit dem Löschen von Daten in Databricks, dessen Nachverfolgung, der Propagierung mit CDF sowie den damit verbundenen Einschränkungen und Compliance-Use-Cases.

**Löschen von Daten in Databricks**

Um Datenschutzvorschriften wie GDPR und CCPA einzuhalten, muss PII in Databricks effektiv und effizient gehandhabt werden – und insbesondere das Löschen von PII erfordert besondere Aufmerksamkeit. Das Löschen wird typischerweise in Pipelines gehandhabt, die von den ETL-Pipelines getrennt sind.

CDF-Daten können verwendet werden, um Löschaktionen an nachgelagerte Tabellen zu propagieren. Das ähnelt dem Filtern von Multiplex-Bronze-Tabellen, um verschiedene nachgelagerte Pipelines für die ETL-Verarbeitung umzusetzen, bei der wir Daten in einen CDC-Feed einspeisen.

Bei Nutzerdaten können Aktionen im Change Data Feed herausgefiltert werden. Für alle Zugänge wie neue Datensätze, neue Nutzer-Datensätze und aktualisierte Nutzer-Datensätze würden wir die Daten weiterhin in unsere Silver-Pipelines einfügen. Für Lösch-Events können wir dies in einer separaten Pipeline behandeln, die die spezifischen Datenschutzanforderungen für das Löschen von Daten adressiert.

Das Löschen von Daten erfordert besondere Aufmerksamkeit!

- Unternehmen müssen Datenlöschanfragen sorgfältig behandeln, um die Compliance mit Datenschutzvorschriften wie GDPR und CCPA zu wahren.
- PII von Nutzern muss in Databricks effektiv und effizient gehandhabt werden, einschließlich des Löschens.
- Diese Operationen werden üblicherweise in Pipelines gehandhabt, die von den ETL-Pipelines getrennt sind.
- CDF-Daten können verwendet werden, um Löschaktionen an nachgelagerte Tabellen zu propagieren.

------

**Wichtige Datenänderungen protokollieren**

Delta Lake unterstützt beliebige Commit-Messages, die im Delta-Transaktionslog aufgezeichnet und in der Tabellenhistorie einsehbar sind. Das kann bei späterem Auditing helfen. Commit-Messages können auf globaler Ebene gesetzt und als Teil einer Schreiboperation angegeben werden. Datenzufügung kann zum Beispiel nach Verarbeitungstyp gelabelt werden, etwa manuell oder automatisiert.

Commit-Messages verwenden

- Delta Lake unterstützt **beliebige Commit-Messages**, die im Delta-Transaktionslog aufgezeichnet und in der Tabellenhistorie einsehbar sind. Das kann bei späterem **Auditing** helfen.
- Commit-Messages können:
  - Auf globaler Ebene gesetzt werden
  - Als Teil einer Schreiboperation angegeben werden. Datenzufügung kann zum Beispiel nach Verarbeitungstyp gelabelt werden: manuell, automatisiert.

------

**Datenlöschung mit CDF propagieren**

Datenlöschanfragen können mit automatisierten Triggern über Structured Streaming optimiert werden. CDF kann separat genutzt werden, um Datensätze zu identifizieren, die in nachgelagerten Tabellen gelöscht oder geändert werden müssen, wie zuvor erwähnt. Beachte: Wenn die History- und CDF-Features von Delta Lake genutzt werden, sind gelöschte Werte in älteren Versionen der Daten weiterhin vorhanden. Wir können dies lösen, indem wir an einer Partitionsgrenze löschen.

Wie kann CDF zur Propagierung von Deletes verwendet werden?

- Datenlöschanfragen können mit automatisierten Triggern über Structured Streaming optimiert werden.
- CDF kann separat genutzt werden, um Datensätze zu identifizieren, die in nachgelagerten Tabellen gelöscht oder geändert werden müssen.

Hinweis: Wenn die History- und CDF-Features von Delta Lake genutzt werden, sind gelöschte PII-Werte in älteren Versionen der Daten weiterhin vorhanden.

- Der Befehl VACUUM löscht PII physisch
- Das Löschen an einer Partitionsgrenze macht den gesamten Prozess effizienter

------

**CDF-Retention-Policy**

Bei der CDF-Retention-Policy erfolgt das Löschen von Dateien erst, wenn die Tabelle mit VACUUM bereinigt wird. CDF-Datensätze folgen derselben Retention-Policy wie die Delta-Tabelle, sodass der Befehl VACUUM CDF-Daten löscht. Standardmäßig verhindert die Delta-Engine automatische VACUUM-Operationen mit weniger als sieben Tagen Retention.

Für diese Dateien musst du die Retention-Duration-Prüfung von Spark deaktivieren. Führe VACUUM mit DRY RUN aus, um die Dateien vor der endgültigen Entfernung zu prüfen, und führe VACUUM mit null Stunden Retention aus. Beachte, dass dies die Schritte sind, die du für Delta-Tabellen unternehmen würdest, wenn du keine Lakeflow Spark Declarative Pipelines verwendest.

Wichtige Hinweise zur CDF-Konfiguration

- Das Löschen von Dateien erfolgt erst, wenn wir unsere Tabelle mit VACUUM bereinigen!
- CDF-Datensätze folgen derselben Retention-Policy wie die Tabelle. Der Befehl VACUUM löscht CDF-Daten.
- Standardmäßig verhindert die Delta-Engine VACUUM-Operationen mit weniger als 7 Tagen Retention. Um VACUUM für diese Dateien manuell auszuführen:
  - Deaktiviere die Retention-Duration-Prüfung von Spark (`retentionDurationCheck.enabled`)
  - Führe VACUUM mit DRY RUN aus, um die Dateien vor der endgültigen Entfernung zu prüfen
  - Führe VACUUM mit RETAIN 0 HOURS aus!

------

**Kann ich DML auf einer Streaming Table ausführen? (z. B. GDPR)**

Die nächste Frage lautet: „Kann ich Data-Manipulation-Aktionen wie Inserts, Updates, Deletes und Merges in eine Streaming Table ausführen?“.

Betrachten wir einen GDPR-Use-Case mit Streaming Tables und Materialized Views.

1. Im Staging werden Informationen aus Kafka eingespeist, wo wir eine begrenzte Retention haben. In diesem Beispiel speisen wir JSON-Dateien ein und streamen sie in unsere Bronze-Tabelle. Append-only wird verwendet, weil wir mit einer Streaming Table arbeiten. Von hier aus wird `APPLY CHANGES INTO` auf unsere Silver-Tabelle angewendet, um die Daten zu verarbeiten.
2. In Lakeflow Spark Declarative Pipelines haben wir eine konfigurierbare Retention, bei der du die Pipeline-Reset-Berechtigung setzen kannst, um zu verhindern, dass die Tabelle aktualisiert wird. Das kann nützlich sein, wenn du einen Nutzer dauerhaft löschen musst.
3. Für nachgelagerte Operationen kannst du Full Refreshes auf den Silver- und Gold-Tabellen mit Materialized Views durchführen, um diese Werte darauf basierend neu zu berechnen. Bei größeren Tabellen kann dies jedoch teuer sein.

![image-20260710143314825](../../../../assets/image-20260710143314825.png)

Du kannst deine Daten außerdem bei Bedarf korrigieren, für Fälle wie:

- Du kannst deine Daten anhand von Datumsintervallen löschen, um die Compliance für Aufbewahrungsfristen sicherzustellen.
- Bereinige dein PII in einer bestimmten Spalte oder führe es mit einer anderen Tabelle zusammen.
- Oder hänge einfach weiterhin neue Daten an.

![image-20260710143419311](../../../../assets/image-20260710143419311.png)

Bei Materialized Views kannst du keine direkten INSERT-, UPDATE- oder DELETE-Operationen ausführen, da sie ihrer Natur nach die Query-Ergebnisse des letzten Refreshs speichern. Das ermöglicht einen schnelleren Datenabruf für die Tabellen der Gold-Schicht. Stattdessen werden Materialized Views über Refresh-Operationen aktualisiert, die während der Lakeflow Spark Declarative Pipelines ausgeführt werden. Wenn eine MV manuell erstellt wird, kann sie manuell mit dem Befehl „Refresh“ aktualisiert werden.

![image-20260710143523134](../../../../assets/image-20260710143523134.png)
