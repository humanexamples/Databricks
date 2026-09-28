# Refresh-Semantik

Referenz zur Refresh-Semantik von Lakeflow-Pipelines, basierend auf `https://docs.databricks.com/aws/en/ldp/concepts/refresh`.

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Default Refresh](#default-refresh)
3. [Full Refresh](#full-refresh)
4. [Reset Checkpoints](#reset-checkpoints)
5. [Zentraler Unterschied: Streaming Tables vs. Materialized Views](#zentraler-unterschied)
6. [Quellen](#quellen)

---

## <a id="ueberblick">1. Überblick</a>

Läuft ein Pipeline-Update, "aktualisiert es die in der Pipeline definierten Materialized Views und Streaming Tables, sodass deren Ergebnisse den aktuellen Zustand der Quelldaten widerspiegeln." Die Doku unterscheidet drei Refresh-Arten.

## <a id="default-refresh">2. Default Refresh</a>

Beim Standard-Refresh verarbeiten Streaming Tables nur neue Datensätze seit dem letzten Update. Materialized Views versuchen entweder ein inkrementelles Refresh oder führen eine vollständige Neuberechnung durch. Auf Serverless-Pipelines verwendet das System dafür ein Kostenmodell, um die effizientere Methode auszuwählen.

## <a id="full-refresh">3. Full Refresh</a>

Ein Full Refresh "verarbeitet alle Datensätze aus den Quelldaten erneut durch die Logik, die das Dataset definiert." Bei Streaming Tables wird dabei die Tabelle geleert (truncate), die Checkpoints werden gelöscht, und alles wird neu verarbeitet. Die Doku empfiehlt, ein Full Refresh "nur dann auszuführen, wenn nötig, etwa wenn eine Definitions- oder Schema-Änderung nicht kompatibel ist."

## <a id="reset-checkpoints">4. Reset Checkpoints</a>

Reset Checkpoints ist ausschließlich für Streaming Tables verfügbar. Dieser Ansatz "löscht die Streaming-Checkpoints für ausgewählte Flows, ohne die bereits in die Streaming Table geschriebenen Daten zu löschen, und verarbeitet anschließend alle Datensätze aus der Quelle über diese Flows erneut."

## <a id="zentraler-unterschied">5. Zentraler Unterschied: Streaming Tables vs. Materialized Views</a>

Ein wesentlicher Unterschied: Streaming Tables priorisieren beim Standard-Refresh "geringere Zeit- und Ressourcenkosten" gegenüber Vollständigkeit, während Materialized Views "volle Korrektheit" bewahren, indem sie automatisch zwischen inkrementeller und vollständiger Neuberechnung anhand einer Kostenanalyse wählen.

**Ungeklärt:** Die genauen Details des von Serverless-Pipelines verwendeten Kostenmodells (welche Faktoren konkret einfließen, ab welcher Schwelle ein Full Refresh statt eines inkrementellen Refreshs gewählt wird) wurden auf dieser Seite nicht im Detail ausgeführt.

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/concepts/refresh
