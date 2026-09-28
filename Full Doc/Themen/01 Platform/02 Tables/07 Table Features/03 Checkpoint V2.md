# Checkpoint V2

„Checkpoint V2 unterstützt mehr nebenläufige Writer und reduziert Schreibkonflikte auf großen oder häufig aktualisierten Delta-Lake-Tabellen." Delta Lake erstellt periodisch Checkpoints, die den Zustand des Transaktionslogs dokumentieren — das ermöglicht schnellere Query-Planung, ohne das gesamte Log erneut abzuspielen. Basierend auf der offiziellen Databricks-Doku-Seite.

## 1. Wesentliche Verbesserungen

- Handhabt eine erhöhte Anzahl gleichzeitiger Writer.
- Minimiert Schreibkonflikte auf Tabellen mit hohem Volumen oder häufigen Änderungen.
- Beschleunigt Query-Planungsoperationen.

## 2. Voraussetzungen

Databricks Runtime 13.3 LTS oder höher für Lese-/Schreibunterstützung; basiert auf der offenen Delta-Lake-Protokoll-Checkpoint-V2-Spezifikation.

## 3. Aktivierung

**Automatisch:** Tabellen mit Liquid Clustering nutzen ab Databricks Runtime 14.1+ standardmäßig Checkpoint V2; automatische Upgrades können Checkpoint V2 für Unity-Catalog-Managed-Tables aktivieren (siehe [Managed Tables.md](../03%20Managed%20Tables.md), Abschnitt 6).

**Manuell — bestehende Tabelle:**

```sql
ALTER TABLE table_name SET TBLPROPERTIES ('delta.checkpointPolicy' = 'v2');
```

**Manuell — neue Tabelle:**

```sql
CREATE TABLE table_name (...) TBLPROPERTIES ('delta.checkpointPolicy' = 'v2');
```

Optionales manuelles Auslösen eines Checkpoints über den `REORG TABLE`-Befehl.

## 4. Downgrade

```sql
ALTER TABLE table_name DROP FEATURE v2Checkpoint;
```

## 5. Verwandte Themen

- Vollständiges, zweistufiges Downgrade-Verhalten: siehe [07 Drop Feature.md](07%20Drop%20Feature.md).
- Runtime-Anforderungen und Protokollversion im Gesamtüberblick: siehe [08 Feature Compatibility.md](08%20Feature%20Compatibility.md).

### Quelle

- https://docs.databricks.com/aws/en/tables/features/checkpoint-v2
