# Migration zum Default Publishing Mode (DPM)

Dieses Dokument beschreibt, wie Pipelines, die das legacy `LIVE`-Virtual-Schema (Legacy Publishing Mode) nutzen, zum aktuellen **Default Publishing Mode** migriert werden. Jede Aussage wurde per `WebFetch` gegen `docs.databricks.com/aws/en/ldp/migrate-to-dpm` verifiziert; spezifische Zahlenwerte (CLI-Version, Tage-Frist) wurden zusätzlich über die Azure-Spiegelseite `learn.microsoft.com/en-us/azure/databricks/ldp/migrate-to-dpm` wörtlich gegengeprüft.

## Abschnittsübersicht

1. [Was ist der Default Publishing Mode?](#was-ist-dpm)
2. [Legacy Publishing Mode erkennen](#erkennen)
3. [Wichtige Überlegungen vor der Migration](#ueberlegungen)
4. [Migrationsschritte](#migrationsschritte)
5. [Pipelines auf die Migration vorbereiten](#vorbereiten)
6. [Troubleshooting](#troubleshooting)
7. [Quellen](#quellen)

---

## <a id="was-ist-dpm">1. Was ist der Default Publishing Mode?</a>

Der Default Publishing Mode erlaubt, dass **eine einzelne Pipeline in mehrere Kataloge und Schemas schreibt**, und bringt eine vereinfachte Syntax für die Arbeit mit Tabellen und Views innerhalb der Pipeline mit. Der Legacy Publishing Mode gilt als veraltet; Databricks empfiehlt, alle Pipelines auf den Default Publishing Mode zu migrieren.

**Wichtige Klarstellung zum Umfang der Migration:** Die Migration betrifft nur die **Metadaten** der Pipeline — sie liest, verschiebt oder schreibt **keine** Datasets.

---

## <a id="erkennen">2. Legacy Publishing Mode erkennen</a>

Drei Indikatoren zeigen an, ob eine Pipeline im Legacy Mode arbeitet:

1. Das **Summary**-Feld in den Lakeflow-Pipeline-Einstellungen der UI.
2. Das Lakeflow-Pipeline-Event-Log: Das jüngste `create_update`-Ereignis enthält `effective_publishing_mode`.
3. Die Pipelines-API-Antwort `GET /api/2.0/pipelines/{pipeline_id}` enthält `effectivePublishingMode`.

---

## <a id="ueberlegungen">3. Wichtige Überlegungen vor der Migration</a>

- Die Migration zum Default Publishing Mode wird über Declarative Automation Bundles **nicht** unterstützt.
- Nach der Migration zum Default Publishing Mode kann die Pipeline **nicht** zurück zum `LIVE`-Virtual-Schema migriert werden — die Umstellung ist endgültig.
- Je nach Syntaxunterschieden zwischen Legacy und Default Mode kann eine Vorbereitung des Codes nötig sein — die meisten Pipelines benötigen aber keine Änderungen.
- Im Default Publishing Mode können Materialized Views und Streaming Tables nach ihrer Erstellung nicht mehr zwischen Schemas verschoben werden.
- Der Default Publishing Mode erfordert **Databricks CLI Version v0.230.0 oder höher**.

---

## <a id="migrationsschritte">4. Migrationsschritte</a>

1. In der Seitenleiste des Workspace auf **Jobs & Pipelines** klicken.
2. Den Namen der zu migrierenden Pipeline in der Liste anklicken.
3. Updates pausieren und laufende Pipeline-Läufe beenden lassen.

    Innerhalb der letzten **60 Tage** vor Abschluss der Migration muss mindestens ein Update gelaufen sein. Ist die Pipeline getriggert oder bereits pausiert, muss manuell ein einzelnes Update ausgeführt werden. Ist die Pipeline kontinuierlich, muss sie zunächst in den Status `RUNNING` gelangen (bzw. bereits dort sein) und anschließend pausiert werden.
4. Optional: vorbereitenden Code anpassen, der migriert werden muss (siehe Abschnitt 5).
5. In den Pipeline-**Settings** die Konfiguration `pipelines.enableDPMForExistingPipeline` hinzufügen und auf `true` setzen.
6. Ein manuelles Update starten und abschließen lassen.
7. Optional: die Konfiguration `pipelines.enableDPMForExistingPipeline` aus den **Settings** wieder entfernen — sie wird nur für die Migration benötigt.
8. Bei Bedarf Zeitplan aktualisieren und Pipeline-Updates wieder aktivieren.

Nach erfolgreichem Abschluss ist der Default Publishing Mode für die Pipeline aktiv. Bei anhaltenden Problemen empfiehlt die Doku, den Databricks Account Manager zu kontaktieren.

---

## <a id="vorbereiten">5. Pipelines auf die Migration vorbereiten</a>

Der Default Publishing Mode ist grundsätzlich rückwärtskompatibel mit dem Legacy Publishing Mode, dennoch können folgende Anpassungen nötig sein:

### Das `LIVE`-Schlüsselwort

Im Legacy Mode qualifiziert das Schlüsselwort `LIVE` Katalog und Schema eines Objekts mit den Pipeline-Standardwerten. Der Default Publishing Mode nutzt `LIVE` nicht mehr zur Qualifizierung — das Schlüsselwort wird ignoriert und durch den Standardkatalog und das Standardschema der Pipeline ersetzt (in der Regel dieselben Werte wie zuvor, sofern nicht später `USE CATALOG`- oder `USE SCHEMA`-Befehle hinzugefügt werden).

Im Legacy Mode nutzen partiell qualifizierte Tabellen-/View-Referenzen ohne `LIVE`-Schlüsselwort (z. B. `table1`) die Spark-Standardwerte. Im Default Mode nutzen partiell qualifizierte Referenzen stattdessen die Pipeline-Standardwerte. Unterscheiden sich Spark-Standardwerte und Pipeline-Einstellungen, sollten partiell qualifizierte Namen vor der Migration vollständig qualifiziert werden.

**Hinweis:** Nach der Migration kann das `LIVE`-Schlüsselwort aus dem Code entfernt oder durch vollständig qualifizierte Tabellen-/View-Namen ersetzt werden.

### Spaltenreferenzen mit dem `LIVE`-Schlüsselwort

Im Default Publishing Mode kann `LIVE` **nicht** zur Definition von Spalten verwendet werden. Dieser Code:

```sql
CREATE OR REPLACE MATERIALIZED VIEW target AS SELECT LIVE.source.id FROM LIVE.source;
```

müsste vor der Migration wie folgt ersetzt werden:

```sql
CREATE OR REPLACE MATERIALIZED VIEW target AS SELECT source.id FROM LIVE.source;
```

Diese Variante funktioniert in beiden Publishing-Modi.

### Änderungen am `flow_progress`-Event

Die Migration ändert den Dataset-Namen für das `flow_progress`-Ereignis im Event Log. Im Legacy Mode ist der Dataset-Name der `table`-Name; im Default Mode ist es der vollständig qualifizierte `catalog.schema.table`-Name. Bestehende Event-Log-Abfragen müssen entsprechend angepasst werden.

### Von Warnungen zu Fehlern

Manche Warnungen des Legacy Publishing Mode werden im Default Publishing Mode zu Fehlern:

**Selbstreferenzen (zirkuläre Referenzen):** Eine Selbst- bzw. zirkuläre Referenz ist im Default Publishing Mode nicht erlaubt (im Legacy Mode war das Ergebnis undefiniert):

```sql
CREATE OR REPLACE MATERIALIZED VIEW table1 AS SELECT * FROM target_catalog.target_schema.table1;
```

Dies erzeugte im Legacy Mode eine Warnung (mit undefiniertem Ergebnis); im Default Mode erzeugt es einen Fehler.

**Mehrteilige Namen (Punkte in Namen):** Punkte in Namen (mehrteilige Namen) sind im Default Publishing Mode nicht erlaubt. Folgender Python-Code ist im Legacy Mode gültig, im Default Mode jedoch nicht:

```python
@dlt.view(name="a.b.c")
def transform():
  return …
```

Vor der Migration muss die Tabelle umbenannt werden, sodass der Name keinen Punkt mehr enthält.

**Hinweis:** Dieses Beispiel nutzt zusätzlich die ältere `@dlt.view`-Syntax; Databricks empfiehlt für Pipelines `@dp.temporary_view()`.

---

## <a id="troubleshooting">6. Troubleshooting</a>

| Fehler | Beschreibung/Lösung |
|---|---|
| `CANNOT_MIGRATE_HMS_PIPELINE` | Migration wird für Hive-Metastore-Pipelines nicht unterstützt. Alternative: Pipeline vor der Migration von Hive Metastore zu Unity Catalog klonen (siehe `HMS zu UC klonen.md`). |
| `MISSING_EXPECTED_PROPERTY` | Zeigt an, dass vor dem Hinzufügen der Konfiguration `pipelines.enableDPMForExistingPipeline` kein aktuelles Update gelaufen ist. Diese Konfiguration entfernen und — falls sie fehlt — die Konfiguration `pipelines.setMigrationHints` auf `true` setzen, ein Update ausführen und dann bei Schritt 3 fortfahren. |
| `PIPELINE_INCOMPATIBLE_WITH_DPM` | Zeigt an, dass der Pipeline-Code nicht vollständig mit dem Default Publishing Mode kompatibel ist (siehe Abschnitt 5). |

---

## <a id="quellen">7. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/migrate-to-dpm
- https://learn.microsoft.com/en-us/azure/databricks/ldp/migrate-to-dpm (Gegenprüfung: CLI-Version v0.230.0, 60-Tage-Frist)

**Stand:** 2026-08-19
