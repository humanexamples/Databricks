# Pipeline-Modi: Triggered vs. Continuous

Referenz zu den beiden Pipeline-Ausführungsmodi, basierend auf `https://docs.databricks.com/aws/en/ldp/concepts/pipeline-mode` (wörtlich per Azure/Microsoft-Learn-Spiegelseite gegengeprüft).

## Abschnittsübersicht

1. [Grundprinzip](#grundprinzip)
2. [Triggered Pipeline Mode](#triggered)
3. [Continuous Pipeline Mode](#continuous)
4. [Vergleichstabelle](#vergleichstabelle)
5. [Kosten-Latenz-Abwägung](#abwaegung)
6. [Empfehlung: Continuous Job statt eingebautem Continuous-Modus](#continuous-job)
7. [Trigger-Intervall für Continuous-Pipelines](#trigger-intervall)
8. [Quellen](#quellen)

---

## <a id="grundprinzip">1. Grundprinzip</a>



Der Triggered-Modus aktualisiert die verfügbaren Daten und stoppt anschließend, während der Continuous-Modus Tabellen fortlaufend aktuell hält, sobald neue Daten eintreffen. Für Workloads, die Latenzen im Millisekundenbereich benötigen, verweist die Doku auf den separaten "Real-Time Mode".

Der Pipeline-Modus ist unabhängig vom Typ der berechneten Tabelle — sowohl Materialized Views als auch Streaming Tables können in beiden Pipeline-Modi aktualisiert werden.

**Hinweis aus der Doku:** Refresh-Operationen für standalone Materialized Views und Streaming Tables laufen immer im Triggered Pipeline Mode.

## <a id="triggered">2. Triggered Pipeline Mode</a>

Im **Triggered**-Modus stoppt das System, nachdem alle Tabellen basierend auf den zum Update-Start verfügbaren Daten aktualisiert wurden.

## <a id="continuous">3. Continuous Pipeline Mode</a>

Im **Continuous**-Modus verarbeitet die Pipeline neue Daten, sobald sie in den Datenquellen eintreffen, um alle Tabellen der Pipeline fortlaufend aktuell zu halten.

Um unnötige Verarbeitung im Continuous-Modus zu vermeiden, überwachen Pipelines automatisch die abhängigen Delta-Tabellen und führen ein Update nur dann durch, wenn sich der Inhalt dieser abhängigen Tabellen tatsächlich geändert hat.

## <a id="vergleichstabelle">4. Vergleichstabelle</a>

| Schlüsselfrage | Triggered | Continuous |
|---|---|---|
| Wann stoppt das Update? | Automatisch, sobald abgeschlossen. | Läuft fortlaufend, bis manuell gestoppt. |
| Welche Daten werden verarbeitet? | Daten, die beim Start des Updates verfügbar sind. | Alle Daten, sobald sie an den konfigurierten Quellen eintreffen. |
| Für welche Aktualitätsanforderungen am besten geeignet? | Datenupdates alle 10 Minuten, stündlich oder täglich. | Datenupdates alle 10 Sekunden bis wenige Minuten gewünscht. |

## <a id="abwaegung">5. Kosten-Latenz-Abwägung</a>

Triggered Pipelines können Ressourcenverbrauch und Kosten senken, da der Cluster nur so lange läuft, wie zur Aktualisierung der Pipeline nötig. Allerdings werden neue Daten erst verarbeitet, wenn die Pipeline erneut ausgelöst wird. Continuous Pipelines benötigen einen dauerhaft laufenden Cluster, was teurer ist, aber die Verarbeitungslatenz reduziert.

## <a id="continuous-job">6. Empfehlung: Continuous Job statt eingebautem Continuous-Modus</a>

Databricks empfiehlt, **Continuous Pipelines** über einen **Continuous Job** auszuführen, statt die Einstellung **Pipeline Mode** direkt auf Continuous zu setzen. Orchestriert ein Continuous Job eine Pipeline, übernimmt der Job die Steuerung des Ausführungs-Lebenszyklus und schaltet zusätzliche Serverless-Performance-Modi frei (etwa den "Standard Mode"), die der eingebaute Continuous-Modus der Pipeline nicht unterstützt.

**Wichtiger Hinweis:** Job-Orchestrierung steuert den Ausführungsmodus nur für Lakeflow-Pipelines. Standalone Materialized Views und Streaming Tables laufen unabhängig von der Job-Orchestrierung immer im Triggered-Modus.

Orchestriert ein Job eine Pipeline, bestimmt der Job den Ausführungsmodus und hat Vorrang vor der Einstellung **Pipeline Mode** der Pipeline: Ein Continuous Job führt seine Pipeline fortlaufend aus, selbst wenn deren **Pipeline Mode** auf Triggered steht; ein Triggered- oder geplanter Job führt seine Pipeline dagegen als einzelnes Update aus, selbst wenn deren **Pipeline Mode** auf Continuous steht.

Da der Job die Pipeline-Modus-Einstellung überschreibt, empfiehlt die Doku, den **Pipeline Mode** der Pipeline auf Triggered (den Standardwert) zu setzen, wenn sie in einen Continuous Job eingebettet wird — das vermeidet unerwartetes Verhalten, falls die Pipeline außerhalb des Jobs läuft.

## <a id="trigger-intervall">7. Trigger-Intervall für Continuous-Pipelines</a>

Der eingebaute Continuous-Modus der Pipeline wird laut Doku nicht entfernt, doch Databricks rät für neue Pipelines vom Muster "eingebauter Continuous-Modus" ab und empfiehlt stattdessen das Continuous-Job-Muster. Zum Wechseln zwischen Triggered und Continuous dient die Einstellung **Pipeline Mode** in den Pipeline-Einstellungen.

Bei der Konfiguration im Continuous-Modus lässt sich zusätzlich ein Trigger-Intervall festlegen, das steuert, wie häufig die Pipeline ein Update für jeden Flow startet. Dieses Trigger-Intervall gilt unabhängig davon, ob die Pipeline über ihre eigene **Pipeline Mode**-Einstellung oder über einen Continuous Job im Continuous-Modus läuft.

Über die Konfiguration `pipelines.trigger.interval` lässt sich das Trigger-Intervall für einen einzelnen Flow (der eine Tabelle aktualisiert) oder für die gesamte Pipeline steuern. Da eine Triggered Pipeline jede Tabelle nur einmal verarbeitet, wird `pipelines.trigger.interval` ausschließlich bei Continuous Pipelines verwendet. Databricks empfiehlt, den Wert auf einzelnen Tabellen zu setzen, da Streaming- und Batch-Queries unterschiedliche Standardwerte haben. Ein Wert auf Pipeline-Ebene sollte nur gesetzt werden, wenn die Verarbeitung für den gesamten Pipeline-Graphen einheitlich gesteuert werden muss.

**Ungeklärt:** Die konkreten Default-Werte von `pipelines.trigger.interval` je Flow-Typ (Streaming vs. Batch) wurden auf dieser Seite nicht genannt — die Doku verweist dafür explizit auf eine gesonderte Property-Referenzseite ("Pipelines trigger interval").

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/concepts/pipeline-mode
- https://learn.microsoft.com/en-us/azure/databricks/ldp/concepts/pipeline-mode (Gegenprüfung, wörtlich)
