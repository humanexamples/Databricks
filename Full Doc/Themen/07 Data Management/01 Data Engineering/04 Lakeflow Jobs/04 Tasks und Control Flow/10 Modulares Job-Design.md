# Modulares Job-Design (Master-Child-Pattern)

Diese Datei behandelt die **Architektur-Perspektive** auf den Run-Job-Task: wie und warum große Jobs in kleinere, unabhängige Jobs zerlegt werden. Die rein technische Konfiguration des Run-Job-Tasks (Dropdown, Parameter-Override, Verschachtelungsgrenzen) steht in `Run-Job-Task.md` im selben Ordner.

## Warum modularisieren?

Ein einzelner, monolithischer Job mit sehr vielen Tasks wird mit wachsender Größe schwer wartbar — Änderungen an einem Teilbereich erfordern Verständnis des gesamten DAGs, Teams stoßen sich gegenseitig bei parallelen Änderungen, und ein Fehler in einem Teilbereich kann den Überblick über den ganzen Job erschweren. Modulare Orchestrierung verwandelt einen solchen monolithischen Workflow in wartbare, wiederverwendbare Komponenten.

## Dekompositionsstrategie

Komplexe DAGs werden nach **fachlichen Einheiten (Business-Units)** zerlegt, nicht nach technischen Komponenten. Jedes Modul sollte eine in sich geschlossene Geschäftsfunktion abbilden, die unabhängig entwickelt, getestet und deployt werden kann — z. B. ein eigener Job pro Fachbereich oder Datendomäne statt ein Job pro technischem Schritt (Extract/Transform/Load quer über alle Domänen).

## Master-Child-Pattern

Ein **Master-Job** orchestriert mehrere **Child-Jobs** über **Run-Job-Tasks** — er ruft die Child-Jobs auf und koordiniert deren Reihenfolge/Abhängigkeiten, während die eigentliche fachliche Logik in den Child-Jobs steckt. Das ergibt eine klare Trennung von Koordination (Master) und Ausführung (Child), bei gleichzeitig erhaltener Gesamt-Workflow-Steuerung.

## Vorteile

- **Maintainability:** Kleinere Jobs sind leichter zu verstehen, zu ändern und zu debuggen als ein großer monolithischer Job.
- **Reusability:** Child-Jobs lassen sich in mehreren Master-Workflows wiederverwenden.
- **Team-Collaboration:** Unterschiedliche Teams können unterschiedliche Module eigenständig verantworten und trotzdem am Gesamt-Workflow mitwirken.
- **Unabhängiges Testen:** Einzelne Module lassen sich isoliert testen — das verbessert die Qualität und senkt das Deployment-Risiko.

Siehe auch `01 Uebersicht/Best Practices fuer Produktion.md`: Der 1.000-Task-Limit pro Job (siehe `02 Job erstellen und konfigurieren/Grosse Jobs.md`) ist ein weiterer praktischer Grund, große Workflows über das Master-Child-Pattern statt als einzelnen Riesen-Job zu bauen.

## Eigenes Beispiel aus Kursmaterial

**Nicht-Databricks-Quelle: privates Kursmaterial** (`Kursmetrial_Databricks/2_Deploy Workloads with Lakeflow Jobs(DONE)/_Abschnitte/15 BONUS LAB - Modular Orchestration(DONE)/E. Adding New Tasks to the Master Job.md`).

Im Bonus-Lab „Modular Orchestration" wird ein Master-Job namens `Lab_15<Schema-Name>` gebaut, der zwei Zweige kombiniert:

- Ein direkter **Notebook-Task** (`creating_high_risk_borrower_gold_table`) innerhalb des Master-Jobs selbst, abhängig von zwei vorgelagerten Tasks.
- Ein **Run-Job-Task** (`creating_low_risk_borrower_gold_table`), der einen separaten, eigenständigen Job namens `Lab_15_Run_Job` als Child-Job aufruft — ebenfalls abhängig von vorgelagerten Tasks im Master-Job, mit „Run if dependencies: All Succeeded".

Damit kombiniert der Master-Job Inline-Tasks für einfache Schritte mit ausgelagerten Child-Jobs für Teile, die eigenständig wiederverwendbar oder von einem anderen Team gepflegt werden sollen — genau das Master-Child-Muster aus dem Abschnitt oben, an einem konkreten Beispiel.

## Quelle

Für Dekompositionsstrategie, Master-Child-Pattern und die genannten Vorteile existiert keine eigenständige Databricks-Dokumentationsseite — der Inhalt stammt aus der Produktions-Best-Practices-Lektion des Kurses.

Nicht-Databricks-Quelle: privates Kursmaterial —
`Kursmetrial_Databricks/2_Deploy Workloads with Lakeflow Jobs(DONE)/_Abschnitte/13 Lecture - Lakeflow Jobs in Production and Best Practices(DONE)/B. Modular Design.md` und
`.../15 BONUS LAB - Modular Orchestration(DONE)/E. Adding New Tasks to the Master Job.md`.

Technischer Hintergrund zum Run-Job-Task selbst: https://docs.databricks.com/aws/en/jobs/tasks/run-job (siehe `Run-Job-Task.md`).
