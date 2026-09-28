# Unity Catalog und Schema-Verwaltung

## 1. Unity Catalog in Pipelines: Grundlagen

UC-konfigurierte Pipelines (Databricks-Empfehlung, Default für neue Pipelines) veröffentlichen alle MV/ST im festgelegten Katalog/Schema und lesen aus anderen UC-Tabellen/-Volumes. Berechtigungen über `GRANT`/`REVOKE` (Abschnitt 1, Unterabschnitt "Materialized Views freigeben").

> **Hinweis:** Dies beschreibt den aktuellen **Default Publishing Mode**. Vor dem 5. Februar 2025 erstellte Pipelines könnten noch den Legacy Publishing Mode mit virtuellem `LIVE`-Schema nutzen (Abschnitt 5).

**Voraussetzungen — Tabellen in Zielschema erstellen:**
- `USE CATALOG` auf Zielkatalog.
- `CREATE MATERIALIZED VIEW` + `USE SCHEMA` auf Zielschema (bei MVs).
- `CREATE TABLE` + `USE SCHEMA` auf Zielschema (bei ST).
- `USE CATALOG` + `CREATE SCHEMA` auf Zielkatalog (bei neuen Schemas).

**Compute:** UC-Pipeline ausführen → Standard Access Mode (Dedicated nicht unterstützt). Erzeugte Tabellen abfragen → SQL Warehouses, Standard-Access-Mode-Compute (DBR ≥ 13.3 LTS), Dedicated-Access-Mode + Fine-Grained Access Control (DBR ≥ 15.4, Serverless im Workspace aktiviert), oder Dedicated-Access-Mode 13.3–15.3 nur wenn der Tabelleneigentümer selbst abfragt.

**Einschränkungen:**
- Nur Pipeline-Owner + Workspace-Admins sehen Driver-Logs standardmäßig.
- Hive-Metastore-Pipelines **nicht** direkt auf UC upgradebar — neue Pipeline mit Re-Ingestion nötig, oder Klon-Weg (Abschnitt 3).
- UC-Pipeline nicht erstellbar in Workspace an UC-Public-Preview-Metastore.
- JARs nicht unterstützt; nur Python-Drittanbieter-Libraries.
- DML, das ST-Schema ändert, nicht unterstützt.
- Eine in einer Pipeline erstellte MV nicht außerhalb dieser Pipeline als Streaming-Quelle nutzbar.
- Tabellendaten: Schema-Speicherort → sonst Katalog-Speicherort → sonst Metastore-Root.
- Catalog-Explorer-**History**-Tab zeigt keine Historie für MVs.
- `LOCATION`-Property bei Tabellendefinition nicht unterstützt.
- UC-Pipelines können nicht in Hive Metastore veröffentlichen.
- Globale Init-Skripte nicht unterstützt (Environment-Settings empfohlen; Classic: Cluster-scoped Init-Skripte möglich aber nicht empfohlen; Serverless: keine Init-Skripte).
- Python-UDF-Support: Public Preview.

> **Wichtig — PII in MV-Speicherdateien:** Backing-Dateien einer MV können Upstream-Daten (inkl. möglicher PII) enthalten, die in der Definition selbst nicht sichtbar sind (für inkrementelles Refresh automatisch hinzugefügt). Beispiel: `COUNT(DISTINCT field_a)` zeigt nur das Aggregat, Backing-Dateien enthalten aber die tatsächlichen `field_a`-Werte — Speicher nicht mit nicht vertrauenswürdigen Konsumenten teilen.

Ein Workspace kann UC- und Hive-Metastore-Pipelines parallel haben; eine einzelne Pipeline schreibt aber **nicht gleichzeitig** in beide. Bestehende Nicht-UC-Pipelines bleiben von neuen UC-Pipelines unberührt.

**Inaktive Tabellen:** entstehen wenn Definition aus Pipeline entfernt wird (nächstes Update markiert inaktiv), oder wenn Standardkatalog/-schema geändert wird ohne vollständig qualifizierte Namen (alte Tabelle inaktiv, neue am neuen Ort). Inaktive Tabellen bleiben abfragbar, werden nicht mehr aktualisiert; Aufräumen via `DROP`. Pipeline löschen → alle Tabellen werden gelöscht (UI-Bestätigung).

- Gelöschte Tabellen: **7 Tage** per `UNDROP` wiederherstellbar.
- Legacy-Verhalten (automatisches UC-Entfernen beim nächsten Update) beibehalten: `"pipelines.dropInactiveTables": "true"` — Daten bleiben ebenfalls 7 Tage, wiederherstellbar durch erneutes Hinzufügen der Definition.

```
DELETE /api/2.0/pipelines/{pipeline_id}?cascade=false
-- Ergebnis: Pipeline wird gelöscht, MV/ST/Views bleiben erhalten (inaktiv, aber abfragbar)
```

Inaktive Tabellen lassen sich in eine neue Pipeline verschieben (reaktiviert sobald an Flow angebunden, siehe Abschnitt 10).

**Nach UC schreiben:** beim Erstellen unter **Storage options** → **Unity Catalog** → Katalog (**Catalog**-Dropdown) + Schema (**Target schema**-Dropdown). Ein Teil der Backing-Daten landet im reservierten Katalog `__databricks_internal` (erwartetes Verhalten).

**In eine UC-Pipeline einlesen** — unterstützte Quellen: UC-Managed/-External-Tables, Views, MV, ST; Hive-Metastore-Tabellen/-Views; Auto Loader via `read_files()` aus UC-External-Locations; Apache Kafka, Amazon Kinesis.

```sql
-- Batch-Ingestion aus UC-Tabelle
CREATE OR REFRESH MATERIALIZED VIEW table_name
AS SELECT * FROM my_catalog.my_schema.table1;
```

```python
@dp.materialized_view
def table_name():
  return spark.read.table("my_catalog.my_schema.table")
```

```sql
-- Änderungen streamen
CREATE OR REFRESH STREAMING TABLE table_name
AS SELECT * FROM STREAM(my_catalog.my_schema.table1);
```

```python
@dp.table
def table_name():
  return spark.readStream.table("my_catalog.my_schema.table")
```

```sql
-- Aus Hive Metastore lesen (Katalog hive_metastore)
CREATE OR REFRESH MATERIALIZED VIEW table_name
AS SELECT * FROM <hms_federation_catalog>.some_schema.table;
```

```sql
-- Via Auto Loader
CREATE OR REFRESH STREAMING TABLE table_name
AS SELECT * FROM STREAM read_files("/path/to/uc/external/location", format => "json")
```

**Materialized Views freigeben** (Default: nur Pipeline-Owner darf abfragen):

```sql
GRANT SELECT ON TABLE my_catalog.my_schema.table_name TO `user@databricks.com`
REVOKE SELECT ON TABLE my_catalog.my_schema.table_name FROM `user@databricks.com`
GRANT CREATE { MATERIALIZED VIEW | TABLE } ON SCHEMA my_catalog.my_schema TO { principal | user }
```

**Lineage:** Catalog Explorer zeigt vor-/nachgelagerte Tabellen für MV/ST einer UC-Pipeline + Link zur produzierenden Pipeline (falls vom aktuellen Workspace aus zugänglich).

**DML an Streaming Tables:** `INSERT`, `UPDATE`, `DELETE`, `MERGE` möglich (z. B. DSGVO). Regeln: DML, das das Schema ändert, nicht unterstützt; nur auf Shared-UC-Cluster/SQL-Warehouse mit DBR ≥ 13.3 LTS; beim Streamen aus geänderter Quell-ST muss `skipChangeCommits` gesetzt werden (ändernde Transaktionen ignoriert) — alternativ MV als Ziel, wenn keine ST nötig.

```sql
DELETE FROM my_streaming_table WHERE id = 123;
UPDATE my_streaming_table SET name = 'Jane Doe' WHERE id = 123;
-- Ergebnis: Zeile id=123 gelöscht bzw. name aktualisiert; Schema der Tabelle bleibt unverändert
```

**Row Filter / Column Masks:** Row Filter filtern Zeilen beim Scan (nur `true`-Prädikat-Zeilen sichtbar); Column Masks maskieren Spaltenwerte beim Scan. Hinzufügen/Ändern/Entfernen via `CREATE OR REFRESH` auf MV/ST.

- Beim Refresh laufen Masken-/Filter-Funktionen mit Rechten des **Pipeline-Owners** (`CURRENT_USER`/`IS_MEMBER` im Owner-Kontext); beim Abfragen im Kontext des **abfragenden Nutzers**.
- MV über Quelltabellen mit Row Filter/Column Mask → Refresh ist **immer Full Refresh**.
- Audit: `DESCRIBE EXTENDED`, `INFORMATION_SCHEMA`, Catalog Explorer.

## 2. Hive Metastore (Legacy)

Alternative zu UC für Workspaces ohne UC. Nach Update abfragbar aus verschiedenen Umgebungen (SQL, Notebooks, andere Pipelines).

> **Wichtig:** Nur Tabellen/Metadaten werden veröffentlicht — **Views werden nicht in den Metastore veröffentlicht**.

- **Konfiguration:** Advanced Options → **„Use Hive Metastore"**; Standard-Zielschema verpflichtend.
- **Speicherort:** stets explizit angeben (Vermeidung von DBFS-Root-Schreiben) — Zugriff erfolgt in der Praxis meist über registrierte Tabellen.

```json
{ "clusters": [ { "aws_attributes": { "instance_profile_arn": "arn:aws:..." } } ] }
```
Alternativ: Settings → Compute → **Instance profile**-Dropdown, oder Cluster-Policy.

- **Event Log:** unter `/system/events` relativ zum Speicherort (z. B. `/Users/username/data/system/events`); ohne Speicherort: `/pipelines/<pipeline-id>/system/events` in DBFS.

```sql
CREATE OR REPLACE TEMP VIEW event_log_raw AS SELECT * FROM delta.`<event-log-path>`;

CREATE OR REPLACE TEMP VIEW latest_update AS
SELECT origin.update_id AS id FROM event_log_raw
WHERE event_type = 'create_update' ORDER BY timestamp DESC LIMIT 1;
```

Für Workspaces ohne UC: importierbare Beispiel-Notebooks (Python/SQL) verfügbar; Pfade nach Import im Feld **Source code** bei Storage-Option „Hive Metastore" angeben.

## 3. Hive-Metastore-Pipeline nach Unity Catalog klonen

REST-API-Klon-Mechanismus: dupliziert Quellcode/Konfiguration, passt Definitionen an UC an, **migriert Daten, Metadaten und Checkpoints** (Streaming Tables setzen an zuvor erreichter Position fort). Nach Klonen: Original und Klon unabhängig.

**Voraussetzungen:**
- Ziel-Pipeline muss Tabellen in festgelegtes Schema veröffentlichen.
- Alle HMS-Referenzen im Quellcode vollständig qualifiziert (`hive_metastore.sales.customers`).
- Quellcode der Quell-Pipeline während Klonens nicht editieren.
- Quell-Pipeline beim Start inaktiv (laufende Updates vorher abschließen/beenden).
- Hive-Metastore-Tabellen mit explizitem Speicherort (`path`/`LOCATION`) → `"pipelines.migration.ignoreExplicitPath": "true"` nötig.
- Auto Loader mit `cloudFiles.schemaLocation`, läuft nach Klonen weiter → **beide** Pipelines brauchen `mergeSchema: true`.

```bash
curl -X POST \
  --header "Authorization: Bearer <personal-access-token>" \
  <databricks-instance>/api/2.0/pipelines/<pipeline-id>/clone \
  --data @clone-pipeline.json
```

```json
{
  "catalog": "<target-catalog-name>",
  "target": "<target-schema-name>",
  "name": "<new-pipeline-name>",
  "clone_mode": "MIGRATE_TO_UC",
  "configuration": { "pipelines.migration.ignoreExplicitPath": "true" }
}
-- Ergebnis: API-Antwort liefert die ID der neuen UC-Pipeline
```
`clone_mode` unterstützt nur `"MIGRATE_TO_UC"`; `target`/`name` optional (Default: Quell-Schema-Name bzw. Quellname + `[UC]`).

**Klonen aus einem Notebook:**

```python
import requests

WORKSPACE = "<databricks-instance>"
SOURCE_PIPELINE_ID = "<pipeline-id>"
TARGET_CATALOG = "<target-catalog-name>"
TARGET_SCHEMA = "<target-schema-name>"
CLONED_PIPELINE_NAME = "<new-pipeline-name>"
CLONE_MODE = "MIGRATE_TO_UC"
OVERRIDE_CONFIGS = {"pipelines.migration.ignoreExplicitPath": "true"}

def get_token():
    ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
    return getattr(ctx, "apiToken")().get()

def request_pipeline_clone():
    payload = {"catalog": TARGET_CATALOG, "clone_mode": CLONE_MODE}
    if TARGET_SCHEMA: payload["target"] = TARGET_SCHEMA
    if CLONED_PIPELINE_NAME: payload["name"] = CLONED_PIPELINE_NAME
    if OVERRIDE_CONFIGS: payload["configuration"] = OVERRIDE_CONFIGS
    return requests.post(
        f"{WORKSPACE}/api/2.0/pipelines/{SOURCE_PIPELINE_ID}/clone",
        headers={"Authorization": f"Bearer {get_token()}"}, json=payload,
    ).json()
```

**Einschränkungen:** Declarative Automation Bundles können den Klon nicht ausführen; nur HMS→UC (nicht umgekehrt); Klon muss im selben Workspace bleiben. **Unterstützte Streaming-Quellen:** Delta, Auto Loader (alle Quellen), Kafka via Structured Streaming (`kafka.group.id` nicht nutzbar), Kinesis via Structured Streaming (`consumerMode` ≠ `efo`). Auto Loader im File-Notification-Modus: Quelle nach Klonen stoppen empfohlen (sonst `cloudFiles.backfillInterval` zur Wiederherstellung). Wartungsaufgaben pausieren während des Klonens für **beide** Pipelines. Time-Travel mit `timestamp_expression` für ursprünglich HMS-Managed-Versionen in geklonten UC-Tabellen **nicht definiert**; `version`-Klausel funktioniert unabhängig vom Ursprung korrekt.

## 4. Migration zum Default Publishing Mode (DPM)

DPM erlaubt einer Pipeline, in mehrere Kataloge/Schemas zu schreiben, mit vereinfachter Syntax. Legacy Mode gilt als veraltet, Migration empfohlen.

> **Wichtig:** Migration betrifft nur **Metadaten** — liest/verschiebt/schreibt **keine** Datasets.

**Legacy Mode erkennen:** **Summary**-Feld der Pipeline-Settings, Event-Log-Feld `effective_publishing_mode` (jüngstes `create_update`-Event), oder `effectivePublishingMode` in `GET /api/2.0/pipelines/{pipeline_id}`.

**Überlegungen:** Migration nicht via Declarative Automation Bundles unterstützt; **unumkehrbar**; ggf. Code-Vorbereitung nötig (meiste Pipelines brauchen keine Änderung); im Default Mode nicht mehr zwischen Schemas verschiebbar nach Erstellung; erfordert **Databricks CLI ≥ v0.230.0**.

**Ablauf:**
1. **Jobs & Pipelines** → Pipeline auswählen.
2. Updates pausieren, laufende Läufe beenden lassen; mind. 1 Update innerhalb der letzten **60 Tage** nötig (ggf. manuell starten; kontinuierlich: erst `RUNNING`, dann pausieren).
3. Optional: Code vorbereiten (siehe unten).
4. **Settings:** `pipelines.enableDPMForExistingPipeline` auf `true`.
5. Manuelles Update starten, abschließen lassen.
6. Optional: `pipelines.enableDPMForExistingPipeline` wieder entfernen.
7. Zeitplan/Updates reaktivieren.

**Code-Vorbereitung:**
- `LIVE`-Schlüsselwort: im Default Mode ignoriert, ersetzt durch Standardkatalog/-schema. Partiell qualifizierte Referenzen ohne `LIVE`: Legacy nutzt Spark-Defaults, Default Mode nutzt Pipeline-Defaults — bei Unterschied vor Migration vollständig qualifizieren.
- `LIVE`-Spaltenreferenzen: im Default Mode nicht zur Spaltendefinition nutzbar. `SELECT LIVE.source.id FROM LIVE.source` → `SELECT source.id FROM LIVE.source`.
- `flow_progress`-Event: Dataset-Name wechselt von `table` (Legacy) zu vollqualifiziertem `catalog.schema.table` (Default) — Event-Log-Queries anpassen.
- Selbstreferenzen (zirkulär): Legacy = Warnung, Default = **Fehler**. Mehrteilige Punkt-Namen (`@dlt.view(name="a.b.c")`) im Default Mode nicht erlaubt — vor Migration umbenennen (`@dp.temporary_view()` statt `@dlt.view` empfohlen).

| Fehler | Lösung |
|---|---|
| `CANNOT_MIGRATE_HMS_PIPELINE` | HMS-Pipelines nicht unterstützt — erst HMS→UC klonen (Abschnitt 3) |
| `MISSING_EXPECTED_PROPERTY` | kein aktuelles Update vor Flag-Aktivierung; Config entfernen, ggf. `pipelines.setMigrationHints=true`, Update ausführen, bei Schritt 3 fortsetzen |
| `PIPELINE_INCOMPATIBLE_WITH_DPM` | Code nicht vollständig kompatibel — Code-Vorbereitung prüfen |

## 5. LIVE-Schema (Legacy)

Virtuelles `LIVE`-Schema: Grenze für alle Datasets einer Pipeline, unabhängig von veröffentlichten Schemas. Legacy Mode: `SELECT * FROM LIVE.bronze_table`. Default Publishing Mode ignoriert diese Syntax — unqualifizierte Bezeichner referenzieren stattdessen das konfigurierte Pipeline-Schema.

> **Support-Hinweis:** `LIVE` und Legacy Publishing Mode sind für Entfernung in künftiger Version vorgesehen.

Zwei Migrationswege (beide unumkehrbar): Tabellen einzeln verschieben (Abschnitt 10) oder Default Publishing Mode aktivieren (Abschnitt 4). Neue Pipelines: nicht mehr im Legacy Mode über UI erstellbar — nur Tabellen von vor dem 5. Februar 2025 nutzen ihn noch standardmäßig.

**Speicherort-/Metadaten-Matrix (Legacy Mode):**

| Zielsystem | Konfiguration | Ergebnis |
|---|---|---|
| Hive Metastore | ohne Speicherort/Zielschema | Daten/Metadaten in DBFS-Root, keine Registrierung |
| Hive Metastore | Speicherort ohne Zielschema | Daten am Speicherort, keine Registrierung |
| Hive Metastore | Zielschema ohne Speicherort | Daten in DBFS-Root, Tabellen im Hive-Schema veröffentlicht |
| Hive Metastore | beides angegeben | Daten am Speicherort, Tabellen im Hive-Schema veröffentlicht |
| Unity Catalog | Katalog ohne Zielschema | Daten im Katalog-Standard-Speicherort, keine Registrierung |
| Unity Catalog | Katalog + Schema | Daten im Schema-/Katalog-Standard-Speicherort, Tabellen im UC-Schema veröffentlicht |

**Quellcode-Anpassung:** Legacy löste unqualifizierte Referenzen gegen Workspace-Default (z. B. `main.default.raw_data`) auf; Default Mode nutzt konfigurierten Pipeline-Katalog/-Schema:

```sql
-- Legacy
CREATE MATERIALIZED VIEW silver_table AS SELECT * FROM raw_data

-- Aktualisiert
CREATE MATERIALIZED VIEW silver_table AS SELECT * FROM main.default.raw_data
```

**Event Log für UC-Legacy-Pipelines** (TVF `event_log`, nach Pipeline-ID oder Tabellen-Zugehörigkeit):

```sql
SELECT * FROM event_log("04c78631-3dd7-4856-b2a6-7d84e9b2638b")
SELECT * FROM event_log(TABLE(my_catalog.my_schema.table1))
```
Erfordert SQL Warehouse oder Shared Cluster. Nur Pipeline-Owner kann aufrufen; keine Multi-Pipeline-Abfrage; erstellte Views nicht mit anderen Nutzern teilbar.

## 6. ALTER-SQL-Anweisungen mit Pipeline-Datasets

**`ALTER STREAMING TABLE`** und **`ALTER MATERIALIZED VIEW`** — funktionieren über Lakeflow-Pipelines, Lakeflow-Connect-Ingestion-Pipelines und Standalone-Databricks-SQL-Pipelines hinweg. Bei Standalone-Pipeline-Datasets zusätzlich `SET OWNER TO` für Eigentümerwechsel.

> **Zentrale Einschränkung:** Der Pipeline-SQL-Code läuft bei jedem Update erneut — kann `ALTER`-Änderungen rückgängig machen.

```sql
CREATE OR REPLACE MATERIALIZED VIEW masked_view (
    id int, name string, region string,
    ssn string MASK catalog.schema.ssn_mask_fn
)
WITH ROW FILTER catalog.schema.us_filter_fn ON (region)
AS SELECT id, name, region, ssn FROM employees;
```

```sql
ALTER MATERIALIZED VIEW masked_view ALTER COLUMN ssn DROP MASK;
-- Ergebnis: Maske entfernt — ABER: nächster Refresh stellt sie wieder her,
-- da die Original-Definition die Maskierung erneut anwendet
```

**Lösung:** zuerst die SQL-Definition der Pipeline anpassen, erst danach `ALTER` ausführen. **Nicht unterstützt:** Zeitplan/Trigger eines in Lakeflow Pipelines definierten Datasets per `ALTER` ändern.

## 7. Pipeline-Updates ausführen

Ein Update: Cluster starten → alle definierten Tabellen/Views ermitteln → auf Analysefehler prüfen (ungültige Spaltennamen, fehlende Abhängigkeiten, Syntaxfehler) → Tabellen/Views mit aktuellsten Daten erstellen/aktualisieren.

| Auslöser | Details |
|---|---|
| Manuell | Lakeflow Pipelines Editor oder Pipelines-Liste |
| Geplant | Jobs, Pipeline-Task |
| Programmatisch | Drittanbieter-Tools, APIs, CLIs |

Manuell ausgelöste Updates aktualisieren standardmäßig alle definierten Datasets.

**Refresh-Semantik:**

| Update-Typ | Materialized View | Streaming Table |
|---|---|---|
| Refresh (Standard) | kostenbasierte Wahl inkrementell/voll | verarbeitet nur neue Datensätze |
| Full Refresh | vollständige Neuberechnung | Tabelle geleert, Checkpoints gelöscht, alle Quelldaten neu |
| Reset Streaming Flow Checkpoints | nicht anwendbar | nur Checkpoints gelöscht (Daten bleiben), Quelle neu verarbeitet |

- Standard-Update aktualisiert alle MV/ST; gezielt ausschließbar via **Select tables for refresh** / **Refresh failed tables** (beide: Standard + Full Refresh).
- Full Refresh nur bei Bedarf (Dauer/Ressourcen ∝ Quellgröße). MV liefert in beiden Fällen gleiches Ergebnis; ST-Full-Refresh setzt State/Checkpoints zurück → möglicher Datenverlust bei nicht mehr verfügbaren Eingabedaten:

| Datenquelle | Grund für Fehlen | Ergebnis eines Full Refresh |
|---|---|---|
| Kafka | kurze Retention | nicht mehr in Kafka vorhandene Datensätze werden aus Zieltabelle entfernt |
| Objektspeicher | Lifecycle-Richtlinie | nicht mehr vorhandene Dateien werden entfernt |
| Tabellendatensätze | Compliance-Löschung | nur noch in Quelltabelle vorhandene Datensätze verarbeitet |

- Full-Refresh-Schutz: Tabellen-Property `pipelines.reset.allowed = false` (Abschnitt 8); alternativ Append Flow statt Full Refresh.

**Selektive/fehlgeschlagene Tabellen:** Editor bietet erneutes Verarbeiten für Datei/ausgewählte Tabellen/einzelne Tabelle. Nach Fehlschlag: **Refresh failed tables** (Monitoring-Seite) oder **Select tables for refresh** → Auswahl → **Refresh selection** (**Full Refresh selection** über Pfeil daneben).

**Selektiver Checkpoint-Reset:** für ausgewählte Streaming Flows Daten neu verarbeiten ohne bereits eingelesene zu löschen (andere Flows laufen normal weiter) — via `updates`-Request + `reset_checkpoint_selection` (Liste vollqualifizierter Flow-Namen `catalog.schema.flow_name`; einfacher Name → `IllegalArgumentException`). Bei explizitem `flow_name` (z. B. `create_auto_cdc_flow`): `<catalog>.<schema>.<flow_name>`; ohne expliziten Namen: vollqualifizierter Zieltabellenname.

```bash
curl -X POST \
-H "Authorization: Bearer <your-token>" \
-H "Content-Type: application/json" \
-d '{"reset_checkpoint_selection": ["my_catalog.my_schema.my_streaming_table"]}' \
https://<your-databricks-instance>/api/2.0/pipelines/<your-pipeline-id>/updates
```

**Dry Run (Public Preview):** löst Definitionen auf, materialisiert/veröffentlicht nichts; meldet Fehler (falsche Tabellen-/Spaltennamen). Start: Pfeil neben **Start** → **Dry run**. Ergebnisse (Fehler, Incrementalization Insights) im Event-Tray; Event Log zeigt nur Dry-Run-Events; kein Metriken-Update im Graph. Sichtbar nur solange Dry Run das jüngste Update ist.

**Verfügbarkeit von Update-Ergebnissen** (Retention **60 Tage**):

| Update-Typ | Verfügbar solange | Entfernt, wenn |
|---|---|---|
| Reguläres Update | innerhalb Retention oder noch aktiv | abgeschlossen + älter als Retention |
| Dry Run | jüngstes Update | ein späteres Update startet (auch Dry Run) |

Event-Log-Ereignisse bleiben in jedem Fall erhalten, auch wenn UI-Ergebnisse verschwinden.

**Ausführungsverhalten je Auslöser:**
- **Fast-Start (Debugging):** UI-„Run now", Ad-hoc-Updates. Cluster wiederverwendet (Standard 2h, via `pipelines.clusterShutdown.delay`); Retries deaktiviert (sofortige Fehlererkennung).
- **Automatisches Retry/Restart:** Jobs, API-Aufrufe, kontinuierliche Pipelines. Cluster-Neustart bei behebbaren Fehlern (Memory Leaks, abgelaufene Credentials); Retry bei bestimmten Fehlern (z. B. Cluster-Start fehlgeschlagen); Cluster fährt sofort nach Abschluss herunter.

Bei getriggerten Pipelines: einzelner Lauf via **Run now with different settings** überschreibbar. Ausführungsverhalten steuert nur Cluster-/Pipeline-Ausführung, nicht Speicherorte/Zielschemas.

## 8. Pipeline-Properties-Referenz

Konfiguration ist größtenteils eine Obermenge der SDP-Projekt-Spezifikation.

**Wie Properties gesetzt werden:**
- Pipeline-JSON/-YAML → Pipeline-Level (`catalog`, `channel`, `edition`).
- `configuration`-Objekt → Spark-Config mit Präfix `pipelines.` für gesamte Pipeline.
- SQL `SET` → nachfolgende Datasets in derselben Datei.
- Python `spark_conf`-Argument → einzelnes Dataset.

Dataset-Ebene überschreibt Pipeline-Level.

**Wichtige Pipeline-Konfigurationen:**

| Property | Default | Beschreibung |
|---|---|---|
| `id` | systemvergeben | eindeutige, unveränderliche Pipeline-ID |
| `name` | erforderlich | Anzeigename |
| `configuration` | optional | Spark-Config Key-Value |
| `parameters` | optional (Beta) | Named-Parameter, nur SQL, nur Lakeflow |
| `libraries` | erforderlich | Array der Code-Dateien |
| `clusters` | automatisch | Cluster-Spezifikationen |
| `development` | `false` | Dev- vs. Prod-Modus |
| `notifications` | optional | E-Mail-Benachrichtigungen |
| `continuous` | `false` | kontinuierlicher Lauf |
| `catalog` | ungesetzt (legacy Hive) | Standardkatalog; Setzen aktiviert UC |
| `schema` | erforderlich | Standardschema |
| `target` (legacy) | — | veralteter Alias für `schema` |
| `storage` (legacy) | `dbfs:/pipelines/` | Speicherort, unveränderlich nach Erstellung |
| `channel` | `current` | `preview` oder `current` |
| `edition` | `ADVANCED` | `CORE`/`PRO`/`ADVANCED` |
| `photon` | `false` | Photon-Engine |
| `serverless` | — | Serverless Compute |
| `event_log` | optional | Ziel für UC-Event-Log-Veröffentlichung |
| `tags` | optional | max. 25 |
| `budget_policy_id` | automatisch | Serverless-Budget-Policy |
| `root_path` | optional | wird zu `sys.path` hinzugefügt |
| `environment` | optional | Python-Abhängigkeiten |
| `pipelines.maxFlowRetryAttempts` | **2** | Retry-Versuche je Flow bei wiederholbarem Fehler (insgesamt 3 Ausführungsversuche) |
| `pipelines.numUpdateRetryAttempts` | **5 (getriggert) / unbegrenzt (kontinuierlich)** | Retry-Versuche für gesamtes Update, nur bei automatischem Retry-/Restart-Verhalten |

**Pipeline-Tabellen-Properties:**

| Property | Default | Beschreibung |
|---|---|---|
| `pipelines.autoOptimize.zOrderCols` | keiner | Z-Order-Spalten, kommasepariert — Liquid Clustering stattdessen empfohlen |
| `pipelines.reset.allowed` | `true` | erlaubt Full Refresh für diese Tabelle |
| `pipelines.autoOptimize.managed` | `true` | automatisch geplante Optimierung |

`pipelines.reset.allowed = false` schützt vor Datenverlust, wenn die Rohquelle Dateien per Lifecycle-Richtlinie entfernt: ohne Schutz würde ein Full Refresh die Tabelle leeren und dann nur noch nachlesen, was in der Quelle tatsächlich noch existiert; mit `false` bleiben bereits eingelesene, inzwischen entfernte Daten erhalten.

**Trigger-Intervall** (`pipelines.trigger.interval`) — Default abhängig vom Flow-Typ: **5s** Streaming-Abfragen, **1 Min.** Complete-Abfragen aus reinen Delta-Quellen, **10 Min.** Complete-Abfragen mit möglichen Nicht-Delta-Quellen. Format: Zahl + Einheit (`second(s)`, `minute(s)`, `hour(s)`, `day(s)`).

```python
@dp.table(spark_conf={"pipelines.trigger.interval" : "10 seconds"})
def <function-name>():
    return (<query>)
```
```sql
SET pipelines.trigger.interval=10 seconds;
CREATE OR REFRESH MATERIALIZED VIEW TABLE_NAME AS SELECT ...
```
```json
{ "configuration": { "pipelines.trigger.interval": "10 seconds" } }
```
Empfohlen: pro Tabelle setzen (Streaming/Batch unterschiedliche Defaults); Pipeline-Ebene nur bei einheitlicher Steuerung des gesamten Graphen.

**Nicht vom Nutzer setzbare Cluster-Attribute:** `cluster_name`, `data_security_mode`/`access_mode`, `spark_version`, `autotermination_minutes`, `runtime_engine` (nur indirekt via Photon), `effective_spark_version`, `cluster_source`, `docker_image`, `workload_type` — vom System verwaltet (Pipeline kontrolliert Cluster-Lebenszyklus; nur relevant für Lakeflow-Pipelines, nicht SDP).

**Quellen-/Query-Optionen:** Schema-Evolution, Schema Hints/-Inferenz, Ingestion-Rate-Limits, Datei-Filterung: nicht als Pipeline-Property, sondern über `read_files`-/Auto-Loader-Optionen (für `from_json`: eigene Schema-Evolution-Syntax).

## 9. Pipelines parametrisieren (Beta)

Veränderliche Key-Value-Paare, machen Quellcode über Umgebungen/Datasets wiederverwendbar. Workspace-Admins steuern Zugriff über Previews-Seite. Werte nur Strings; gültige Key-Zeichen: alphanumerisch, `_`, `-`, `.`.

| Parameter | Configuration |
|---|---|
| Werte, die sich zwischen Updates ändern (Zielkatalog, Quellpfad) | statische, strukturelle Pipeline-Eigenschaften |
| von Job-/Task-Ebene durchgereicht | Spark-Konfiguration (z. B. `pipelines.enzyme.enabled`) |
| SQL-Named-Parameter-Syntax | `${key}` in SQL oder `spark.conf.get("key")` in Python |

**Definieren** (UI: Settings → **Parameters** → Edit; oder JSON/REST):

```json
{ "name": "Sales pipeline", "parameters": { "source_catalog": "dev_catalog", "source_schema": "sales", "start_date": "2026-01-01" } }
```

oder YAML/Bundle:

```yaml
resources:
  pipelines:
    my_pipeline:
      name: Sales pipeline
      parameters:
        source_catalog: dev_catalog
        source_schema: sales
        start_date: '2026-01-01'
```

**Im SQL referenzieren** (Doppelpunkt-Syntax):

```sql
CREATE OR REFRESH MATERIALIZED VIEW transaction_summary AS
SELECT account_id, COUNT(txn_id) AS txn_count, SUM(txn_amount) AS account_revenue
FROM :source_catalog.sales.transactions
WHERE txn_date >= :start_date
GROUP BY account_id
```

Für Bezeichner-Positionen: `IDENTIFIER()`:

```sql
USE CATALOG IDENTIFIER(:source_catalog);
USE SCHEMA IDENTIFIER(:source_schema);
CREATE OR REFRESH MATERIALIZED VIEW daily_sales AS
SELECT date(timestamp) AS date, SUM(price) AS total_sales
FROM transactions GROUP BY date;
```

Fehlende Parameterwerte → Update schlägt fehl; nicht referenzierte Parameter werden ignoriert.

**Überschreiben/Priorität:** Pipeline-UI (**Run with different settings**), Pipeline-Task im Job, API (Parameter-Map im Start-Update-Request). Priorität (höchste zuerst): Job-Run-Parameter → Job-Parameter → Pipeline-Task-Parameter → Pipeline-Parameter (Standardwerte). In Lakeflow Jobs: Tasks überschreiben Defaults; dynamische Referenzen wie `{{job.trigger.time.iso_date}}`, `{{job.parameters.region}}`, `{{tasks.<task_name>.values.<value_name>}}` nutzbar; Job-Parameter kaskadieren automatisch zu Pipeline-Tasks.

**Einschränkungen:**
- **Concurrency:** Pipelines laufen sequenziell (max. 1 Update gleichzeitig) — bei `max_concurrent_runs` > 1 oder For-Each-Task-Einbettung wird Concurrency auf 1 begrenzt.
- **Datumsfilterung:** Filterung auf **beiden Seiten** eines Datumsbereichs macht inkrementelle MV-Verarbeitung ungültig (Full Refresh bei jedem Update):

```sql
-- Problematisch (Full Refresh)
WHERE order_date >= :start_date AND order_date < :end_date;

-- Bevorzugt (inkrementell)
WHERE order_date >= :start_date;
```

- **Sprachunterstützung:** Named Parameters nur SQL; Python braucht das Configuration-Feld.

**Configuration-Feld (älterer Mechanismus, funktioniert parallel):**

```sql
CREATE OR REFRESH MATERIALIZED VIEW customer_events
AS SELECT * FROM source_table WHERE date > '${mypipeline.start_date}';
```

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col

@dp.table
def customer_events():
  start_date = spark.conf.get("mypipeline.start_date")
  return spark.read.table("source_table").where(col("date") > start_date)
```

## 10. Tabellen zwischen Pipelines verschieben

ST und MV ohne Full Refresh/Datenverlust von einer Pipeline in eine andere verschiebbar. Anwendungsfälle: große Pipelines aufteilen, separate Pipelines konsolidieren, individuelle Refresh-Zeitpläne, Übergang von älteren Publishing-Methoden, Verschieben über Workspace-Grenzen.

**Voraussetzungen:**
- DBR **≥ 16.3** für `ALTER`; **≥ 17.2** speziell für Workspace-übergreifende Verschiebungen.
- Beide Pipelines teilen sich einen Metastore (prüfbar mit `current_metastore`).
- Ausführender Nutzer/Service Principal = Run-As-User für **beide** Pipelines; beide gehören ihm.
- Ziel-Pipeline sollte im Default Publishing Mode laufen; alternativ beide im Legacy Mode mit identischen `catalog`-/`target`-Einstellungen.
- **Nicht unterstützt:** Default-Mode-Pipeline → Legacy-Mode-Pipeline.

**Ablauf:**
1. Quell-Pipeline anhalten (vollständig beenden lassen).
2. Tabellendefinition aus Quellcode der Quell-Pipeline entfernen (abhängiger, weiterhin benötigter Code bleibt).
3. `ALTER`-Befehl ausführen (aus Notebook/SQL-Editor im Workspace der Quell-Pipeline):

```sql
ALTER [MATERIALIZED VIEW | STREAMING TABLE | TABLE] <table-name>
SET TBLPROPERTIES("pipelines.pipelineId"="<destination-pipeline-id>");
-- Ergebnis: Tabelle wird der Ziel-Pipeline zugeordnet; Quell-Pipeline behandelt sie fortan als extern
```
`ALTER MATERIALIZED VIEW` (UC-MV), `ALTER STREAMING TABLE` (UC-ST), `ALTER TABLE` (Hive-Metastore-Tabellen); `pipelineId` muss gültig sein (`null` nicht erlaubt).

4. Tabelle zur Ziel-Pipeline hinzufügen (Definition in Ziel-Code einfügen). Bei abweichenden Katalog-/Schema-Einstellungen: vollständig qualifizieren. Append-once-Flows entfernen/auskommentieren, um erneute Ausführung zu vermeiden.

**Beispiel** (Verschieben von `table_b` aus einer 3-Tabellen-Pipeline):

```python
# Quell-Pipeline vorher
@dp.table
def table_a():
    return spark.read.table("source_table")

@dp.table
def table_b():
    return spark.read.table("table_a").select(col("column1"), col("column2"))

@dp.table
def table_c():
    return spark.read.table("table_b").groupBy(col("column1")).agg(sum("column2").alias("sum_column2"))
```

```sql
ALTER MATERIALIZED VIEW table_b
SET TBLPROPERTIES("pipelines.pipelineId"="<new-pipeline-id>");
```

```python
# Ziel-Pipeline (vollständig qualifizierte Variante)
@dp.table(name="source_catalog.source_schema.table_b")
def table_b():
    return (
        spark.read.table("source_catalog.source_schema.table_a")
        .select(col("column1"), col("column2"))
    )
```

| Fehler | Erklärung |
|---|---|
| `DESTINATION_PIPELINE_NOT_IN_DIRECT_PUBLISHING_MODE` | Quelle im Default Mode, Ziel im Legacy-LIVE-Modus — nicht unterstützt |
| `PIPELINE_TYPE_NOT_WORKSPACE_PIPELINE_TYPE` | nur Workspace-Pipelines verschiebbar, keine Standalone-Tabellen |
| `DESTINATION_PIPELINE_NOT_FOUND` | `pipelineId` ungültig oder `null` |
| Tabelle aktualisiert sich nicht im Ziel | Rückverschiebung zur Quelle zur schnellen Wiederherstellung |
| `PIPELINE_PERMISSION_DENIED_NOT_OWNER` | beide Pipelines müssen dem ausführenden Nutzer gehören |
| `TABLE_ALREADY_EXISTS` | kollidierende Backing-Tabelle per `DROP` entfernen |

**Einschränkungen:** Eigenständige MV/ST nicht verschiebbar; Append-once-Flows (`append_flow(once=True)`, `INSERT INTO ONCE`) nicht unterstützt (Status bleibt nicht erhalten); private Tabellen/Views ausgeschlossen; beide Pipelines müssen Workspace-Pipelines im selben Workspace/mit gemeinsamem Metastore sein; Eigentümer-Anforderung gilt für beide; Default-Mode-Pipelines nicht zu Legacy-Mode verschiebbar; bei Legacy-Mode müssen Quelle/Ziel übereinstimmende `catalog`-/`target`-Einstellungen haben.

---

**Stand:** 2026-09-14.
