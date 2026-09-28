# Feature Compatibility

Verständnis von Reader-/Writer-Protokollversionen zur Sicherstellung der Client-Kompatibilität bei Delta-Lake-Tabellen. Basierend auf der offiziellen Databricks-Doku-Seite.

## 1. Protokollversionen und Kompatibilitätsbestimmung

**Reader-/Writer-Protokollversionen:** Delta-Lake-Tabellen legen Kompatibilität über `minReaderVersion` (Werte 1–3) und `minWriterVersion` (Werte 2–7) fest. Diese Ganzzahlen geben an, welche Features ein Client unterstützen muss, um auf die Tabelle zuzugreifen. „Write-Protokolle und Writer-Features beeinflussen nur die Kompatibilität mit schreibenden Clients — Legacy-Workloads erhalten weiterhin lesenden Zugriff."

**Table Features (moderner Ansatz):** Bei `minReaderVersion` = 3 und `minWriterVersion` = 7 nutzt Delta Lake stattdessen Table Features — feingranulare Flags, die identifizieren, welche Fähigkeiten eine Tabelle nutzt. Das ermöglicht präzisere Kompatibilitätsprüfungen zwischen Clients und Tabellen.

## 2. Feature-Klassifikation

| Klasse | Bedeutung |
|---|---|
| **Writer Features** | erfordern Unterstützung durch schreibende Clients, blockieren aber nicht den nur-lesenden Zugriff |
| **Reader Features** | erfordern Unterstützung durch sowohl lesende als auch schreibende Clients — „ein Client kann nicht in eine Tabelle schreiben, die er nicht lesen kann" |

## 3. Externe Client-Kompatibilität prüfen

„Werden Tabellen von externen Systemen gelesen oder beschrieben, muss geprüft werden, dass diese Clients die auf den eigenen Tabellen aktivierten Table Features unterstützen." Vor der Aktivierung neuer Features auf Produktionstabellen die Client-Dokumentation gegen die Feature-Compatibility-Matrix prüfen.

**Protokoll-Upgrade-Auslöser:** Features aktivieren sich (und heben damit das Protokoll an) auf drei Wegen — über SQL-Syntax (z. B. löst `CLUSTER BY` Liquid Clustering aus), über explizite Tabelleneigenschaften (z. B. `'delta.enableDeletionVectors' = true`), oder als Nebeneffekt abhängiger Features (z. B. aktiviert das Einschalten von Iceberg Reads automatisch Column Mapping mit).

**Wichtige Warnung:** Databricks empfiehlt ausdrücklich, `minReaderVersion` und `minWriterVersion` **niemals direkt zu verändern** — ein manuelles Setzen dieser Eigenschaften verhindert weder anstehende Upgrades noch ermöglicht es Downgrades. Vor der Aktivierung neuer Features auf Produktionstabellen sollte die Kompatibilität mit externen Systemen getestet werden; Lakeflow Pipelines und Databricks SQL aktualisieren ihre Protokoll-Unterstützung automatisch mit regulären Releases.

## 4. Kompatibilitätsmatrix

**Databricks-Runtime-Mindestanforderungen je Feature:**

| Feature | Mindest-Runtime |
|---|---|
| `CHECK`-Constraints | alle unterstützten Versionen |
| Change Data Feed | alle unterstützten Versionen |
| Generated/Identity Columns | alle unterstützten Versionen |
| Column Mapping | alle unterstützten Versionen |
| Deletion Vectors | alle unterstützten Versionen |
| TimestampNTZ | 13.3 LTS |
| Iceberg Reads | 13.3 LTS |
| Liquid Clustering | 13.3 LTS |
| Row Tracking | 14.3 LTS |
| Type Widening | 15.4 LTS |
| VARIANT | 15.4 LTS |
| Collations | 16.1 |
| Protected Checkpoints | 16.3 |
| Catalog Commits | 16.4 LTS |

**Protokollversionen je Feature** (Delta `minWriterVersion`/`minReaderVersion` sowie Feature-Typ):

| Feature | minWriterVersion | minReaderVersion | Typ |
|---|---|---|---|
| Grundfunktionalität | 2 | 1 | Writer |
| `CHECK`-Constraints | 3 | 1 | Writer |
| Change Data Feed | 4 | 1 | Writer |
| Generated Columns | 4 | 1 | Writer |
| Column Mapping | 5 | 2 | Reader & Writer |
| Identity Columns | 6 | 1 | Writer |
| Row Tracking | 7 | 1 | Writer |
| Deletion Vectors | 7 | 3 | Reader & Writer |
| TimestampNTZ | 7 | 3 | Reader & Writer |
| Liquid Clustering | 7 | 3 | Reader & Writer |
| Iceberg Reads | 7 | 2 | Writer |
| Type Widening | 7 | 3 | Reader & Writer |
| VARIANT | 7 | 3 | Reader & Writer |
| Collations | 7 | 3 | Reader & Writer |
| Protected Checkpoints | 7 | 1 | Writer |
| Catalog Commits | 7 | 3 | Reader & Writer |

**Cross-Runtime-Kompatibilität:** Tabellen, die von einer niedrigeren Databricks-Runtime-Version geschrieben wurden, sind in höheren Versionen vollständig lese- und schreibfähig. Tabellen aus höheren Versionen können dagegen Features nutzen, die in niedrigeren Versionen nicht unterstützt werden.

**Backported Support:** Table-Feature-Unterstützung wurde für zuvor bereits unterstützte Fähigkeiten teils bis Runtime 11.3 LTS und darunter zurückportiert — Generated Columns funktionieren beispielsweise bereits ab Runtime 9.1 LTS, Identity Columns benötigen mindestens Runtime 10.4 LTS. Bei Nutzung zurückportierter Features empfiehlt sich ein Kompatibilitätstest mit OSS Delta Lake.

## 5. Besonderheiten bei Apache Iceberg

Iceberg nutzt eine einzelne `format-version`-Angabe statt getrennter Reader-/Writer-Versionen. Features sind bei Iceberg grundsätzlich Opt-in — mit Ausnahme von Row Tracking, das in `format-version` 3 automatisch enthalten ist. „Liquid Clustering implementiert dabei Hidden Partitioning." Iceberg Reads setzt zudem aktiviertes Column Mapping voraus.

**Nicht anwendbar auf Iceberg** (Delta-spezifische Features): `CHECK`-Constraints, Change Data Feed, Generated Columns, Column Mapping, Identity Columns, Iceberg Reads, Type Widening, Collations, Protected Checkpoints, Catalog Commits.

**Iceberg Reads (UniForm) im Detail:** siehe [14 Iceberg Reads (UniForm).md](14%20Iceberg%20Reads%20%28UniForm%29.md).

## 6. Verwandte Themen

- Kontrolliertes Entfernen aktivierter Features, das das Protokoll wieder herabstuft: siehe [07 Drop Feature.md](07%20Drop%20Feature.md).

### Quelle

- https://docs.databricks.com/aws/en/tables/features/feature-compatibility
