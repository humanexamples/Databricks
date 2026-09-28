# Zusammenfassung: Databricks Data Privacy

## 1_Storing Data Securely

### 1_1_Regulatory Compliance

- GDPR und CCPA sind die wichtigsten Compliance-Vorgaben; eine globale Policy, die beide erfüllt, vereinfacht das Datenmanagement
- Unternehmen müssen Nutzerdaten identifizieren, exportieren, aktualisieren oder löschen können
- Bei GDPR-Verstößen (keine Antwort innerhalb 30 Tagen): Strafen bis 4% des Jahresumsatzes oder 20 Mio. €
- Bei CCPA: Empfangsbestätigung innerhalb 10 Werktagen, Bearbeitung innerhalb 45 Tagen, Strafen bis 2.500 $/Verstoß
- Delta Lake/Lakehouse reduziert Compliance-Aufwand durch Transaktionsgarantien und Datenqualitätsprüfungen

### 1_2_Data Privacy

- Drei Kernaspekte: **Identify** (Datenquellen, -nutzung erkennen), **Assess** (Schutzoptionen bewerten), **Manage** (Rechte wie "Recht auf Vergessenwerden" umsetzen)
- Identify-Phase: Data Discovery, Data Classification, Data Mapping
- Protect-Phase: Verschlüsselung, Zugriffskontrollen, Datenminimierung
- Manage-Phase: Data Governance, Compliance Management, laufendes Monitoring/Auditing

---

## 2_Unity Catalog

### 2_1_Zentrale Konzepte und Komponenten

- Vor Unity Catalog: fragmentierte Governance (Data Lake, Warehouse, ML-Assets jeweils unterschiedliche Berechtigungsmodelle) → keine feingranularen Zugriffskontrollen, kein gemeinsames Metadaten-Layer
- Unity Catalog vereint Governance über alle Daten- und KI-Assets: ACLs mit Prinzip **Who** (User/Group/Service Principal), **What** (Objekt), **How** (Privilege wie SELECT, MODIFY)
- Automatische Lineage-Erfassung über Tabellen, Spalten, Dashboards, Jobs, Notebooks etc.
- Feingranulare Zugriffskontrolle: (1) Spalten verstecken, (2) Zeilen filtern, (3) Spaltenwerte transformieren/maskieren
- Zwei Umsetzungswege: Dynamic Views vs. Row Filtering & Column Masking (UDFs mit `SET ROW FILTER`/`SET MASK`)
- Praxisbeispiel SEEK: PII-Erkennung im großen Maßstab mit HuggingFace + Unity Catalog Lineage

### 2_2_Ihre Daten auditieren

- System-Tabellen im `system`-Katalog beantworten Fragen zu Ownership, Zugriff, Nutzung
- `information_schema`: welche Tabellen existieren, wer hat zuletzt geändert, wer hat Zugriff, wer ist Owner
- `system.billing.usage`: DBU-Verbrauch nach Tag, User, SKU, Job
- `system.access.audit`: wer hat wann auf welche Tabelle zugegriffen/gelöscht (Public Preview)
- `system.access.table_lineage`: Quell-/Zieltabellen und lesende Queries nachvollziehen

### 2_3_Data Isolation

- Drei-Ebenen-Namespace: **Metastore** (1 pro Region, mehrere Workspaces) → **Catalog** (primäre Isolationseinheit, oft Prod/Dev getrennt) → **Volumes** (unstrukturierte Daten, kein Tabellen-Ersatz)
- Storage-Locations konfigurierbar auf Metastore-, Catalog- oder Schema-Ebene
- Zentralisiertes vs. dezentralisiertes Governance-Modell (Catalog-Owner als Domain-Owner)
- External Locations + Storage Credentials binden Cloud-Storage an Unity Catalog, sollten nicht direkt zugänglich sein
- Security-Modell: Query → UC validiert → temporärer Scoped Token pro Objekt → Compute liest direkt aus Storage → Row/Column-Filtering "last mile"
- Verschlüsselung: TLS/SSL in transit, AES-256 at rest, Envelope Encryption (DEK+CMK) für Control Plane
- Best Practices: kein direkter Objektstore-Zugriff, Minimierung von Keys, keine Credentials im Code, Migration weg von Hive Metastore/DBFS

---

## 3_PII Data Security

### 3_1_Pseudonymization & Anonymization (inkl. 3_1_1)

- Grundprinzip: Re-Identifikation ist nie vollständig ausgeschlossen, nur risikoreduziert
- **Pseudonymisierung**: reversibel, Record-Level, gilt weiterhin als personenbezogene Daten (GDPR)
  - **Hashing**: deterministisch, Salting empfohlen (Salt via Databricks Secrets API), erhöht Datengröße
  - **Tokenisierung**: Werte → Token in sicherem Lookup-Vault; langsam beim Schreiben, schnell beim Lesen
- **Anonymisierung**: irreversibel, schützt ganze Datensätze, meist Kombination mehrerer Techniken
  - **Data Suppression**: Zeilen/Spalten mit niedrigen Counts filtern, um Re-Identifikation zu verhindern
  - **Generalization**: Categorical Generalization (Stadt→Land), Binning (Alters-/Gehaltsbänder), IP-Truncation (/24), Rounding

### 3_2_Zusammenfassung & Best Practices

- Vergleichstabelle: Data Masking, Pseudo-Anonymisierung, Hashing, Column Encryption, Tokenisierung (Schutzgrad Low→High)
- Best Practices: kein PII ist besser als PII; Anonymisierung > Pseudonymisierung > Klartext; gesunde Paranoia; Kombinierbarkeit von Datensätzen bedenken (Re-Identifikationsrisiko); Teams schulen; nicht alles PII ist gleich sensibel; PIA-Reviews; PII-Umgebungen isolieren

---

## 4_Streaming-Daten und CDF

### 4_1_Capturing Changed Data

- Structured Streaming erwartet append-only Quellen → Updates/Deletes brechen diese Annahme
- **Lösung 1 – Ignore Change**: `ignoreDeletes` (nur Partition-Deletes) bzw. `skipChangeCommits` (ersetzt deprecated `ignoreChanges`, ignoriert alle Änderungen)
- **Lösung 2 – Change Data Feed (CDF)**: trackt Row-Level-Änderungen (`_change_data`-Ordner), muss explizit aktiviert werden, zusätzlicher Storage-Overhead
- CDF-Vorteile: effiziente Silver/Gold-Updates, Materialized Views ohne Re-Aggregation, Change-Export an externe Systeme, Audit-Trail
- CDF vs. klassisches CDC: CDF ist Delta-spezifisch (`table_changes`-Funktion), CDC ist generisches Konzept (`APPLY CHANGES`)
- Ausgabe enthält `_change_type` (insert/delete/update_preimage/update_postimage), `_commit_version`, `_commit_timestamp`
- Konsum via **Stream Mode** (Micro-Batches ab Checkpoint) oder **Batch Mode** (High-Watermark alle X Minuten)
- Aktivierung: `ALTER TABLE ... SET TBLPROPERTIES (delta.enableChangeDataFeed = true)`

### 4_2_Daten in Databricks löschen

- Löschanfragen (GDPR/CCPA) werden i.d.R. in separaten Pipelines von der ETL-Pipeline gehandhabt
- CDF propagiert Delete-Events gezielt in nachgelagerte Tabellen
- Commit-Messages im Delta-Log unterstützen Auditing (global oder pro Write-Operation)
- **Wichtig**: gelöschte Werte bleiben in alten Delta-Versionen/CDF bestehen, bis `VACUUM` ausgeführt wird (Default-Schutz: 7 Tage Retention, für sofortiges Löschen `retentionDurationCheck.enabled` deaktivieren + `VACUUM RETAIN 0 HOURS`, vorher `DRY RUN`)
- DML auf Streaming Tables: über `APPLY CHANGES INTO`, konfigurierbare Retention/Pipeline-Reset zum permanenten User-Löschen
- Materialized Views erlauben kein direktes INSERT/UPDATE/DELETE – nur Refresh
