## 3_1_Pseudonymization & Anonymization

**PII Data Security**

Tauchen wir etwas tiefer in die Ansätze zur Pseudonymisierung und Anonymisierung ein.

Bevor wir beginnen, beachte jedoch: Mit ausreichend Zeit und Zugriff auf zusätzliche Daten ist es oft möglich, die meisten Daten wieder zu re-identifizieren – unabhängig vom verwendeten Ansatz. Das Anwenden von Pseudonymisierungs- und Anonymisierungstechniken auf Datensätze reduziert das Risiko der Datenexfiltration und verringert die Sichtbarkeit für die meisten Nutzer des Datensatzes, beseitigt das Risiko aber nicht vollständig.

Links siehst du ein Beispiel für Pseudonymisierung, bei dem „John Doe“ in der Spalte „Name“ zu „User-321“ geändert wurde. Dieser Schlüssel kann später auch genutzt werden, um Daten zu joinen. Falls du ihn löschen musst, lässt sich leicht sicherstellen, dass die Daten nicht an anderer Stelle kompromittiert werden.

Das Bild rechts ist ein Beispiel für Anonymisierung. Dies kann mit Dynamic Views umgesetzt werden – basierend auf den Berechtigungen, die du für eine Nutzergruppe oder ein Mitglied konfigurierst. Konkret kannst du bestimmte Informationen verbergen oder die Art ändern, wie du sie darstellst.

![image-20260710095158170](../../../../assets/image-20260710095158170.png)

------

### 3_1_1_Pseudonymization

Pseudonymisierung bedeutet, PII (personenbezogene Informationen) durch künstliche Identifikatoren oder Pseudonyme zu ersetzen. Beachte, dass auch pseudonymisierte Daten weiterhin als personenbezogene Informationen gelten.

Sie bietet Datenschutz auf Record-Ebene, indem sie aussagekräftige Werte durch generierte, aber ebenso eindeutige Werte wie Tokens, Hashes oder verschlüsselte Daten ersetzt.

Pseudonymisierung ermöglicht die Umkehrung des Prozesses und eine Re-Identifikation, wenn nötig.

Das Anwenden von Pseudonymisierung auf personenbezogene Daten kann die Risiken für die betroffenen Personen verringern und Controllern und Auftragsverarbeitern helfen, ihre Datenschutzanforderungen zu erfüllen. Data Scientists können weiterhin mit vollständigen Datensätzen arbeiten, aber nicht ohne Weiteres auf die tatsächlichen Werte zugreifen, die durch die zufälligen Zeichenketten repräsentiert werden, die sie analysieren.

Hier haben wir zwei Optionen: Hashing und Tokenisierung.

Überblick über den Ansatz

- Ersetzt den ursprünglichen Datenpunkt durch ein Pseudonym zur späteren Re-Identifikation
- Nur autorisierte Nutzer haben Zugriff auf Keys/Hash/Tabelle für die Re-Identifikation
- Schützt Datensätze auf Record-Ebene für Machine Learning
- Ein Pseudonym gilt nach der GDPR weiterhin als personenbezogene Daten
- Zwei wichtige Pseudonymisierungsmethoden: Hashing und Tokenisierung

------

**Methode: Hashing**

Das Anwenden einer Hash-Funktion auf personenbezogene Informationen ergibt eine zufällige Zeichenkette, die die Datenwerte für Endnutzer verschleiert.

Da Hashes deterministisch sind, kann das Hinzufügen einer zufälligen Zeichenkette am Anfang oder Ende eines Werts helfen, das Risiko zu verringern, dass ein Hash umgekehrt wird. Das nennt man Salting. Wenn du zum Beispiel eine bestimmte Sozialversicherungsnummer übergibst, kannst du sie – statt den Wert einfach an die Hash-Funktion zu übergeben – an eine zufällige Zeichenkette anhängen.

Wir können auch die Databricks Secrets API nutzen, um diese Salt-Werte zu speichern. Berechtigungen auf diese Secrets können nur Produktions-Jobs und autorisierten Nutzern gewährt werden, und so wird sichergestellt, dass Salt-Werte niemals im Klartext in den Notebooks angezeigt werden.

Hashing erfordert zwar keine vollständige Neuarchitektur eines Datensystems, führt aber zu einer gewissen Zunahme der Datengröße, da Hash-Werte mehr Bytes belegen als die Daten, die sie ersetzen. Beachte, dass verschiedene Hashes unterschiedlich viele Bytes verwenden. Manche Operationen sind weniger effizient, und bestimmte Daten müssen möglicherweise vor dem Hashing extrahiert werden, um die nachgelagerte Verarbeitung zu ermöglichen.

Wenn ein ML-Vorverarbeitungsschritt zum Beispiel die Domain aus einer E-Mail-Adresse vor der Vorhersage extrahiert, sollte die Domain in einer separaten Spalte vom Hash der vollständigen E-Mail-Adresse gespeichert und gehasht werden, damit die gehashte Domain weiterhin verwendet werden kann.

![image-20260710095655347](../../../../assets/image-20260710095655347.png)

------

**Methode: Tokenisierung**

Bei der Tokenisierung wandeln wir all unsere PII in Keys um und speichern unsere Werte schließlich in einer sicheren Lookup-Tabelle. Das ist langsam beim Schreiben, aber schnell beim Lesen – zum Teil, weil unsere de-identifizierten Daten in weniger Bytes gespeichert werden, üblicherweise indem nur der Key kodiert wird, mit dem wir die Daten in einem Long-Wert nachschlagen.

Um einen Datensatz zu tokenisieren, beginnen wir damit, alle Spalten zu erfassen und sie in ein Array von Structs umzuwandeln. Sobald alle Werte identifiziert wurden, wird jedem eindeutigen Wert ein Token zugewiesen. Diese Tokens werden als Keys für eindeutige Werte im Token Vault verwendet. Die für Endnutzer sichtbare Tabelle enthält nur diese Keys, üblicherweise als Long-Werte gespeichert.

![image-20260710101119873](../../../../assets/image-20260710101119873.png)

Zur Anonymisierung:

- Sie schützt ganze Datensätze, einschließlich Tabellen, Datenbanken und ganzer Datenkataloge, und verändert personenbezogene Daten unumkehrbar, um eine direkte oder indirekte Identifikation betroffener Personen zu verhindern. Das ist kein Problem, da Business-Analysten oft eher an Aggregationen und Trends interessiert sind, die sich auch ohne Einsicht in jeden einzelnen Datensatz verfolgen lassen.
- Anonymisierung verwendet in realen Szenarien typischerweise eine Kombination mehrerer Techniken, z. B. Data Suppression und Generalization.

Überblick über den Ansatz

- Schützt den **gesamten Datensatz** (Tabellen, Datenbanken oder ganze Datenkataloge), meist für Business Intelligence
- Personenbezogene Daten werden **unumkehrbar verändert**, sodass eine betroffene Person weder direkt noch indirekt identifiziert werden kann
- Üblicherweise wird in realen Szenarien eine Kombination mehrerer Techniken verwendet
- Zwei wichtige Anonymisierungsmethoden: **Data Suppression und Generalization**

------

**Methode: Data Suppression**

Bedingte Filter und dynamische Zugriffskontrollen können verwendet werden, um den Zugriff auf Spalten oder Zeilen von Daten zu entfernen, ohne die Fähigkeit der Analysten zu Reporting einzuschränken.

Aggregiertes Reporting für eine Region kann zum Beispiel weiterhin durchgeführt werden, ohne Zugriff auf vollständige Kundennamen oder Adressen. In manchen Fällen können demografische Daten leicht dazu verwendet werden, jemanden zu re-identifizieren. Selbst große Unternehmen können zum Beispiel nur eine begrenzte Anzahl von Kunden in einer kleinen Stadt haben – insbesondere, wenn es für eine bestimmte Geografie nur einen einzigen entsprechenden Datensatz gibt.

Aggregation verschleiert die zugrunde liegenden Daten nicht und kann sensible Daten möglicherweise über Reports und Dashboards offenlegen. Das Setzen eines Filters, um Zeilen mit niedrigen Counts für Gruppierungsspalten zu entfernen, kann helfen, einzelne Identitäten zu schützen. Databricks verfügt über dynamische Zugriffskontrollen, mit denen Daten auf Basis von Gruppenmitgliedschaften geschwärzt oder gefiltert werden können – das besprechen wir später im Kurs.

![image-20260710101722520](../../../../assets/image-20260710101722520.png)

------

**Methode: Generalization**

Generalization kann als eine Möglichkeit verstanden werden, Daten durch Entfernen von Genauigkeit zu anonymisieren. Verschiedene Datentypen unterstützen verschiedene Arten von Generalization, z. B. kategoriale Generalisierung, Binning, das Kürzen von IP-Adressen und Rundung.

- **Kategoriale Generalisierung**: Bei der kategorialen Generalisierung besteht das Ziel darin, Präzision aus den Daten zu entfernen. In diesem Beispiel gruppieren wir kleinere Städte in größere regionale Gruppen wie Bundesstaat oder Land, um sicherzustellen, dass kleinere Geografien nicht offengelegt werden.

  Wenn du zum Beispiel eine anonyme Feedback-Umfrage einreichst, sie am Ende aber nach Team ausgewertet wird und du die einzige Person warst, die in deinem Team geantwortet hat, sind all deine Informationen offengelegt.

  Stattdessen würdest du diesen Grad an Genauigkeit anonymisieren und dann nach Abteilung oder Organisation gruppieren. Und weil so viele Daten aus Social Media gesammelt und geleakt wurden, können selbst scheinbar harmlose Präferenzen genutzt werden, um Einzelpersonen leicht zu identifizieren und gezielt anzusprechen.

![image-20260710102115598](../../../../assets/image-20260710102115598.png)

- **Binning**: Beispiele für Binning wären das Erstellen einer 10-Jahres-Altersspanne, um altersbasierte Trends zu reporten, oder das Gruppieren von Gehältern in Bänder auf Basis veröffentlichter Standards. Reports und Dashboards können weiterhin aussagekräftige Erkenntnisse liefern, aber Analysten können das genaue Gehalt einer bestimmten Person nicht ermitteln.

  Fachwissen kann nützlich sein, wenn es darum geht, sinnvolle Gruppen zu definieren. Analysten können helfen zu definieren, wie Bins auf Basis der Reporting-Anforderungen berechnet werden. Je nach den Use Cases derjenigen, die deine Daten analysieren, solltest du also Gruppen erstellen, die sinnvoll sind. In manchen Fällen brauchst du diese Information vielleicht gar nicht. In anderen musst du dir einen anderen Weg überlegen, weil du diese Information einfach entfernst. Es ist also sehr spezifisch für die Zielgruppe und den Use Case.

![image-20260710102226024](../../../../assets/image-20260710102226024.png)

- **IP-Adressen kürzen**: Eine weitere Art der generalisierten Anonymisierungsmethode ist das Kürzen (Truncating), ein gängiger Use Case für IP-Adressen. Um eine IP-Adresse zu kürzen, können wir das letzte Byte davon nehmen und durch eine Null ersetzen, sodass sie im /24-CIDR-Bereich liegt.

![image-20260710102324853](../../../../assets/image-20260710102324853.png)

- **Rundung**: Viele Reports lassen sich sicher mit gerundeten Daten erstellen. Allgemeine Trends sind dieselben wie in ungerundeten Analysen, da Daten gleichmäßig auf- und abgerundet werden. Überlege dir also, welche Präzision nötig ist, um Erkenntnisse zu liefern. Wenn Trends im Tausenderbereich auftreten, gibt es keinen Grund, Präzision bis in den Zehnerbereich zu speichern oder offenzulegen.

  Ein einfaches Beispiel wäre, alles auf die nächsten 5 zu runden. Beachte, dass selbst bei Rundung die niedrigsten und höchsten Gruppen noch Ausreißer offenlegen können, die unterdrückt werden müssen.

![image-20260710102416511](../../../../assets/image-20260710102416511.png)
