## 1_1_Regulatory Compliance

Auch wenn dein Team möglicherweise nicht direkt mit Daten arbeitet, die personenbezogene Informationen (PII) enthalten, ist dein Unternehmen höchstwahrscheinlich von regulatorischen Compliance-Anforderungen betroffen – und zumindest von einigen seiner Datenpraktiken. Wir besprechen hier einige Ansätze, um sensible Informationen aus der Perspektive von PII sicher zu speichern. Viele dieser Praktiken lassen sich jedoch auf alle Daten anwenden, die bei einem Leak die Geschäftstätigkeit gefährden würden, nicht nur auf PII.

Beginnen wir mit einem kurzen Überblick über zwei der bekanntesten Leitregelwerke. Auch wenn sich die Details von GDPR und CCPA leicht unterscheiden, müssen die meisten Unternehmen Richtlinien umsetzen, die beiden entsprechen – vorausgesetzt, sie sind in der EU und in Kalifornien geschäftlich tätig. Die Definition einer globalen Richtlinie, die beide Regelwerke erfüllt, vereinfacht daher die Datenmanagement-Praktiken.

Grundsätzlich müssen Unternehmen in der Lage sein, die zu einem bestimmten Nutzer gehörenden Daten zu identifizieren und bei Bedarf zu exportieren, zu aktualisieren oder zu löschen. Diese Anfragen müssen zwar nicht sofort nach Eingang bearbeitet werden, aber zeitnah beantwortet werden. Audits, bei denen Unternehmen als nicht compliant befunden werden, können für das Unternehmen extrem teuer werden – und die Skalierung auf jeden einzelnen Nutzer treibt die Kosten weiter in die Höhe. Nach der GDPR können Unternehmen, die nicht innerhalb von 30 Tagen auf Anfragen reagieren, mit bis zu 4 % ihres Jahresumsatzes oder 20 Millionen Euro bestraft werden, je nachdem, welcher Betrag höher ist. Nach der CCPA gilt zusätzlich, dass du den Eingang innerhalb von 10 Werktagen bestätigen, die Anfrage innerhalb von 45 Tagen bearbeiten musst; Bußgelder liegen bei bis zu 2.500 $ pro Verstoß und 750 $ pro Verbraucher und Vorfall.

Überblick:

- EU = GDPR (General Data Protection Regulation / Datenschutz-Grundverordnung)
- USA = CCPA (California Consumer Privacy Act)
  - Vereinfachte Compliance-Anforderungen
  - Kunden darüber informieren, welche personenbezogenen Informationen erhoben werden
  - Personenbezogene Informationen auf Anfrage löschen, aktualisieren oder exportieren
  - Anfragen zeitnah bearbeiten (30 Tage)

------

Ohne die Transaktionsgarantien und die Qualitätsdurchsetzung von Delta wäre es ein enormer Compliance-Aufwand, personenbezogene Daten in Databricks abzulegen. Delta Lake und die Lakehouse-Architektur der Databricks Data Intelligence Platform insgesamt ermöglichen es, riesige Datenmengen effizient zu speichern und schnell abzufragen, wodurch die Gesamtzahl der Systeme reduziert wird, die Kopien der Nutzerdaten für analytische Workloads benötigen.

Mit der Durchsetzung von Datenqualität kannst du dem Problem begegnen, dass PII aufgrund von Schema-Abweichungen oder Eingabefehlern von Queries übersehen wird, da die Transaktionen garantieren, dass beim Löschen oder Aktualisieren von Datensätzen die Jobs vollständig erfolgreich sind. Delta-Transaktionslogs können genutzt werden, um diese Verarbeitung zu bestätigen.

Wie Databricks Compliance vereinfacht

- Reduziere die Anzahl der Kopien deiner PII
- Finde personenbezogene Informationen schnell
- Ändere, lösche oder exportiere Daten zuverlässig
- Integrierte Data-Skipping-Optimierungen (Z-Order) und Housekeeping veralteter/gelöschter Daten (VACUUM)
- Nutze Transaktionslogs für Auditing
