# Sicherheitsmodell, Credential Vending und Verschlüsselung

Ergänzt die Zugriffskontroll-Kapitel um die technische Frage: Wie gelangt eine Query eigentlich sicher an die Rohdaten im Cloud-Speicher, und wie ist die Databricks-Plattform selbst verschlüsselt?

## Credential Vending: wie Compute auf Cloud-Speicher zugreift

Unity Catalog gibt Compute-Ressourcen keinen dauerhaften Zugriff auf Cloud-Speicher. Stattdessen validiert Unity Catalog jede Anfrage und stellt **kurzlebige, auf den jeweiligen Pfad beschränkte Credentials** aus — dieser Mechanismus heißt **Credential Vending**.

- Es gibt zwei Varianten: **Table Credential Vending** (Zugriff auf im Metastore registrierte Daten) und **Path Credential Vending** (Zugriff auf External Locations im Metastore).
- Ausgestellte Credentials erlauben direkten Zugriff auf den Cloud-Speicherort, beschränkt auf den jeweils relevanten Pfad, laufen automatisch nach kurzer Zeit ab und gewähren keinen Zugriff über die definierte Tabelle/Location hinaus.
- Die vergebenen Credentials erben die Privilegien des Databricks-Principals, der die Anfrage stellt.
- Für den Zugriff externer Systeme (über Unity-REST-API oder Apache-Iceberg-REST-Catalog) muss External Access auf dem Metastore konfiguriert und `EXTERNAL USE SCHEMA` an den anfragenden Principal vergeben sein.

**Praktisch bedeutet das:** Eine Query greift nie direkt und dauerhaft auf einen Storage-Bucket zu — jede Anfrage wird von Unity Catalog geprüft (Namespace, Metadaten, Grants) und erhält für die Dauer der Query ein eigenes, eng begrenztes Zugriffstoken. Row- und Column-Level-Filterung (siehe `07 Filters und Masks/` und `08 ABAC/`) wird zusätzlich "last mile" auf dem Compute selbst durchgesetzt, nachdem die Daten aus dem Speicher gelesen wurden.

## Verschlüsselung: Control Plane vs. Data Plane

Databricks unterscheidet zwei Architekturbereiche:

- **Control Plane** (von Databricks betrieben): Web-Anwendung, Notebooks, Secrets, SQL-Queries, Dashboards, Metadaten, AI/BI-Dashboards, Genie Agents.
- **Data Plane** (im Cloud-Account des Kunden): Cluster-Storage, EBS-Volumes/Managed Disks, Workspace-Storage-Buckets und optional der DBFS-Root.

Daten in der Control Plane werden standardmäßig verschlüsselt gespeichert (Managed-Services-Daten "at rest").

### Envelope Encryption

Für Customer-Managed Keys (Enterprise-Tier) nutzt Databricks eine dreistufige Schlüsselhierarchie:

1. **Data Encryption Key (DEK):** ein eindeutiger AES-256-Schlüssel, der die eigentlichen Inhalte verschlüsselt.
2. **Customer-Managed Key (CMK):** der eigene Schlüssel des Kunden (in AWS KMS oder Azure Key Vault), der den DEK umschließt ("wrapped").
3. **Databricks-Managed Key (DMK):** ein von Databricks kontrollierter Schlüssel, der den bereits umschlossenen DEK zusätzlich erneut verschlüsselt.

Geschützt werden dadurch u. a. Notebooks/Queries (Code), verarbeitete Daten und Query-Ergebnisse, ML-Modelle/-Artefakte sowie gespeicherte Credentials/Secrets. Wird der CMK gelöscht oder der Zugriff darauf entzogen, kann Databricks die damit verschlüsselten Daten **nicht mehr entschlüsseln** — auch nicht im Fall einer internen Kompromittierung.

Für Workspace-Storage (S3-Buckets, optional EBS-Volumes bei Classic Compute) lässt sich zusätzlich unabhängig ein CMK konfigurieren. Serverless Workspaces nutzen ausschließlich die Managed-Services-Verschlüsselung.

## Bezug zu den Unity-Catalog-Best-Practices

Mehrere der offiziellen Unity-Catalog-Best-Practices konkretisieren dieses Sicherheitsmodell:

- **Unity Catalog nie umgehen:** Storage-Accounts nicht gleichzeitig als DBFS-Mount **und** als External Location nutzen — sonst existiert ein Zugriffsweg an Unity Catalog vorbei.
- **Direkten Bucket-Zugriff einschränken:** Nutzer mit direktem Cloud-Zugriff auf Buckets begrenzen, die auch über Unity Catalog verwaltet werden — sonst gehen Audit-Trail und Zugriffskontrolle auf Managed Tables/Volumes verloren.
- **`CREATE EXTERNAL LOCATION` restriktiv vergeben:** nur an Administratoren, die für Storage-Setup zuständig sind — External Locations gewähren breiten Speicherzugriff.
- **DBFS vermeiden:** In Unity-Catalog-aktivierten Workspaces sollten Volumes statt DBFS für unstrukturierte Daten (Checkpoints, Bibliotheken, Konfigurationsdateien) genutzt werden; Buckets, die zuvor als DBFS-Root dienten, nicht als neuen Managed-Storage-Speicherort wiederverwenden.

## Quellen

- https://docs.databricks.com/aws/en/external-access/credential-vending
- https://www.databricks.com/trust/security-features/data-protection-with-customer-managed-keys
- https://docs.databricks.com/aws/en/data-governance/unity-catalog/best-practices
