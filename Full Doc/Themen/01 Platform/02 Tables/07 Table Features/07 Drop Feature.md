# Features entfernen: DROP FEATURE

`DROP FEATURE` entfernt ein aktiviertes Delta-Lake-Table-Feature kontrolliert wieder und stuft das Tabellenprotokoll auf die minimal nötige Version herab. Basierend auf der offiziellen Databricks-Doku-Seite.

## 1. Grundsyntax

```sql
ALTER TABLE <table-name> DROP FEATURE <feature-name>;
```

**Für vollständiges Protokoll-Downgrade mit Historien-Truncation:**

```sql
ALTER TABLE <table-name> DROP FEATURE <feature-name> TRUNCATE HISTORY;
```

## 2. Voraussetzungen

- **Runtime:** Databricks Runtime 16.3 oder höher (16.4 LTS empfohlen).
- **Berechtigungen:** `MODIFY`-Zugriff auf der Zieltabelle.
- **Einschränkung:** „Pro `DROP FEATURE`-Befehl lässt sich nur ein Tabellen-Feature entfernen."
- **Konflikte:** alle nebenläufigen Schreiboperationen werden während der Operation blockiert.

## 3. Entfernbare Features

- `catalogManaged` (siehe [01 Catalog Commits.md](01%20Catalog%20Commits.md))
- `checkConstraints` (siehe [12 Constraints.md](12%20Constraints.md))
- `collations-preview` (siehe [04 Collation.md](04%20Collation.md))
- `columnMapping` (siehe [05 Column Mapping.md](05%20Column%20Mapping.md))
- `deletionVectors` (siehe [06 Deletion Vectors.md](06%20Deletion%20Vectors.md))
- `typeWidening` (siehe [13 Type Widening.md](13%20Type%20Widening.md))
- `v2Checkpoint` (siehe [03 Checkpoint V2.md](03%20Checkpoint%20V2.md))
- `checkpointProtection`

**Alle übrigen Delta-Lake-Table-Features lassen sich nicht per `DROP FEATURE` entfernen.** Zudem können manche Features andere, von ihnen abhängige Features aktivieren — das kann deren eigenständige Entfernung blockieren.

## 4. Verhaltensänderungen beim Entfernen

Beim Entfernen eines Features handhabt Delta Lake:

- Deaktiviert zugehörige Tabelleneigenschaften.
- Schreibt Datendateien neu, um Feature-Spuren zu eliminieren.
- Erstellt geschützte Checkpoints für Historien-Kompatibilität.
- Fügt `checkpointProtection` dem Protokoll hinzu.
- Stuft das Protokoll auf die minimal erforderlichen Versionen herab.

**Das `checkpointProtection`-Feature im Detail:** Wird beim Entfernen eines Features automatisch hinzugefügt, wird von allen Databricks-Runtime-Versionen unterstützt, blockiert weder Databricks-Lese- noch -Schreibzugriffe, erlaubt das Protokoll-Downgrade bei erhaltenem Zugriff auf die Historie, und blockiert auch keinen lesenden Zugriff von OSS-Delta-Lake-Clients.

## 5. Zweistufiger vollständiger Downgrade-Prozess

Vollständig nötig ist dieser Prozess nur, wenn externe Writer `checkpointProtection` **nicht** unterstützen.

**Schritt 1** (sofort): `DROP FEATURE <name> TRUNCATE HISTORY` ausführen — deaktiviert das Feature, setzt Tabelleneigenschaften zurück, schreibt benötigte Dateien neu und bereitet das Downgrade vor.

**Schritt 2** (nach 24+ Stunden): denselben Befehl erneut ausführen, um die Historie zu truncaten, zu bestätigen, dass keine Transaktionen das Feature mehr nutzen, und das Protokoll-Downgrade abzuschließen.

**Wichtige Warnung:** Der zweite Schritt entfernt **alle Transaktionslog-Daten, die älter als 24 Stunden sind**, und beseitigt damit die Time-Travel-Fähigkeit für diesen Zeitraum. Databricks empfiehlt, das Standardverhalten zunächst ohne `TRUNCATE HISTORY` zu testen sowie abhängige Workloads vor der Aktivierung protokoll-relevanter Features zu prüfen.

## 6. Verwandte Themen

- Gesamtüberblick über Protokollversionen und welche Features sie auslösen: siehe [08 Feature Compatibility.md](08%20Feature%20Compatibility.md).

### Quelle

- https://docs.databricks.com/aws/en/tables/features/drop-feature
