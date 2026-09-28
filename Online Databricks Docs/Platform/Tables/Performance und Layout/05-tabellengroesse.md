# Tabellengröße in Databricks

Die angezeigte Tabellengröße unterscheidet sich oft von der tatsächlichen Größe im Objektspeicher. Dieser Artikel erklärt, warum das so ist und wie man Speicherplatz zurückgewinnt.

Die für Delta-Lake- und Apache-Iceberg-Tabellen angezeigte Größe unterscheidet sich von der Gesamtgröße der zugehörigen Verzeichnisse im Cloud Object Storage. Diese Datenformate behalten frühere Versionen von Datendateien, um Time-Travel-Abfragen zu ermöglichen. Datendateien werden erst gelöscht, wenn `VACUUM` nach Ablauf der Aufbewahrungsfrist läuft.

## Warum die Tabellengröße von der Verzeichnisgröße abweicht

Die in Databricks über die Oberfläche und über `DESCRIBE`-Befehle angezeigten Tabellengrößen beziehen sich auf die Gesamtgröße der Datendateien, die in der aktuellen Version der Tabelle referenziert werden. Die meisten Schreiboperationen auf Tabellen erfordern ein Neuschreiben der zugrunde liegenden Datendateien. Alte Datendateien bleiben dabei erhalten, um Time-Travel-Abfragen zu ermöglichen.

> **Hinweis:** Wenn regelmäßig Datensätze gelöscht oder aktualisiert werden, können Deletion Vectors Abfragen beschleunigen und die Gesamtgröße der Datendateien reduzieren.

## Speicher-Metriken für eine Tabelle berechnen

**Gilt für:** Databricks Runtime 18.0 und höher

Um zu verstehen, warum die Gesamtspeichergröße von der Tabellengröße abweicht, nutzt man `ANALYZE TABLE … COMPUTE STORAGE METRICS`. Dieser Befehl zeigt eine detaillierte Aufschlüsselung der Speicherbelegung. Damit kann man:

- **Optimierungspotenzial erkennen:** sehen, wie viel Speicher mit `VACUUM` zurückgewonnen werden kann
- **Time-Travel-Overhead analysieren:** die Kosten der Aufbewahrung historischer Daten verstehen
- **Speichermuster verfolgen:** durch regelmäßiges Ausführen des Befehls beobachten, wie sich der Speicherverbrauch einer Tabelle entwickelt
- **Speicher über Tabellen hinweg prüfen:** den Befehl in einer Schleife ausführen, um den gesamten Datenbestand zu analysieren

Der Befehl liefert umfassende Metriken, unter anderem:

- **Gesamtspeichergröße:** der komplette Speicherbedarf inklusive aller Daten, Metadaten und Logs
- **Aktive Daten:** Größe der aktuellen Tabellenversion
- **Durch VACUUM freigebbare Daten:** Speicherplatz, der zurückgewonnen werden kann
- **Time-Travel-Daten:** historische Daten für Rollbacks

Das ist besonders wertvoll für Unity-Catalog-Managed-Tables, bei denen Databricks den Speicher automatisch über Predictive Optimization verwaltet.

Die vollständige Syntax und Beispiele findet man unter „ANALYZE TABLE … COMPUTE STORAGE METRICS".

## Predictive Optimization zur Steuerung der Datengröße nutzen

Databricks empfiehlt Unity-Catalog-Managed-Tables mit aktivierter Predictive Optimization. Bei Managed Tables mit Predictive Optimization führt Databricks automatisch die Befehle `OPTIMIZE` und `VACUUM` aus. Das verhindert die Anhäufung ungenutzter Datendateien. Ein Unterschied zwischen der Größe der aktuellen Tabellenversion und der Gesamtgröße der Datendateien im Cloud Object Storage ist normal. Nicht in der aktuellen Version referenzierte Datendateien werden für Time-Travel-Abfragen benötigt.

## VACUUM-Speicher-Metriken

Wenn ungenutzte Datendateien mit `VACUUM` aufgeräumt werden, oder wenn man mit `DRY RUN` die zur Löschung vorgesehenen Dateien vorab anzeigt, melden die Metriken die Anzahl und Größe der entfernten Dateien. Größe und Anzahl der von `VACUUM` entfernten Dateien schwanken stark. Es ist aber üblich, dass die Größe der entfernten Dateien die Gesamtgröße der aktuellen Tabellenversion übersteigt.

## OPTIMIZE-Speicher-Metriken

Wenn `OPTIMIZE` auf einer Zieltabelle läuft, fassen neue Datendateien Datensätze aus bestehenden Datendateien zusammen. Die während `OPTIMIZE` committeten Änderungen betreffen nur die Datenorganisation. Der Inhalt der zugrunde liegenden Daten ändert sich nicht. Die Gesamtgröße der zugrunde liegenden Datendateien der Tabelle steigt nach `OPTIMIZE` zunächst an, weil die neuen komprimierten Dateien im selben Verzeichnis neben den alten, nicht optimierten Datendateien liegen.

Die nach `OPTIMIZE` angezeigte Tabellengröße ist in der Regel kleiner als vor dem Lauf, weil die Gesamtgröße der von der aktuellen Tabellenversion referenzierten Datendateien durch die Datenkomprimierung sinkt. Um die zugrunde liegenden Datendateien zu entfernen, muss `VACUUM` nach Ablauf der Aufbewahrungsfrist laufen.

> **Hinweis:** Ähnliche Metriken kann man auch bei Operationen wie `REORG TABLE` oder `DROP FEATURE` beobachten. Alle Operationen, die ein Neuschreiben von Datendateien erfordern, erhöhen die Gesamtgröße der Daten im Verzeichnis, bis `VACUUM` die nicht mehr in der aktuellen Tabellenversion referenzierten Datendateien entfernt.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/size  
**Stand:** 2026-08-06
