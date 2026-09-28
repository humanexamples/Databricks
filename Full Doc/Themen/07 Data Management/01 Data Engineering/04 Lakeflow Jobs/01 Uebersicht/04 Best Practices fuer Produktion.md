# Best Practices für Produktions-Jobs (Checkliste)

Bündelt Einzelfakten, die im Vault bereits an anderer Stelle detailliert dokumentiert sind, zu einer Checkliste für den Übergang von Entwicklung zu Produktion. Jeder Punkt verlinkt auf die Datei mit den Details.

## Compute & Kostenoptimierung

- [ ] **Job- oder Serverless-Compute statt All-Purpose/Interactive-Cluster** in Produktion einsetzen — Interactive Clusters sind für Ad-hoc-Analyse und Entwicklung gedacht, nicht für Produktionslasten (Kostenrisiko durch Leerlaufzeiten, Ressourcenkonkurrenz zwischen Nutzern). Details: `02 Job erstellen und konfigurieren/Classic Jobs.md`, `02 Job erstellen und konfigurieren/Serverless Jobs.md`.
- [ ] **Photon aktivieren** für schnellere und günstigere Ausführung — bei Serverless Compute standardmäßig aktiv. Details: `02 Job erstellen und konfigurieren/Serverless Jobs.md`.
- [ ] **Compute zwischen Tasks teilen**, wo sinnvoll, um Start-Latenz zu reduzieren (Abwägung gegen Leerlaufzeiten geteilten Computes). Details: `02 Job erstellen und konfigurieren/Compute fuer Jobs.md`.

## Orchestrierung & Modularität

- [ ] **Komplexe Pipelines in modulare Jobs zerlegen** (Master-Child-Pattern über Run-Job-Tasks) statt einen monolithischen Job zu bauen. Details: `04 Tasks und Control Flow/Modulares Job-Design.md`, `04 Tasks und Control Flow/Run-Job-Task.md`.
- [ ] **Multi-Task-Jobs** für parallele, skalierbare Ausführung nutzen.
- [ ] **Bedingte Logik** (Run If, If/Else, For Each) für reale, verzweigte Anwendungsfälle einsetzen. Details: `04 Tasks und Control Flow/Bedingte Ausfuehrung (Run If).md`, `04 Tasks und Control Flow/If-Else Task.md`, `04 Tasks und Control Flow/For-Each Task.md`.
- [ ] **Task-Anzahl pro Job begrenzt halten** (Hard Limit: 1.000 Tasks pro Job) — bei größerem Bedarf modular über mehrere Jobs verteilen. Details: `02 Job erstellen und konfigurieren/Grosse Jobs.md`.

## Monitoring & Governance

- [ ] **Service Principal statt persönlichem Account als Run-as-Identität** verwenden — verhindert Fehlschläge, wenn der Job-Ersteller den Workspace verlässt oder Rechte verliert. Details: `06 Berechtigungen und Monitoring/Privilegien.md`.
- [ ] **Benachrichtigungen für Fehlschläge, Verzögerungen und Abschlüsse** konfigurieren. Details: `06 Berechtigungen und Monitoring/Benachrichtigungen.md`.
- [ ] **Repair & Run statt vollständigem Neustart** nutzen, um Kosten und Zeit bei erneuten Läufen zu sparen — dabei auf Idempotenz der Tasks achten. Details: `06 Berechtigungen und Monitoring/Fehler beheben (Repair).md`.
- [ ] **Tasks parametrisieren** für Wiederverwendbarkeit und Flexibilität über Umgebungen hinweg. Details: `07 Parameter/Job-Parameter.md`, `07 Parameter/Task-Parameter.md`.

## Quelle

Struktur und Auswahl der Punkte basieren auf der Produktions-Best-Practices-Lektion des Kurses; die technischen Details sind bereits einzeln in den oben verlinkten Dateien gegen die offizielle Databricks-Dokumentation verifiziert.

Nicht-Databricks-Quelle: privates Kursmaterial —
`Kursmetrial_Databricks/2_Deploy Workloads with Lakeflow Jobs(DONE)/_Abschnitte/13 Lecture - Lakeflow Jobs in Production and Best Practices(DONE)/D. Best Practices.md`.
