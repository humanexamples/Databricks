# Externer Zugriff auf Materialized Views und Streaming Tables

Dieses Dokument fasst die Databricks-Referenzseite "Access materialized views and streaming tables using external systems" zusammen. Verifiziert per `WebFetch` gegen die AWS-Seite (`docs.databricks.com/aws/en/ldp/external-access`) und wörtlich vollständig extrahiert von der inhaltlich übereinstimmenden Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/external-access`).

## Abschnittsübersicht

1. [Ausgangslage](#ausgangslage)
2. [External Data Access](#external-data-access)
3. [Compatibility Mode](#compatibility-mode)
4. [Empfehlung](#empfehlung)
5. [Vergleichstabelle](#vergleich)
6. [Vertiefung: Delta UniForm als zugrunde liegender Mechanismus](#delta-uniform)
7. [Quellen](#quellen)

---

## <a id="ausgangslage">1. Ausgangslage</a>

Standardmäßig sind Materialized Views und Streaming Tables **nicht** von externen Systemen aus zugreifbar. Databricks stellt zwei Funktionen bereit, um Datasets für Delta-Lake- oder Iceberg-Clients verfügbar zu machen:

- **External Data Access**
- **Compatibility Mode**

## <a id="external-data-access">2. External Data Access</a>

Das Aktivieren von *External Data Access* für Pipeline-verwaltete und eigenständige ("standalone") Materialized Views und Streaming Tables veröffentlicht extern zugängliche Metadaten, die es Clients erlauben, die Unity-Catalog- oder Iceberg-REST-APIs zu nutzen — ohne eine vollständige Datenkopie oder einen separaten Refresh-Zeitplan zu benötigen. Clients müssen die Catalog-REST-APIs verwenden und entweder Delta Lake 4.0.0 oder höher oder die Iceberg-V3-Spezifikation unterstützen.

## <a id="compatibility-mode">3. Compatibility Mode</a>

*Compatibility Mode* befindet sich im **Public Preview**. Das Aktivieren von Compatibility Mode für ein Dataset erzeugt an einem gewählten Speicherort eine schreibgeschützte Version der Daten, die aktualisiert werden muss, wenn die Tabellen aktualisiert werden. Die Compatibility-Version enthält v1-Metadaten sowohl für Delta Lake als auch für Iceberg zusammen mit der schreibgeschützten Datenkopie — das erlaubt Zugriff für eine breitere Palette von Clients (einschließlich Clients, die Tabellendaten direkt lesen müssen statt über eine API), auf Kosten von Verzögerungen bei Datenaktualisierungen und Kosten für die Datenkopie.

## <a id="empfehlung">4. Empfehlung</a>

Unterstützen externe Clients die REST-APIs, empfiehlt Databricks, External Data Access zu verwenden, um diesen Clients Zugriff auf Materialized Views oder Streaming Tables zu geben. Für eine breitere Palette von Clients — insbesondere ältere Clients — sowie für andere Unity-Catalog-verwaltete Tabellen wird Compatibility Mode verwendet.

## <a id="vergleich">5. Vergleichstabelle</a>

Wörtlich übernommene Vergleichstabelle aus der Doku:

| Eigenschaft | External Data Access | Compatibility Mode |
|---|---|---|
| Datenkopie | Keine Datenkopie erforderlich. | Datenkopie erforderlich. |
| Konsistenz | Read-after-write-Konsistenz. Externe Clients sehen Änderungen, sobald sie im Dataset passieren. | Updates erfolgen nach einem Zeitplan. Standardmäßig wird die Compatibility-Tabelle stündlich aktualisiert. Dies kann so eingestellt werden, dass sie unmittelbar nach einer Änderung der Quelltabelle aktualisiert wird — verzögert sich aber weiterhin um die Datenkopierzeit. |
| Zugriff | Erfordert "modernen" REST-API-Zugriff. Unterstützt Delta-4.0.0-oder-höher-Catalog-APIs oder Iceberg-v3-Spezifikations-APIs (erfordert Unterstützung von Deletion Vectors). | Kompatibel mit allen Delta-Lake- oder Iceberg-Clients. |
| Einzelnes Tabellenobjekt | Materialized Views und Streaming Tables erscheinen für externe Clients als Managed Tables mit demselben Namen wie das Original-Dataset. | Compatibility-Tabellen erscheinen für externe Clients als neue Tabelle an einem neuen Speicherort. |
| Unterstützung des Tabellentyps | Unterstützt Materialized Views und Streaming Tables, verwaltet von einer Lakeflow-Pipeline oder als eigenständige Objekte erstellt. | Unterstützt Materialized Views und Streaming Tables — ob von einer Lakeflow-Pipeline verwaltet oder eigenständig — sowie jede andere Unity-Catalog-verwaltete Tabelle. |
| Kosten | Die Kosten für die Pflege der extern zugänglichen Metadaten sind Teil der Refresh-Kosten der Materialized View oder Streaming Table. Das liegt generell unter 1 % der Kosten und Zeit für den Refresh. | Der Großteil der Kosten für Compatibility Mode entsteht durch die Übertragung der Legacy-Daten an den neuen Speicherort. |

**Ungeklärt:** Konkrete UI- oder SQL-Konfigurationsschritte zum Aktivieren der beiden Funktionen wurden auf dieser Übersichtsseite nicht im Detail behandelt — die Seite verweist stattdessen auf zwei separate Detailseiten ("Enable external data access to streaming tables and materialized views" bzw. "Compatibility Mode"), die außerhalb der vier hier zugewiesenen URLs liegen und daher nicht mit abgerufen wurden.

## <a id="delta-uniform">6. Vertiefung: Delta UniForm als zugrunde liegender Mechanismus</a>

Aus einer privaten Kurs-Notiz übernommen und gegen `https://docs.databricks.com/aws/en/delta/uniform` abgeglichen (Stand der Notiz, nicht in dieser Bearbeitung erneut per `WebFetch` verifiziert) — eine Ergänzung zum älteren, manuellen Vorläufer-Mechanismus von External Data Access.

**Funktionsweise:** Delta UniForm (Universal Format) macht eine Delta-Tabelle gleichzeitig als Apache-Iceberg-Tabelle lesbar, ohne die zugrunde liegenden Parquet-Dateien zu duplizieren. Delta Lake und Apache Iceberg bauen beide auf Parquet-Datendateien plus einer Metadatenschicht auf — UniForm generiert nach jedem Delta-Commit asynchron zusätzlich Iceberg-Metadaten für dieselben Parquet-Dateien. Das Ergebnis: **ein Datensatz, zwei logische Sichten** (Delta-Transaktionslog für Databricks-Clients, Iceberg-`metadata/*.metadata.json` für externe Tools wie Snowflake, Trino oder Athena), ohne Datenkopie.

**Aktivierung** erfordert vier Tabelleneigenschaften, in dieser Reihenfolge vor dem ersten Schreibzugriff zu setzen:

| Property | Zweck |
|---|---|
| `delta.enableDeletionVectors = false` | Iceberg v2 kennt keine Delta-Soft-Delete-Marker — alle Deletes müssen Hard Deletes sein. |
| `delta.columnMapping.mode = name` | Hält Spaltenidentifikatoren zwischen Delta- und Iceberg-Schema konsistent. Diese Einstellung ist **dauerhaft** — sie lässt sich nach dem Setzen nicht mehr entfernen. |
| `delta.enableIcebergCompatV2 = true` | Aktiviert Delta-Schreibprotokoll-Kompatibilität mit Iceberg v2. |
| `delta.universalFormat.enabledFormats = iceberg` | Löst die asynchrone Iceberg-Metadatengenerierung nach jedem Delta-Commit aus. |

**Zentrale Einschränkung mit Bezug zu Lakeflow-Pipelines:** Pipeline-verwaltete Streaming Tables und Materialized Views können `delta.universalFormat.enabledFormats` nicht direkt gesetzt bekommen — UniForm lässt sich nur auf einer **plain external Delta-Tabelle** aktivieren, etwa einer über einen Delta-Sink (siehe `09 Sinks/Sinks.md`) beschriebenen Tabelle. Ein Append- oder Update-Flow schreibt dafür aus der Pipeline heraus in einen per `create_sink()` angelegten Delta-Sink; auf der resultierenden plain-Delta-Zieltabelle lassen sich die vier Properties einmalig setzen. Weitere Einschränkungen: Iceberg-Clients erhalten nur Lesezugriff (Schreiben bleibt Delta vorbehalten), und Unity Catalog übernimmt dabei die Rolle des Iceberg-REST-Catalogs.

**Einordnung gegenüber External Data Access:** External Data Access (Abschnitt 2) deckt seit seiner Einführung denselben Anwendungsfall — externer Iceberg-/Delta-Zugriff auf Databricks-Tabellen — direkt für pipeline-verwaltete Streaming Tables und Materialized Views ab, ohne den Umweg über einen Delta-Sink und ohne die vier manuellen UniForm-Properties. Für **plain Delta-Tabellen außerhalb einer Pipeline** (z. B. Sink-Ziele) bleibt die manuelle UniForm-Konfiguration weiterhin der relevante Weg.

---

## <a id="quellen">7. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/external-access
- https://learn.microsoft.com/en-us/azure/databricks/ldp/external-access (wörtliche Vollzitat-Quelle, inhaltlich mit AWS-Seite abgeglichen)
- https://docs.databricks.com/aws/en/delta/uniform (Delta-UniForm-Mechanismus, Abschnitt 6 — aus Kurs-Notiz übernommen, nicht in dieser Bearbeitung erneut per `WebFetch` verifiziert)
