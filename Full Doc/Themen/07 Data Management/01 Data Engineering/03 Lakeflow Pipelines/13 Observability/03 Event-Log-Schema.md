# Event-Log-Schema

Vollständige Feldreferenz für das Pipeline-Event-Log: das `PipelineEvent`-Objekt, das `details`-Objekt je Event-Typ sowie alle referenzierten Hilfsobjekte. Diese Seite listet sehr viele Felder tabellarisch — alle Tabellen wurden vollständig reproduziert, nicht nur eine Auswahl. Jede Aussage und jedes Feld wurde per `WebFetch` gegen die Azure-Spiegelseite `learn.microsoft.com/en-us/azure/databricks/ldp/monitor-event-log-schema` verifiziert (inhaltlich deckungsgleich mit `docs.databricks.com/aws/en/ldp/monitor-event-log-schema`).

**Hinweis der Quelle:** Manche Felder im Event Log sind für die interne Nutzung durch Databricks bestimmt. Die folgende Dokumentation beschreibt nur die für Kunden vorgesehenen Felder.

## Abschnittsübersicht

1. [PipelineEvent-Objekt](#pipelineevent)
2. [Das details-Objekt (Übersicht je event_type)](#details-uebersicht)
3. [Details-Typen im Einzelnen](#details-typen)
4. [Weitere Objekte (Enums und Hilfsstrukturen)](#weitere-objekte)
5. [Quellen](#quellen)

---

## <a id="pipelineevent">1. PipelineEvent-Objekt</a>

Repräsentiert ein einzelnes Pipeline-Ereignis im Event Log.

| Feld | Beschreibung |
|---|---|
| `id` | Eindeutiger Bezeichner für den Event-Log-Eintrag. |
| `sequence` | JSON-String mit Metadaten zur Identifizierung und Ordnung von Ereignissen. |
| `origin` | JSON-String mit Metadaten zum Ursprung des Ereignisses, z. B. Cloud-Provider, Cloud-Region, Nutzer und Pipeline-Informationen. Siehe Origin-Objekt (Abschnitt 4). |
| `timestamp` | Zeitpunkt der Aufzeichnung des Ereignisses, in UTC. |
| `message` | Menschenlesbare Nachricht, die das Ereignis beschreibt. |
| `level` | Warnstufe. Mögliche Werte: `INFO` (informative Ereignisse), `WARN` (unerwartete, aber nicht kritische Probleme), `ERROR` (Fehlschlag, der ggf. Nutzeraufmerksamkeit erfordert), `METRICS` (für Hochvolumen-Ereignisse, nur in der Delta-Tabelle gespeichert, nicht in der Pipelines-UI angezeigt). |
| `maturity_level` | Stabilität des Event-Schemas. Mögliche Werte: `STABLE` (Schema ist stabil und ändert sich nicht), `NULL` (Schema ist stabil; der Wert kann `NULL` sein, falls der Datensatz vor Einführung des Feldes `maturity_level` erstellt wurde, Release 2022.37), `EVOLVING` (Schema ist nicht stabil und kann sich ändern), `DEPRECATED` (Schema ist veraltet, die Lakeflow-Pipelines-Runtime kann die Erzeugung dieses Ereignisses jederzeit einstellen). Es wird nicht empfohlen, Monitoring oder Alerts auf `EVOLVING`- oder `DEPRECATED`-Feldern aufzubauen. |
| `error` | Bei einem Fehler: Details zur Fehlerbeschreibung. |
| `details` | JSON-String mit strukturierten Details des Ereignisses — das primäre Feld zur Analyse von Ereignissen. Das Format hängt vom `event_type` ab (siehe Abschnitt 2). |
| `event_type` | Der Ereignistyp. Für die Liste der Event-Typen und der jeweils erzeugten `details`-Objekttypen siehe Abschnitt 2. |

---

## <a id="details-uebersicht">2. Das details-Objekt (Übersicht je event_type)</a>

Jedes Ereignis hat je nach `event_type` unterschiedliche `details`-Eigenschaften. Diese Tabelle listet alle `event_type`-Werte und die zugehörigen `details`-Objekte.

| `event_type` | Beschreibung |
|---|---|
| `create_update` | Erfasst die vollständige Konfiguration, mit der ein Pipeline-Update gestartet wurde — inklusive jeglicher von Databricks gesetzter Konfiguration. |
| `user_action` | Liefert Details zu jeder Nutzeraktion an der Pipeline (inklusive Erstellung der Pipeline sowie Starten oder Abbrechen eines Updates). |
| `runtime_details` | Liefert Details zur für das Pipeline-Update genutzten Runtime. |
| `flow_progress` | Beschreibt den Lebenszyklus eines Flows von Start über Laufen bis Abschluss oder Fehlschlag. |
| `update_progress` | Beschreibt den Lebenszyklus eines Pipeline-Updates von Start über Laufen bis Abschluss oder Fehlschlag. |
| `flow_definition` | Definiert Schema und Query-Plan für Transformationen eines gegebenen Flows — quasi die Kanten des Dataflow-DAG. Dient zur Berechnung der Lineage je Flow sowie zur Einsicht des erklärten Query-Plans. |
| `dataset_definition` | Definiert ein Dataset, das entweder Quelle oder Ziel eines gegebenen Flows ist. |
| `sink_definition` | Definiert einen gegebenen Sink. |
| `deprecation` | Listet Features, die für die aktuelle Pipeline demnächst oder bereits veraltet sind. |
| `cluster_resources` | Informationen zu Cluster-Ressourcen für Pipelines auf klassischem Compute — nur für klassisches Compute befüllt. |
| `autoscale` | Informationen zum Autoscaling für Pipelines auf klassischem Compute — nur für klassisches Compute befüllt. |
| `planning_information` | Planungsinformationen zu inkrementellem vs. vollständigem Refresh einer Materialized View — nützlich, um Details zu erfahren, warum eine Materialized View vollständig neu berechnet wird. |
| `hook_progress` | Zeigt den aktuellen Status eines Nutzer-Hooks während des Pipeline-Laufs an — dient dem Monitoring des Status von Event Hooks, z. B. für externe Observability-Produkte. |
| `operation_progress` | Informationen zum Fortschritt einer Operation. |
| `stream_progress` | Informationen zum Fortschritt einer Pipeline (Streaming). |
| `behavior_change_in_spark_connect` | Meldet ein von der Environment-Version-Kompatibilitätsprüfung erkanntes Code-Muster, das sich unter einer Environment-Version anders verhalten oder fehlschlagen würde. |

---

## <a id="details-typen">3. Details-Typen im Einzelnen</a>

### Details für `create_update`

| Feld | Beschreibung |
|---|---|
| `run_as` | Die Nutzer-ID, in deren Namen das Update läuft — typischerweise der Pipeline-Owner oder ein Service Principal. |
| `cause` | Grund für das Update. Typischerweise `JOB_TASK` bei Ausführung aus einem Job, oder `USER_ACTION` bei interaktiver Ausführung durch einen Nutzer. |

### Details für `user_action`

| Feld | Beschreibung |
|---|---|
| `user_name` | Name des Nutzers, der ein Pipeline-Update ausgelöst hat. |
| `user_id` | ID des Nutzers, der ein Pipeline-Update ausgelöst hat — nicht zwingend identisch mit dem `run_as`-Nutzer, der ein Service Principal oder ein anderer Nutzer sein kann. |
| `action` | Die vom Nutzer ausgeführte Aktion, u. a. `START` und `CREATE`. |

### Details für `runtime_details`

| Feld | Beschreibung |
|---|---|
| `dbr_version` | Version der Databricks Runtime. |
| `image_key` | Der für das Update genutzte Databricks-Runtime-Build. |
| `effective_environment_version` | Die Environment-Version, mit der die Pipeline lief — entweder explizit gesetzt oder von Databricks im Rahmen einer automatischen Migration gewählt (siehe `14 Developer Reference/Environment-Versionen.md`, Abschnitt "Automatische Migration"). Leer, wenn die Pipeline keine Environment-Version nutzt. |

### Details für `flow_progress`

| Feld | Beschreibung |
|---|---|
| `status` | Neuer Status des Flows. Mögliche Werte: `QUEUED`, `STARTING`, `RUNNING`, `COMPLETED`, `FAILED`, `SKIPPED`, `STOPPED`, `IDLE`, `EXCLUDED`. |
| `metrics` | Metriken zum Flow (siehe FlowMetrics-Objekt). |
| `data_quality` | Datenqualitätsmetriken zum Flow und zugehörigen Expectations (siehe DataQualityMetrics-Objekt). |

### Details für `update_progress`

| Feld | Beschreibung |
|---|---|
| `state` | Neuer Status des Updates. Mögliche Werte: `QUEUED`, `CREATED`, `WAITING_FOR_RESOURCES`, `INITIALIZING`, `RESETTING`, `SETTING_UP_TABLES`, `RUNNING`, `STOPPING`, `COMPLETED`, `FAILED`, `CANCELED`. Nützlich, um die Dauer verschiedener Update-Phasen zu berechnen, z. B. Gesamtdauer vs. Wartezeit auf Ressourcen. |
| `cancellation_cause` | Grund, warum ein Update in den Status `CANCELED` überging. U. a. `USER_ACTION` oder `WORKFLOW_CANCELLATION` (der auslösende Workflow wurde abgebrochen). |

### Details für `flow_definition`

| Feld | Beschreibung |
|---|---|
| `input_datasets` | Die von diesem Flow gelesenen Eingaben. |
| `output_dataset` | Das Ziel-Dataset, in das dieser Flow schreibt. |
| `output_sink` | Der Ziel-Sink, in den dieser Flow schreibt. |
| `explain_text` | Der erklärte Query-Plan. |
| `schema_json` | Spark-SQL-JSON-Schema-String. |
| `schema` | Schema dieses Flows. |
| `flow_type` | Typ des Flows. Mögliche Werte: `COMPLETE` (Streaming Table schreibt im Complete-/Streaming-Modus ins Ziel), `CHANGE` (Streaming Table via `APPLY_CHANGES_INTO`), `SNAPSHOT_CHANGE` (Streaming Table via `APPLY CHANGES INTO ... FROM SNAPSHOT ...`), `APPEND` (Streaming Table schreibt im Append-/Streaming-Modus ins Ziel), `MATERIALIZED_VIEW` (Ausgabe in eine Materialized View), `VIEW` (Ausgabe in eine View). |
| `comment` | Nutzerkommentar bzw. Beschreibung des Datasets. |
| `spark_conf` | Für diesen Flow gesetzte Spark-Konfigurationen. |
| `language` | Für diesen Flow genutzte Sprache: `SCALA`, `PYTHON` oder `SQL`. |
| `once` | Ob dieser Flow als einmalig auszuführen deklariert wurde. |

### Details für `dataset_definition`

| Feld | Beschreibung |
|---|---|
| `dataset_type` | Unterscheidet zwischen Materialized Views und Streaming Tables. |
| `num_flows` | Anzahl der in das Dataset schreibenden Flows. |
| `expectations` | Die dem Dataset zugeordneten Expectations. |

### Details für `sink_definition`

| Feld | Beschreibung |
|---|---|
| `format` | Format des Sinks. |
| `options` | Die dem Sink zugeordneten Key-Value-Optionen. |

### Details-Enum für `deprecation`

Das `deprecation`-Ereignis hat ein `message`-Feld. Mögliche Werte (unvollständige, mit der Zeit wachsende Liste):

| Wert | Beschreibung |
|---|---|
| `TABLE_MANAGED_BY_MULTIPLE_PIPELINES` | Eine Tabelle wird von mehreren Pipelines verwaltet. |
| `INVALID_CLUSTER_LABELS` | Verwendung nicht unterstützter Cluster-Labels. |
| `PINNED_DBR_VERSION` | Verwendung von `dbr_version` statt `channel` in den Pipeline-Einstellungen. |
| `PREVIOUS_CHANNEL_USED` | Verwendung des Release-Channels `PREVIOUS`, der in einem zukünftigen Release entfallen könnte. |
| `LONG_DATASET_NAME` | Verwendung eines Dataset-Namens, der die unterstützte Länge überschreitet. |
| `LONG_SINK_NAME` | Verwendung eines Sink-Namens, der die unterstützte Länge überschreitet. |
| `LONG_FLOW_NAME` | Verwendung eines Flow-Namens, der die unterstützte Länge überschreitet. |
| `ENHANCED_AUTOSCALING_POLICY_COMPLIANCE` | Cluster-Policy ist nur konform, wenn Enhanced Autoscaling eine feste Cluster-Größe nutzt. |
| `DATA_SAMPLE_CONFIGURATION_KEY` | Verwendung des Konfigurationsschlüssels zur Konfiguration von Data Sampling ist veraltet. |
| `INCOMPATIBLE_CLUSTER_SETTINGS` | Aktuelle Cluster-Einstellungen oder Cluster-Policy sind mit Lakeflow-Pipelines nicht mehr kompatibel. |
| `STREAMING_READER_OPTIONS_DROPPED` | Verwendung von Streaming-Reader-Optionen, die entfallen sind. |
| `DISALLOWED_SERVERLESS_STATIC_SPARK_CONFIG` | Setzen statischer Spark-Configs über die Pipeline-Konfiguration ist für Serverless-Pipelines nicht erlaubt. |
| `INVALID_SERVERLESS_PIPELINE_CONFIG` | Serverless-Kunde übergibt eine ungültige Pipeline-Konfiguration. |
| `UNUSED_EXPLICIT_PATH_ON_UC_MANAGED_TABLE` | Angabe ungenutzter expliziter Tabellenpfade auf UC-Managed-Tables. |
| `FOREACH_BATCH_FUNCTION_NOT_SERIALIZABLE` | Die übergebene `foreachBatch`-Funktion ist nicht serialisierbar. |
| `DROP_PARTITION_COLS_NO_PARTITIONING` | Entfernen des Attributs `partition_cols` führt zu keiner Partitionierung. |
| `PYTHON_CREATE_TABLE` | Verwendung von `@dlt.create_table` statt `@dp.table` bzw. `@dp.materialized_view`. |
| `PYTHON_CREATE_VIEW` | Verwendung von `@dlt.create_view` statt `@dp.temporary_view`. |
| `PYTHON_CREATE_STREAMING_LIVE_TABLE` | Verwendung von `create_streaming_live_table` statt `create_streaming_table`. |
| `PYTHON_CREATE_TARGET_TABLE` | Verwendung von `create_target_table` statt `create_streaming_table`. |
| `FOREIGN_KEY_TABLE_CONSTRAINT_CYCLE` | Die von der Pipeline verwalteten Tabellen enthalten einen Zyklus in den Foreign-Key-Constraints. |
| `PARTIALLY_QUALIFIED_TABLE_REFERENCE_INCOMPATIBLE_WITH_DEFAULT_PUBLISHING_MODE` | Eine partiell qualifizierte Tabellenreferenz, die im Default Publishing Mode und im Legacy Publishing Mode unterschiedliche Bedeutung hat. |

### Details für `cluster_resources`

Nur relevant für Pipelines auf klassischem Compute.

| Feld | Beschreibung |
|---|---|
| `task_slot_metrics` | Task-Slot-Metriken des Clusters (siehe TaskSlotMetrics-Objekt). |
| `autoscale_info` | Status der Autoscaler (siehe AutoscaleInfo-Objekt). |

### Details für `autoscale`

Nur relevant, wenn die Pipeline klassisches Compute nutzt.

| Feld | Beschreibung |
|---|---|
| `status` | Status dieses Ereignisses. Mögliche Werte: `SUCCEEDED`, `RESIZING`, `FAILED`, `PARTIALLY_SUCCEEDED`. |
| `optimal_num_executors` | Vom Algorithmus vorgeschlagene optimale Anzahl Executor, vor Anwendung der `min_workers`-/`max_workers`-Grenzen. |
| `requested_num_executors` | Anzahl Executor nach Kürzung der vom Algorithmus vorgeschlagenen optimalen Anzahl auf die `min_workers`-/`max_workers`-Grenzen. |

### Details für `planning_information`

Nützlich, um Details zur gewählten Refresh-Methode für einen gegebenen Flow während eines Updates zu sehen. Kann helfen zu debuggen, warum ein Update vollständig statt inkrementell aktualisiert wird.

| Feld | Beschreibung |
|---|---|
| `technique_information` | Refresh-bezogene Informationen — sowohl zur gewählten Refresh-Methodik als auch zu den erwogenen Alternativen. Nützlich zum Debuggen, warum eine Materialized View nicht inkrementalisiert werden konnte (siehe TechniqueInformation-Objekt). |
| `source_table_information` | Informationen zur Quelltabelle — kann beim Debuggen hilfreich sein (siehe TableInformation-Objekt). |
| `target_table_information` | Informationen zur Zieltabelle (siehe TableInformation-Objekt). |

### Details für `hook_progress`

| Feld | Beschreibung |
|---|---|
| `name` | Name des Nutzer-Hooks. |
| `status` | Status des Nutzer-Hooks. |

### Details für `operation_progress`

| Feld | Beschreibung |
|---|---|
| `type` | Art der verfolgten Operation. Einer von: `AUTO_LOADER_LISTING`, `AUTO_LOADER_BACKFILL`, `CONNECTOR_FETCH`, `CDC_SNAPSHOT`. |
| `status` | Status der Operation. Einer von: `STARTED`, `COMPLETED`, `CANCELED`, `FAILED`, `IN_PROGRESS`. |
| `duration_ms` | Gesamte verstrichene Zeit der Operation in Millisekunden. Nur im End-Ereignis enthalten (Status `COMPLETED`, `CANCELED` oder `FAILED`). |

### Details für `stream_progress`

| Feld | Beschreibung |
|---|---|
| `stream_progress` | Details des Pipeline-Streams — ähnlich den `StreamingQueryListener`-Metriken von Structured Streaming (Unterschiede siehe `Event Logs ueberwachen.md`, Abschnitt Pipeline-Streaming-Metriken). |

### Details für `behavior_change_in_spark_connect`

Wird von der Environment-Version-Kompatibilitätsprüfung mit Level `WARN` ausgelöst — ein Ereignis je erkanntem Code-Muster.

| Feld | Beschreibung |
|---|---|
| `issue` | Das erkannte Muster. Für die vollständige Liste der Issue-Codes, Beispiele und empfohlenen Korrekturen verweist die Doku auf die Compatibility-Events-Referenz. |

---

## <a id="weitere-objekte">4. Weitere Objekte (Enums und Hilfsstrukturen)</a>

### AutoscaleInfo-Objekt

Autoscale-Metriken für einen Cluster. Nur relevant für Pipelines auf klassischem Compute.

| Feld | Beschreibung |
|---|---|
| `state` | Autoscaling-Status. Mögliche Werte: `SUCCEEDED`, `RESIZING`, `FAILED`, `PARTIALLY_SUCCEEDED`. |
| `optimal_num_executors` | Optimale Anzahl Executor — die vom Algorithmus vorgeschlagene optimale Größe, vor Kürzung durch die nutzerdefinierten Min-/Max-Grenzen. |
| `latest_requested_num_executors` | Vom State Manager beim letzten Request an den Cluster-Manager angeforderte Anzahl Executor — die Zielgröße, auf die der State Manager zu skalieren versucht; wird aktualisiert, wenn der State Manager den Scaling-Zustand bei Timeouts zu verlassen versucht. Nicht befüllt, wenn kein Request aussteht. |
| `request_pending_seconds` | Dauer, seit der der Scaling-Request aussteht. Nicht befüllt, wenn kein Request aussteht. |

### CostModelRejectionSubType-Objekt

Enum der Gründe, aus denen eine Inkrementalisierung basierend auf dem Kostenvergleich Full-Refresh vs. Incremental-Refresh in einem `planning_information`-Ereignis abgelehnt wird.

| Wert | Beschreibung |
|---|---|
| `NUM_JOINS_THRESHOLD_EXCEEDED` | Full Refresh, weil die Abfrage zu viele Joins enthält. |
| `CHANGESET_SIZE_THRESHOLD_EXCEEDED` | Full Refresh, weil sich zu viele Zeilen in den Basistabellen geändert haben. |
| `TABLE_SIZE_THRESHOLD_EXCEEDED` | Full Refresh, weil die Größe der Basistabelle den Schwellenwert überschritten hat. |
| `EXCESSIVE_OPERATOR_NESTING` | Full Refresh, weil die Abfragedefinition komplex ist und viele Ebenen an Operator-Verschachtelung aufweist. |
| `COST_MODEL_REJECTION_SUB_TYPE_UNSPECIFIED` | Full Refresh aus einem anderen Grund. |

### DataQualityMetrics-Objekt

Metriken dazu, wie gut Expectations innerhalb des Flows erfüllt werden. Genutzt in den Details eines `flow_progress`-Ereignisses.

| Feld | Beschreibung |
|---|---|
| `dropped_records` | Anzahl der Datensätze, die verworfen wurden, weil sie eine oder mehrere Expectations nicht erfüllten. |
| `expectations` | Metriken für Expectations, die einem Dataset im Query-Plan des Flows hinzugefügt wurden. Bei mehreren Expectations lässt sich damit nachverfolgen, welche erfüllt bzw. nicht erfüllt wurden (siehe ExpectationMetrics-Objekt). |

### ExpectationMetrics-Objekt

Metriken zu einer spezifischen Expectation.

| Feld | Beschreibung |
|---|---|
| `name` | Name der Expectation. |
| `dataset` | Name des Datasets, dem die Expectation hinzugefügt wurde. |
| `passed_records` | Anzahl der Datensätze, die die Expectation erfüllen. |
| `failed_records` | Anzahl der Datensätze, die die Expectation nicht erfüllen. Erfasst nur, ob die Expectation erfüllt wurde — nicht, was mit den Datensätzen geschieht (warnen, fehlschlagen oder verwerfen). |

### FlowMetrics-Objekt

Metriken zum Flow — sowohl Gesamtwerte für den Flow als auch aufgeschlüsselt nach einzelner Quelle. Genutzt in den Details eines `flow_progress`-Ereignisses.

Jede Streaming-Quelle unterstützt nur bestimmte Flow-Metriken:

| Quelle | Backlog Bytes | Backlog Records | Backlog Seconds | Backlog Files |
|---|---|---|---|---|
| Kafka | ✓ | ✓ | | |
| Kinesis | ✓ | | ✓ | |
| Delta | ✓ | | | ✓ |
| Auto Loader | ✓ | | | ✓ |
| Google Pub/Sub | ✓ | ✓ | | |

| Feld | Beschreibung |
|---|---|
| `num_output_rows` | Anzahl der von einem Flow-Update geschriebenen Output-Zeilen. |
| `backlog_bytes` | Gesamter Backlog in Bytes über alle Eingabequellen des Flows. |
| `backlog_records` | Gesamter Backlog an Datensätzen über alle Eingabequellen des Flows. |
| `backlog_files` | Gesamter Backlog an Dateien über alle Eingabequellen des Flows. |
| `backlog_seconds` | Maximaler Backlog in Sekunden über alle Eingabequellen des Flows. |
| `executor_time_ms` | Summe aller Task-Ausführungszeiten in Millisekunden dieses Flows über den Berichtszeitraum. |
| `executor_cpu_time_ms` | Summe aller Task-CPU-Ausführungszeiten in Millisekunden dieses Flows über den Berichtszeitraum. |
| `num_upserted_rows` | Anzahl der durch ein Flow-Update in das Dataset upserteten Output-Zeilen. |
| `num_deleted_rows` | Anzahl der durch ein Flow-Update aus dem Dataset gelöschten bestehenden Output-Zeilen. |
| `num_output_bytes` | Anzahl der von einem Flow-Update geschriebenen Output-Bytes. |
| `source_metrics` | Metriken je Eingabequelle des Flows. Nützlich zum Monitoring des Ingestion-Fortschritts von Quellen außerhalb von Lakeflow-Pipelines (z. B. Apache Kafka, Pulsar, Auto Loader). Enthält die Felder `source_name`, `backlog_bytes`, `backlog_records`, `backlog_files`, `backlog_seconds`. |

### IncrementalizationIssue-Objekt

Repräsentiert Probleme mit der Inkrementalisierung, die bei der Planung eines Updates zu einem Full Refresh führen könnten.

| Feld | Beschreibung |
|---|---|
| `issue_type` | Ein Issue-Typ, der die Inkrementalisierung der Materialized View verhindern könnte (siehe IssueType-Objekt). |
| `prevent_incrementalization` | Ob dieses Problem die Inkrementalisierung tatsächlich verhindert hat. |
| `table_information` | Tabelleninformationen zu Issues wie `CDF_UNAVAILABLE`, `INPUT_NOT_IN_DELTA`, `DATA_FILE_MISSING`. |
| `operator_name` | Plan-bezogene Information. Gesetzt bei Issue-Typ `PLAN_NOT_DETERMINISTIC` oder `PLAN_NOT_INCREMENTALIZABLE` — der Operator bzw. Ausdruck, der die Nicht-Determinismus- bzw. Nicht-Inkrementalisierbarkeit verursacht. |
| `expression_name` | Der Name des Ausdrucks. |
| `join_type` | Zusatzinformation, wenn der Operator ein Join ist, z. B. `JOIN_TYPE_LEFT_OUTER` oder `JOIN_TYPE_INNER`. |
| `plan_not_incrementalizable_sub_type` | Detailkategorie, wenn der Issue-Typ `PLAN_NOT_INCREMENTALIZABLE` ist (siehe PlanNotIncrementalizableSubType-Objekt). |
| `plan_not_deterministic_sub_type` | Detailkategorie, wenn der Issue-Typ `PLAN_NOT_DETERMINISTIC` ist (siehe PlanNotDeterministicSubType-Objekt). |
| `fingerprint_diff_before` | Der Diff zum vorherigen Fingerprint. |
| `fingerprint_diff_current` | Der Diff zum aktuellen Fingerprint. |
| `cost_model_rejection_subtype` | Detailkategorie, wenn der Issue-Typ `INCREMENTAL_PLAN_REJECTED_BY_COST_MODEL` ist (siehe CostModelRejectionSubType-Objekt). |

### IssueType-Objekt

Enum der Issue-Typen, die zu einem Full Refresh führen können. Zentrale Refresh-Issues werden zusätzlich im Pipeline-Editor und beim Monitoring als „Incrementalization Insights" hervorgehoben.

| Wert | Beschreibung |
|---|---|
| `CDF_UNAVAILABLE` | Change Data Feed (CDF) ist auf manchen Basistabellen nicht aktiviert. `table_information` gibt an, welche Tabelle betroffen ist. Aktivierung über `ALTER TABLE <table-name> SET TBLPROPERTIES ('delta.enableChangeDataFeed' = true)`. Ist die Quelltabelle eine Materialized View, sollte CDF standardmäßig `ON` sein. |
| `DELTA_PROTOCOL_CHANGED` | Full Refresh, weil manche Basistabellen (Details in `table_information`) eine Delta-Protokolländerung hatten. |
| `DATA_SCHEMA_CHANGED` | Full Refresh, weil manche Basistabellen (Details in `table_information`) eine Datenschemaänderung in den von der Materialized-View-Definition genutzten Spalten hatten. Nicht relevant, wenn eine von der Materialized View nicht genutzte Spalte geändert oder hinzugefügt wurde. |
| `PARTITION_SCHEMA_CHANGED` | Full Refresh, weil manche Basistabellen (Details in `table_information`) eine Partitionsschemaänderung hatten. |
| `INPUT_NOT_IN_DELTA` | Full Refresh, weil die Materialized-View-Definition eine Nicht-Delta-Eingabe einbezieht. |
| `DATA_FILE_MISSING` | Full Refresh, weil manche Basistabellendateien wegen ihrer Retention-Frist bereits vakuumiert wurden. |
| `PLAN_NOT_DETERMINISTIC` | Full Refresh, weil manche Operatoren oder Ausdrücke in der Materialized-View-Definition nicht deterministisch sind. `operator_name` und `expression_name` geben Auskunft über die Ursache. |
| `PLAN_NOT_INCREMENTALIZABLE` | Full Refresh, weil manche Operatoren oder Ausdrücke in der Materialized-View-Definition nicht inkrementalisierbar sind. |
| `SERIALIZATION_VERSION_CHANGED` | Full Refresh, weil es eine signifikante Änderung der Query-Fingerprinting-Logik gab. |
| `QUERY_FINGERPRINT_CHANGED` | Full Refresh, weil sich die Materialized-View-Definition geändert hat oder ein Lakeflow-Pipelines-Release eine Änderung der Query-Evaluationspläne verursacht hat. |
| `CONFIGURATION_CHANGED` | Full Refresh, weil sich zentrale Konfigurationen (z. B. `spark.sql.ansi.enabled`), die die Query-Auswertung beeinflussen können, geändert haben. Eine vollständige Neuberechnung ist nötig, um inkonsistente Zustände in der Materialized View zu vermeiden. |
| `CHANGE_SET_MISSING` | Full Refresh, weil es die erste Berechnung der Materialized View ist — erwartetes Verhalten bei der initialen Berechnung. |
| `EXPECTATIONS_NOT_SUPPORTED` | Full Refresh, weil die Materialized-View-Definition Expectations enthält, die für inkrementelle Updates nicht unterstützt werden. Expectations entfernen oder außerhalb der Materialized-View-Definition behandeln, falls inkrementelle Unterstützung benötigt wird. |
| `TOO_MANY_FILE_ACTIONS` | Full Refresh, weil die Anzahl der Datei-Aktionen den Schwellenwert für inkrementelle Verarbeitung überschritten hat. Datei-Churn in Basistabellen reduzieren oder Schwellenwerte erhöhen. |
| `INCREMENTAL_PLAN_REJECTED_BY_COST_MODEL` | Full Refresh, weil das Kostenmodell ermittelt hat, dass ein Full Refresh effizienter ist als inkrementelle Pflege. Kostenmodell-Verhalten oder Komplexität des Query-Plans prüfen, um inkrementelle Updates zu ermöglichen. |
| `ROW_TRACKING_NOT_ENABLED` | Full Refresh, weil Row Tracking auf einer oder mehreren Basistabellen nicht aktiviert ist. Aktivierung über `ALTER TABLE <table-name> SET TBLPROPERTIES ('delta.enableRowTracking' = true)`. |
| `TOO_MANY_PARTITIONS_CHANGED` | Full Refresh, weil sich zu viele Partitionen in den Basistabellen geändert haben. Anzahl der Partitionsänderungen begrenzen, um innerhalb der Grenzen inkrementeller Verarbeitung zu bleiben. |
| `MAP_TYPE_NOT_SUPPORTED` | Full Refresh, weil die Materialized-View-Definition einen Map-Typ enthält, der für inkrementelle Updates nicht unterstützt wird. Datenstruktur ggf. anpassen, um Map-Typen zu vermeiden. |
| `TIME_ZONE_CHANGED` | Full Refresh, weil sich die Session- oder System-Zeitzoneneinstellung geändert hat. |
| `DATA_HAS_CHANGED` | Full Refresh, weil sich die für die Materialized View relevanten Daten so geändert haben, dass inkrementelle Updates verhindert werden. Datenänderungen und Struktur der View-Definition auf Kompatibilität mit inkrementeller Logik prüfen. |
| `PRIOR_TIMESTAMP_MISSING` | Full Refresh, weil der Zeitstempel des letzten erfolgreichen Laufs fehlt — kann nach Metadatenverlust oder manuellem Eingriff auftreten. |

### MaintenanceType-Objekt

Enum der Wartungstypen, die während eines `planning_information`-Ereignisses gewählt werden können. Ist der Typ weder `MAINTENANCE_TYPE_COMPLETE_RECOMPUTE` noch `MAINTENANCE_TYPE_NO_OP`, handelt es sich um ein inkrementelles Refresh.

| Wert | Beschreibung |
|---|---|
| `MAINTENANCE_TYPE_COMPLETE_RECOMPUTE` | Vollständige Neuberechnung; wird immer angezeigt. |
| `MAINTENANCE_TYPE_NO_OP` | Wenn sich Basistabellen nicht geändert haben. |
| `MAINTENANCE_TYPE_PARTITION_OVERWRITE` | Inkrementelles Refresh betroffener Partitionen, wenn die Materialized View mit einer der Quelltabellen co-partitioniert ist. |
| `MAINTENANCE_TYPE_ROW_BASED` | Inkrementelles Refresh durch Erstellen modularer Changesets für verschiedene Operationen (`JOIN`, `FILTER`, `UNION ALL`) und deren Kombination zur Berechnung komplexer Abfragen. Genutzt, wenn Row Tracking für die Quelltabellen aktiviert ist und die Abfrage nur eine begrenzte Anzahl an Joins hat. |
| `MAINTENANCE_TYPE_APPEND_ONLY` | Inkrementelles Refresh durch ausschließliche Berechnung neuer Zeilen, da es keine Upserts oder Deletes in den Quelltabellen gab. |
| `MAINTENANCE_TYPE_GROUP_AGGREGATE` | Inkrementelles Refresh durch Berechnung von Änderungen je Aggregatwert. Genutzt, wenn assoziative Aggregate (`count`, `sum`, `mean`, `stddev`) auf oberster Ebene der Abfrage stehen. |
| `MAINTENANCE_TYPE_GENERIC_AGGREGATE` | Inkrementelles Refresh durch Berechnung nur der betroffenen Aggregatgruppen. Genutzt bei Aggregaten wie `median` (nicht nur assoziativen) auf oberster Ebene der Abfrage. |
| `MAINTENANCE_TYPE_WINDOW_FUNCTION` | Inkrementelles Refresh von Abfragen mit Fensterfunktionen wie `PARTITION BY` durch Neuberechnung nur der geänderten Partitionen. Genutzt, wenn alle Fensterfunktionen eine `PARTITION BY`- oder `JOIN`-Klausel haben und auf oberster Ebene der Abfrage stehen. |

### Origin-Objekt

Ursprung des Ereignisses.

| Feld | Beschreibung |
|---|---|
| `cloud` | Der Cloud-Provider. Mögliche Werte: AWS, Azure, GCP. |
| `region` | Die Cloud-Region. |
| `org_id` | Die Org-ID bzw. Workspace-ID des Nutzers — eindeutig innerhalb einer Cloud. Nützlich, um den Workspace zu identifizieren oder mit anderen Tabellen zu joinen, z. B. System-Billing-Tabellen. |
| `pipeline_id` | Die ID der Pipeline — eindeutiger Bezeichner. Nützlich, um die Pipeline zu identifizieren oder mit anderen Tabellen zu joinen. |
| `pipeline_type` | Typ der Pipeline, zeigt an, wo die Pipeline erstellt wurde. Mögliche Werte: `WORKSPACE` (eine ETL-Pipeline, erstellt über eine Lakeflow-Pipeline), `DBSQL` (eine eigenständige Pipeline), `MANAGED_INGESTION` (eine von Lakeflow Connect verwaltete Ingestion-Pipeline), `DATABASE_TABLE_SYNC` (eine Pipeline, die eine Tabelle mit einer Lakebase-Datenbank synchronisiert), `BRICKSTORE` (eine Pipeline zur Aktualisierung einer Online-Tabelle für Real-Time Feature Serving — Online Tables sind legacy), `BRICKINDEX` (eine Pipeline zur Aktualisierung einer Vektordatenbank, siehe Databricks AI Search). |
| `pipeline_name` | Name der Pipeline. |
| `cluster_id` | ID des Clusters, auf dem eine Ausführung stattfindet — global eindeutig. |
| `update_id` | ID einer einzelnen Ausführung der Pipeline, entspricht der Run-ID. |
| `table_name` | Name der (Delta-)Tabelle, in die geschrieben wird. |
| `dataset_name` | Vollständig qualifizierter Name eines Datasets. |
| `sink_name` | Name eines Sinks. |
| `flow_id` | ID des Flows. Verfolgt den Zustand des Flows über mehrere Updates hinweg. Solange die `flow_id` gleich bleibt, wird der Flow inkrementell aktualisiert. Die `flow_id` ändert sich bei Full Refresh der Materialized View, Checkpoint-Reset oder vollständiger Neuberechnung innerhalb der Materialized View. |
| `flow_name` | Name des Flows. |
| `batch_id` | ID eines Microbatches — eindeutig innerhalb eines Flows. |
| `request_id` | ID des Requests, der ein Update ausgelöst hat. |

### PlanNotDeterministicSubType-Objekt

Enum nicht-deterministischer Fälle für ein `planning_information`-Ereignis.

| Wert | Beschreibung |
|---|---|
| `STREAMING_SOURCE` | Full Refresh, weil die Materialized-View-Definition eine Streaming-Quelle einbezieht, die nicht unterstützt wird. |
| `USER_DEFINED_FUNCTION` | Full Refresh, weil die Materialized View eine nicht unterstützte benutzerdefinierte Funktion einbezieht. Nur deterministische Python-UDFs werden unterstützt; andere UDFs können inkrementelle Updates verhindern. |
| `TIME_FUNCTION` | Full Refresh, weil die Materialized View eine zeitbasierte Funktion wie `CURRENT_DATE` oder `CURRENT_TIMESTAMP` einbezieht. `expression_name` gibt den Namen der nicht unterstützten Funktion an. |
| `NON_DETERMINISTIC_EXPRESSION` | Full Refresh, weil die Abfrage einen nicht-deterministischen Ausdruck wie `RANDOM()` einbezieht. `expression_name` gibt die nicht-deterministische Funktion an, die die inkrementelle Pflege verhindert. |

### PlanNotIncrementalizableSubType-Objekt

Enum der Gründe, warum ein Update-Plan nicht inkrementalisierbar sein könnte.

| Wert | Beschreibung |
|---|---|
| `OPERATOR_NOT_SUPPORTED` | Full Refresh, weil der Query-Plan einen nicht unterstützten Operator enthält. `operator_name` gibt den Namen des nicht unterstützten Operators an. |
| `AGGREGATE_NOT_TOP_NODE` | Full Refresh, weil ein Aggregat (`GROUP BY`) nicht auf oberster Ebene des Query-Plans steht. Inkrementelle Pflege unterstützt Aggregate nur auf oberster Ebene — ggf. zwei Materialized Views zur Trennung der Aggregation nutzen. |
| `AGGREGATE_WITH_DISTINCT` | Full Refresh, weil die Aggregation eine `DISTINCT`-Klausel enthält, die für inkrementelle Updates nicht unterstützt wird. |
| `AGGREGATE_WITH_UNSUPPORTED_EXPRESSION` | Full Refresh, weil die Aggregation nicht unterstützte Ausdrücke enthält. `expression_name` gibt den problematischen Ausdruck an. |
| `SUBQUERY_EXPRESSION` | Full Refresh, weil die Materialized-View-Definition einen Subquery-Ausdruck enthält, der nicht unterstützt wird. |
| `WINDOW_FUNCTION_NOT_TOP_LEVEL` | Full Refresh, weil eine Fensterfunktion nicht auf oberster Ebene des Query-Plans steht. |
| `WINDOW_FUNCTION_WITHOUT_PARTITION_BY` | Full Refresh, weil eine Fensterfunktion ohne `PARTITION BY`-Klausel definiert ist. |

### TableInformation-Objekt

Details zu einer während eines `planning_information`-Ereignisses betrachteten Tabelle.

| Feld | Beschreibung |
|---|---|
| `table_name` | In der Abfrage genutzter Tabellenname aus Unity Catalog oder Hive Metastore. Bei pfadbasiertem Zugriff ggf. nicht verfügbar. |
| `table_id` | Erforderlich. Tabellen-ID aus dem Delta-Log. |
| `catalog_table_type` | Typ der Tabelle, wie im Katalog angegeben. |
| `partition_columns` | Partitionsspalten der Tabelle. |
| `table_change_type` | Änderungstyp der Tabelle. Einer von: `TABLE_CHANGE_TYPE_UNKNOWN`, `TABLE_CHANGE_TYPE_APPEND_ONLY`, `TABLE_CHANGE_TYPE_GENERAL_CHANGE`. |
| `full_size` | Gesamtgröße der Tabelle in Bytes. |
| `change_size` | Größe der geänderten Zeilen in geänderten Dateien. Berechnet als `change_file_read_size * num_changed_rows / num_rows_in_changed_files`. |
| `num_changed_partitions` | Anzahl geänderter Partitionen. |
| `is_size_after_pruning` | Ob `full_size` und `change_size` die Daten nach statischem File Pruning repräsentieren. |
| `is_row_id_enabled` | Ob Row ID auf der Tabelle aktiviert ist. |
| `is_cdf_enabled` | Ob CDF auf der Tabelle aktiviert ist. |
| `is_deletion_vector_enabled` | Ob Deletion Vectors auf der Tabelle aktiviert sind. |
| `is_change_from_legacy_cdf` | Ob die Tabellenänderung aus Legacy-CDF oder Row-ID-basiertem CDF stammt. |

### TaskSlotMetrics-Objekt

Task-Slot-Metriken für einen Cluster. Gilt nur für Pipeline-Updates auf klassischem Compute.

| Feld | Beschreibung |
|---|---|
| `summary_duration_ms` | Dauer in Millisekunden, über die aggregierte Metriken (z. B. `avg_num_task_slots`) berechnet werden. |
| `num_task_slots` | Anzahl der Spark-Task-Slots zum Berichtszeitpunkt. |
| `avg_num_task_slots` | Durchschnittliche Anzahl Spark-Task-Slots über die Berichtsdauer. |
| `avg_task_slot_utilization` | Durchschnittliche Task-Slot-Auslastung (Anzahl aktiver Tasks geteilt durch Anzahl Task-Slots) über die Berichtsdauer. |
| `num_executors` | Anzahl der Spark-Executor zum Berichtszeitpunkt. |
| `avg_num_queued_tasks` | Durchschnittliche Task-Warteschlangengröße (Gesamtzahl Tasks minus Anzahl aktiver Tasks) über die Berichtsdauer. |

### TechniqueInformation-Objekt

Refresh-Methodik-Informationen für ein Planungsereignis.

| Feld | Beschreibung |
|---|---|
| `maintenance_type` | Der zu dieser Information gehörende Wartungstyp. Ist der Typ weder `MAINTENANCE_TYPE_COMPLETE_RECOMPUTE` noch `MAINTENANCE_TYPE_NO_OP`, wurde der Flow inkrementell aktualisiert (siehe MaintenanceType-Objekt). |
| `is_chosen` | `true` für die tatsächlich gewählte Refresh-Technik. |
| `is_applicable` | Ob der Wartungstyp anwendbar ist. |
| `incrementalization_issues` | Inkrementalisierungsprobleme, die ein Update zum Full Refresh zwingen könnten (siehe IncrementalizationIssue-Objekt). |
| `change_set_information` | Informationen zum final erzeugten Changeset. Werte: `CHANGE_SET_TYPE_APPEND_ONLY` oder `CHANGE_SET_TYPE_GENERAL_ROW_CHANGE`. |

---

## <a id="quellen">5. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/monitor-event-log-schema
- https://learn.microsoft.com/en-us/azure/databricks/ldp/monitor-event-log-schema (primäre Quelle für die vollständige Feldreproduktion)

**Stand:** 2026-08-19
