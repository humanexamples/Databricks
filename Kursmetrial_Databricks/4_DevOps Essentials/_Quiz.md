# Quiz

1. **Nachdem alle Hilfsfunktionen per Unit-Test geprüft wurden, möchte ein Team sicherstellen, dass die von der End-to-End-Pipeline erzeugten Bronze-, Silber- und Gold-Tabellen bei jedem Pipeline-Lauf Datenqualitätsregeln erfüllen (keine Nullwerte in Schlüsselspalten, erwartete Wertebereiche, erwartete Zeilenanzahlen). Das Team möchte nach Möglichkeit keinen zusätzlichen Setup- und Validierungscode schreiben. Welcher Ansatz erfüllt diese Anforderung AM BESTEN?**

   - Einen separaten Workflow mit mehreren Notebook-Tasks erstellen, die jede Ausgabetabelle erneut lesen und nach Abschluss der Pipeline Validierungsabfragen ausführen.
   - Expectations direkt in einer deklarativen Pipeline definieren, sodass Datenqualitätsregeln beim Aufbau jeder Tabelle inline ausgewertet werden und in der Pipeline-UI sichtbar sind.
   - Jede Tabelle nach jedem Pipeline-Lauf manuell in einem Notebook prüfen und Auffälligkeiten in einer gemeinsamen Tabelle dokumentieren.
   - Die vorhandenen Unit-Tests nach jedem Pipeline-Lauf erneut gegen die Produktionstabellen ausführen.

2. **Welches der folgenden Szenarien würde ein Integrationstest erkennen, ein Unit-Test aber NICHT?**

   - Eine Mapping-Funktion, die bei einer Null-Eingabe 'Unknown' statt der erwarteten Kategoriebezeichnung zurückgibt
   - Eine Join-Bedingung in der Pipeline, die beim Übergang von Bronze zu Silber unbemerkt Zeilen verwirft
   - Eine Schemafunktion, die ein Feld mit IntegerType statt DoubleType zurückgibt
   - Eine Funktion zum Umbenennen von Spalten, die Namen in Klein- statt in Großbuchstaben umwandelt

3. **Welche der folgenden Aussagen beschreibt AM BESTEN, warum für Mapping-Operationen eine Funktion, die einen PySpark-Column-Ausdruck zurückgibt, einer Funktion vorzuziehen ist, die einen transformierten DataFrame zurückgibt?**

   - Column-Ausdrücke behandeln Nullwerte automatisch ohne zusätzliche Logik
   - Column-Ausdrücke werden sofort (eager) ausgeführt, was Transformationen beschleunigt
   - Von Funktionen zurückgegebene DataFrames können nicht in Delta-Tabellen geschrieben werden
   - Column-Ausdrücke sind kombinierbar und werden verzögert (lazy) ausgewertet, wodurch sie in withColumn- oder select-Aufrufen wiederverwendbar sind

4. sdfg

5. sdfgd

6. dsfg

7. dsfg

8. dfg

9. sdfg

10. dfg

11. dfg

12. ddfhg

13. sdfg

14. dfg

15. dfg

16. dfg

17. dfg

18. dfg

19. dfg

20. dfg

