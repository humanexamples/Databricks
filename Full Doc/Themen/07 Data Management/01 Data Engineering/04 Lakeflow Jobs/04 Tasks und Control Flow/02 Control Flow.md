# Kontrollfluss von Tasks steuern

Viele Jobs bestehen aus mehreren aufeinander aufbauenden Tasks. Die Ausführungsreihenfolge wird über Abhängigkeiten gesteuert — sequenziell oder parallel. Fortgeschrittene Steuerung umfasst Verzweigungen mit bedingten Tasks, Fehlerbehandlung und Aufräumoperationen.

## Mechanismen im Überblick

- **Retries:** legen fest, wie oft ein fehlgeschlagener Task erneut ausgeführt wird. Viele Fehler sind transient und lösen sich durch einen Neustart. Manche Databricks-Features (z. B. Schema Evolution mit Structured Streaming) setzen voraus, dass Jobs mit Retries laufen, um die Umgebung zurückzusetzen und den Workflow fortzusetzen. Nicht jede Job-Konfiguration unterstützt Task-Retries; Continuous-Jobs nutzen automatisch Exponential-Backoff-Retries.
- **Run-if-Bedingungen:** der Task-Typ **Run if** erlaubt bedingte Ausführung nachgelagerter Tasks anhand des Ergebnisses vorgelagerter Tasks — unterstützte Bedingungen: All succeeded, At least one succeeded, None failed, All done, At least one failed, All failed (siehe `Bedingte Ausfuehrung (Run If).md`).
- **If/else-Tasks:** bedingte Verzweigung anhand berechneter Werte. Lakeflow Jobs unterstützt Task Values, die Berechnungsergebnisse oder Zustand an die Job-Umgebung zurückgeben; Bedingungen können Task Values, Job-Parameter oder dynamische Werte referenzieren. Unterstützte Operatoren: `==`, `!=`, `>`, `>=`, `<`, `<=` (siehe `If-Else Task.md`).
- **For-each-Tasks:** führt einen anderen Task iterativ mit unterschiedlichen Parametern je Durchlauf aus — benötigt einen `For each`-Task plus einen verschachtelten Standard-Task (siehe `For-Each Task.md`).
- **Deaktivierte Tasks:** übersprungen zur Laufzeit, Konfiguration/Historie bleiben erhalten; Lakeflow Jobs wertet die Run-if-Bedingungen nachgelagerter Tasks entsprechend aus (siehe `Deaktivierte Tasks.md`).

## Gängige Workload-Muster (Kursbegriffe, nicht dokuverifiziert)

Aus privatem Kursmaterial übernommen — drei wiederkehrende DAG-Formen, keine offiziellen Databricks-Begriffe, aber eine nützliche gedankliche Einordnung:

- **Sequence:** lineare Kette von Tasks, typisch für Transformationsschritte oder die Medallion-Architektur (Bronze → Silver → Gold).
- **Funnel:** mehrere Quell-Tasks laufen in einen gemeinsamen nachgelagerten Task zusammen (Fan-in) — typisch beim Einsammeln mehrerer Datenquellen.
- **Fan-out:** ein einzelner Quell-Task verzweigt sich sternförmig in mehrere nachgelagerte Tasks — typisch bei der Verteilung einer Quelle an mehrere Ziele.

## Quelle

- https://docs.databricks.com/aws/en/jobs/control-flow
