# Serverless vs. Classic Compute

Referenz zum Vergleich von Serverless- und Classic-Compute für Lakeflow-Pipelines, basierend auf `https://docs.databricks.com/aws/en/ldp/concepts/serverless-vs-classic-compute` (wörtlich per Azure/Microsoft-Learn-Spiegelseite gegengeprüft).

## Abschnittsübersicht

1. [Grundprinzip: Compute-Typ ist eine Pro-Pipeline-Einstellung](#grundprinzip)
2. [Empfehlung: Serverless für fast alle Pipelines](#empfehlung)
3. [Wichtiger Hinweis: Inkrementelles Refresh nur auf Serverless](#inkrementelles-refresh)
4. [Vergleichstabelle](#vergleichstabelle)
5. [Wann Serverless verwenden?](#wann-serverless)
6. [Wann Classic Compute verwenden?](#wann-classic)
7. [Compute-Typ einstellen](#einstellen)
8. [Quellen](#quellen)

---

## <a id="grundprinzip">1. Grundprinzip: Compute-Typ ist eine Pro-Pipeline-Einstellung</a>

Jede Lakeflow-Pipeline führt ihre Updates entweder auf Serverless- oder auf Classic-Compute aus. Der Compute-Typ ist eine Pro-Pipeline-Einstellung, die in den Pipeline-Einstellungen gewählt wird. Es handelt sich **nicht** um eine automatische Entscheidung: Eine Pipeline läuft nur dann auf Serverless-Compute, wenn die Einstellung **Serverless** aktiviert ist — andernfalls läuft sie auf Classic-Compute.

## <a id="empfehlung">2. Empfehlung: Serverless für fast alle Pipelines</a>

Databricks empfiehlt Serverless-Compute für nahezu alle Pipelines. Bei Serverless verwaltet Databricks die Infrastruktur: Es müssen keine Cluster dimensioniert, konfiguriert, abgesichert oder mit Berechtigungen versehen werden. Zusätzlich stehen Fähigkeiten zur Verfügung, die Classic Compute nicht bietet, etwa inkrementelles Refresh und vertikales Autoscaling. Bei Classic Compute liegt diese Infrastrukturverantwortung dagegen bei den Nutzenden.

Serverless unterstützt nahezu alles, was Classic Compute auch kann. Die Ausnahmen sind der Legacy-Hive-Metastore und bestimmte Netzwerkkonfigurationen. Für die meisten Pipelines bedeutet die Wahl von Classic Compute manuellen Mehraufwand, den Serverless andernfalls übernehmen würde.

## <a id="inkrementelles-refresh">3. Wichtiger Hinweis: Inkrementelles Refresh nur auf Serverless</a>

**Wichtig:** Inkrementelles Refresh für Materialized Views ist ausschließlich auf Serverless-Pipelines verfügbar. Materialized Views, die auf Classic Compute laufen, werden immer vollständig neu berechnet. Ist inkrementelles Refresh eine Anforderung für den jeweiligen Workload, muss Serverless-Compute verwendet werden.

## <a id="vergleichstabelle">4. Vergleichstabelle</a>

| Fähigkeit | Serverless | Classic |
|---|---|---|
| Infrastrukturverwaltung | Databricks verwaltet die gesamte Infrastruktur. Keine Cluster-Konfiguration nötig. | Cluster müssen konfiguriert werden, einschließlich Autoscaling, Instance-Typen und Cluster-Policies. |
| Inkrementelles Refresh für Materialized Views | Unterstützt. Materialized Views werden inkrementell aktualisiert, wann immer es kosteneffizient ist, um Compute-Kosten zu senken. | Nicht unterstützt. Materialized Views werden immer vollständig neu berechnet. |
| Autoscaling | Erweitertes Autoscaling, das sowohl horizontal (mehr Executors) als auch vertikal (größere Executors) skaliert. | Erweitertes Autoscaling, das horizontal skaliert. Instance-Typen werden selbst gewählt. |
| Stream Pipelining | Standardmäßig aktiviert. Microbatches laufen gleichzeitig, um Durchsatz und Latenz zu verbessern. | Nicht verfügbar. |
| Berechtigung zur Compute-Erstellung | Nicht erforderlich. Alle Workspace-Nutzer können standardmäßig Serverless-Pipelines ausführen. | Erforderlich. Nutzer benötigen uneingeschränkte Cluster-Erstellungsberechtigung oder Zugriff auf eine Compute-Policy. |
| Compute-Policies und Instance-Typen | Von Databricks verwaltet. Instance-Typen und Compute-Policy werden nicht selbst festgelegt. | Manuell: Eine Compute-Policy wird angewendet, Worker- und Driver-Instance-Typen werden selbst gewählt. |
| Unity Catalog | Verwendet immer Unity Catalog. | Kann Unity Catalog oder den Legacy-Hive-Metastore verwenden. |
| Kostenzuordnung | Benutzerdefinierte Tags über eine Serverless-Nutzungsrichtlinie (Usage Policy). | Benutzerdefinierte Tags direkt an der Pipeline. Tag-Daten müssen manuell mit Abrechnungsdaten verknüpft werden. |
| Update- und Wartungscluster | Von Databricks verwaltet. | Werden separat selbst konfiguriert. |
| Single-Node-Compute | Nicht nötig. Databricks dimensioniert das Compute automatisch passend zum Workload. | Wird für kleine oder nicht-verteilte Workloads selbst konfiguriert. |

## <a id="wann-serverless">5. Wann Serverless verwenden?</a>

Serverless-Compute wird für jede Pipeline empfohlen, die nicht auf eine der Classic-only-Einschränkungen (Abschnitt 6) trifft. Insbesondere ist Serverless die richtige Wahl, wenn:

- Databricks die Infrastruktur verwalten soll, einschließlich vertikalem Autoscaling und Instance-Auswahl, statt eigene Cluster zu konfigurieren und zu pflegen.
- Inkrementelles Refresh für Materialized Views gewünscht ist, um Refresh-Kosten zu senken.
- Workspace-Nutzer Pipelines ausführen sollen, ohne Cluster-Erstellungsberechtigungen zu benötigen.

Serverless-Pipelines erfordern einen Workspace mit aktiviertem Unity Catalog sowie eine Serverless-fähige Region.

## <a id="wann-classic">6. Wann Classic Compute verwenden?</a>

Da Serverless nahezu jeden Pipeline-Workload unterstützt, sollte Classic Compute nur verwendet werden, wenn Serverless die Pipeline überhaupt nicht ausführen kann:

- Die Tabellen verwenden den Legacy-Hive-Metastore statt Unity Catalog.
- Die Pipeline benötigt privates Networking, das Serverless nicht unterstützt.
- Die Pipeline läuft in einer Region, in der Serverless nicht verfügbar ist.

Bei Classic Compute müssen Compute-Policies, Instance-Typen, Single-Node-Compute sowie separate Update- und Wartungscluster selbst konfiguriert und gepflegt werden — Arbeit, die Serverless sonst übernimmt.

## <a id="einstellen">7. Compute-Typ einstellen</a>

Der Compute-Typ wird in den **Compute**-Einstellungen der Pipeline über die Einstellung **Serverless** (aktiviert/deaktiviert) gewählt. Neue Pipelines verwenden standardmäßig Serverless. Eine bestehende, mit Unity Catalog konfigurierte Pipeline kann ebenfalls zu Serverless konvertiert werden.

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/concepts/serverless-vs-classic-compute
- https://learn.microsoft.com/en-us/azure/databricks/ldp/concepts/serverless-vs-classic-compute (Gegenprüfung, wörtlich)
