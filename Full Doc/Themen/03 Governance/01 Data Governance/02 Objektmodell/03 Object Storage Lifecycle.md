# Object Storage Lifecycle

Was beim Löschen eines Objekts mit den zugrunde liegenden Datendateien passiert, hängt vom Objekttyp ab.

## Verhalten je Typ

- **Managed Tables/Volumes:** Unity Catalog kontrolliert Speicherort und Datei-Lebenszyklus. Die Daten liegen in Managed Storage (von Databricks bereitgestellt oder kundeneigen) und durchlaufen einen mehrstufigen Löschprozess (siehe unten).
- **External Tables/Volumes:** Der Nutzer kontrolliert Speicherort und Lebenszyklus. Beim Löschen entfernt Unity Catalog nur die Metadaten aus dem Metastore — die Datendateien bleiben am Cloud-Speicherort erhalten.
- **Foreign/Federated Catalogs:** Nur die Verbindungsmetadaten werden entfernt; die Daten im Quellsystem bleiben unberührt.

## Wiederherstellbarkeit

| Objekttyp | Wiederherstellbar? |
|---|---|
| Tabellen, Materialized Views, Streaming Tables | Ja, über `UNDROP` innerhalb von **7 Tagen** |
| Catalogs, Schemas, Volumes, Views, Funktionen, Modelle | Nein, nach dem Löschen nicht wiederherstellbar |

## Lebenszyklus von Managed-Daten

1. **Phase 1 — Wiederherstellungsfenster (7 Tage):** Unity Catalog behält die soft-gelöschten Daten, um eine Wiederherstellung zu ermöglichen. In diesem Zeitraum läuft die Speicherabrechnung weiter.
2. **Phase 2 — Endgültige Löschung (innerhalb von 48 Stunden):** Unity Catalog löscht die Datendateien endgültig, spätestens 48 Stunden nach Ende des Wiederherstellungsfensters.

## Abrechnung im Überblick

| Speicherart | Abrechnungsverhalten |
|---|---|
| **Databricks-Standardspeicher** | Abrechnung endet nach dem 7-Tage-Wiederherstellungsfenster. |
| **Kundeneigener Managed Storage** | Cloud-Speicherrichtlinien (Objekt-Versionierung, Soft-Delete, Lifecycle-Regeln) können Dateien darüber hinaus behalten — der Cloud-Anbieter berechnet dann nach diesen Richtlinien weiter. |
| **External Storage** | Der Cloud-Anbieter berechnet fortlaufend weiter, da Unity Catalog die Dateien nie löscht. |

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/object-storage-lifecycle
