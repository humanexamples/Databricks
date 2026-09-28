# Environment-Versionen

## Abschnittsübersicht

1. [Zweck](#zweck)
2. [Voraussetzung: Unity Catalog](#voraussetzung)
3. [Unterstützte Versionen](#versionen)
4. [Konfigurationswege](#konfiguration)
5. [Automatische Migration](#automatische-migration)
6. [Hinweis zu Spark Connect](#spark-connect)
7. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck</a>

Eine Environment-Version fixiert die Python-Sprachversion sowie die Menge vorinstallierter Python-Bibliotheken, die dem Pipeline-Code zur Verfügung stehen — wörtlich: *"An environment version pins the Python language version and the set of preinstalled Python libraries"* — und entkoppelt damit die Python-Laufzeit von Databricks-Runtime-Upgrades.

---

## <a id="voraussetzung">2. Voraussetzung: Unity Catalog</a>

Die Doku verlangt ausdrücklich Unity Catalog: *"The pipeline must use Unity Catalog. Hive metastore pipelines are not supported."* Pipelines auf Basis des Hive-Metastore werden nicht unterstützt.

---

## <a id="versionen">3. Unterstützte Versionen</a>

Lakeflow-Pipelines unterstützen die Environment-Versionen 3 und 4, sowohl auf serverlosem als auch auf klassischem Compute — wörtlich: *"Lakeflow pipelines support environment versions 3 and 4 on both serverless and classic compute."*

---

## <a id="konfiguration">4. Konfigurationswege</a>

Drei Wege zur Konfiguration der Environment-Version:

1. **UI**: In den Pipeline-Einstellungen eine Environment-Version aus dem Dropdown auswählen.
2. **REST API**: POST-Request mit einem `environment`-Block, der `environment_version` und optional `dependencies` enthält.
3. **Bundles**: Felder `environment_version` und `dependencies` in der Pipeline-YAML-Definition ergänzen.

---

## <a id="automatische-migration">5. Automatische Migration</a>

Hat eine Pipeline keine `environment_version` explizit gesetzt, kann Databricks sie beim nächsten Update automatisch auf eine Environment-Version migrieren. Ausgenommen von der automatischen Migration sind Pipelines mit ungelösten Spark-Connect-Kompatibilitätswarnungen (siehe `Environment-Versionskompatibilitaet.md`), Pipelines ohne Unity Catalog sowie Pipelines, die `foreach_batch`-Sinks, Event Hooks, AUTO CDC oder Custom Images nutzen.

Der Migrationsvorgang enthält zwei Schutzmechanismen:

- **Verhaltensprüfung:** Der Code wird auf Muster geprüft, die sich unter Spark Connect anders verhalten würden; die Output-Pläne vor und nach der Migration werden verglichen.
- **Automatisches Rollback:** Schlägt die Migration fehl, wird das Update gestoppt, bevor Daten geschrieben werden, und die Pipeline kehrt automatisch zur vorherigen Laufzeitumgebung zurück.

Eine manuell gesetzte `environment_version` wird von der automatischen Migration nie überschrieben. Nach erfolgreicher Migration läuft die Pipeline dauerhaft mit der neuen Environment-Version. Welche Version eine gegebene Pipeline tatsächlich nutzte, lässt sich im Event Log am Feld `effective_environment_version` ablesen (siehe `13 Observability/Event-Log-Schema.md`, Details für `runtime_details`).

## <a id="spark-connect">6. Hinweis zu Spark Connect</a>

Pipelines mit Environment-Versionen führen Python-Code über Spark Connect aus (*"run Python code through Spark Connect"*), was das Pipeline-Verhalten verändert. Die Doku empfiehlt, vor der Aktivierung an bestehenden Pipelines die Kompatibilitäts-Hinweise zu prüfen (siehe [Environment-Versionskompatibilitaet.md](Environment-Versionskompatibilitaet.md)).

---

## <a id="quellen">7. Quellen</a>

- Configure the environment version (Zweck, Unity-Catalog-Voraussetzung, unterstützte Versionen 3/4, Konfigurationswege UI/REST/Bundle, automatische Migration, Spark-Connect-Hinweis): https://docs.databricks.com/aws/en/ldp/developer/environment-versions

**Stand:** 2026-08-20.
