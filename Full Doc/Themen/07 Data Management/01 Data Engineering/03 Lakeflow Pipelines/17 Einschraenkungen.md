# Einschränkungen von Lakeflow-Pipelines

Referenz zu den dokumentierten Einschränkungen von Lakeflow-Pipelines, basierend auf `https://docs.databricks.com/aws/en/ldp/limitations` (wörtlich per Azure/Microsoft-Learn-Spiegelseite `learn.microsoft.com/en-us/azure/databricks/ldp/limitations` gegengeprüft — beide Seiten liefern identischen Text).

## Abschnittsübersicht

1. [Nebenläufigkeit: Concurrent Pipeline Updates](#nebenlaeufigkeit)
2. [Grenzen für Quell-Dateien und -Ordner](#quelldateien)
3. [Datasets als Ziel nur einer einzigen Operation](#dataset-ziel)
4. [Identity-Columns](#identity-columns)
5. [Zugriff durch externe Systeme](#externer-zugriff)
6. [Unity-Catalog-Compute-Anforderungen](#uc-compute)
7. [Time Travel](#time-travel)
8. [`pivot()`-Funktion nicht unterstützt](#pivot)
9. [Ressourcen-Quoten](#ressourcen-quoten)
10. [Quellen](#quellen)

---

## <a id="nebenlaeufigkeit">1. Nebenläufigkeit: Concurrent Pipeline Updates</a>

Ein Databricks-Workspace ist auf **1000 gleichzeitige Pipeline-Updates** begrenzt. Die Anzahl der Datasets, die eine einzelne Pipeline enthalten kann, wird durch die Pipeline-Konfiguration und die Komplexität des Workloads bestimmt.

## <a id="quelldateien">2. Grenzen für Quell-Dateien und -Ordner</a>

Die Konfiguration einer Pipeline enthält Referenzen auf Quell-Dateien und -Ordner:

- Referenziert die Konfiguration **ausschließlich einzelne** Notebooks oder Dateien, liegt das Limit pro Pipeline bei **100 Quell-Dateien**.
- Enthält die Konfiguration **Ordner**, können bis zu **50 Quell-Einträge** (Dateien oder Ordner) referenziert werden.
  - Das Referenzieren eines Ordners referenziert indirekt auch die darin enthaltenen Dateien. In diesem Fall liegt das Limit für die Anzahl der (direkt oder indirekt) referenzierten Dateien bei **1000**.

Werden mehr als 100 Quell-Dateien benötigt, sollten diese in Ordnern organisiert werden (siehe "Pipeline Asset Browser" im Lakeflow-Pipelines-Editor).

## <a id="dataset-ziel">3. Datasets als Ziel nur einer einzigen Operation</a>

Pipeline-Datasets können nur einmal definiert werden. Deshalb können sie über alle Pipelines hinweg nur das Ziel einer einzigen Operation sein. Die Ausnahme bilden Streaming Tables mit Append-Flow-Verarbeitung: Diese erlauben es, aus mehreren Streaming-Quellen in dieselbe Streaming Table zu schreiben (siehe "Flows.md", Abschnitt Append-Flows).

## <a id="identity-columns">4. Identity-Columns</a>

Identity-Columns unterliegen folgenden Einschränkungen:

- Identity-Columns werden bei Tabellen, die Ziel einer **AUTO-CDC**-Verarbeitung sind, nicht unterstützt.
- Identity-Columns können bei Updates einer Materialized View neu berechnet werden. Databricks empfiehlt daher, Identity-Columns in Pipelines nur bei Streaming Tables zu verwenden.

## <a id="externer-zugriff">5. Zugriff durch externe Systeme</a>

Standardmäßig können Materialized Views und Streaming Tables nur von Databricks-Clients und -Anwendungen abgerufen werden. Um sie für externe Systeme zugänglich zu machen, verweist die Doku auf eine separate Seite ("Access materialized views and streaming tables using external systems").

## <a id="uc-compute">6. Unity-Catalog-Compute-Anforderungen</a>

Für das Compute, das zur Ausführung und Abfrage von Unity-Catalog-Pipelines benötigt wird, gelten Einschränkungen. Die Doku verweist dafür auf die "Requirements" für Pipelines, die nach Unity Catalog publizieren.

**Ungeklärt:** Die konkreten Compute-Anforderungen selbst wurden auf der Limitations-Seite nicht ausgeführt, sondern nur referenziert — Details finden sich laut Doku auf der Unity-Catalog-spezifischen Unterseite.

## <a id="time-travel">7. Time Travel</a>

Delta-Lake-Time-Travel-Abfragen werden **nur bei Streaming Tables** unterstützt und sind bei Materialized Views **nicht** unterstützt.

## <a id="pivot">8. `pivot()`-Funktion nicht unterstützt</a>

Die `pivot()`-Funktion wird nicht unterstützt. Die `pivot`-Operation in Spark erfordert das eager (vorzeitige) Laden der Eingabedaten, um das Ausgabeschema zu berechnen — diese Fähigkeit wird in Pipelines nicht unterstützt.

## <a id="ressourcen-quoten">9. Ressourcen-Quoten</a>

Für Ressourcen-Quoten von Lakeflow-Pipelines verweist die Doku auf eine separate Seite ("Resource limits").

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/limitations
- https://learn.microsoft.com/en-us/azure/databricks/ldp/limitations (Gegenprüfung, wörtlich identisch)
