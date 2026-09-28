# DBFS Grundlagen

Das Databricks File System (DBFS) ist der historische, inzwischen **veraltete** Weg, wie Databricks mit Cloud-Storage interagiert. Dieses Dokument erklärt, was DBFS ist, warum es abgelöst wurde, und was speziell an DBFS Root sowie den standardmäßigen Root-Verzeichnissen zu wissen ist. Basierend auf offiziellen Databricks-Doku-Seiten (jeweils am Ende jedes Abschnitts referenziert). Ergänzt [Mounts und Migration.md](Mounts%20und%20Migration.md), das DBFS Mounts und den Umstieg auf Unity Catalog behandelt.

## Abschnittsübersicht

1. [Was ist DBFS?](#was-ist)
2. [Deprecation-Status und empfohlene Alternativen](#deprecation)
3. [DBFS Root im Detail](#dbfs-root)
4. [Standardmäßige Root-Verzeichnisse](#root-verzeichnisse)
5. [Zusammenfassung](#zusammenfassung)

---

## <a id="was-ist">1. Was ist DBFS?</a>

DBFS steht für „Databricks File System, das das verteilte Dateisystem beschreibt, das Databricks zur Interaktion mit Cloud-basiertem Storage nutzt." Der Begriff umfasst zwei Komponenten: **DBFS Root** (siehe Abschnitt 3) und **DBFS Mounts** (siehe [Mounts und Migration.md](Mounts%20und%20Migration.md)).

### Quelle

- https://docs.databricks.com/aws/en/dbfs/

---

## <a id="deprecation">2. Deprecation-Status und empfohlene Alternativen</a>

**Wichtiger Hinweis:** Sowohl DBFS Root als auch DBFS Mounts sind **veraltet**. „Neue Konten werden ohne Zugriff auf diese Features bereitgestellt."

### Empfohlene Alternativen

Databricks empfiehlt, DBFS zu ersetzen durch:

- **Unity Catalog Volumes** (siehe [Unity Catalog Volumes.md](../Unity%20Catalog%20Volumes.md))
- **External Locations**
- **Workspace Files** (siehe [Datei-Speicheroptionen und Workspace Files.md](../Datei-Speicheroptionen%20und%20Workspace%20Files.md))

### Kernkomponenten im Überblick

- **DBFS Root:** ein bei der Workspace-Erstellung bereitgestellter Speicherort — von der Speicherung von Produktionsdaten, Bibliotheken oder Skripten wird abgeraten.
- **DBFS Mounts:** erlauben den Zugriff auf Cloud-Object-Storage als lokale Dateisystem-Ressourcen, indem Hadoop-Konfigurationen gespeichert werden — veraltet zugunsten von Unity-Catalog-Volumes.
- **Unity-Catalog-Integration:** bietet Sicherheitskontrollen über External Locations, Storage Credentials und Volumes für Zugriff nach dem Least-Privilege-Prinzip.

### Quelle

- https://docs.databricks.com/aws/en/dbfs/

---

## <a id="dbfs-root">3. DBFS Root im Detail</a>

### 3.1 Was es ist

DBFS Root ist ein Standard-Speicherort innerhalb von DBFS, der für alle Workspace-Nutzer zugänglich ist. „Databricks nutzt das DBFS-Root-Verzeichnis als Standard-Speicherort für bestimmte Workspace-Aktionen."

### 3.2 Standardmäßige Nutzung

DBFS Root dient als Standard-Speicherort für Managed Tables im Hive Metastore. Die Dokumentation betont jedoch ausdrücklich: „Databricks rät davon ab, Produktionsdaten oder sensible Informationen im DBFS Root zu speichern."

### 3.3 Wichtige Eigenschaften

- Für alle Workspace-Nutzer zugänglich.
- Veraltet und für neue Konten nicht empfohlen.
- Ein separater, privater Speicherort (internes DBFS) existiert für Databricks-Konfigurationen — getrennt vom nutzerzugänglichen DBFS Root.

### 3.4 Empfehlungen für den (Übergangs-)Betrieb

1. **Nutzeraufklärung:** Nutzer anweisen, keine sensiblen Daten in DBFS Root zu speichern, da „alle Nutzer auf hier gespeicherte Daten zugreifen können."
2. **Audit-Logging:** Monitoring und S3-Object-Level-Logging zur Untersuchung aktivieren.
3. **Verschlüsselung:** Customer-Managed Keys für Verschlüsselung einsetzen.
4. **Bessere Alternativen:** stattdessen Unity Catalog Volumes, External Locations oder Workspace Files nutzen.

### Quelle

- https://docs.databricks.com/aws/en/dbfs/dbfs-root

---

## <a id="root-verzeichnisse">4. Standardmäßige Root-Verzeichnisse</a>

| Verzeichnis | Zweck |
|---|---|
| **`/Volumes`** | pfadbasierter Zugriff auf Unity-Catalog-Volumes-Daten — die empfohlene moderne Alternative zu den Legacy-Root-Verzeichnissen |
| **`/databricks-datasets`** | Open-Source-Datensätze von Databricks — zugänglich über alle Access-Mode-Konfigurationen hinweg (sofern nicht von Workspace-Admins eingeschränkt), unterstützt Tutorials, Demos und eigenständige Exploration |
| **`/user/hive/warehouse`** | „der Standard-Speicherort für Daten von Managed Tables, die im `hive_metastore` registriert sind" |
| **`/FileStore`** | speichert über die Databricks-UI hochgeladene Daten und Bibliotheken, plus Bilddateien generierter Plots — „primär Legacy-Verhalten", da die meisten UI-Uploads inzwischen Workspace Files oder Volumes nutzen |
| **`/databricks-results`** | speichert Dateien, die beim Herunterladen vollständiger Query-Ergebnisse aus Notebooks generiert werden |
| **`/databricks/init`** | enthält in manchen Workspaces Legacy-Global-Init-Skripte — diese sind veraltet und sollten nicht mehr genutzt werden |

**Wichtiger Hinweis:** „DBFS Root ist veraltet. Neue Konten werden ohne Zugriff auf dieses Feature bereitgestellt. Databricks empfiehlt stattdessen die Nutzung von Unity Catalog Volumes und Workspace Files."

### Quelle

- https://docs.databricks.com/aws/en/dbfs/root-locations

---

## <a id="zusammenfassung">5. Zusammenfassung</a>

- **DBFS** ist Databricks' historisches verteiltes Dateisystem, bestehend aus DBFS Root und DBFS Mounts — **beide veraltet**, neue Konten haben standardmäßig keinen Zugriff mehr darauf.
- **DBFS Root** ist ein für alle Workspace-Nutzer zugänglicher Standard-Speicherort, u. a. Standardziel für Hive-Metastore-Managed-Tables — von Produktionsdaten und sensiblen Informationen dort wird ausdrücklich abgeraten.
- Sechs Standard-Root-Verzeichnisse decken unterschiedliche Legacy-Zwecke ab (`/Volumes`, `/databricks-datasets`, `/user/hive/warehouse`, `/FileStore`, `/databricks-results`, `/databricks/init`) — nur `/Volumes` verweist bereits auf die moderne Unity-Catalog-Alternative.
- Die durchgängige Empfehlung lautet, DBFS vollständig durch **Unity Catalog Volumes**, **External Locations** und **Workspace Files** zu ersetzen.
