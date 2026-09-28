# Datasets über Lakeflow Pipelines hinweg organisieren

Dieses Dokument behandelt die Frage, welche Tabellen innerhalb einer einzigen Pipeline gruppiert werden sollten und wann eine Aufteilung auf mehrere Pipelines sinnvoll ist. Der vollständige Seiteninhalt (Azure-Spiegelseite) konnte wörtlich abgerufen werden.

## Abschnittsübersicht

1. [Grundproblem](#grundproblem)
2. [Die Parallelitätsgrenze kennen](#parallelitaetsgrenze)
3. [Was in dieselbe Pipeline gehört](#gleiche-pipeline)
4. [Was in eine separate Pipeline gehört](#separate-pipeline)
5. [Praktische Faustregel](#faustregel)
6. [Einschränkungen](#einschraenkungen)
7. [Quellen](#quellen)

---

## <a id="grundproblem">1. Grundproblem</a>

Lakeflow-Pipelines können ein bis mehrere hundert Datasets in einer einzigen Pipeline verarbeiten. Eine Entscheidung, die in Tutorials nie auftaucht, wird in echten Deployments wichtig: Welche Tabellen gehören in dieselbe Pipeline, und wann sollte etwas eine eigene Pipeline sein? Diese Entscheidung falsch zu treffen, ist laut Doku eine der häufigsten Arten, wie sich Teams selbst in eine Ecke manövrieren. Der klassische Fehlschlag ist, "everything" in eine einzige riesige Pipeline zu packen und später auf Skalierungs-, Nebenläufigkeits- und Blast-Radius-Probleme zu stoßen, die sich nur schwer rückgängig machen lassen.

Es gibt keine einzelne richtige Antwort, aber klare Kräfte, die in jede Richtung ziehen — sowie eine harte Beschränkung, die man vor dem Design kennen sollte.

## <a id="parallelitaetsgrenze">2. Die Parallelitätsgrenze kennen</a>

**"A single triggered pipeline update runs at most 16 dataset updates in parallel."** — Ein einzelnes getriggertes Pipeline-Update führt maximal 16 Dataset-Updates parallel aus. Dies ist die häufigste Überraschung für Teams, die alles in eine Pipeline packen: Sobald mehr als etwa 16 Datasets vorhanden sind, die andernfalls gleichzeitig laufen könnten, reihen sich die zusätzlichen hinter den ersten 16 ein, statt parallel zu laufen — die Gesamtdauer des Updates verlängert sich dadurch unnötig, obwohl Compute-Kapazität verfügbar wäre. Wer Dutzende unabhängiger Datasets hat und auf die Wanduhrzeit des Updates Wert legt, hat allein darin einen Grund, diese nicht alle in eine Pipeline zu quetschen.

## <a id="gleiche-pipeline">3. Was in dieselbe Pipeline gehört</a>

Datasets sollten zusammengehalten werden, wenn sie Struktur oder Zeitplanung teilen:

- Datasets, die eine Abhängigkeitskette oder eine logische Domäne bilden — etwa die Bronze-, Silber- und Gold-Tabellen für Bestellungen. Einen zusammenhängenden gerichteten azyklischen Graphen (DAG) beisammen zu halten, erlaubt es der Pipeline, ihn als kohärente Einheit zu planen, zu checkpointen und Full-Refresh durchzuführen, und hält die Lineage lesbar.
- Datasets, die dieselbe Frische-Anforderung und Ausführungskadenz teilen — Dinge, die zusammen, auf demselben Trigger, innerhalb derselben Transaktionsgrenze aktualisiert werden sollten.
- Datasets, die in Summe klein genug sind, dass der gesamte Graph bequem unter der Parallelitätsgrenze bleibt und in akzeptabler Zeit refresht.

## <a id="separate-pipeline">4. Was in eine separate Pipeline gehört</a>

Datasets sollten getrennt werden, wenn sie sich in Ownership, Layer oder Latenz unterscheiden:

- **Unterschiedliche Domänen oder Teams.** Getrennte Ownership sollte üblicherweise auch getrennte Pipelines bedeuten, damit die Änderung oder der Fehlschlag eines Teams nicht das andere blockiert.
- **Layer, die unabhängig skaliert oder geplant werden sollen.** Eine weithin empfohlene Aufteilung ist, Ingestion (Bronze) von Transformation (Silber und Gold) in getrennte Pipelines zu trennen, damit eine langsame oder fehlschlagende Ingestion die Transformation nicht aufhält und jede Pipeline ihre Compute-Größe an eigene Bedürfnisse anpassen kann.
- **Unterschiedliche Latenzprofile.** Ein kontinuierlicher Low-Latency-Stream sollte sich keine Pipeline mit einem einmal täglichen Batch-Aggregat teilen.
- **Datasets, die über die Parallelitätsgrenze hinausgehen** und andernfalls in eine Warteschlange geraten würden.

Um eine Gruppe von Datasets isoliert auszuführen, kommt eine Standalone Pipeline infrage (siehe "15 Databricks SQL fuer LDP/").

## <a id="faustregel">5. Praktische Faustregel</a>

Weder standardmäßig eine einzige monolithische Pipeline noch jede Tabelle in eine eigene Pipeline zersplittern. Gruppierung nach *Domäne + geteilte Kadenz + Abhängigkeit*, Aufteilung an den Grenzen *Ownership, Layer und Latenz* — und die Anzahl unabhängig aktualisierbarer Datasets pro Pipeline bequem unter der Parallelitätsgrenze halten. Im Zweifel sind mehrere mittelgroße, domänenorientierte Pipelines einer einzigen riesigen Pipeline vorzuziehen. Es ist deutlich einfacher, zwei kleine Pipelines später zusammenzuführen, als einen bereits produktiven Monolithen aufzuteilen.

## <a id="einschraenkungen">6. Einschränkungen</a>

- **Ein einzelnes getriggertes Update führt maximal 16 Dataset-Updates parallel aus.** Datasets über dieser Grenze reihen sich ein, statt gleichzeitig zu laufen — eine Pipeline mit Dutzenden unabhängiger Datasets kann daher länger für ein Update brauchen, selbst wenn Compute verfügbar ist.
- **Eine Aufteilung auf mehrere Pipelines kostet etwas End-to-End-Sichtbarkeit.** Bei einer Aufteilung sollten die System-Tabellen (`system.lakeflow.pipelines`, `system.lakeflow.job_run_timeline`) genutzt und die Teile über einen Lakeflow Job orchestriert werden, um weiterhin eine einzelne End-to-End-Sicht auf den Gesamtablauf zu erhalten.

---

## <a id="quellen">7. Quellen</a>

1. Organize datasets across Lakeflow pipelines (AWS): https://docs.databricks.com/aws/en/ldp/best-practices/organize-datasets
2. Organize datasets across Lakeflow pipelines (Azure-Spiegelseite, für vollständige wörtliche Wiedergabe inkl. Parallelitätsgrenze genutzt): https://learn.microsoft.com/en-us/azure/databricks/ldp/best-practices/organize-datasets
