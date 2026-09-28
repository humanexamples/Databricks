# Notebook Workflows als Testing-Orchestrierung (Legacy-Beispiel)

Die angefragte Legacy-Seite `_extras/notebooks/source/testing.html` war ein Beispiel-Notebook, das `dbutils.notebook.run()` zur Orchestrierung mehrerer Test-Notebooks demonstrierte. Sie leitet inzwischen (Canonical-Link) auf die aktuelle Konzept-Seite „Notebook workflows" um — dieses Dokument fasst deren `dbutils.notebook.run()`/`exit()`-Mechanik zusammen, die dem alten Testing-Beispiel zugrunde lag. Teil der [Testing](../Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Herkunft dieser Seite](#herkunft)
2. [Kernkonzept: `dbutils.notebook.run()`](#run)
3. [Parameter und Rückgabewerte](#parameter)
4. [Strukturierte Datenübergabe](#strukturiert)
5. [Fehlerbehandlung](#fehler)
6. [Bezug zu Testing und Nebenläufigkeit](#testing-bezug)
7. [Quelle](#quelle)

---

## <a id="herkunft">1. Herkunft dieser Seite</a>

Die ursprünglich angefragte URL `https://docs.databricks.com/_extras/notebooks/source/testing.html` ist eine alte, statisch exportierte Notebook-Seite ohne direkt extrahierbaren Inhalt (client-seitig gerendert). Ihr `<link rel="canonical">`-Tag verweist auf `https://docs.databricks.com/en/notebooks/notebook-workflows.html` — die aktuelle Dokumentationsseite zu Notebook Workflows. Dieses frühere Testing-Beispiel demonstrierte vermutlich ein „Driver-Notebook", das mehrere Test-Notebooks über `dbutils.notebook.run()` ausführt und deren Erfolg/Fehlschlag aggregiert — ein Muster, das im Blogartikel „Automate Deployment and Testing with Databricks Notebooks and MLflow" (siehe [05 Andere Themen/05 Blog - MLOps, DataOps und KI-gestuetzte Entwicklung.md](../05%20Andere%20Themen/05%20Blog%20-%20MLOps%2C%20DataOps%20und%20KI-gestuetzte%20Entwicklung.md)) in modernisierter Form beschrieben wird.

## <a id="run">2. Kernkonzept: `dbutils.notebook.run()`</a>

Ermöglicht Orchestrierung, indem „ein neuer, ephemerer Job gestartet wird, der sofort läuft" — erlaubt die Parameterübergabe zwischen Notebooks sowie den Rückfluss von Rückgabewerten.

**Signatur:** `run(path: String, timeout_seconds: int, arguments: Map): String`

Der Timeout-Parameter steuert die Ausführungsdauer; `0` bedeutet unbegrenzt. Der Aufruf wirft eine Exception, wenn die Zeitspanne überschritten wird. Hinweis: „Ist Databricks länger als 10 Minuten nicht erreichbar, schlägt der Notebook-Run fehl" — unabhängig von den Timeout-Einstellungen.

## <a id="parameter">3. Parameter und Rückgabewerte</a>

Sowohl Argumente als auch Rückgabewerte müssen Strings sein. Der `arguments`-Parameter setzt Widget-Werte im Ziel-Notebook — `("A": "B")` lässt Widget A den Wert „B" abrufen. Wichtig: „Der `arguments`-Parameter akzeptiert nur lateinische Zeichen (ASCII-Zeichensatz). Nicht-ASCII-Zeichen führen zu einem Fehler."

Rückgabewerte nutzen `dbutils.notebook.exit()`. „Es lässt sich nur ein einzelner String über `dbutils.notebook.exit()` zurückgeben" — strukturierte Datenübergabe wird über Zwischenspeicher-Mechanismen ermöglicht.

## <a id="strukturiert">4. Strukturierte Datenübergabe</a>

**Temporary-Views-Ansatz:** Das aufgerufene Notebook erstellt eine Global Temporary View und beendet sich mit deren Namen. Das aufrufende Notebook ruft den Namen ab und greift über `spark.sql.globalTempDatabase` auf die Daten zu.

**DBFS-Storage-Ansatz:** Für größere Datensätze schreibt das aufgerufene Notebook Ergebnisse an einen DBFS-Pfad und beendet sich mit diesem Pfad. Das aufrufende Notebook lädt und zeigt den zurückgegebenen Pfad.

**JSON-Serialisierungs-Ansatz:** Mehrere Werte werden beim Exit zu einem JSON-String serialisiert und im aufrufenden Notebook deserialisiert.

## <a id="fehler">5. Fehlerbehandlung</a>

„Fehler werfen eine `WorkflowException`." Standard-Try-Catch-Konstrukte ermöglichen Retry-Logik über reguläre Scala- und Python-Kontrollflussmechanismen.

## <a id="testing-bezug">6. Bezug zu Testing und Nebenläufigkeit</a>

Die offizielle Doku erwähnt, dass frühere Dokumentationsversionen „dedizierte Testing-Notebooks enthielten, die Validierungsmuster demonstrierten." Mehrere Notebooks lassen sich gleichzeitig über „Standard-Scala- und Python-Konstrukte wie Threads" und Futures nebenläufig ausführen — die technische Grundlage für Driver-Notebook-Testmuster, bei denen mehrere Test-Notebooks parallel orchestriert werden.

## <a id="quelle">7. Quelle</a>

- https://docs.databricks.com/_extras/notebooks/source/testing.html (Legacy-Seite, Inhalt clientseitig gerendert und nicht extrahierbar; Canonical-Verweis genutzt)
- https://docs.databricks.com/en/notebooks/notebook-workflows.html (aktuelle Zielseite)

**Stand:** 2026-08-21.
