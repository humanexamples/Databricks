# KI-generierte Dokumentation (AI-Generated Comments)

DatabricksIQ kann für Unity-Catalog-Objekte automatisch Beschreibungen (Comments) generieren — basierend auf Schema und Spaltennamen, nicht auf den eigentlichen Dateninhalten. Das verbessert Auffindbarkeit (siehe [Discoverability und Tag-Suche.md](Discoverability%20und%20Tag-Suche.md)) und reduziert manuellen Dokumentationsaufwand. Basierend auf einer privaten Kursnotiz sowie der offiziellen Databricks-Dokumentation.

## Funktionsweise

Ein von Databricks entwickeltes, custom-gebautes Large Language Model generiert Metadaten-Beschreibungen auf Basis von Tabellenschema und Spaltennamen — die Kommentare sind auf einen geschäftlichen/unternehmerischen Kontext zugeschnitten und wurden anhand von Beispielschemata aus mehreren offenen Datensätzen verschiedener Branchen trainiert bzw. abgestimmt.

## Unterstützte Objekttypen

- Catalogs, Schemas
- Tabellen, Views, Materialized Views
- Tabellenspalten
- Functions, Models, Volumes

## Benötigte Berechtigungen

- Für die meisten Objekte (Catalogs, Schemas, Tabellen, Functions, Models, Volumes): **Owner**-Status **oder** `MODIFY`-Privileg.
- Für Views und Materialized Views: **ausschließlich Owner**-Status (kein `MODIFY`-Äquivalent).

## Nutzung im Catalog Explorer

**Für Tabellen (bzw. andere Objekte):**

1. Objekt im Catalog Explorer öffnen, im „Overview"-Tab bzw. „About this object"-Panel auf **AI generate** klicken.
2. DatabricksIQ schlägt eine „AI Suggested Description" vor.
3. Vorschlag übernehmen, bearbeiten oder verwerfen — auch nachträgliches Anpassen ist jederzeit möglich.

**Für Spalten:**

1. Im „Overview"-Tab unterhalb des angezeigten Schemas den Button **AI generate** anklicken.
2. DatabricksIQ generiert Beschreibungen für alle Spalten gleichzeitig.
3. Vorschläge einzeln übernehmen, verwerfen oder anpassen.

Die Sprache der generierten Kommentare lässt sich über das Overflow-Menü konfigurieren.

## Einschränkungen und Hinweise

- **Sorgfaltspflicht:** KI-Modelle sind nicht immer akkurat — generierte Kommentare müssen vor dem Speichern überprüft werden.
- **Nicht für PII-Klassifizierung geeignet:** Die Funktion ersetzt keine Datenklassifizierung sensibler Daten (siehe `12 PII und Pseudonymisierung/`).
- **Auswirkung auf Pipelines:** Das Speichern von Kommentaren löst intern `ALTER`-Befehle auf dem betroffenen Objekt aus, was laufende Pipelines beeinträchtigen kann.

## Quellen

- https://docs.databricks.com/aws/en/comments/ai-comments
- Private Kursnotiz (Nutzungsschritte in Catalog Explorer, Berechtigungshinweis)
