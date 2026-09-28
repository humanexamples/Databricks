# 03 Governance — Gesamtübersicht

Konsolidierte Übersicht aller 62 Original-Markdown-Dateien im Ordner `03 Governance\01 Data Governance\` (12 Unterordner: Übersicht, Objektmodell, Setup, Access Control, Privilegien verwalten, Table ACLs, Filters und Masks, ABAC, Service Policies, Governed Tags, Auditing und System Tables, PII und Pseudonymisierung) mit **allen** enthaltenen Code-Beispielen und einer kurzen, einfachen Einführung pro Thema. Jede Originaldatei bleibt die primäre, ausführliche Quelle — dieses Dokument dient als kompakter Überblick plus vollständige Code-Referenz an einem Ort.

## Inhalt

1. Was ist Data Governance mit Unity Catalog
2. Data-Privacy-Rahmenwerk: Identify, Protect, Manage
3. Was ist Unity Catalog?
4. Securable Objects — schützbare Objekte im Überblick
5. Managed vs. External Assets
6. Object Storage Lifecycle
7. Voraussetzungen für Unity Catalog
8. Erste Schritte mit Unity Catalog
9. Unity Catalog einrichten (5 Schritte)
10. Metastore verwalten
11. Table ACLs (Hive Metastore) — Legacy-Übersicht
12. Table Access Control aktivieren — Legacy
13. Privilegien und schützbare Objekte — Legacy
14. Das schützbare Objekt `ANY FILE` — Legacy
15. Access Control — Überblick über die vier Mechanismen
16. Sicherheitsmodell: Credential Vending und Verschlüsselung
17. Berechtigungskonzepte: Objekthierarchie, Vererbung und Eigentümerschaft
18. Privilegien-Referenz: die vollständige Tabelle
19. Workspace-Catalog-Bindung
20. Privilegien verwalten — Überblick
21. Prinzipal-Typen: Nutzer, Gruppen, Service Principals
22. Schlüsselprivilegien im Detail: Abhängigkeiten und Ausnahmen
23. Standardrechte ohne expliziten Grant
24. GRANT, REVOKE und SHOW GRANTS — vollständige Syntax
25. Eigentümerschaft übertragen (OWNER TO)
26. Admin-Privilegien: Account-, Workspace- und Metastore-Admin
27. Access Request Destinations (Request for Access)
28. Grant-Rezepte für häufige Szenarien
29. Häufige Stolpersteine bei der Privilegienvergabe
30. ABAC — Überblick und Kernkomponenten
31. ABAC — Grundkonzepte (Governed Tags, Policy-Typen, Funktionen)
32. ABAC — Voraussetzungen, Kontingente und Einschränkungen
33. ABAC vs. tabellenbezogene Row Filter/Column Masks
34. ABAC-Policies erstellen und verwalten (CREATE POLICY, DROP POLICY, SHOW/DESCRIBE)
35. ABAC GRANT-Policies (Beta) — dynamische Privilegienvergabe
36. Policy Evaluation — Auswertung und Laufzeitverhalten
37. Neue Tabellen standardmäßig absichern (Secure by Default)
38. Tutorial: ABAC über Catalog Explorer (UI) konfigurieren
39. Tutorial: ABAC vollständig mit SQL konfigurieren
40. Mapping-Tabellen für dynamische Zugriffskontrolle
41. Häufige Muster für Row Filter und Column Masks
42. Multi-Domain Column Masking mit Sensitivitätsstufen
43. ABAC und OpenSharing
44. Performance-Überlegungen für Row Filter und Column Masks
45. ABAC — Best Practices
46. Row Filter und Column Masks — Überblick
47. Row Filter und Column Masks manuell anwenden
48. Service Policies für KI-Assets — Überblick
49. Sensible Daten erkennen (`detect_sensitive_data`)
50. Service Policy erstellen und anhängen
51. Service-Policy-Funktionsreferenz
52. Service-Policy-Beispiele
53. Governed Tags — Überblick
54. Governed Tags erstellen und verwalten
55. Berechtigungen für Governed Tags verwalten
56. Automatische Tag-Zuweisung (Beta)
57. KI-generierte Dokumentation (AI-Generated Comments)
58. Discoverability und Tag-Suche
59. System Tables — Überblick
60. Audit Logs, Billing und Lineage per System Tables abfragen
61. Insights-Tab (Catalog Explorer)
62. Pseudonymisierung und Anonymisierung von PII
63. Verbose Audit Logs (Log Delivery), SCIM API und Cluster-Nutzungsanalyse

---

## 1. Was ist Data Governance mit Unity Catalog

**Einfach erklärt:** Unity Catalog ist die zentrale Governance-Schicht für Daten und KI in Databricks. Sie sorgt dafür, dass Zugriff kontrolliert, Assets auffindbar, Datenflüsse (Lineage) nachvollziehbar und sensible Daten klassifiziert werden — über alle Workspaces hinweg an einem Ort. Neben Tabellen und Volumes verwaltet Unity Catalog auch Modelle, Funktionen und andere KI-Assets als "securable objects".

**Governance-Fähigkeiten im Überblick:**

| Bereich | Beschreibung |
|---|---|
| **Access Control** | Feingranularer Zugriff auf Daten- und KI-Assets über Privilegien, Attribute-Based Access Control sowie Row Filter und Column Masks |
| **Governed Tags** | Definition und Steuerung von Klassifizierungs-Tags für schützbare Objekte |
| **Data Discovery** | Auffinden von Assets über Catalog Explorer, KI-generierte Kommentare und Zertifizierung |
| **Data & AI Lineage** | Nachverfolgung des Datenflusses bis auf Spaltenebene |
| **Data Classification** | Automatisches Scannen und Taggen sensibler Daten (z. B. PII) |
| **Data Quality Monitoring** | Erkennung von Anomalien und statistisches Profiling von Tabellen |
| **Auditing** | Nachverfolgung von Zugriffen und Aktionen über Audit-Logs |
| **Data Sharing** | Sichere organisationsübergreifende Freigabe via OpenSharing, Clean Rooms und Marketplace |
| **AI Governance** | Steuerung von KI-Laufzeit-Interaktionen über Unity AI Gateway (Modell-APIs, Coding Agents, Agents, KI-Traffic, Guardrails) |

Account- und Metastore-Admins finden auf der **Data**-Seite im Governance Hub eine konsolidierte Übersicht des gesamten Datenbestands — Nutzungsmetriken, Klassifizierungsabdeckung und Datenqualitätsbewertungen.

Keine Code-Beispiele in dieser Datei.

---

## 2. Data-Privacy-Rahmenwerk: Identify, Protect, Manage

**Einfach erklärt:** Dieses Rahmenwerk ordnet Datenschutz in drei Phasen: Erst herausfinden, welche sensiblen Daten überhaupt existieren (**Identify**), dann entscheiden, wie sie geschützt werden (**Protect**), und schließlich dafür sorgen, dass Rechte und Vorgaben dauerhaft eingehalten werden (**Manage**).

- **1. Identify — sensible Daten erkennen:** Data Discovery (organisationsweite Bestandsaufnahme), Data Classification (Einstufung nach Sensibilität wie PII, Finanz- oder Gesundheitsdaten), Data Mapping (Nachvollziehen von Speicherort, Zugriffsberechtigten und Datenfluss).
- **2. Protect — Schutzmaßnahmen abwägen:** Technische Schutzmaßnahmen (Verschlüsselung, Zugriffskontrollen, Firewalls), Data Minimization (nur notwendige Daten erheben); Consent Management und Privacy by Design liegen außerhalb des Databricks-Funktionsumfangs. Zentrale Frage: anonymisieren oder pseudonymisieren, und wie der Schutz vor Reversion abgesichert wird.
- **3. Manage — Rechte laufend durchsetzen:** Data Governance (Richtlinien über den gesamten Datenlebenszyklus), Compliance Management (laufende Einhaltung von GDPR, CCPA, HIPAA usw.), Ongoing Monitoring & Auditing (regelmäßige Überprüfung); DSARs und Incident Response liegen außerhalb des Databricks-Funktionsumfangs.

Keine Code-Beispiele in dieser Datei.

---

## 3. Was ist Unity Catalog?

**Einfach erklärt:** Unity Catalog ist die einheitliche, fest in Databricks integrierte Governance-Schicht für Daten und KI. Sie erzwingt automatisch Zugriffskontrolle, verfolgt Lineage und protokolliert Aktivitäten workspaceübergreifend. Alle nach dem 8. November 2023 erstellten Workspaces haben Unity Catalog standardmäßig aktiviert; der Zugriff erfolgt über Catalog Explorer, SQL, Databricks CLI und REST-APIs.

Unity Catalog organisiert Daten- und KI-Assets in einem dreistufigen Namespace (`catalog.schema.objekt`). Assets sind entweder **Managed** (Unity Catalog steuert Governance und Datei-Speicher) oder **External** (Unity Catalog übernimmt nur die Governance, der Speicher bleibt extern verwaltet). Weitere Objekte wie Storage Credentials und Connections existieren auf Metastore-Ebene, oberhalb der Katalog-Hierarchie.

Kernfähigkeiten: Zugriffskontrolle über Privilegien und ABAC, automatische Lineage-Verfolgung, Audit-Logging, Datenklassifizierung und Qualitätsüberwachung, Data Sharing über OpenSharing sowie Integration von KI-Governance.

Keine Code-Beispiele in dieser Datei.

---

## 4. Securable Objects — schützbare Objekte im Überblick

**Einfach erklärt:** Unity Catalog organisiert alle schützbaren Objekte hierarchisch, mit dem Metastore als oberster Ebene. Man unterscheidet Datenobjekte (dreistufiger Namespace `catalog.schema.objekt`, z. B. Tabellen, Views, Volumes, Funktionen) und Nicht-Daten-Objekte auf Metastore-Ebene (z. B. Storage Credentials, Connections, Shares).

**Datenobjekte: Metastore → Catalog → Schema → …**

| Objekt | Beschreibung | Wichtige Privilegien |
|---|---|---|
| **Metastore** | Oberstes schützbares Objekt, an eine einzelne Cloud-Region gebunden. Privilegien vererben sich **nicht** an Kindobjekte. | — |
| **Catalog** | Container-Objekt. `SELECT` vererbt sich automatisch an alle aktuellen und künftigen Kindobjekte. `BROWSE` erlaubt Metadaten-Entdeckung ohne Datenzugriff. | `USE CATALOG`, `BROWSE` |
| **Schema** | Zweite Organisationsebene, ebenfalls mit Vererbung. Zugriff erfordert `USE CATALOG` + `USE SCHEMA`. | `USE SCHEMA` |
| **Tabellen** | Managed, External oder Foreign. Zugriff erfordert `USE CATALOG` + `USE SCHEMA` + Tabellenprivileg. | `SELECT`, `MODIFY` |
| **Views** | Nur lesbar, per SQL-Query definiert. Privilegien des View-Eigentümers gelten zur Laufzeit. Materialized Views unterstützen `REFRESH`. | — |
| **Volumes** | Objekte für unstrukturierte Daten, dateibasierter Zugriff. | `READ VOLUME`, `WRITE VOLUME` |
| **Funktionen** | UDFs, Stored Procedures, registrierte Modelle. | `EXECUTE` |
| **Modelle** | Versioniertes/unversioniertes KI-Modell. | `EXECUTE`, `APPLY TAG` |
| **Services** | Governte KI-Assets (Model Services, MCP Services in Beta). | `EXECUTE`, `CREATE SERVICE` |
| **Secrets** | Zugriff auf sensible Werte, ohne den Wert offenzulegen. | `CREATE SECRET`, `READ SECRET`, `WRITE SECRET`, `REFERENCE SECRET` |
| **Features** | ML-Feature-Definitionen (Public Preview). | `CREATE FEATURE`, `READ FEATURE` |

**Nicht-Daten-Objekte (Metastore-Ebene):**

| Objekt | Beschreibung | Wichtige Privilegien |
|---|---|---|
| **Storage Credentials** | Authentifizierungsobjekte für Cloud-Speicherzugriff. | `CREATE STORAGE CREDENTIAL` |
| **External Locations** | Kombinieren Storage Credential mit Cloud-Speicherpfad. Zugriff bevorzugt über Volumes statt direkt `READ FILES`/`WRITE FILES`. | — |
| **External Metadata** | Benutzerdefinierte Lineage-Beziehungen für externe Systeme. | `CREATE EXTERNAL METADATA` + `MODIFY` |
| **Service Credentials** | Authentifizierung für externe Cloud-Dienste. | `CREATE SERVICE CREDENTIAL` |
| **Connections** | Endpunkte/Credentials für externe Systeme (Federation, Ingestion, JDBC, HTTP). | `CREATE CONNECTION` |
| **Shares / Providers / Recipients** | OpenSharing-Objekte für organisationsübergreifende Freigabe. | — |
| **Clean Rooms** | Sichere Zusammenarbeit an gemeinsamen Daten, ohne dass eine Partei ihre Daten offenlegt. | `EXECUTE CLEAN ROOM TASK`, `MODIFY CLEAN ROOM` |

Keine Code-Beispiele in dieser Datei.

---

## 5. Managed vs. External Assets

**Einfach erklärt:** Für Tabellen und Volumes gibt es zwei Betriebsmodelle: Bei **Managed Assets** steuert Unity Catalog sowohl Governance als auch Speicherort/Lebenszyklus der Dateien. Bei **External Assets** übernimmt Unity Catalog nur die Governance — Speicherort und Lebenszyklus bleiben in Nutzerverantwortung. Wichtig: Bei Managed Assets behält man trotzdem volle Eigentümerschaft an den Daten — die Dateien verbleiben immer im eigenen Cloud-Account.

**Vergleich:**

| Eigenschaft | Managed | External |
|---|---|---|
| Speicherort | Von Unity Catalog festgelegt (im eigenen Cloud-Account) | Vom Nutzer festgelegt |
| Datei-Lebenszyklus | Von Unity Catalog verwaltet (Optimierung, Organisation, Löschung) | Vom Nutzer verwaltet |
| Verhalten bei `DROP` | Datendateien werden nach 8-tägiger Aufbewahrungsfrist endgültig gelöscht | Datendateien bleiben unverändert bestehen |
| Dateneigentümerschaft | Ja | Ja |

Diese Unterscheidung gilt ausschließlich für Tabellen und Volumes. Andere schützbare Objekte wie Views, Modelle und Funktionen haben keine Managed-/External-Varianten. Der Begriff "managed" wird mit unterschiedlichen Bedeutungen verwendet: Governance-Zugriffskontrolle, Speicherort-Festlegung, Lebenszyklus-Steuerung oder ein konkretes Privileg. Der Kontext entscheidet, welche Bedeutung gemeint ist.

Keine Code-Beispiele in dieser Datei.

---

## 6. Object Storage Lifecycle

**Einfach erklärt:** Was beim Löschen eines Objekts mit den zugrunde liegenden Datendateien passiert, hängt vom Objekttyp ab. Bei Managed Tables/Volumes kontrolliert Unity Catalog Speicherort und Lebenszyklus und durchläuft einen mehrstufigen Löschprozess. Bei External Tables/Volumes entfernt Unity Catalog beim Löschen nur die Metadaten — die Dateien bleiben am Cloud-Speicherort erhalten. Bei Foreign/Federated Catalogs werden nur Verbindungsmetadaten entfernt, die Quelldaten bleiben unberührt.

**Wiederherstellbarkeit:**

| Objekttyp | Wiederherstellbar? |
|---|---|
| Tabellen, Materialized Views, Streaming Tables | Ja, über `UNDROP` innerhalb von 7 Tagen |
| Catalogs, Schemas, Volumes, Views, Funktionen, Modelle | Nein, nach dem Löschen nicht wiederherstellbar |

**Lebenszyklus von Managed-Daten:** Phase 1 — Wiederherstellungsfenster (7 Tage): Unity Catalog behält soft-gelöschte Daten, Speicherabrechnung läuft weiter. Phase 2 — Endgültige Löschung: spätestens 48 Stunden nach Ende des Wiederherstellungsfensters.

**Abrechnung im Überblick:**

| Speicherart | Abrechnungsverhalten |
|---|---|
| Databricks-Standardspeicher | Abrechnung endet nach dem 7-Tage-Wiederherstellungsfenster |
| Kundeneigener Managed Storage | Cloud-Speicherrichtlinien (Versionierung, Soft-Delete, Lifecycle-Regeln) können Dateien darüber hinaus behalten, Cloud-Anbieter berechnet weiter |
| External Storage | Cloud-Anbieter berechnet fortlaufend weiter, da Unity Catalog die Dateien nie löscht |

Keine Code-Beispiele in dieser Datei.

---

## 7. Voraussetzungen für Unity Catalog

**Einfach erklärt:** Bevor Unity Catalog genutzt werden kann, müssen bestimmte Rahmenbedingungen erfüllt sein — unterstützte Regionen und Runtimes, erlaubte Dateiformate, Namensregeln und ein paar wichtige Einschränkungen, die man kennen sollte.

Alle Regionen unterstützen Unity Catalog. Cluster benötigen mindestens **Databricks Runtime 11.3 LTS** und müssen im Standard- oder Dedicated Access Mode laufen; SQL-Warehouses unterstützen Unity Catalog standardmäßig.

**Unterstützte Dateiformate:**

| Tabellentyp | Unterstützte Formate |
|---|---|
| Managed Tables | nur Delta oder Iceberg |
| External Tables | Delta, CSV, JSON, Avro, Parquet, ORC, Text |

**Namensregeln:** maximal 255 Zeichen pro Objektname; verbotene Zeichen sind Punkte, Leerzeichen, Schrägstriche, ASCII-Steuerzeichen (00–1F hex) und DELETE (7F hex); Unity Catalog speichert alle Objektnamen klein geschrieben; Sonderzeichen wie Bindestriche müssen in SQL mit Backticks maskiert werden.

**Wichtige Einschränkungen:** Workspace-Gruppen können nicht in `GRANT`-Anweisungen verwendet werden (stattdessen Account-Gruppen); R-Workloads benötigen Runtime 15.4 LTS+ für dynamische View-Sicherheit; Managed Tables benötigen Runtime 13.3 LTS+, External Tables 14.2+ für Shallow Clone; Bucketing wird nicht unterstützt; Python-UDFs benötigen Runtime 13.3 LTS+; Standard-Scala-Thread-Pools sind untersagt (stattdessen `org.apache.spark.util.ThreadUtils`). Unity Catalog erzwingt zudem Ressourcen-Kontingente (Quotas) für schützbare Objekte, überwachbar über die Resource-Quotas-APIs.

Keine Code-Beispiele in dieser Datei.

---

## 8. Erste Schritte mit Unity Catalog

**Einfach erklärt:** Nach der Aktivierung von Unity Catalog gibt es zwei Einstiegspfade: eine Setup-Anleitung für Workspaces, in denen Unity Catalog bereits aktiv ist (Admin-Rollen, Nutzer, Compute, Berechtigungen, Catalogs), und eine Upgrade-Anleitung für bestehende Workspaces von vor Unity Catalog (Aktivierung plus Datenmigration).

Nach dem Grundsetup stehen fortgeschrittene Governance-Fähigkeiten zur Verfügung:

- **Attribute-Based Access Control (ABAC):** dynamische, feingranulare Policies basierend auf Daten- und Nutzer-Attributen — Row-Level-Filtering und Column-Level-Masking ohne Verwaltung einzelner Tabellenberechtigungen.
- **Data Classification:** ein Agent scannt Kataloge automatisch, identifiziert und taggt sensible Daten (PII, Finanzdaten, Zugangsdaten) und verknüpft die Klassifizierung mit ABAC-Policies.
- **Data Quality Monitoring:** Anomalieerkennung über alle Tabellen eines Schemas sowie Daten-Profiling auf Tabellenebene.
- **Data Lineage:** verfolgt den Datenfluss über Tabellen, Notebooks, Jobs und Pipelines bis auf Spaltenebene — ermöglicht Impact-Analysen vor Schema-Änderungen.
- **Unity AI Gateway:** erweitert die Governance auf KI-Systeme — Zugriffskontrolle, Audit-Logging und Observability über alle KI-Interaktionen hinweg.

Keine Code-Beispiele in dieser Datei.

---

## 9. Unity Catalog einrichten (5 Schritte)

**Einfach erklärt:** Diese Anleitung richtet sich an Workspace-Admins und beschreibt die initiale Einrichtung von Unity Catalog in fünf Schritten: Aktivierung prüfen, Workspace-Zugriff verwalten, UC-fähiges Compute erstellen, Catalogs/Schemas anlegen und Privilegien vergeben. Ein **Metastore** ist der oberste Unity-Catalog-Container, an eine Cloud-Region gebunden; ein **Catalog** ist der höchste Datencontainer darin; es gibt drei Admin-Rollen (Account, Workspace, Metastore).

**Schritt 1 — Aktivierung prüfen** (per SQL auf UC-fähigem Compute):

```sql
SELECT CURRENT_METASTORE();
```

**Schritt 2 — Workspace-Zugriff verwalten:** Nutzer hinzufügen, in Gruppen organisieren (empfohlen), Admin-Rollen zuweisen.

**Schritt 3 — UC-fähiges Compute erstellen:**

| Compute-Typ | UC-fähig |
|---|---|
| SQL-Warehouse | Ja |
| Serverless Compute | Ja |
| Cluster — Single User | Ja |
| Cluster — Shared | Ja |
| Cluster — No Isolation Shared | Nein |

**Schritt 4 — Catalogs und Schemas erstellen:**

```sql
CREATE CATALOG IF NOT EXISTS <catalog-name>;
CREATE SCHEMA IF NOT EXISTS <catalog-name>.<schema-name>;
```

**Schritt 5 — Privilegien vergeben**

Nur-Lese-Zugriff:

```sql
GRANT USE CATALOG ON CATALOG <catalog-name> TO `<group-name>`;
GRANT USE SCHEMA ON SCHEMA <catalog-name>.<schema-name> TO `<group-name>`;
GRANT SELECT ON SCHEMA <catalog-name>.<schema-name> TO `<group-name>`;
```

Lese-Schreib-Zugriff:

```sql
GRANT USE CATALOG ON CATALOG <catalog-name> TO `<group-name>`;
GRANT USE SCHEMA ON SCHEMA <catalog-name>.<schema-name> TO `<group-name>`;
GRANT SELECT, MODIFY ON SCHEMA <catalog-name>.<schema-name> TO `<group-name>`;
```

Für Data Discovery zusätzlich `BROWSE` vergeben — erlaubt Nutzern zu sehen, dass Objekte existieren, und deren Metadaten einzusehen, ohne die Daten selbst lesen zu können.

**Checkliste:** (1) Unity-Catalog-Aktivierung bestätigt, (2) Nutzerverwaltung eingerichtet, (3) UC-fähiges Compute verfügbar, (4) Catalogs/Schemas organisiert, (5) Privilegien konfiguriert.

---

## 10. Metastore verwalten

**Einfach erklärt:** Metastore-Verwaltung umfasst die automatische Zuweisung neuer Workspaces, das Hinzufügen/Entfernen von Managed Storage sowie administrative Aufgaben wie Admin-Zuweisung und Löschung des Metastore.

Account-Admins können die automatische Metastore-Zuweisung für neu erstellte Workspaces derselben Region aktivieren — dabei werden automatisch Workspace-Catalogs erstellt und Nutzern die nötigen Privilegien zur Objekterstellung erteilt.

**Managed Storage hinzufügen** (drei Schritte): (1) einen S3-Bucket in derselben Region wie der Metastore anlegen, (2) eine External Location in Unity Catalog einrichten (per AWS Quickstart empfohlen, oder manuell), (3) den Speicherpfad als Account-Administrator zur Metastore-Konfiguration hinzufügen. Voraussetzung: mindestens ein Workspace muss bereits an den Unity-Catalog-Metastore angebunden sein.

**Speicher entfernen:** Wird Speicher auf Metastore-Ebene entfernt, erhalten bestehende Catalogs ohne eigenen Speicher-Root den Cloud-Speicherort des Metastore; dabei kann automatisch eine neue External Location namens `prior_metastore_root_location` entstehen.

**Weitere Admin-Aufgaben:** Metastore-Admins zuweisen (für Zugriffsverwaltung über Workspaces hinweg); Metastore löschen (unumkehrbare Aktion, betrifft alle verwalteten Objekte, Daten von External Tables bleiben erhalten). Wichtig: Managed-Table-Daten und -Metadaten benötigen nach dem Löschen eines Metastore 30 Tage, bevor sie automatisch entfernt werden.

Keine Code-Beispiele in dieser Datei.

---

## 11. Table ACLs (Hive Metastore) — Legacy-Übersicht

**Einfach erklärt:** Table Access Control für den in jedem Workspace eingebauten Hive Metastore ist ein Legacy-Governance-Modell. Databricks empfiehlt stattdessen Unity Catalog, das einen zentralen Ort für Datenzugriff über mehrere Workspaces hinweg bietet. Jeder Workspace enthält einen eingebauten Hive Metastore; ist Table Access Control aktiviert, können Admins Berechtigungen für Datenobjekte programmatisch über Python und SQL verwalten. Standardmäßig erlaubt ein Cluster allen Nutzern Zugriff auf alle vom eingebauten Hive Metastore verwalteten Daten, sofern Table Access Control nicht aktiviert ist.

Voraussetzungen: mindestens ein Premium-Abonnement sowie ein Data-Science-&-Engineering-Cluster mit passender Konfiguration oder ein SQL-Warehouse.

Themen in diesem Kapitel: Aktivierung von Table Access Control auf Clustern, verfügbare Privilegien und schützbare Objekte, sowie das schützbare Objekt `ANY FILE`.

Keine Code-Beispiele in dieser Datei.

---

## 12. Table Access Control aktivieren — Legacy

**Einfach erklärt:** Dieses Legacy-Governance-Modell für den Hive Metastore lässt sich auf zwei Arten aktivieren: **Nur SQL** (beschränkt Nutzer auf SQL-Befehle) oder **Python und SQL** (erlaubt zusätzlich Python/PySpark, mit strengeren Einschränkungen wie eingeschränktem Netzwerkzugriff). Die Einrichtung erfolgt auf Workspace-Ebene über den Security-Tab in den Workspace-Einstellungen. Wichtig: Selbst bei aktiviertem Table Access Control haben Databricks-Workspace-Administratoren weiterhin Zugriff auf Daten auf Dateiebene; die Funktion wird nicht mit Machine Learning Runtime unterstützt.

**Zwei Varianten:**
- **Nur SQL:** per Spark-Konfiguration `spark.databricks.acl.sqlOnly true`.
- **Python und SQL:** erzwingt niedrig privilegierten Ausführungsnutzer auf Cluster-Knoten, Netzwerkzugriff nur über Ports 80/443 (mit Ausnahmen für eingebaute Spark-Funktionen), konfigurierbare Outbound-Port-Whitelist über `spark.databricks.pyspark.iptable.outbound.whitelisted.ports`.

**Einrichtung auf Workspace-Ebene:** (1) zum Tab Security in den Workspace-Einstellungen navigieren, (2) die Option Table Access Control aktivieren, (3) Nutzern verbieten, Cluster ohne aktiviertes Table Access Control zu erstellen oder sich damit zu verbinden.

### Legacy-Privilegien im Hive Metastore (`GRANT`/`REVOKE`)

Im Legacy-Modus (ohne Unity Catalog) funktionieren `GRANT` und `REVOKE` syntaktisch identisch zu Unity Catalog, wirken aber nur auf Hive-Metastore-Objekte (Tabellen/Schemas ohne Catalog-Ebene):

```sql
-- Privileg an einen Nutzer vergeben
GRANT SELECT ON TABLE t TO `alf@melmak.et`;

-- Privileg auf einem Schema entziehen
REVOKE USAGE ON SCHEMA some_schema FROM `alf@melmak.et`;
```

### `MSCK REPAIR ... PRIVILEGES` — verwaiste ACLs aufräumen

Wird ein Objekt gelöscht, ohne dass zuvor alle Berechtigungen darauf entzogen wurden, bleiben verwaiste Zugriffskontrolleinträge zurück. `MSCK REPAIR PRIVILEGES` entfernt diese Legacy-Table-ACL-Reste für alle Nutzer auf einmal:

```sql
MSCK REPAIR object PRIVILEGES

object  { [ SCHEMA | DATABASE ] schema_name |
    FUNCTION function_name |
    TABLE table_name |
    VIEW view_name |
    ANONYMOUS FUNCTION |
    ANY FILE }
```

```sql
MSCK REPAIR SCHEMA gone_from_hive PRIVILEGES;
MSCK REPAIR ANONYMOUS FUNCTION PRIVILEGES;
MSCK REPAIR TABLE default.dropped PRIVILEGES;
```

---

## 13. Privilegien und schützbare Objekte — Legacy

**Einfach erklärt:** Auch dieses Legacy-Governance-Modell für den Hive Metastore wird von Databricks nicht mehr empfohlen — stattdessen soll Unity Catalog genutzt werden. Voraussetzungen: ein Admin muss Table Access Control für den Workspace aktivieren und erzwingen, der Cluster muss dafür aktiviert sein; in Databricks SQL ist Datenzugriffskontrolle unabhängig von den Workspace-Einstellungen immer aktiviert.

Die Hierarchie der schützbaren Objekte lautet `CATALOG` → `SCHEMA` → `TABLE`/`VIEW`/`FUNCTION`, zusätzlich `ANONYMOUS FUNCTION` und `ANY FILE` (umgeht Catalog-Beschränkungen, wenn vergeben). Es gibt acht vergebbare Privilegientypen: `SELECT`, `CREATE`, `MODIFY`, `USAGE`, `READ_METADATA`, `CREATE_NAMED_FUNCTION`, `MODIFY_CLASSPATH`, `ALL PRIVILEGES`. `USAGE` ist erforderlich, um eine Aktion auf einem Schema-Objekt auszuführen — erfüllt entweder durch Admin-Status, direkten Grant, Grant auf Catalog-Ebene oder Eigentümerschaft. Die Eigentümerschaft eines Objekts geht bei aktiviertem Table Access Control auf den Ersteller über; Eigentümer oder Workspace-Admin können sie neu zuweisen. Databricks stellt außerdem dynamische View-Funktionen wie `current_user()` und `is_member()` bereit, um Column-Level-, Row-Level- und Daten-Maskierungsberechtigungen direkt in View-Definitionen umzusetzen.

**Privilegien verwalten:**

```sql
GRANT privilege_type ON securable_object TO principal;
```

Weitere Befehle: `REVOKE`, `DENY`, `MSCK`, `SHOW GRANTS`.

**Eigentümerschaft neu zuweisen:**

```sql
ALTER <object> OWNER TO <principal>;
```

---

## 14. Das schützbare Objekt `ANY FILE` — Legacy

**Einfach erklärt:** `ANY FILE` ist ein Legacy-Objekt aus dem Hive-Metastore-Modell, das direkten Zugriff auf Dateisystem und Cloud-Speicher gewährt — unabhängig von Hive-Table-ACLs auf Datenbankobjekten. Nutzer können `MODIFY`- oder `SELECT`-Privilegien darauf erhalten; Workspace-Administratoren besitzen standardmäßig `MODIFY` und können damit Zugriff an andere vergeben oder entziehen.

Ist Unity Catalog aktiviert, dienen `ANY FILE`-Privilegien nur noch als **Fallback-Mechanismus** für Speicherpfade und Datenquellen, die nicht unter Unity-Catalog-Governance stehen. Wichtig: Diese Privilegien können Unity-Catalog-Privilegien nicht überschreiben und erweitern keine Rechte auf von Unity Catalog verwalteten Datenobjekten.

`SELECT` auf `ANY FILE` ist u. a. erforderlich für: Cloud-Speicherzugriff über URIs, Nutzung von DBFS-Root oder -Mounts, Datenquellen aus benutzerdefinierten Bibliotheken, externe Quellen außerhalb von Unity Catalog, bestimmte Streaming-Muster.

**Einschränkungen:** `ANY FILE`-Privilegien umgehen Legacy-Hive-Table-ACLs, aber niemals Unity-Catalog-Schutzmechanismen. Das Objekt erscheint nicht im Information Schema (entsprechend seinem Legacy-Status). Databricks rät zu besonderer Vorsicht bei der Vergabe dieser Privilegien in gemischten Governance-Umgebungen.

Keine Code-Beispiele in dieser Datei.

---

## 15. Access Control — Überblick über die vier Mechanismen

**Einfach erklärt:** Unity Catalog steuert Zugriff nicht über einen einzigen Mechanismus, sondern über vier ergänzende Bausteine: klassische Privilegien/Eigentümerschaft, tag-basierte ABAC-Policies, tabellenspezifische Row-/Column-Filter und Workspace-Bindings, die den Zugriff auf bestimmte Workspaces begrenzen. Databricks empfiehlt mittlerweile ABAC als zentralen, skalierbaren Ansatz, Row Filter/Column Masks bleiben aber für tabellenspezifische Fälle sinnvoll.

| Mechanismus | Gilt für | Definiert über | Anwendungsfall |
|---|---|---|---|
| **Privilegien & Eigentümerschaft** | Catalogs, Schemas, Tabellen | Grants (`GRANT`, `REVOKE`), Ownership | Basiszugriff und Delegation |
| **ABAC-Policies** | Getaggte Objekte (Tabellen, Schemas) | Policies mit Governed Tags und UDFs | Zentralisierte, tag-getriebene Policies mit dynamischer Durchsetzung |
| **Tabellenbezogene Row-/Column-Filter** | Einzelne Tabellen | UDFs direkt auf der Tabelle | Tabellenspezifische Filterung/Maskierung |
| **Workspace-Bindings** | Catalogs, External Locations, Storage Credentials | Workspace-Zuweisung | Zugriff auf Objekte auf bestimmte Workspaces beschränken |

Keine Code-Beispiele in dieser Datei.

---

## 16. Sicherheitsmodell: Credential Vending und Verschlüsselung

**Einfach erklärt:** Eine Query greift nie direkt und dauerhaft auf einen Cloud-Storage-Bucket zu. Unity Catalog prüft jede Anfrage und stellt stattdessen kurzlebige, auf den jeweiligen Pfad begrenzte Zugriffs-Credentials aus ("Credential Vending") — die Rechte des anfragenden Nutzers werden dabei vererbt. Zusätzlich verschlüsselt Databricks Daten in der Control Plane standardmäßig; bei Customer-Managed Keys kommt eine dreistufige Schlüsselhierarchie (Envelope Encryption) zum Einsatz, bei der ein vom Kunden kontrollierter Schlüssel den eigentlichen Datenschlüssel umschließt.

**Credential Vending:**
- Zwei Varianten: Table Credential Vending (registrierte Daten im Metastore) und Path Credential Vending (External Locations).
- Ausgestellte Credentials sind pfadbeschränkt, laufen automatisch schnell ab und vererben die Privilegien des anfragenden Principals.
- Für externe Systeme (Unity-REST-API, Apache-Iceberg-REST-Catalog) muss External Access am Metastore konfiguriert sein und `EXTERNAL USE SCHEMA` vergeben sein.

**Verschlüsselung — Control Plane vs. Data Plane:**
- Control Plane (Databricks-betrieben): Web-App, Notebooks, Secrets, SQL-Queries, Dashboards, Metadaten, AI/BI-Dashboards, Genie Agents.
- Data Plane (im Cloud-Account des Kunden): Cluster-Storage, EBS-Volumes/Managed Disks, Workspace-Storage-Buckets, optional DBFS-Root.

**Envelope Encryption (Customer-Managed Keys, Enterprise-Tier):**
1. Data Encryption Key (DEK) — AES-256, verschlüsselt die eigentlichen Inhalte.
2. Customer-Managed Key (CMK) — eigener Schlüssel des Kunden (AWS KMS/Azure Key Vault), umschließt den DEK.
3. Databricks-Managed Key (DMK) — verschlüsselt den bereits umschlossenen DEK zusätzlich.

Wird der CMK gelöscht/entzogen, kann Databricks die damit verschlüsselten Daten nicht mehr entschlüsseln — auch nicht bei interner Kompromittierung. Serverless Workspaces nutzen ausschließlich Managed-Services-Verschlüsselung.

**Best-Practice-Bezüge:** Unity Catalog nie umgehen (kein gleichzeitiges DBFS-Mount und External-Location-Zugriff auf denselben Storage-Account); direkten Bucket-Zugriff einschränken; `CREATE EXTERNAL LOCATION` restriktiv vergeben; DBFS vermeiden (stattdessen Volumes).

Keine Code-Beispiele in dieser Datei.

---

## 17. Berechtigungskonzepte: Objekthierarchie, Vererbung und Eigentümerschaft

**Einfach erklärt:** Unity Catalog organisiert Daten in einer dreistufigen Hierarchie `catalog.schema.tabelle`. Catalogs und Schemas sind Container: Privilegien darauf vererben sich automatisch an alle aktuellen und künftigen Kindobjekte. Um auf ein Kindobjekt zuzugreifen, reicht ein Grant auf diesem Objekt aber nicht — man braucht zusätzlich `USE CATALOG` auf dem Catalog und `USE SCHEMA` auf dem Schema. Jedes Objekt hat genau einen Eigentümer, der automatisch alle Rechte darauf besitzt, aber Eigentümerschaft vererbt sich nicht nach unten (nur automatische `MANAGE`-Fähigkeit auf Kindobjekten).

**Wichtige Privilegien im Überblick:**

| Privileg | Bedeutung |
|---|---|
| `SELECT` | Lesezugriff auf Tabellen/Views |
| `MODIFY` | Schreibzugriff auf Tabellen |
| `USE CATALOG` / `USE SCHEMA` | Navigationsrechte, erforderlich für den Zugriff auf Kindobjekte |
| `CREATE TABLE` / `CREATE SCHEMA` | Rechte zur Objekterstellung |
| `MANAGE` | Volle Kontrolle inkl. Privilegienverwaltung und Übertragung der Eigentümerschaft |
| `BROWSE` | Metadaten-Entdeckung ohne Datenzugriff |

**Kontrollgrenze:** `USE CATALOG` ist eine wichtige Zugriffskontrollgrenze — selbst wenn ein Table-Owner `SELECT` gewährt, bleibt der Zugriff wirkungslos ohne `USE CATALOG`/`USE SCHEMA` auf den Elternobjekten. Da nur Catalog-/Schema-Owner (oder `MANAGE`-Inhaber) diese Usage-Privilegien vergeben können, behalten sie die Kontrolle darüber, wer wirklich zugreifen kann.

**Ausnahme `BROWSE`:** ermöglicht Objekt-Entdeckung und Metadaten-Einsicht ganz ohne `USE CATALOG`/`USE SCHEMA`, gewährt aber keinen Datenzugriff.

**Vererbung:** Grants auf einem übergeordneten Objekt kaskadieren automatisch an alle aktuellen und künftigen Kindobjekte — Ausnahme: Grants auf Metastore-Ebene vererben sich nicht, sie steuern Metastore-weite Operationen wie `CREATE CATALOG`.

Keine Code-Beispiele in dieser Datei.

---

## 18. Privilegien-Referenz: die vollständige Tabelle

**Einfach erklärt:** Diese Referenztabelle listet jedes einzelne Unity-Catalog-Privileg, auf welche Objekttypen es sich anwenden lässt und was es konkret erlaubt — sie ist die zentrale Nachschlage-Grundlage für alle `GRANT`-Entscheidungen.

| Privileg | Gilt für | Erlaubt |
|---|---|---|
| `ACCESS` | Service Credential | Ein Service Credential zum Zugriff auf einen externen Dienst nutzen |
| `ALL PRIVILEGES` | Catalog, Schema, Tabelle, View, Materialized View, Volume, Funktion, Feature, Connection, External Location, External Metadata, Secret, Service, Service Credential, Storage Credential | Alle auf das Objekt anwendbaren Fähigkeiten |
| `APPLY TAG` | Catalog, Schema, Tabelle, View, Materialized View, Volume, Funktion (nur Modelle), External Metadata | Tags auf einem Objekt hinzufügen/bearbeiten |
| `BROWSE` | Catalog, External Location, External Metadata, Clean Room | Objekte entdecken, Metadaten einsehen, Zugriff anfragen |
| `CREATE CATALOG` | Metastore | Einen Catalog im Metastore erstellen |
| `CREATE CLEAN ROOM` | Metastore | Multi-Party-Zusammenarbeit ohne Offenlegung der zugrunde liegenden Daten |
| `CREATE CONNECTION` | Metastore, Service Credential | Eine Connection zu einer externen Datenbank erstellen |
| `CREATE EXTERNAL LOCATION` | Metastore, Storage Credential | Cloud-Speicher mit einem Credential verknüpfen |
| `CREATE EXTERNAL METADATA` | Metastore | Objekte für benutzerdefinierte Data Lineage anlegen |
| `CREATE EXTERNAL TABLE` | External Location, Storage Credential | External Tables an Cloud-Speicherpfaden erstellen |
| `CREATE EXTERNAL VOLUME` | External Location | External Volumes über eine External Location erstellen |
| `CREATE FEATURE` | Catalog, Schema | Feature-Erstellung in Schemas |
| `CREATE FOREIGN CATALOG` | Connection | Foreign Catalogs über eine Lakehouse-Federation-Connection erstellen |
| `CREATE FOREIGN SECURABLE` | External Location | Autorisierte Pfade für Foreign Catalogs festlegen |
| `CREATE FUNCTION` | Catalog, Schema | Funktionen in einem Schema erstellen |
| `CREATE MANAGED STORAGE` | External Location | Benutzerdefinierten Speicherort für Managed Tables festlegen |
| `CREATE MATERIALIZED VIEW` | Catalog, Schema | Materialized Views in einem Schema erstellen |
| `CREATE MODEL` | Catalog, Schema | MLflow-registrierte Modelle in einem Schema erstellen |
| `CREATE MODEL VERSION` | Model | Neue Version eines bestehenden MLflow-Modells registrieren |
| `CREATE PROVIDER` | Metastore | Ein OpenSharing-Provider-Objekt erstellen |
| `CREATE RECIPIENT` | Metastore | Ein OpenSharing-Recipient-Objekt erstellen |
| `CREATE SCHEMA` | Catalog | Ein Schema in einem Catalog erstellen |
| `CREATE SECRET` | Catalog, Schema | Ein Secret in einem Schema erstellen |
| `CREATE SERVICE` | Catalog, Schema | Model- oder MCP-Service erstellen |
| `CREATE SERVICE CREDENTIAL` | Metastore | Ein Service Credential im Metastore erstellen |
| `CREATE SHARE` | Metastore | Einen OpenSharing-Share erstellen |
| `CREATE STORAGE CREDENTIAL` | Metastore | Ein Storage Credential im Metastore erstellen |
| `CREATE TABLE` | Catalog, Schema | Tabellen oder Views in einem Schema erstellen |
| `CREATE VOLUME` | Catalog, Schema | Volumes in einem Schema erstellen |
| `EXECUTE` | Catalog, Schema, Funktion, Service | Eine Funktion aufrufen oder ein Modell zur Inferenz laden |
| `EXECUTE CLEAN ROOM TASK` | Clean Room | Notebooks ausführen und Details in einem Clean Room einsehen |
| `EXTERNAL USE LOCATION` | External Location | Zugriff über externe Verarbeitungs-Engines |
| `EXTERNAL USE SCHEMA` | Schema | Zugriff auf Unity-Catalog-Tabellen von externen Engines aus |
| `MANAGE` | Catalog, Schema, Tabelle, View, Materialized View, Volume, Funktion, Feature, Connection, External Location, External Metadata, Secret, Service, Service Credential, Storage Credential, Clean Room | Privilegien verwalten, Eigentümerschaft übertragen, umbenennen, löschen |
| `MANAGE ALLOWLIST` | Metastore | Init-Skripte und Bibliotheken auf Clustern kontrollieren |
| `MODIFY` | Catalog, Schema, Tabelle, External Metadata | Daten in einer Tabelle einfügen, aktualisieren, löschen |
| `MODIFY CLEAN ROOM` | Clean Room | Daten-Assets, Notebooks und Kommentare aktualisieren |
| `READ FEATURE` | Catalog, Schema, Feature | Feature-Metadaten und materialisierte Daten lesen |
| `READ FILES` | External Location | Dateien direkt aus Cloud-Speicher lesen |
| `READ METADATA` | Metastore, Catalog, Schema, Tabelle, View, Materialized View, Volume, Funktion, Feature, Connection, External Location, External Metadata, Secret, Service Credential, Storage Credential, Service, Clean Room | Alle für den Eigentümer sichtbaren Metadaten einsehen, ohne zu ändern |
| `READ SECRET` | Catalog, Schema, Secret | Einen Secret-Wert aus einem Notebook oder Job abrufen |
| `READ VOLUME` | Catalog, Schema, Volume | Dateien und Verzeichnisse in einem Volume lesen |
| `REFERENCE SECRET` | Catalog, Schema, Secret | Secrets referenzieren, ohne den Wert offenzulegen |
| `REFRESH` | Catalog, Schema, Materialized View | Ein manuelles Refresh einer Materialized View auslösen |
| `SELECT` | Catalog, Schema, Tabelle, View, Materialized View, Share | Daten aus einer Tabelle, View oder einem Share abfragen |
| `SET SHARE PERMISSION` | Metastore | Einem OpenSharing-Recipient Zugriff auf einen Share gewähren |
| `USE CATALOG` | Catalog | Erforderlich, um mit Objekten innerhalb eines Catalogs zu interagieren |
| `USE CONNECTION` | Connection | Connection-Details auflisten und einsehen |
| `USE MARKETPLACE ASSETS` | Metastore | Zugriff auf Datenprodukte im Databricks Marketplace |
| `USE PROVIDER` | Metastore | OpenSharing-Provider einsehen und Catalogs mounten |
| `USE RECIPIENT` | Metastore | OpenSharing-Recipients und Shares einsehen |
| `USE SCHEMA` | Catalog, Schema | Erforderlich, um mit Objekten innerhalb eines Schemas zu interagieren |
| `USE SHARE` | Metastore | OpenSharing-Shares und deren Assets einsehen |
| `WRITE FILES` | External Location | Dateien direkt in Cloud-Speicherpfade schreiben |
| `WRITE SECRET` | Catalog, Schema, Secret | Einen Secret-Wert aktualisieren |
| `WRITE VOLUME` | Catalog, Schema, Volume | Dateien in einem Volume hinzufügen, ändern, löschen |

**Wichtige Hinweise:**
- `ALL PRIVILEGES` schließt explizit `EXTERNAL USE SCHEMA`, `EXTERNAL USE LOCATION`, `MANAGE` und `READ METADATA` **aus**.
- `BROWSE` ermöglicht Discovery, ohne dass `USE CATALOG` oder `USE SCHEMA` nötig sind. `BROWSE` gilt **nicht** für Secrets; `CREATE SECRET` wird auf Catalog- oder Schema-Ebene vergeben.
- `CREATE FOREIGN CATALOG` (Lakehouse Federation) hat eine doppelte Voraussetzung: Neben dem Privileg auf der `CONNECTION` (oder alternativ auf dem Metastore) wird zusätzlich `CREATE CATALOG` auf dem Metastore benötigt, und der Ausführende muss Owner der Connection sein oder `CREATE FOREIGN CATALOG` darauf besitzen. Ist der Foreign Catalog einmal erstellt, gelten für ihn dieselben Regeln wie für jeden regulären Catalog.
- `READ METADATA` ist sicherheitssensibel — es legt Berechtigungen, Row Filter und Column Masks offen.
- Vererbung greift bei Grants auf Container-Ebene (Catalog/Schema).
- Grundsatz: geringstmögliches Privileg. Empfehlung: Erstellungsrechte eher auf Schema- als auf Catalog-Ebene vergeben.

Keine Code-Beispiele in dieser Datei.

---

## 19. Workspace-Catalog-Bindung

**Einfach erklärt:** Standardmäßig ist jeder Catalog von jedem Workspace aus zugänglich, der am selben Metastore hängt. Workspace-Catalog-Binding erlaubt es, einen Catalog auf bestimmte Workspaces zu beschränken — Zugriffsversuche aus nicht zugewiesenen Workspaces werden abgelehnt, selbst wenn der Nutzer eigentlich passende Privilegien besitzt. Das Feature dient z. B. dazu, Produktionsdaten von Entwicklungsumgebungen zu isolieren.

**Anwendungsfälle:** Produktionsdaten von Dev/Test isolieren; verhindern, dass bestimmte Datendomänen zusammen gejoint werden; sicherstellen, dass sensible Daten nur in dafür vorgesehenen Workspaces verarbeitet werden.

**Weitere Eigenschaften:**
- Nur-Lese-Zugriff: Workspaces lassen sich auf Lesezugriff beschränken, alle Schreiboperationen werden dann blockiert.
- Plattformweite Durchsetzung: Information-Schema-Abfragen, Data Lineage und Catalog Explorer zeigen jeweils nur die im aktuellen Workspace zugänglichen Catalogs.
- Erweiterter Geltungsbereich: gilt nicht nur für Catalogs, sondern auch für External Locations, Storage Credentials und Service Credentials.

**Voraussetzungen:** Metastore-Admin, Catalog-Eigentümer oder `MANAGE`-Privileg auf dem Catalog.

**CLI-Ablauf:** 1. Isolation Mode auf `ISOLATED` setzen. 2. `workspace-bindings update-bindings` mit dem gewünschten Binding-Typ ausführen — `BINDING_TYPE_READ_WRITE` oder `BINDING_TYPE_READ_ONLY`.

Keine Code-Beispiele in dieser Datei.

---

## 20. Privilegien verwalten — Überblick

**Einfach erklärt:** Ganz zu Beginn hat niemand automatisch Zugriff auf Daten in einem Metastore — nur Account-Admins, Workspace-Admins und Metastore-Admins besitzen standardmäßig Verwaltungsrechte für Unity Catalog. Wer sonst Privilegien vergeben darf, hängt von der Rolle ab: Objekteigentümer, Eigentümer des übergeordneten Catalogs/Schemas, Nutzer mit `MANAGE`-Privileg oder Metastore-Admins.

**Grants anzeigen:** Nutzer mit `MANAGE`-Privileg können alle Grants auf einem Objekt einsehen. Aktuelle Einschränkung: Nutzer mit `MANAGE`-Privileg auf einem Objekt können nicht alle Grants für dieses Objekt im `INFORMATION_SCHEMA` einsehen.

Keine Code-Beispiele in dieser Datei.

---

## 21. Prinzipal-Typen: Nutzer, Gruppen, Service Principals

**Einfach erklärt:** In `GRANT`/`REVOKE`-Statements kann der Empfänger eines Privilegs ein Nutzer, ein Service Principal oder eine Gruppe sein. Namen mit Sonderzeichen — z. B. E-Mail-Adressen (enthalten `@` und `.`) oder Gruppennamen mit Bindestrich — müssen dabei in Backticks eingeschlossen werden. Service Principals werden über ihre `applicationId` referenziert, Gruppen syntaktisch wie einfache Nutzer behandelt.

```sql
GRANT SELECT ON TABLE sample_data TO `alf@melmak.et`;
GRANT CREATE TABLE ON SCHEMA main.default TO `finance-team`;
```

```sql
-- Privileg an den Service Principal fab9e00e-ca35-11ec-9d64-0242ac120002 vergeben
GRANT SELECT ON TABLE t TO `fab9e00e-ca35-11ec-9d64-0242ac120002`;
```

```sql
GRANT ALL PRIVILEGES ON TABLE forecasts TO finance;
```

**Vertiefung — Prinzipal-Syntax (`sql-ref-principal`):**

```sql
{ `<user>@<domain-name>` | `<sp-application-id>` | group_name | users | `account users` }
```

```sql
-- Privileg an die Sondergruppe "alle Account-Nutzer" entziehen
REVOKE SELECT ON TABLE t FROM `account users`;

-- Eigentümerschaft eines Schemas auf eine Gruppe übertragen
ALTER SCHEMA some_schema OWNER TO `some-group`;
```

**`CREATE GROUP`:**

```sql
CREATE GROUP group_principal
  [ WITH
    [ USER user_principal [, ...] ]
    [ GROUP subgroup_principal [, ...] ]
  ]
```

```sql
-- Leere Gruppe anlegen
CREATE GROUP humans;

-- Gruppe mit zwei Nutzern als Mitglieder anlegen
CREATE GROUP tv_aliens WITH USER `alf@melmak.et`, `thor@asgaard.et`;

-- Gruppe mit einem Nutzer UND einer Untergruppe anlegen (verschachtelte Gruppen)
CREATE GROUP aliens WITH USER `hilo@jannus.et` GROUP tv_aliens;
```

**`ALTER GROUP` — Mitglieder hinzufügen/entfernen:**

```sql
ALTER GROUP parent_principal { ADD | DROP }
  { GROUP group_principal [, ...] | USER user_principal [, ...] } [...]
```

```sql
ALTER GROUP aliens ADD GROUP tv_aliens;
ALTER GROUP aliens DROP USER `alf@melmak.et`;
ALTER GROUP tv_aliens ADD USER `alf@melmak.et`;
```

**`DROP GROUP`:**

```sql
DROP GROUP group_principal
```

```sql
DROP GROUP aliens;
```

---

## 22. Schlüsselprivilegien im Detail: Abhängigkeiten und Ausnahmen

**Einfach erklärt:** Viele Privilegien funktionieren nicht isoliert, sondern setzen andere Privilegien voraus — dieses Thema erklärt die genauen Regeln hinter `ALL PRIVILEGES`, `MANAGE`, den Create-Privilegien sowie `SELECT`/`MODIFY` und den File-/Volume-Privilegien.

**`ALL PRIVILEGES`:** Erlaubt alle Fähigkeiten auf dem Objekt und seinen Kindobjekten. Bei `SHOW GRANTS` wird nur `ALL PRIVILEGES` angezeigt, nicht die Einzelrechte. Es wird zum Zeitpunkt der Zugriffsprüfung neu ausgewertet (dynamisch), nicht zum Zeitpunkt des Grants. Ausnahme: umfasst nicht `EXTERNAL USE SCHEMA`, `EXTERNAL USE LOCATION`, `MANAGE` oder `READ METADATA`.

**`OWNERSHIP`:** Owner besitzen automatisch alle Fähigkeiten auf ihrem Objekt. Wird nicht nach unten vererbt, aber Owner erhalten automatisch die Fähigkeit, Kindobjekte zu verwalten (z. B. Catalog-Owner besitzt Kind-Schemas nicht, kann sie aber verwalten). Der ursprüngliche Ersteller eines Objekts wird automatisch dessen Owner.

**`MANAGE`:** Erlaubt Privilegienverwaltung, Ownership-Übertragung und Löschen des Objekts, ohne dessen Owner zu sein. Entscheidend: `MANAGE`-Inhaber erhalten nicht automatisch alle anderen Privilegien — jedes muss separat gewährt werden, kann sich aber selbst zuweisen. `MANAGE` auf einem Container vererbt sich auf alle Kindobjekte. `MANAGE` ist nicht in `ALL PRIVILEGES` enthalten.

**`CREATE TABLE`/`CREATE SCHEMA`/`CREATE VOLUME`:** Reichen jeweils allein nicht aus. `CREATE SCHEMA` braucht zusätzlich `USE CATALOG`; `CREATE TABLE` und `CREATE VOLUME` brauchen zusätzlich `USE CATALOG` und `USE SCHEMA`.

**`SELECT`/`MODIFY`:** `SELECT` erfordert zusätzlich `USE CATALOG` und `USE SCHEMA`. `MODIFY` erfordert zusätzlich `SELECT` auf derselben Tabelle sowie `USE SCHEMA` und `USE CATALOG`.

**`READ VOLUME`/`WRITE VOLUME`:** Beide erfordern zusätzlich `USE SCHEMA` und `USE CATALOG`.

**`READ FILES`/`WRITE FILES`:** `WRITE FILES` erfordert, dass `READ FILES` ebenfalls auf derselben External Location gewährt ist — sonst `PERMISSION_DENIED`. Databricks empfiehlt stattdessen Volumes (`READ VOLUME`/`WRITE VOLUME`) für den regulären Zugriff.

**`CREATE EXTERNAL TABLE`:** Sollte eher auf einer External Location als auf einem Storage Credential vergeben werden (pfadgebunden, mehr Kontrolle).

**`EXECUTE`:** Erlaubt Aufruf einer Function bzw. Laden eines Models zur Inferenz; bei Functions zusätzlich Einsicht in Definition/Metadaten. Erfordert zusätzlich `USE CATALOG`/`USE SCHEMA`.

**`READ METADATA`:** Kind-Privileg von `MANAGE`, nicht in `ALL PRIVILEGES` enthalten, muss explizit vergeben werden. Erlaubt Einsicht aller eigentümersichtbaren Metadaten (inkl. Grants, Row-Filter, Column-Masks, ABAC-Policies), aber keine Änderung.

Keine Code-Beispiele in dieser Datei.

---

## 23. Standardrechte ohne expliziten Grant

**Einfach erklärt:** Nicht jede Berechtigung muss manuell vergeben werden — Unity Catalog stattet neue Nutzer automatisch mit ein paar Grundrechten aus, ohne dass ein Admin dafür einen `GRANT` ausführen muss.

- **Catalog `main`:** Alle Nutzer besitzen standardmäßig `USE CATALOG` darauf.
- **Workspace-Catalog:** Alle Workspace-Nutzer erhalten `USE CATALOG` auf dem Workspace-Catalog. Zusätzlich erhalten sie auf dem Schema `default` in diesem Catalog: `USE SCHEMA`, `CREATE TABLE`, `CREATE VOLUME`, `CREATE MODEL`, `CREATE FUNCTION`, `CREATE MATERIALIZED VIEW`.

Keine Code-Beispiele in dieser Datei.

---

## 24. GRANT, REVOKE und SHOW GRANTS — vollständige Syntax

**Einfach erklärt:** Diese drei SQL-Befehle bilden das Kernwerkzeug der Zugriffsverwaltung: `GRANT` vergibt Privilegien, `REVOKE` entzieht sie wieder (auch wenn sie nie vergeben waren — kein Fehler), und `SHOW GRANTS` zeigt alle wirksamen Privilegien auf einem Objekt, inklusive geerbter und verweigerter. Zusätzlich gibt es `DENY`, das jeden Grant übersteuert und die stärkste Regel in der Hierarchie ist.

**`GRANT`:**

```sql
GRANT privilege_types ON securable_object TO principal

privilege_types { ALL PRIVILEGES | privilege_type [, ...] }
```

```sql
GRANT CREATE ON SCHEMA my_schema TO `alf@melmak.et`;
GRANT ALL PRIVILEGES ON TABLE forecasts TO finance;
GRANT SELECT ON TABLE sample_data TO `alf@melmak.et`;

-- Privileg an einen Service Principal vergeben
GRANT SELECT ON TABLE t TO `fab9e00e-ca35-11ec-9d64-0242ac120002`;
```

Hinweis: Der `samples`-Catalog lässt sich nicht per `GRANT` verändern — er ist für alle Workspaces verfügbar, aber schreibgeschützt.

**`GRANT ... ON SHARE` (Delta Sharing) — eigene Syntax:**

```sql
GRANT SELECT ON SHARE <share-name> TO RECIPIENT <recipient-name>;
REVOKE SELECT ON SHARE <share-name> FROM RECIPIENT <recipient-name>;
```

**`REVOKE`:**

```sql
REVOKE privilege_types ON securable_object FROM principal

privilege_types { ALL PRIVILEGES | privilege_type [, ...] }
```

```sql
REVOKE ALL PRIVILEGES ON SCHEMA default FROM `alf@melmak.et`;
REVOKE SELECT ON TABLE t FROM aliens;
```

**`SHOW GRANTS`:**

```sql
SHOW GRANTS [ principal ] ON securable_object
```

```sql
SHOW GRANTS `alf@melmak.et` ON SCHEMA my_schema;
-- principal      actionType  objectType  objectKey
-- alf@melmak.et  USE         DATABASE    my_schema

SHOW GRANTS ON SHARE some_share;
-- recipient  actionType  objectType  objectKey
-- A_Corp     SELECT
-- B.com      SELECT

SHOW GRANTS ON CONNECTION mysql_connection;
-- principal      actionType              objectType  objectKey
-- alf@melmak.et  CREATE FOREIGN CATALOG  CONNECTION  mysql_connection
-- alf@melmak.et  USE CONNECTION          CONNECTION  mysql_connection
```

Auf Metastore-Ebene entfällt der Objektname:

```sql
SHOW GRANTS [ principal ] ON METASTORE;
```

**Vertiefung — `DENY`:**

```sql
DENY privilege_types ON securable_object TO principal

privilege_types { ALL PRIVILEGES | privilege_type [, ...] }
```

```sql
-- Alf das Recht verweigern, `t` abzufragen
DENY SELECT ON TABLE t TO `alf@melmak.et`;

-- DENY wieder aufheben
REVOKE SELECT ON TABLE t FROM `alf@melmak.et`;
```

**Vertiefung — `sql-ref-privileges`, weitere Privilegtypen:**

```sql
GRANT SELECT ON TABLE t TO `alf@melmak.et`;
REVOKE USE SCHEMA ON SCHEMA some_schema FROM `account users`;
GRANT READ METADATA ON SCHEMA some_schema TO `auditors`;
```

**Vertiefung — `SHOW GRANTS`, zusätzliches Beispiel:**

```sql
SHOW GRANTS `alf@melmak.et` ON SCHEMA my_schema;
SHOW GRANTS ON SHARE some_share;
SHOW GRANTS ON CONNECTION mysql_connection;
```

---

## 25. Eigentümerschaft übertragen (OWNER TO)

**Einfach erklärt:** Mit `ALTER ... OWNER TO` lässt sich die Eigentümerschaft eines Objekts (Catalog, Schema, Table, View, Volume, External Location, Storage Credential) auf einen anderen Nutzer, ein Service Principal oder eine Gruppe übertragen. Bei sensiblen Objekttypen wie Views, Functions, Models und Shares gelten schärfere Regeln, um Privilege Escalation zu verhindern.

```sql
ALTER <securable-type> <securable-name> OWNER TO <principal>;
```

```sql
ALTER TABLE mycatalog.myschema.orders OWNER TO `accounting`;
```

```sql
ALTER CATALOG some_cat OWNER TO 'alf@melmak.et';
```

```sql
ALTER SCHEMA main.bronze OWNER TO `data-engineers`;
```

```sql
ALTER VOLUME main.bronze.landing_files SET OWNER TO `data-engineers`;
```

**Unterstützte Objekttypen:** Catalogs, Schemas, Tables, Views, Volumes, External Locations und Storage Credentials. Ausdrücklich nicht unterstützt: `METASTORE`.

**Wer darf übertragen?** Aktueller Owner, Metastore-Admin, Owner des Containers (Catalog für ein Schema, Schema für eine Table) oder Nutzer mit `MANAGE`-Privileg auf dem Objekt.

**Einschränkung bei Views/Functions/Models:** Nur ein Metastore-Admin kann die Ownership an einen beliebigen Nutzer/SP/Gruppe im Account übertragen. Aktuelle Owner und `MANAGE`-Inhaber dürfen die Ownership nur an sich selbst oder eine Gruppe übertragen, deren Mitglied sie sind. Bei Shares gilt ebenfalls: Nur ein Metastore-Admin kann die Share-Eigentümerschaft übertragen.

---

## 26. Admin-Privilegien: Account-, Workspace- und Metastore-Admin

**Einfach erklärt:** Databricks unterscheidet drei Admin-Rollen mit unterschiedlichem Geltungsbereich: Account-Admins verwalten den gesamten Account, Workspace-Admins einzelne Workspaces, und Metastore-Admins (optional, aber hochprivilegiert) einen einzelnen Metastore.

**Account-Admin** (Account-Ebene): Metastores und Workspaces erstellen/verwalten, Metastores mit Workspaces verknüpfen, Admin-Rollen im gesamten Account zuweisen, Storage Credentials und System-Tabellen verwalten, OpenSharing aktivieren.

**Workspace-Admin:** Catalogs und Metastore-Objekte erstellen (in Workspaces, die nach dem 8. November 2023 für Unity Catalog aktiviert wurden, erhalten Workspace-Admins dafür standardmäßig Metastore-Privilegien), Workspace-Mitgliedschaft und Job-Eigentümerschaft verwalten, Workspace-Objekte kontrollieren (Notebooks, Dashboards, Queries), die Workspace-Admin-Rolle weitergeben. Workspace-Admins sind standardmäßig Eigentümer des Workspace-Catalogs, sofern für den Workspace einer bereitgestellt wurde.

**Metastore-Admin (optional):** Catalogs, Connections, External Locations erstellen; Storage- und Service-Credentials verwalten; Shares, Recipients und Providers erstellen; Objekteigentümerschaft ändern und Privilegien verwalten. Zuweisung durch einen Account-Admin über die Account Console.

Keine Code-Beispiele in dieser Datei.

---

## 27. Access Request Destinations (Request for Access)

**Einfach erklärt:** Mit dem Feature "Request for Access" (RFA) können Nutzer direkt aus dem Produkt heraus fehlende Privilegien anfragen, statt einen Admin manuell kontaktieren zu müssen. Admins legen dafür "Access Request Destinations" fest — also wohin diese Anfragen geleitet werden (E-Mail, Slack, Teams, Webhook oder eine Redirect-URL).

**Mögliche Ziele:** E-Mail-Adressen, Slack-Kanäle, Microsoft-Teams-Kanäle, Webhook-Endpunkte, Redirect-URLs zu externen Systemen (nur eine pro Objekt möglich — ist eine URL gesetzt, können keine weiteren Ziele gesetzt werden, Nutzer werden dann direkt dorthin umgeleitet statt das In-Product-Formular zu sehen).

**Einstiegspunkte für Nutzer:** Catalog Explorer (Catalog durchsuchen, zusätzliche Privilegien anfragen), SQL-Editor/Notebooks (Zugriff über Berechtigungsfehlermeldungen anfragen), AI/BI-Dashboards (Zugriff für fehlende Datensätze anfragen), Genie Agents (Zugriff über ein "Zugriff verweigert"-Banner anfragen).

**Auflösungsreihenfolge der Ziele** (bei aktiviertem RFA auf Metastore-Ebene):
1. Explizites Ziel auf Objektebene
2. E-Mail des Objekteigentümers (falls Einzelnutzer)
3. Ziel des übergeordneten Objekts (falls Eigentümer eine Gruppe/ein Service Principal ist)
4. Ziel auf Metastore-Ebene

Ziele vererben sich nach unten: Ein auf einer höheren Ebene der Unity-Catalog-Hierarchie konfiguriertes Ziel gilt auch für alle Kindobjekte.

**Konfiguration:** Metastore-Admins aktivieren Request for Access auf Metastore-Ebene über die Catalog-Einstellungen. Objekteigentümer oder Nutzer mit `MANAGE`-Privileg konfigurieren Ziele für einzelne Objekte über Catalog Explorer, REST-API oder Terraform.

**Genehmigungsprozess:** Genehmiger erhalten Benachrichtigungen mit Links zur Prüfung der Anfrage. Sie können Anfragende zu bestehenden Gruppen hinzufügen oder Privilegien direkt über Presets wie "Data Reader" vergeben.

Keine Code-Beispiele in dieser Datei.

---

## 28. Grant-Rezepte für häufige Szenarien

**Einfach erklärt:** Dieses Thema sammelt vollständige, direkt kopierbare `GRANT`-Kombinationen für die häufigsten Zugriffs-Szenarien im Alltag — vom reinen Lesezugriff über Tabellenerstellung, Volume-Zugriff, `COPY INTO`/`read_files` bis zu einem zusammengesetzten "Data Engineer"-Rollenprofil. Jedes Rezept berücksichtigt konsequent die `USE CATALOG`/`USE SCHEMA`-Kette, ohne die ein Grant wirkungslos bleibt.

### a) Nutzer/Gruppe soll eine Tabelle nur lesen können

```sql
GRANT USE CATALOG ON CATALOG main TO `data-consumers`;
GRANT USE SCHEMA ON SCHEMA main.default TO `data-consumers`;
GRANT SELECT ON TABLE main.default.department TO `data-consumers`;
```

Alternative, kompakter über Vererbung: `SELECT` auf dem gesamten Schema statt auf einer einzelnen Tabelle vergeben — gilt dann automatisch für alle aktuellen und künftigen Tabellen/Views darin:

```sql
GRANT USE CATALOG ON CATALOG main TO `data-consumers`;
GRANT USE SCHEMA ON SCHEMA main.default TO `data-consumers`;
GRANT SELECT ON SCHEMA main.default TO `data-consumers`;
```

### b) Nutzer/Gruppe soll neue Tabellen in einem Schema anlegen können

```sql
GRANT CREATE TABLE ON SCHEMA main.default TO `finance-team`;
GRANT USE SCHEMA ON SCHEMA main.default TO `finance-team`;
GRANT USE CATALOG ON CATALOG main TO `finance-team`;
```

### c) Nutzer/Gruppe soll Dateien aus einem Volume lesen bzw. lesen+schreiben können

```sql
-- Nur Lesezugriff
GRANT READ VOLUME ON VOLUME unstructured_data_lab.raw.files_volume
TO `<user-or-group-name>`;

-- Lese- und Schreibzugriff
GRANT READ VOLUME, WRITE VOLUME ON VOLUME unstructured_data_lab.raw.files_volume
TO `<user-or-group-name>`;

-- Alle Privilegien auf dem Volume
GRANT ALL PRIVILEGES ON VOLUME unstructured_data_lab.raw.files_volume
TO `<user-or-group-name>`;
```

Zusätzlich (analog zu a/b) auf den Elternobjekten nötig:

```sql
GRANT USE CATALOG ON CATALOG unstructured_data_lab TO `<user-or-group-name>`;
GRANT USE SCHEMA ON SCHEMA unstructured_data_lab.raw TO `<user-or-group-name>`;
```

Aktuelle Rechte auf dem Volume anzeigen:

```sql
SHOW GRANTS ON VOLUME unstructured_data_lab.raw.files_volume;
```

### d) Ein Volume selbst anlegen können (managed oder external)

```sql
-- Voraussetzung für ein managed Volume
GRANT USE CATALOG ON CATALOG main TO `data-engineers`;
GRANT USE SCHEMA ON SCHEMA main.bronze TO `data-engineers`;
GRANT CREATE VOLUME ON SCHEMA main.bronze TO `data-engineers`;

CREATE VOLUME main.bronze.landing_files;
```

```sql
-- Zusätzlich für ein external Volume
GRANT CREATE EXTERNAL VOLUME ON EXTERNAL LOCATION my_ext_location TO `data-engineers`;

CREATE EXTERNAL VOLUME main.bronze.landing_files_ext
LOCATION 's3://my-bucket/landing/';
```

### e) Per `read_files`/`COPY INTO` aus einer External Location oder einem Volume laden

Voraussetzung: `READ VOLUME`-Privileg auf einem Volume **oder** `READ FILES`-Privileg auf einer External Location, plus `USE SCHEMA` auf dem Schema der Ziel-Table und `USE CATALOG` auf dem übergeordneten Catalog.

```sql
-- Laden aus einem Volume
GRANT USE CATALOG ON CATALOG quickstart_catalog TO `data-engineers`;
GRANT USE SCHEMA ON SCHEMA quickstart_catalog.quickstart_schema TO `data-engineers`;
GRANT READ VOLUME ON VOLUME quickstart_catalog.quickstart_schema.quickstart_volume TO `data-engineers`;

COPY INTO quickstart_catalog.quickstart_schema.landing_table
FROM '/Volumes/quickstart_catalog/quickstart_schema/quickstart_volume/raw_data'
FILEFORMAT = PARQUET;
```

```sql
-- Laden aus einer External Location
GRANT USE CATALOG ON CATALOG quickstart_catalog TO `data-engineers`;
GRANT USE SCHEMA ON SCHEMA quickstart_catalog.quickstart_schema TO `data-engineers`;
GRANT READ FILES ON EXTERNAL LOCATION my_ext_location TO `data-engineers`;

COPY INTO my_json_data
FROM 'abfss://container@storageAccount.dfs.core.windows.net/jsonData'
FILEFORMAT = JSON;
```

**Wichtige Einschränkung zur External-Location-Vererbung:** Berechtigungen auf einer External Location gewähren keine Privilegien auf Verzeichnissen oberhalb oder parallel zum angegebenen Pfad — sie gelten nur für den definierten Pfad und dessen Unterverzeichnisse.

Für `read_files` gilt dieselbe Grundregel:

```sql
GRANT READ FILES, WRITE FILES ON EXTERNAL LOCATION <location-name> TO <principal>;

SELECT * FROM read_files('s3://<bucket>/<path>', format => 'csv');
```

### f) Neue externe Tabelle direkt an einem Cloud-Speicherpfad anlegen

```sql
GRANT USE CATALOG ON CATALOG main TO `data-engineers`;
GRANT USE SCHEMA ON SCHEMA main.bronze TO `data-engineers`;
GRANT CREATE TABLE ON SCHEMA main.bronze TO `data-engineers`;
GRANT CREATE EXTERNAL TABLE ON EXTERNAL LOCATION my_ext_location TO `data-engineers`;
```

### g) Ein „Data Engineer"-Rollenprofil: Bronze-Tabellen aus Cloud-Speicher bauen

Dieses zusammengesetzte Rollenprofil kombiniert die einzelnen Anforderungen der Rezepte (b), (d) und (e).

```sql
-- 1. Zugriff auf Ziel-Catalog/-Schema (Bronze-Layer)
GRANT USE CATALOG ON CATALOG main TO `data-engineers`;
GRANT USE SCHEMA ON SCHEMA main.bronze TO `data-engineers`;

-- 2. Tabellen im Bronze-Schema anlegen und befüllen dürfen
GRANT CREATE TABLE ON SCHEMA main.bronze TO `data-engineers`;
GRANT SELECT, MODIFY ON SCHEMA main.bronze TO `data-engineers`;

-- 3a. Rohdaten aus einem Volume lesen (empfohlener Weg)
GRANT READ VOLUME ON VOLUME main.landing.raw_files TO `data-engineers`;

-- 3b. Alternativ: Rohdaten direkt aus einer External Location lesen
-- GRANT READ FILES ON EXTERNAL LOCATION my_ext_location TO `data-engineers`;
```

### h) Rechte wieder entziehen (REVOKE)

Gleiche Syntax wie `GRANT`, nur mit `FROM` statt `TO`:

```sql
REVOKE CREATE TABLE ON SCHEMA main.default FROM `finance-team`;
REVOKE WRITE VOLUME ON VOLUME main.bronze.landing_files FROM `data-engineers`;
REVOKE ALL PRIVILEGES ON SCHEMA default FROM `alf@melmak.et`;
```

Ein `REVOKE` schlägt nicht fehl, selbst wenn die Berechtigung vorher nie erteilt wurde.

---

## 29. Häufige Stolpersteine bei der Privilegienvergabe

**Einfach erklärt:** Diese Checkliste fasst die häufigsten Fehlerquellen beim Vergeben von Unity-Catalog-Privilegien zusammen. Sie dient als schnelle Erinnerungsliste vor dem produktiven `GRANT`.

1. **`SELECT` allein reicht nicht.** Ohne `USE CATALOG` auf dem Catalog und `USE SCHEMA` auf dem Schema bleibt ein `SELECT`-Grant auf einer Tabelle wirkungslos.
2. **`WRITE FILES` ohne `READ FILES` schlägt fehl.** Schreibversuche auf einer External Location, bei der nur `WRITE FILES` (nicht zusätzlich `READ FILES`) vergeben ist, enden mit `PERMISSION_DENIED`.
3. **`MODIFY` setzt `SELECT` auf derselben Tabelle voraus** — nicht nur die Elternprivilegien `USE CATALOG`/`USE SCHEMA`.
4. **`ALL PRIVILEGES` ist kein Freifahrtschein.** Es deckt weder `MANAGE`, `READ METADATA`, `EXTERNAL USE SCHEMA` noch `EXTERNAL USE LOCATION` ab — diese vier müssen immer explizit vergeben werden.
5. **`MANAGE` ist nicht gleichbedeutend mit Ownership.** Ein Nutzer mit `MANAGE` kann Rechte verwalten und Eigentümerschaft übertragen, besitzt aber nicht automatisch `SELECT`/`MODIFY`/etc. — er müsste sich diese explizit selbst zuweisen.
6. **External-Location-Rechte wirken nicht auf Nachbar-/Elternpfade.** Ein Grant auf `.../raw-data` erlaubt keinen Zugriff auf `.../raw-data/../` oder `.../json-data` daneben.
7. **Views/Functions/Models: Eigentumsübertragung an beliebige Dritte nur durch Metastore-Admins.** Normale Owner bzw. `MANAGE`-Inhaber dürfen die Eigentümerschaft nur an sich selbst oder eine eigene Gruppe übertragen.
8. **`samples`-Catalog ist nicht änderbar.** `GRANT`/`REVOKE` auf dem mitgelieferten `samples`-Catalog werden nicht unterstützt.

**Verwandte, aber getrennte Governance-Mechanismen:** `GRANT`/`REVOKE` ist nicht der einzige Zugriffssteuerungs-Mechanismus in Databricks — Row Filters und Column Masks (zeilen-/spaltenweise Einschränkung des Datenzugriffs), Attribute-Based Access Control/ABAC (taggesteuertes Policy-System, das auch dynamisch Privilegien vergeben kann), Workspace-Catalog-Bindung (schränkt den Zugriff auf einen Catalog auf bestimmte Workspaces ein, unabhängig von individuellen `GRANT`-Privilegien) sowie Lakeflow-Jobs-Berechtigungen (separates System aus Job-ACLs plus Run-as-Identität, wirkt zusätzlich zu, nicht anstelle von, Unity-Catalog-Privilegien) wirken zusammen mit oder werden oft mit `GRANT`/`REVOKE` verwechselt.

Keine Code-Beispiele in dieser Datei.

---

## 30. ABAC — Überblick und Kernkomponenten

**Einfach erklärt:** ABAC (Attribute-Based Access Control) ist ein Zugriffskontrollmodell in Unity Catalog, bei dem nicht mehr jede Tabelle einzeln mit Grants versehen wird, sondern der Zugriff dynamisch anhand von **Attributen** (Tags) der Daten entschieden wird. Eine einzige Policy kann so automatisch für alle passenden — auch künftig neu erstellten — Objekte gelten. ABAC deckt drei Policy-Typen ab: Row-Filter-Policies (welche Zeilen sichtbar sind), Column-Mask-Policies (wie Spaltenwerte angezeigt werden) und GRANT-Policies (Beta, dynamische Privilegienvergabe). Diese gelten für Tabellen, Materialized Views und Streaming Tables.

Kernkomponenten:
- **Governed Tags & Policies:** Attribute werden über Governed Tags dargestellt und über Policies umgesetzt, die auf Hierarchieebenen (Catalog, Schema, Tabelle) angehängt werden und dynamisch ausgewertet werden.
- **Unterstützte Policy-Typen:** Row-Filter-Policies, Column-Mask-Policies, GRANT-Policies (Beta).

Keine Code-Beispiele in dieser Datei.

---

## 31. ABAC — Grundkonzepte (Governed Tags, Policy-Typen, Funktionen)

**Einfach erklärt:** ABAC-Entscheidungen basieren auf Policies, die gegen Attribute (Governed Tags) ausgewertet werden statt gegen Grants pro Einzelobjekt. Governed Tags sind Schlüssel-Wert-Paare auf Account-Ebene, die auf Catalogs, Schemas, Tabellen, Spalten, Modelle und Volumes angewendet werden und sich normalerweise vom übergeordneten Objekt vererben — außer auf Spaltenebene. Eingebaute Funktionen wie `has_tag()` und `has_tag_value()` prüfen diese Tags zur Laufzeit. Eine klare Aufgabentrennung (Separation of Duties) sorgt dafür, dass unterschiedliche Rollen für Tag-Taxonomie, Tag-Zuweisung, Policy-Erstellung, Objekterstellung und Datenzugriff zuständig sind.

Drei Policy-Typen:
1. **Row-Filter-Policies** — schränken sichtbare Zeilen anhand getaggter Spalten ein.
2. **Column-Mask-Policies** — steuern angezeigte Werte für getaggte Spalten.
3. **GRANT-Policies** (Beta) — vergeben Privilegien dynamisch, wenn Bedingungen zutreffen.

| Funktion | Zweck |
|---|---|
| `has_tag('tag_key')` | prüft, ob ein Tag vorhanden ist |
| `has_tag_value('tag_key', 'tag_value')` | prüft einen konkreten Tag-Wert |
| `get_tag_value('tag_key')` | extrahiert Tag-Werte zur Nutzung in UDFs |
| Identity-Attribut-Funktionen (Beta) | werten Nutzereigenschaften aus dem Identity Provider aus |

Separation of Duties (fünf Schritte, jeweils unterschiedliche Berechtigungen):
1. Tag-Taxonomie erstellen (Account-Admin)
2. Tags auf Assets anwenden (Data Stewards)
3. Policies verfassen (Governance-Admins)
4. Governte Objekte erstellen (Datenersteller)
5. Auf kontrollierte Daten zugreifen (Endnutzer)

Vorteile gegenüber Objekt-für-Objekt-Kontrolle: automatische Anwendung auf neu erstellte Objekte, geringerer laufender Pflegeaufwand, da Regeln zentral statt pro Tabelle verwaltet werden.

Keine Code-Beispiele in dieser Datei.

---

## 32. ABAC — Voraussetzungen, Kontingente und Einschränkungen

**Einfach erklärt:** Damit ABAC-Policies überhaupt greifen, braucht es bestimmte Compute-Konfigurationen (Serverless oder Runtime 16.4+) und ausschließlich Governed Tags (keine ungoverned Tags). Databricks legt zudem harte Obergrenzen für die Anzahl an Policies, Principals und Spaltenbedingungen fest, und es gibt wichtige funktionale Einschränkungen — etwa bei Views, Time Travel/Cloning, Materialized Views/Streaming Tables und AI-Search-Indizes.

Compute-Anforderungen — eine der folgenden Konfigurationen ist nötig:
- Serverless Compute
- Standard Compute mit Databricks Runtime 16.4+
- Dedicated Compute mit Databricks Runtime 16.4+ und aktivierter feingranularer Zugriffskontroll-Filterung

Standard- und Dedicated Compute mit Runtime-Versionen vor 16.4 können **nicht** auf ABAC-geschützte Tabellen zugreifen.

Governed Tags erforderlich: ABAC-Policies benötigen Governed Tags (keine ungoverned Tags), definiert auf Account-Ebene mit eigenen Zugriffskontrollen. Nach dem Zuweisen/Ändern eines Tags kann es einige Minuten dauern, bis die Änderung wirksam wird.

| Ressource | Limit |
|---|---|
| Policies pro Metastore | 10.000 |
| Policies pro Catalog oder Schema | 100 |
| Policies pro Tabelle | 50 |
| Principals pro Policy (`TO`- und `EXCEPT`-Klauseln zusammen) | 20 |
| Spaltenbedingungen pro `MATCH COLUMNS`-Klausel | 3 |

Wichtige Einschränkungen:
- **Views:** ABAC-Policies lassen sich nicht direkt auf Views anwenden. Fragt ein Nutzer jedoch eine View ab, die auf Tabellen mit ABAC-Policies verweist, werden diese Policies dennoch berücksichtigt.
- **Time Travel & Cloning:** ABAC-Policies lassen sich nicht gegen historische Snapshots auswerten — diese Operationen schlagen auf geschützten Tabellen fehl.
- **Materialized Views/Streaming Tables:** Policies werden mit der Identität des Pipeline-Eigentümers ausgewertet — das kann Daten dauerhaft maskieren.
- **Mehrere Policies:** Pro Tabelle und Nutzer kann sich zur Laufzeit nur **ein** eindeutiger Row Filter auflösen, um Konflikte zu vermeiden.
- **AI-Search-Indizes:** ABAC-Policies auf Quelltabellen gelten nicht für daraus erzeugte Indizes.

Keine Code-Beispiele in dieser Datei.

---

## 33. ABAC vs. tabellenbezogene Row Filter/Column Masks

**Einfach erklärt:** Es gibt zwei Wege, um Zeilen zu filtern oder Spalten zu maskieren: den klassischen, tabellenbezogenen Weg über `ALTER TABLE` (fest an eine bestimmte Tabelle gebunden) und den dynamischen ABAC-Weg über `CREATE POLICY` auf Catalog-, Schema- oder Tabellenebene, der Tabellen/Spalten automatisch anhand von Governed Tags matcht. ABAC lohnt sich vor allem bei vielen Tabellen und wachsendem Datenbestand, tabellenbezogene Kontrollen bei kleinen, stabilen Tabellenmengen mit sehr spezifischer Logik. Beide Ansätze können auf derselben Tabelle koexistieren, solange pro Spalte nur je ein eindeutiger Filter/eine Maske zur Laufzeit gilt.

| Aspekt | ABAC | Tabellenbezogen |
|---|---|---|
| **Scope/Skalierung** | Gilt für alle Tabellen im Policy-Scope; neue getaggte Tabellen automatisch erfasst | Einzeln konfiguriert; jede Tabelle braucht eigenes Setup |
| **Dynamisches Matching** | Über `has_tag()` / `has_tag_value()` | Kein dynamisches Matching — Filter/Masken sind fest an bestimmte Tabellen gebunden |
| **Governance-Kontrolle** | Catalog-/Schema-Eigentümer setzen Policies durch; Tabelleneigentümer können nicht übersteuern | Tabelleneigentümer verwalten direkt und können Einschränkungen ändern/entfernen |
| **Syntax** | `CREATE POLICY ... ON CATALOG/SCHEMA/TABLE` | `ALTER TABLE ... SET ROW FILTER` / `ALTER TABLE ... ALTER COLUMN ... SET MASK` |

**ABAC wählen, wenn:** organisationsweite Konsistenz über viele Tabellen benötigt wird, der Datenbestand wächst, und eine Aufgabentrennung zwischen Policy-Autoren und Data Stewards besteht.

**Tabellenbezogene Filter/Masken wählen, wenn:** einzelne Tabellen spezifische, nicht verallgemeinerbare Logik benötigen, Tabelleneigentümer die Einschränkungen direkt verwalten sollen, oder die Tabellenmenge klein und stabil ist.

Keine Code-Beispiele in dieser Datei.

---

## 34. ABAC-Policies erstellen und verwalten (CREATE POLICY, DROP POLICY, SHOW/DESCRIBE)

**Einfach erklärt:** Eine ABAC-Policy verknüpft eine SQL-UDF mit einem Scope (Catalog/Schema/Tabelle), Principals (`TO`/`EXCEPT`) und Bedingungen, welche Spalten sie betrifft (`MATCH COLUMNS`, meist über Tags). Bei einer Row-Filter-Policy liefert die UDF `TRUE`/`FALSE` pro Zeile; bei einer Column-Mask-Policy transformiert die UDF den Spaltenwert. Voraussetzung ist `MANAGE`-Privileg oder Eigentümerschaft auf dem schützbaren Objekt, Runtime 16.4+/Serverless, sowie eine UDF mit `EXECUTE`-Privileg. Policies lassen sich über Catalog-Explorer-UI, SQL oder Python SDK erstellen, verwalten und einsehen.

| Operation | Mittel |
|---|---|
| Erstellen | Catalog-Explorer-UI, SQL `CREATE POLICY`, Python SDK |
| Bearbeiten | Beschreibung, Principals, Bedingungen und Funktionszuordnung änderbar — Name und Scope **nicht** |
| Löschen | `DROP POLICY` |
| Anzeigen | `SHOW [EFFECTIVE] POLICIES`, `DESCRIBE POLICY` |
| Auditieren | `INFORMATION_SCHEMA.ABAC_POLICY_DEFINITIONS` |

**`CREATE POLICY`-Syntax — Row Filter:**

```sql
CREATE [OR REPLACE] POLICY policy_name
ON { CATALOG catalog_name | SCHEMA schema_name | TABLE table_name }
[COMMENT description]
ROW FILTER function_name
TO principal [, ...]
[EXCEPT principal [, ...]]
FOR TABLES
[WHEN condition]
[MATCH COLUMNS condition [[AS] alias] [, ...]]
[USING COLUMNS (function_arg [, ...])]
```

**`CREATE POLICY`-Syntax — Column Mask:**

```sql
CREATE [OR REPLACE] POLICY policy_name
ON { CATALOG catalog_name | SCHEMA schema_name | TABLE table_name }
[COMMENT description]
COLUMN MASK function_name
TO principal [, ...]
[EXCEPT principal [, ...]]
FOR TABLES
[WHEN condition]
[MATCH COLUMNS condition [[AS] alias] [, ...]]
ON COLUMN alias
[USING COLUMNS (function_arg [, ...])]
```

**Beispiel: Column-Mask-Policy** — maskiert SSN-Spalten für US-Analysten (außer Admins) auf die letzten 4 Zeichen:

```sql
CREATE FUNCTION ssn_to_last_nr (ssn STRING, nr INT) RETURNS STRING
RETURN right(ssn, nr);

CREATE POLICY mask_ssn
ON SCHEMA prod.customers
COLUMN MASK ssn_to_last_nr
TO us_analysts EXCEPT admins
FOR TABLES
MATCH COLUMNS has_tag_value('pii', 'ssn') AS ssn
ON COLUMN ssn
USING COLUMNS (4);
```

**Beispiel: Row-Filter-Policy** — blendet europäische Kunden in sensiblen Tabellen für US-Analysten aus:

```sql
CREATE FUNCTION non_eu_region (geo_region STRING) RETURNS BOOLEAN
RETURN geo_region <> 'eu';

CREATE POLICY hide_eu_customers
ON SCHEMA prod.customers
COMMENT 'Exclude rows with European customers from sensitive tables'
ROW FILTER non_eu_region
TO us_analysts
FOR TABLES
WHEN has_tag_value('sensitivity', 'high')
MATCH COLUMNS has_tag('geo_region') AS region
USING COLUMNS (region);
```

Scope und Bedingungen: Policies werden an Catalogs, Schemas oder Tabellen angehängt. Tabellenbedingungen unterstützen Tag-basiertes Matching oder eigene Boolean-Ausdrücke über `has_tag()` und `has_tag_value()`. Principals können Gruppen, Service Principals oder "alle Account-Nutzer" sein.

**Vertiefung — `CREATE POLICY` (Language-Manual-Referenzbeispiele):** Der Column-Mask-Scope ist hier ein `CATALOG` (statt `SCHEMA`), und `TO`/`EXCEPT` verwenden Klartext-Prinzipalnamen in einfachen Anführungszeichen (`'All Users'`, `'HR admins'`):

```sql
CREATE FUNCTION ssn_to_last_nr (ssn STRING, nr INT) RETURNS STRING
  RETURN right(ssn, nr);

CREATE POLICY ssn_mask
  ON CATALOG employees
  COLUMN MASK ssn_to_last_nr
  TO 'All Users' EXCEPT 'HR admins'
  FOR TABLES
  MATCH COLUMNS has_tag('ssn') AS ssn
  ON COLUMN ssn
  USING COLUMNS (4);
```

```sql
CREATE FUNCTION non_eu_region (geo_region STRING) RETURNS BOOLEAN
  RETURN geo_region <> 'eu';

CREATE POLICY hide_eu_customers
  ON SCHEMA prod.customers
  COMMENT 'Hide European customers from sensitive tables'
  ROW FILTER non_eu_region
  TO analysts
  FOR TABLES
  WHEN has_tag_value('sensitivity', 'high')
  MATCH COLUMNS has_tag('geo_region') AS region
  USING COLUMNS (region);
```

**`DROP POLICY`** — beim Löschen muss der Scope (`ON CATALOG`/`SCHEMA`/`TABLE`) exakt mitangegeben werden, unter dem die Policy erstellt wurde — Name und Scope zusammen identifizieren die Policy eindeutig:

```sql
DROP POLICY policy_name
ON { CATALOG catalog_name | SCHEMA schema_name | TABLE table_name }
```

```sql
DROP POLICY ssn_mask ON CATALOG employees;
DROP POLICY hide_eu_customers ON SCHEMA prod.customers;
```

**`DESCRIBE POLICY` und `SHOW [EFFECTIVE] POLICIES`** — `DESCRIBE POLICY` zeigt Details einer einzelnen Policy (Typ, Funktion, Prinzipale, Zeitstempel); `SHOW POLICIES` listet alle direkt an einem Objekt definierten Policies, `SHOW EFFECTIVE POLICIES` zusätzlich die von übergeordneten Containern geerbten:

```sql
{ DESC | DESCRIBE } POLICY policy_name ON { CATALOG catalog_name | SCHEMA schema_name | TABLE table_name }
```

```sql
DESCRIBE POLICY rf ON TABLE datagov.test.orders;
```

```sql
SHOW [ EFFECTIVE ] POLICIES ON { CATALOG catalog_name | SCHEMA schema_name | TABLE table_name }
```

```sql
SHOW POLICIES ON SCHEMA mycatalog.myschema;
SHOW EFFECTIVE POLICIES ON SCHEMA mycatalog.myschema;
```

---

## 35. ABAC GRANT-Policies (Beta) — dynamische Privilegienvergabe

**Einfach erklärt:** GRANT-Policies sind ein dritter ABAC-Policy-Typ (Beta), der Unity-Catalog-Privilegien dynamisch anhand passender Governed Tags vergibt — statt über feste Einzel-Grants. Sie werden nur an Catalogs oder Schemas angehängt und gelten aktuell für KI-bezogene Objekttypen (Modelle, Model Services, MCP Services, Agent Services). Die effektiven Privilegien eines Nutzers sind die Vereinigung aus direkten Grants und zutreffenden GRANT-Policies.

Scope und Geltungsbereich: nur an Catalogs oder Schemas angehängt, nicht an Einzelobjekte. Vergeben Privilegien für die Objekttypen `MODEL`, `MODEL_SERVICE`, `MODEL_PROVIDER_SERVICE`, `MCP_SERVICE`, `AGENT_SERVICE`. Unterstützte Privilegien je Objekttyp: `APPLY_TAG`, `EXECUTE`, `READ_METADATA`.

**`CREATE POLICY`-Syntax:**

```sql
CREATE [OR REPLACE] POLICY policy_name
ON { CATALOG catalog_name | SCHEMA schema_name }
[COMMENT description]
TO principal [, ...]
[EXCEPT principal [, ...]]
GRANT privilege [, ...] FOR MODELS
[WHEN condition]
```

**Beispiele:**

```sql
CREATE POLICY grant_production_model_access
ON SCHEMA production.ml_models
COMMENT 'Grant EXECUTE on production MLflow models'
TO `analysts`
GRANT EXECUTE FOR MODELS
WHEN has_tag_value('lifecycle', 'production');
```

```sql
CREATE POLICY grant_anthropic_foundation_models
ON SCHEMA system.ai
COMMENT 'Grant EXECUTE on Anthropic foundation models'
TO `data_scientists`
EXCEPT `contractors`
GRANT EXECUTE FOR MODELS
WHEN has_tag_value('ai.model_creator', 'anthropic');
```

Zugriffslogik: Ein Principal erhält Zugriff, wenn eine der Bedingungen gilt — eine GRANT-Policy listet ihn in `TO` (und nicht in `EXCEPT`) und die Tag-Bedingung trifft zu, **oder** ein direkter `GRANT` existiert auf Objekt, Schema oder Catalog.

**Verwaltung:**

```sql
SHOW [EFFECTIVE] POLICIES ON { CATALOG | SCHEMA } securable_name;
DESCRIBE POLICY policy_name ON { CATALOG | SCHEMA } securable_name;
DROP POLICY IF EXISTS policy_name ON SCHEMA schema_name;
```

System-Tags für Foundation-Modelle: Modelle in `system.ai` tragen vorab Tags wie `ai.model_creator` (z. B. `anthropic`, `openai`, `google`, `meta`) und `ai.model_family` (z. B. `claude-opus`, `gpt`, `gemini`, `qwen`).

Wichtige Einschränkungen: `CREATE MODEL` und `CREATE MODEL_VERSION` werden nicht unterstützt. `USE CATALOG`/`USE SCHEMA` bleiben als Voraussetzung direkte Grants. `ALL_PRIVILEGES`, `MANAGE`, `MODIFY` werden nicht unterstützt. SQL-Erstellung ist auf Modelle beschränkt — für andere Typen Catalog Explorer oder REST-API nutzen. `SHOW GRANTS` zeigt policy-vergebene Privilegien **nicht** an. Delta Sharing ist mit GRANT-Policies auf Modellen nicht kompatibel.

Best Practices: Gruppen statt Einzelnutzer in `TO`/`EXCEPT` verwenden. Policies auf dem engstmöglichen Scope anhängen, der die Ziele abdeckt. GRANT-Policies von direkten Grants für dasselbe Privileg trennen. Direkte Grants nur für die Voraussetzungen `USE CATALOG`/`USE SCHEMA` reservieren.

Voraussetzung: SQL-Operationen erfordern klassisches Compute mit Databricks Runtime 18 LTS oder höher.

---

## 36. Policy Evaluation — Auswertung und Laufzeitverhalten

**Einfach erklärt:** Bei jeder Query laufen zwei Stufen ab: Policy Evaluation in Unity Catalog (welche Policies gelten anhand von Nutzeridentität/Gruppen) und Policy Enforcement in der Databricks Runtime (wie sie tatsächlich durchgesetzt werden). ABAC arbeitet dabei "fail-closed" — kann eine Prüfung nicht abgeschlossen werden, wird der Zugriff standardmäßig verweigert statt gewährt. Fehlende Abhängigkeiten (gelöschtes Tag, gelöschte Funktion) führen zu klar definierten Fehlern statt zu stillem Datenleck.

Zweistufiger Auswertungsprozess: Die Zugriffskontrolle läuft in zwei Stufen ab — Policy Evaluation in Unity Catalog und Policy Enforcement in der Databricks Runtime — beide bestimmen gemeinsam, wie die Kontrollen anhand von Nutzeridentität und Gruppenmitgliedschaften auf eine konkrete Query angewendet werden.

Fail-Closed-Sicherheitsmodell: Kann eine Prüfung nicht abgeschlossen werden, verweigert das System den Zugriff standardmäßig, statt ihn zu gewähren. Das gilt für nicht unterstützte Compute-Versionen, inkompatible Operationen und fehlende Policy-Abhängigkeiten.

Anforderungen: ABAC-Policies benötigen Databricks Runtime 16.4 oder höher, oder Serverless Compute. Ältere Runtimes werden vom Zugriff auf geschützte Tabellen blockiert. Bestimmte Workflows — Time-Travel-Queries, Klon-Operationen, Pipeline-Refreshes, AI-Search-Indexierung — erfordern, dass die betroffenen Principals explizit in einer `EXCEPT`-Klausel gelistet sind, um die Policy-Durchsetzung zu umgehen.

| Szenario | Verhalten |
|---|---|
| Governed Tag gelöscht | Queries schlagen fehl mit `INVALID_PARAMETER_VALUE.UC_ABAC_UNKNOWN_TAG_POLICY` |
| Getaggte Spalte soll gelöscht werden | Blockiert, sofern das Tag nicht zuvor von autorisierten Nutzern entfernt wurde |
| Funktion gelöscht | Fehler `UC_DEPENDENCY_DOES_NOT_EXIST` |

Konfliktauflösung: Pro Tabelle und Nutzer darf zur Query-Zeit nur **ein** eindeutiger Row Filter gelten — analog für Column Masks. Mehrere widersprüchliche Policies lösen einen Fehler aus und blockieren den Zugriff. `SHOW EFFECTIVE POLICIES` und die `INFORMATION_SCHEMA`-Tabellen helfen, Konflikte zu diagnostizieren.

Type Casting: Databricks castet Eingabe und Ausgabe von Column-Mask-Funktionen automatisch, um Typkonsistenz sicherzustellen — inklusive Struct-zu-`VARIANT`-Konvertierung ab Runtime 18.1.

Keine Code-Beispiele in dieser Datei.

---

## 37. Neue Tabellen standardmäßig absichern (Secure by Default)

**Einfach erklärt:** Dieses Muster sorgt dafür, dass neue Tabellen sofort nach dem Anlegen gesperrt sind, bis Data Stewards sie geprüft haben — ganz ohne manuelle Konfiguration pro Tabelle. Ein Schema-Level-Tag `review_status` (`pending`/`reviewed`) vererbt sich automatisch an jede neue Tabelle im Schema. Solange der Status `pending` ist, maskiert eine Policy alle Spalten; nach automatischer Data-Classification und manueller Freigabe durch einen Steward (Status `reviewed`) werden nur noch tatsächlich klassifizierte, sensible Spalten maskiert.

Voraussetzungen: Databricks Runtime 16.4+ oder Serverless Compute. Account-/Workspace-Admin-Rechte, `MANAGE` auf Ziel-Catalog/-Schema.

Ablauf:
1. **Data Classification** auf dem Catalog aktivieren.
2. Governed Tag `review_status` erstellen.
3. Tag mit Wert `pending` auf das Schema anwenden.
4. **Pending-Policy:** eine Column-Mask-Policy, die `system.data_classification.mask_value` auf **jede** Spalte anwendet — unabhängig vom Tag — solange `review_status = pending` gilt.
5. Eine Beispieltabelle (z. B. Mitarbeiterverzeichnis) wird angelegt und erbt automatisch den `pending`-Status → alle Spalten erscheinen maskiert.
6. **Data-Classification-Scan** erkennt sensible Spalten automatisch und vergibt `class.*`-System-Tags (z. B. `class.us_ssn`, `class.email_address`).
7. **Reviewed-Policy:** eine zweite Policy maskiert nur noch `class.*`-getaggte Spalten, sofern `review_status = reviewed` gilt.
8. Nach Prüfung durch einen Data Steward wird das Tabellen-Tag auf `reviewed` gesetzt — das überschreibt das vom Schema geerbte Tag, und nicht-klassifizierte Spalten werden wieder sichtbar.
9. Neue Tabellen im selben Schema erben automatisch wieder den `pending`-Status, ganz ohne zusätzliche Konfiguration.

Eingebaute Maskierungsfunktion: `system.data_classification.mask_value` maskiert typgerecht: `0` für Integer, `DATE '1970-01-01'` für Datumswerte, SHA-256-Hashes für Strings.

Keine Code-Beispiele in dieser Datei.

---

## 38. Tutorial: ABAC über Catalog Explorer (UI) konfigurieren

**Einfach erklärt:** Praxisbeispiel per UI: Ein US-Analyseteam soll keinen Zugriff auf EU-Kundendaten und Sozialversicherungsnummern (SSN) erhalten, aber auf die übrigen Kundendaten derselben Tabelle zugreifen dürfen. Der Tutorial-Ablauf zeigt Schritt für Schritt, wie man über den Catalog Explorer ein Governed Tag anlegt, Spalten taggt, UDFs für Row-Filter und Column-Mask erstellt und daraus Policies baut — ganz ohne SQL-Editor.

Voraussetzungen: Databricks Runtime 16.4+ oder Serverless Compute. Account- oder Workspace-Admin-Rechte. `ASSIGN` auf Governed Tags und `APPLY TAG` auf der Zieltabelle. `MANAGE` auf Ziel-Catalog/-Schema. `EXECUTE` auf den UDFs.

Schritte:
1. **Governed Tag erstellen:** Catalog → Govern → Governed Tags. Tag `pii` mit erlaubten Werten `ssn` und `address`.
2. **Kundentabelle erstellen:** Catalog `abac`, Schema `customers`, Tabelle `profiles` mit Spalten `First_Name`, `Last_Name`, `Phone_Number`, `Address`, `SSN` — Beispieldaten für US- und EU-Kunden einfügen.
3. **PII-Spalten taggen:** `SSN` mit `pii:ssn`, `Address` mit `pii:address` über `ALTER TABLE`.
4. **UDF zur EU-Adresserkennung erstellen:**

```sql
CREATE OR REPLACE FUNCTION is_not_eu_address(address STRING)
RETURNS BOOLEAN
RETURN (
    SELECT CASE
        WHEN LOWER(address) LIKE '%eu%'
          OR LOWER(address) LIKE '%e.u.%'
          OR LOWER(address) LIKE '%europe%'
        THEN FALSE
        ELSE TRUE
    END);
```

5. **Row-Filter-Policy `hide_eu_customers` erstellen:** gilt für alle Account-Nutzer, blendet Zeilen aus, für die `is_not_eu_address()` `FALSE` liefert, zugeordnet zu Spalten mit Tag `pii:address`.
6. **Testen:** Die Query liefert nur Nicht-EU-Bewohner (10 von 15 Datensätzen).
7. **SSN-Maskierungs-UDF erstellen:**

```sql
CREATE FUNCTION mask_SSN(ssn STRING)
RETURN '***-**-****';
```

8. **Column-Mask-Policy `mask_ssn` erstellen:** gilt für alle Account-Nutzer, maskiert Spalten mit Tag `pii:ssn`.
9. **Kombiniert prüfen:** Die Query zeigt maskierte SSNs (`***-**-****`) ausschließlich für Nicht-EU-Bewohner — Row Filter und Column Mask greifen gemeinsam.

Ergebnis: Die Kombination aus Row-Level-Filterung nach Adresse und Column-Level-Maskierung von SSNs, beide tag-basiert angewendet, ist gut wartbar, da neue Spalten/Zeilen nur getaggt statt einzeln konfiguriert werden müssen.

---

## 39. Tutorial: ABAC vollständig mit SQL konfigurieren

**Einfach erklärt:** Dasselbe Szenario wie im UI-Tutorial (US-Analysten sollen EU-Kunden und SSNs nicht sehen), hier aber komplett über SQL-Befehle statt über den Catalog Explorer. Zusätzlich wird eine dritte, zustimmungsabhängige Maskierungsregel für E-Mail-Adressen gezeigt, die zwei Tags gleichzeitig über `MATCH COLUMNS` kombiniert.

Voraussetzungen: Databricks Runtime 16.4+ oder Serverless Compute. Account- oder Workspace-Admin-Rechte für Governed Tags. `MANAGE` auf Ziel-Catalog/-Schema, `EXECUTE` auf den UDFs.

**Schritt 1 — Governed Tags erstellen:** Tag `pii` mit Werten `ssn`, `address`, `email`. Tag `consent` nur als Schlüssel (ohne feste Werte).

**Schritt 2 — Kundentabelle erstellen:**

```sql
CREATE CATALOG IF NOT EXISTS abac_tutorial;
USE CATALOG abac_tutorial;
CREATE SCHEMA IF NOT EXISTS customers;
CREATE OR REPLACE TABLE profiles (
    first_name STRING,
    last_name STRING,
    email STRING,
    phone_number STRING,
    home_address STRING,
    ssn_number STRING,
    has_consent BOOLEAN);
```

**Schritt 3 — Governed Tags auf Spalten anwenden:** `ssn_number`, `home_address` und `email` werden mit `pii` getaggt, `has_consent` mit `consent` — jeweils über `ALTER TABLE`.

**Schritt 4 — UDF zur EU-Adresserkennung:**

```sql
CREATE OR REPLACE FUNCTION is_not_eu_address(address STRING)
RETURNS BOOLEAN
RETURN (SELECT CASE
    WHEN LOWER(address) LIKE '%eu%'
      OR LOWER(address) LIKE '%e.u.%'
      OR LOWER(address) LIKE '%europe%'
    THEN FALSE
    ELSE TRUE
END);
```

**Schritt 5 — Row-Filter-Policy:**

```sql
CREATE POLICY hide_eu_customers
ON SCHEMA abac_tutorial.customers
ROW FILTER is_not_eu_address
TO `account users`
FOR TABLES
MATCH COLUMNS has_tag_value('pii', 'address') AS addr_col
USING COLUMNS (addr_col);
```

**Schritt 6 — Testen:** Die Query liefert nur Nicht-EU-Kunden; EU-Kunden werden ausgeblendet.

**Schritt 7 — SSN-Maskierungs-UDF:**

```sql
CREATE OR REPLACE FUNCTION redact_ssn(ssn STRING)
RETURNS STRING
RETURN '***-**-****';
```

**Schritt 8 — Column-Mask-Policy:**

```sql
CREATE POLICY redact_ssn_policy
ON SCHEMA abac_tutorial.customers
COLUMN MASK redact_ssn
TO `account users`
FOR TABLES
MATCH COLUMNS has_tag_value('pii', 'ssn') AS ssn_col
ON COLUMN ssn_col;
```

**Erweiterung — Zustimmungsabhängige E-Mail-Maskierung:**

```sql
CREATE OR REPLACE FUNCTION mask_email_by_consent(email STRING, consent BOOLEAN)
RETURNS STRING
RETURN CASE
  WHEN consent = TRUE THEN email
  ELSE CONCAT(LEFT(email, 1), '***@', SUBSTRING_INDEX(email, '@', -1))
END;
```

```sql
CREATE POLICY mask_email_by_consent_policy
ON SCHEMA abac_tutorial.customers
COLUMN MASK mask_email_by_consent
TO `account users`
FOR TABLES
MATCH COLUMNS has_tag_value('pii', 'email') AS email_col,
  has_tag('consent') AS consent_col
ON COLUMN email_col
USING COLUMNS (consent_col);
```

Diese Policy zeigt die E-Mail nur an, wenn `has_consent = TRUE` ist — sonst wird sie teilweise maskiert.

Aufräumen: Am Ende des Tutorials werden Policies, Funktionen und Tabellen wieder per SQL entfernt (`DROP POLICY`, `DROP FUNCTION`, `DROP TABLE`).

---

## 40. Mapping-Tabellen für dynamische Zugriffskontrolle

**Einfach erklärt:** Statt für jede Region-Abteilungs-Kombination eine eigene Gruppe anzulegen (z. B. 16+ Gruppen), verwaltet dieses Muster Zugriffsrechte über eine einzige Lookup-Tabelle. Zugriffsänderungen erfolgen dann durch einfache `INSERT`/`UPDATE`-Zeilen in dieser Tabelle statt durch Änderungen an Policies oder Gruppen. Ein `expires_on`-Feld ermöglicht sogar automatischen Zugriffsentzug ohne manuellen Eingriff.

**Mapping-Tabelle:**

```sql
CREATE OR REPLACE TABLE abac_tutorial.mapping_demo.user_access (
  user_email STRING,
  region STRING,
  department STRING,
  pii_access STRING,
  expires_on DATE);

INSERT INTO abac_tutorial.mapping_demo.user_access VALUES
  (current_user(),      'us_east', 'engineering', 'masked', '2099-12-31'),
  ('bob@example.com',   'us_west', 'sales',       'full',   '2099-12-31'),
  ('carol@example.com', 'eu',      'engineering', 'none',   '2099-12-31'),
  ('david@example.com', 'apac',    'marketing',   'masked', '2099-12-31');
```

Das Feld `expires_on` ermöglicht automatischen Zugriffsentzug ohne manuellen Eingriff.

**Row-Filter-UDF:**

```sql
CREATE OR REPLACE FUNCTION abac_tutorial.mapping_demo.access_filter(
  region_val STRING,
  dept_val STRING)
RETURNS BOOLEAN
RETURN EXISTS (
  SELECT 1 FROM abac_tutorial.mapping_demo.user_access
  WHERE user_email = current_user()
    AND region = region_val
    AND department = dept_val
    AND expires_on >= current_date());
```

**Column-Mask-UDF (bedingte Maskierung)** — maskiert PII abhängig von der Freigabestufe des Nutzers **und** der Priorität der Zeile; als `confidential` markierte Bestellungen werden unabhängig von der Freigabestufe des Nutzers vollständig geschwärzt:

```sql
CREATE OR REPLACE FUNCTION abac_tutorial.mapping_demo.pii_mask(
  val STRING,
  pii_type STRING,
  order_pri STRING)
RETURNS STRING
RETURN CASE
  WHEN order_pri = 'confidential' THEN '***REDACTED***'
  WHEN EXISTS (
    SELECT 1 FROM abac_tutorial.mapping_demo.user_access
    WHERE user_email = current_user() AND pii_access = 'full'
  ) THEN val
  WHEN EXISTS (
    SELECT 1 FROM abac_tutorial.mapping_demo.user_access
    WHERE user_email = current_user() AND pii_access = 'masked'
  ) THEN
    CASE pii_type
      WHEN 'email' THEN CONCAT(LEFT(val, 1), '***@', SUBSTRING_INDEX(val, '@', -1))
      WHEN 'name'  THEN CONCAT(LEFT(val, 1), '***')
      ELSE CONCAT(LEFT(val, 1), '***')
    END
  ELSE '***REDACTED***'
END;
```

**Policies:**

```sql
CREATE POLICY user_access_filter
ON SCHEMA abac_tutorial.mapping_demo
ROW FILTER abac_tutorial.mapping_demo.access_filter
TO `account users`
FOR TABLES
MATCH COLUMNS has_tag('region') AS r, has_tag('department') AS d
USING COLUMNS (r, d);

CREATE POLICY pii_mask_name
ON SCHEMA abac_tutorial.mapping_demo
COLUMN MASK abac_tutorial.mapping_demo.pii_mask
TO `account users`
FOR TABLES
MATCH COLUMNS has_tag_value('pii', 'name') AS m,
  has_tag('priority') AS pri
ON COLUMN m
USING COLUMNS ('name', pri);

CREATE POLICY pii_mask_email
ON SCHEMA abac_tutorial.mapping_demo
COLUMN MASK abac_tutorial.mapping_demo.pii_mask
TO `account users`
FOR TABLES
MATCH COLUMNS has_tag_value('pii', 'email') AS m,
  has_tag('priority') AS pri
ON COLUMN m
USING COLUMNS ('email', pri);
```

Vorteile: Skalierbarkeit (neue Regionen/Abteilungen erfordern nur neue Tabellenzeilen, keine neuen Gruppen), Wartbarkeit (Zugriffsänderungen aktualisieren Mapping-Tabellen-Einträge, nicht Policies oder UDFs), Flexibilität (Nutzer können über mehrere Zeilen Zugriff auf mehrere Region-Abteilungs-Kombinationen erhalten).

---

## 41. Häufige Muster für Row Filter und Column Masks

**Einfach erklärt:** Diese Sammlung zeigt elf wiederkehrende Implementierungsmuster für Row-Filter- und Column-Mask-UDFs — von Typkompatibilität über VARIANT-basierte Mehrzweck-Maskierung bis zu Performance-freundlichen String-Operationen statt Regex und konsistentem Hashing für Pseudonymisierung.

1. **Cast-kompatible Maskierungsfunktionen:** Jeder `CASE`-Zweig muss einen Typ liefern, der zum Zieltyp passt oder dorthin castbar ist — z. B. eine `DOUBLE`-Spalte maskieren und in jedem Zweig `DOUBLE` zurückgeben.

2. **Numerischen Überlauf vermeiden:** Rechenoperationen innerhalb der Maskierungsfunktion (z. B. `score + 1000`) können bei schmalen Zieltypen wie `TINYINT` zu einem Cast-Überlauf führen, wenn das Ergebnis den Wertebereich überschreitet.

3. **`VARIANT`-basierte Maskierung für mehrere Typen:** Eine einzige Funktion für `INT`, `DOUBLE` und `DECIMAL` über `VARIANT`-Rückgabetyp:

```sql
CREATE FUNCTION mask_numeric(val VARIANT) RETURNS VARIANT DETERMINISTIC
RETURN 0::VARIANT;
```

4. **Struct-Spalten-Maskierung mit `VARIANT` (Runtime 18.1+):** Maskiert einzelne Struct-Felder selektiv, über `schema_of_variant()` zur Formerkennung und `to_variant_object()`/`named_struct()` zur Schwärzung.

5. **Tag-basierte Zugriffskontrolle:** Ein `classification:unverified`-Tag blockiert den Zugriff, bis Data Stewards die Klassifizierung aktualisieren — löst automatische Policy-Übergänge aus (siehe Abschnitt "Secure by Default").

6. **Teilweise Offenlegung ohne Regex:** String-Operationen statt Regex für bessere Performance:

```sql
CONCAT('***-**-', RIGHT(ssn, show_last))
```

7. **Konsistentes Hashing / deterministische Pseudonymisierung:** Erzeugt identische Hashes über Tabellen hinweg, mit Versionsparameter zur Unterstützung von Key-Rotation:

```sql
SHA2(CONCAT(val, CAST(version AS STRING)), 256)
```

8. **Maskierung anhand von Identitätsattributen:**

```sql
NOT has_identity_attribute_value('department', 'HR')
```

Schränkt den Zugriff für alle Nutzer außerhalb der HR-Abteilung ein.

9. **Row-Filterung mit reinen Spalten-Prädikaten:** Ermöglicht Predicate Pushdown durch einfache Boolean-Logik:

```sql
array_contains(split(allowed, ','), lower(region))
```

10. **Row-Filterung über mehrere Spalten:** Kombiniert mehrere Spaltenbedingungen über separate `MATCH COLUMNS`-Klauseln, die beide Spalten an eine gemeinsame UDF übergeben — für zusammenhängende Attribute.

11. **Zugriffsregeln über Lookup-Tabellen:** Referenziert externe Tabellen für dynamischen Zugriff:

```sql
EXISTS (SELECT 1 FROM access_rules WHERE principal = session_user())
```

---

## 42. Multi-Domain Column Masking mit Sensitivitätsstufen

**Einfach erklärt:** Dieses Muster kombiniert domänenbewusste Column-Masks (wer besitzt eine Spalte: HR, Finance, Marketing) mit regionsbasierter Row-Filterung, über zwei zusammenwirkende Governed Tags — `domain` und `sensitivity`. Da jede Spalte genau einen `domain`-Wert und einen `sensitivity`-Wert trägt, trifft pro Nutzer genau eine Policy auf jede Spalte zu. Der zentrale Trick ist die `EXCEPT`-Klausel: Jede Policy zielt auf "alle Account-Nutzer" außer die jeweils zuständige Domain-Gruppe, sodass Mitglieder mehrerer Domain-Gruppen automatisch unmaskierte Daten aller ihrer Domänen sehen.

Zwei Tags im Zusammenspiel:
- **`domain`** — welches Team eine Spalte besitzt (`hr`, `finance`, `marketing`).
- **`sensitivity`** — Maskierungsintensität (`internal`, `confidential`).

Ablauf:
1. **Governed Tags erstellen:** `region` (nur Schlüssel), `domain` (drei Werte), `sensitivity` (zwei Werte).
2. **Beispieldaten:** Tabelle `employee_records` mit Spalten aus HR, Finance und Marketing.
3. **Tags anwenden:** jede sensible Spalte erhält sowohl `domain`- als auch `sensitivity`-Tag — z. B. die SSN-Spalte: `domain='hr'`, `sensitivity='confidential'`.
4. **UDFs erstellen:** `region_filter()` (vergleicht die Region der Zeile), `partial_mask()` (liefert ersten Buchstaben plus `***`), `redact()` (liefert `***REDACTED***`).
5. **Policies erstellen:** sechs Column-Mask-Policies (eine je Domain-Sensitivity-Kombination) und zwei Row-Filter-Policies, die die UDFs über `AND`-Bedingungen in `MATCH COLUMNS` auf getaggte Spalten anwenden.

Durchsetzungsmuster über `EXCEPT`: Der zentrale Mechanismus ist, dass jede Policy auf "alle Account-Nutzer" **außer** die jeweils zuständige Domain-Gruppe zielt. Nutzer, die mehreren Domain-Gruppen angehören, sehen dadurch automatisch die unmaskierten Daten aller ihrer Domänen, während alle anderen die entsprechend der Sensitivitätsstufe maskierten Werte sehen.

Keine Code-Beispiele in dieser Datei (das Original beschreibt UDFs und Policies nur konzeptionell, ohne konkrete SQL-Syntax).

---

## 43. ABAC und OpenSharing

**Einfach erklärt:** ABAC-geschützte Tabellen und Views lassen sich auch über OpenSharing (Delta-Sharing-basiertes Teilen) an externe Empfänger weitergeben. Entscheidend ist, dass der Share-Eigentümer (nicht mehr der View-Eigentümer, seit einer Änderung im April 2026) über die `EXCEPT`-Klausel von den ABAC-Policies ausgenommen ist — sonst würden die eigenen Policies das Teilen selbst blockieren. Der Recipient sieht dann standardmäßig ungefilterte Daten und kann eigene Policies anwenden.

Voraussetzungen: Databricks Runtime 16.4+ oder Serverless Compute. Account-/Workspace-Admin-Rechte für Governed Tags. `MANAGE` auf Ziel-Catalog/-Schema, `EXECUTE` auf den UDFs. Konfiguriertes OpenSharing zwischen Provider und Recipient.

ABAC-geschützte Tabellen teilen: Share-Eigentümer können Tabellen mit ABAC-Schutz weitergeben, wenn sie (1) die nötigen OpenSharing-Berechtigungen besitzen, und (2) über die `EXCEPT`-Klausel von den ABAC-Policies ausgenommen sind. Der Recipient sieht dann standardmäßig ungefilterte Daten und kann eigene Policies anwenden.

ABAC-geschützte Views teilen: Share-Eigentümer können auch Views teilen, die auf ABAC-geschützte Basistabellen verweisen — vorausgesetzt, sie sind von den zugrunde liegenden Tabellen-Policies ausgenommen. **Wichtige Änderung seit dem 23. April 2026:** Zuvor musste der View-Eigentümer ausgenommen sein, jetzt muss stattdessen der Share-Eigentümer ausgenommen sein.

Recipient-seitige Views über geteilte Tabellen: Wird recipient-seitiger Schutz über Views benötigt, sollten nur Basistabellen geteilt werden (keine providerseitigen Views). Recipients erstellen lokale Views über den geteilten Tabellen in separaten Schemas, da OpenSharing-Schemas nur lesbar sind. ABAC-Policies auf den Basistabellen bleiben auch beim Zugriff über recipient-seitig erstellte Views wirksam.

Keine Code-Beispiele in dieser Datei.

---

## 44. Performance-Überlegungen für Row Filter und Column Masks

**Einfach erklärt:** ABAC-Policies führen UDFs zur Query-Zeit aus — pro Zeile bzw. pro Spaltenwert. Das ist mächtig, aber nicht kostenlos: Wer die UDF-Logik einfach hält, auf Principal-Targeting statt komplexer Bedingungen setzt, deterministische SQL-Funktionen verwendet und Python-UDFs vermeidet, minimiert den Performance-Einfluss deutlich. Eine `SecureView`-Barriere kann außerdem verhindern, dass komplexe Prädikate in die Speicherschicht durchgereicht werden (Predicate Pushdown), was volle Table Scans erzwingen kann.

Empfehlungen:
- **UDF-Logik einfach halten:** einfache `CASE`-Anweisungen und schlichte Boolean-Ausdrücke statt komplexer Funktionen — diese verschlechtern die Query-Performance direkt.
- **Principal-Targeting statt UDF-Logik:** komplexe Logik lieber über die `TO`/`EXCEPT`-Klauseln der Policy und Identitätsattribute in der `WHEN`-Klausel abbilden. Identitätsfunktionen wie `is_account_group_member()` werden nur einmal während der Analyse aufgelöst, nicht pro Zeile — das minimiert den Overhead.
- **Deterministische Ausdrücke verwenden:** fehlersichere SQL-Alternativen wie `try_divide` statt `/` und `try_cast` statt `CAST`. Nicht-deterministische Funktionen verhindern Optimizer-Caching und Constant Folding.
- **SQL statt Python:** Python-UDFs in ABAC-Policies wenn möglich vermeiden — der Optimizer kann sie nicht inlinen, sie laufen für jede Zeile erneut.
- **Größe von Lookup-Tabellen begrenzen:** externe Referenztabellen klein genug halten für Broadcast-Hash-Joins statt Shuffle-Joins — reduziert den Performance-Einfluss deutlich.

Herausforderungen bei der Query-Optimierung:
- **`SecureView`-Barriere:** Policies führen eine `SecureView`-Barriere ein, die bestimmte Prädikate am Pushdown in die Speicherschicht hindert. Komplexe Prädikate mit Funktionen wie `date_format()` lassen sich nicht pushdownen und erzwingen volle Table Scans. Einfache Gleichheitsvergleiche bleiben dagegen optimierbar.
- **Column-Mask-Wiederverwendung:** Dieselbe Maskierungsfunktion über mehrere Spalten hinweg wiederverwenden reduziert Overhead gegenüber separaten Funktionen pro Spalte.
- **Regex auf Textfeldern:** `regexp_replace` auf serialisierten Dokumenten (XML/JSON) vermeiden — stattdessen sensible Felder in typisierten Spalten separater Tabellen materialisieren.

Testanforderung: UDF-Performance vor dem Produktivgang mit mindestens 1 Million Zeilen und repräsentativen Workload-Queries validieren, um den tatsächlichen Overhead der Policy zu isolieren.

Keine Code-Beispiele in dieser Datei.

---

## 45. ABAC — Best Practices

**Einfach erklärt:** Acht zentrale Empfehlungen für den produktiven ABAC-Einsatz: eine konsistente Tag-Taxonomie etablieren, das Setzen von Tags als Sicherheitsgrenze streng kontrollieren, restriktive Fallback-Regeln für unklassifizierte Daten definieren, Policies möglichst hoch im Hierarchie-Scope ansiedeln, Policy Sprawl vermeiden (ABAC soll Regeln reduzieren, nicht vermehren), direkte Grants und GRANT-Policies gemeinsam auditieren, `TO`/`EXCEPT` statt komplexer UDF-Logik für Principal-Zuordnung nutzen, und die dynamische Auswertung über `SHOW EFFECTIVE POLICIES` nachvollziehbar dokumentieren.

1. **Attribute und Namensgebung standardisieren:** Eine konsistente Tag-Taxonomie teamübergreifend etablieren. Statt überlappender Tags: ein einziges kontrolliertes Set — z. B. ein `sensitivity`-Tag mit Werten wie `public`, `internal`, `confidential`, `restricted`.

2. **Kontrollieren, wer Tags setzen darf:** Tagging ist eine Sicherheitsgrenze in ABAC. Das Erstellen und Ändern von Tags über die Governed-Tags-Konfiguration auf autorisierte Data Stewards oder Governance-Admins beschränken. Tag-Änderungen regelmäßig über System-Tabellen auditieren.

3. **Fallback-Regeln für unklassifizierte Daten festlegen:** Neuen Objekten standardmäßig restriktive Tags zuweisen (z. B. `classification:unverified`), bis sie geprüft wurden. Policies erstellen, die den Zugriff auf ungetaggte oder ungeprüfte Objekte einschränken.

4. **Policies auf dem höchstmöglichen Scope definieren:** Policies möglichst auf Catalog- oder Schema-Ebene statt auf Tabellenebene anhängen — dadurch erhalten neue Tabellen automatisch die passenden bestehenden Policies anhand ihrer Tags.

5. **Policy Sprawl vermeiden:** ABAC ist darauf ausgelegt, die Anzahl an Zugriffsregeln zu reduzieren, nicht zu erhöhen. Mit breiten Policies beginnen statt separater Regeln für Randfälle. Überlappende Policies regelmäßig überprüfen und konsolidieren.

6. **Direkte Grants und ABAC-GRANT-Policies gemeinsam auditieren:** Die effektiven Privilegien eines Nutzers ergeben sich aus direkten Grants und ABAC-GRANT-Policies — beide Quellen gemeinsam prüfen, um unbeabsichtigte Berechtigungen zu vermeiden.

7. **`TO`/`EXCEPT` für Principal-Zuordnung bevorzugen:** Die Klauseln `TO` und `EXCEPT` einer Policy nutzen, um zutreffende Nutzer/Gruppen festzulegen — die UDF-Logik selbst einfach halten.

8. **Dynamische Policy-Auswertung einplanen:** `SHOW EFFECTIVE POLICIES` nutzen, um zu verstehen, was auf eine konkrete Tabelle zutrifft, und das eigene Governance-Modell klar dokumentieren.

Keine Code-Beispiele in dieser Datei.

---

## 46. Row Filter und Column Masks — Überblick

**Einfach erklärt:** Row Filter entscheiden, welche *Zeilen* einer Tabelle ein Nutzer sehen darf (Row-Level-Security), Column Masks entscheiden, welche *Werte* in einer Spalte sichtbar sind (z. B. Klartext oder geschwärzt). Beides sind SQL-UDFs, die bei jeder Query pro Zeile bzw. Spalte ausgewertet werden. Databricks empfiehlt inzwischen primär ABAC-Policies (catalog-/schema-weit über Governed Tags) statt manuell gepflegter Filter auf Einzeltabellen; alternativ lassen sich dynamische Views mit `is_account_group_member()` nutzen.

Row Filter schränken ein, welche **Zeilen** ein Nutzer sehen kann. Eine SQL-UDF wird zur Query-Zeit für jede Zeile ausgewertet — Zeilen, für die die Funktion `FALSE` zurückgibt, werden aus dem Ergebnis ausgeschlossen.

Column Mask steuert, welche **Werte** in bestimmten Spalten sichtbar sind. Die Maske ist eine SQL-UDF, die den Spaltenwert als Eingabe nimmt und entweder den Originalwert oder eine maskierte Version zurückgibt. Pro Spalte lässt sich genau eine Maske anwenden.

**Empfohlener Ansatz:** Databricks empfiehlt primär ABAC-Policies: Sie werden auf Catalog- oder Schema-Ebene angehängt und gelten automatisch für Tabellen und Spalten anhand von Governed Tags. Alternativ dynamische Views, die Basistabellen mit Filterlogik über `is_account_group_member()` (kontoweite Gruppenzugehörigkeit) in `WHERE`- oder `CASE`-Ausdrücken umschließen. Von der veralteten Funktion `is_member()` (nur Workspace-Gruppen) wird für Unity-Catalog-Daten abgeraten.

**Performance-Hinweise:** einfache UDFs statt komplexer Queries; Anzahl unterschiedlicher Column Masks auf großen Tabellen begrenzen; Anzahl der UDF-Argumente reduzieren; Row Filter mit vielen `AND`-Bedingungen vermeiden; deterministische, fehlerfreie Ausdrücke verwenden; SQL-UDFs gegenüber Python-UDFs bevorzugen.

**Wichtige Einschränkungen:** Views können keine Row-Level-Security erhalten; Iceberg-REST-Catalogs werden nicht unterstützt; Delta-Lake-APIs werden nicht unterstützt; OpenSharing-Provider können Tabellen mit Table-Level-Schutz nicht teilen; Time Travel funktioniert nicht in Kombination mit diesen Mechanismen.

Keine Code-Beispiele in dieser Datei.

---

## 47. Row Filter und Column Masks manuell anwenden

**Einfach erklärt:** Diese Datei zeigt, wie man Row Filter und Column Masks selbst per SQL erstellt und an Tabellen anhängt — als SQL-UDF definieren, dann per `ALTER TABLE` zuweisen. Python-Logik muss dafür in eine SQL-Wrapper-Funktion verpackt werden. Zusätzlich gibt es Wege, Masken/Filter direkt bei `CREATE TABLE` inline zu setzen, und eine `INFORMATION_SCHEMA`-View, um bestehende Column Masks aufzufinden.

**Voraussetzungen:** Ein für Unity Catalog aktivierter Workspace; SQL-UDFs, in Unity Catalog registriert (Python-/Scala-Logik muss in eine SQL-UDF verpackt werden); Privilegien `EXECUTE` auf der Funktion, `USE SCHEMA`, `USE CATALOG`; für bestehende Tabellen Eigentümerstatus oder sowohl `MANAGE` als auch `SELECT`; Compute: SQL-Warehouses, Standard Access Mode (Runtime 12.2+) oder Dedicated Access Mode (Runtime 15.4+).

Jede Tabelle unterstützt maximal **einen** Row Filter.

```sql
CREATE FUNCTION <function_name> (<parameter_name> <parameter_type>, ...)
RETURN {Filterausdruck, dessen Ergebnis ein Boolean sein muss};

ALTER TABLE <table_name> SET ROW FILTER <function_name> ON (<column_name>, ...);
```

**Beispiel — Zugriff nach Region:**

```sql
CREATE FUNCTION us_filter(region STRING)
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('admin'), true, region='US');

ALTER TABLE sales SET ROW FILTER us_filter ON (region);
```

Admins sehen alle Zeilen uneingeschränkt; alle anderen Nutzer sehen nur Datensätze mit `region = 'US'`.

**Entfernen:**

```sql
ALTER TABLE <table_name> DROP ROW FILTER;
```

**Column Mask:**

```sql
CREATE FUNCTION <function_name> (<parameter_name> <parameter_type>, ...)
RETURN {Ausdruck mit demselben Typ wie der erste Parameter};

ALTER TABLE <table_name> ALTER COLUMN <col_name> SET MASK <mask_func_name> USING COLUMNS <additional_columns>;
```

**Beispiel — SSN maskieren:**

```sql
CREATE FUNCTION ssn_mask(ssn STRING)
RETURN CASE WHEN is_account_group_member('HumanResourceDept') THEN ssn ELSE '***-**-****' END;

ALTER TABLE users ALTER COLUMN ssn SET MASK ssn_mask;
```

**Python-UDF als Wrapper** — Python-Logik muss über eine SQL-Wrapper-Funktion angewendet werden, nicht direkt:

```sql
CREATE FUNCTION email_mask_python(email STRING)
RETURNS STRING
LANGUAGE PYTHON
AS $$
import re
return re.sub(r'^[^@]+', lambda m: '*' * len(m.group()), email)
$$;

CREATE FUNCTION email_mask_sql(email STRING)
RETURN email_mask_python(email);
```

Angewendet wird der SQL-Wrapper (`email_mask_sql`), nicht die Python-UDF direkt.

**Bedingte Maskierung mit `USING COLUMNS`:**

```sql
CREATE FUNCTION mask_address_by_country(address STRING, country STRING, group_suffix STRING DEFAULT '_address_viewers')
RETURN IF(
  is_account_group_member(country || group_suffix),
  address,
  'REDACTED');

ALTER TABLE customers
ALTER COLUMN address
SET MASK mask_address_by_country USING COLUMNS (country, '_address_viewers');
```

**Mapping-Tabellen (Zugriffslisten)** — Tabellen, die festlegen, welche Zeilen für bestimmte Nutzer/Gruppen zugänglich sind:

```sql
CREATE TABLE valid_users(username string);
INSERT INTO valid_users VALUES ('fred@databricks.com'), ('barney@databricks.com');

CREATE FUNCTION row_filter()
RETURN EXISTS(
  SELECT 1 FROM valid_users v
  WHERE v.username = SESSION_USER());
```

**Wichtiger Hinweis:** Alle Filter laufen mit den Rechten des Definierers ("definer's rights") — außer Funktionen, die den Nutzerkontext prüfen (z. B. `SESSION_USER`, `IS_ACCOUNT_GROUP_MEMBER`); diese laufen mit den Rechten des Aufrufers ("invoker's rights").

**Weiteres Beispiel:** Row Filter, der den Kundenstamm nach Treuestufe einschränkt, und eine Column Mask, die eine numerische ID durch einen Platzhalter ersetzt:

```sql
-- Row Filter: Mitglieder der Gruppe 'supervisors' sehen alle Zeilen,
-- alle anderen nur Kunden mit loyalty_segment < 3
CREATE OR REPLACE FUNCTION loyalty_row_filter(loyalty_segment STRING)
RETURNS BOOLEAN
RETURN IF(is_account_group_member('supervisors'), true, loyalty_segment < 3);

ALTER TABLE customers_silver_with_row_filter
SET ROW FILTER loyalty_row_filter ON (loyalty_segment);
```

```sql
-- Column Mask: customer_id wird für alle außer 'supervisors' durch
-- einen festen Platzhalterwert ersetzt, statt Zeichen zu schwärzen
CREATE OR REPLACE FUNCTION redact_customer_id(customer_id BIGINT)
RETURN CASE WHEN is_account_group_member('supervisors')
  THEN customer_id
  ELSE 9999999
END;

ALTER TABLE customers_silver_with_row_filter
  ALTER COLUMN customer_id
  SET MASK redact_customer_id;
```

**Wichtige Warnungen:** Wird eine Funktion gelöscht, bevor der zugehörige Filter entfernt wurde, wird die Tabelle unzugänglich. Typkonflikte zwischen UDF-Parametern und Spalten führen zu impliziter Konvertierung; bei deaktiviertem ANSI-Modus werden inkompatible Werte stillschweigend zu `NULL`. Row Filter und Column Masks bleiben bei `REPLACE TABLE` erhalten, sofern die Schema-Spalten übereinstimmen.

**Vertiefung — Column Mask direkt bei `CREATE TABLE` inline anwenden**, anwendbar bei `CREATE TABLE`, `ALTER TABLE ... ADD COLUMN`, `ALTER TABLE ... ALTER COLUMN`. Benötigte Privilegien bei neuen Tabellen: `EXECUTE` auf der Funktion, `USE SCHEMA`, `USE CATALOG`, `CREATE TABLE` auf dem Schema; bei bestehenden Tabellen: Eigentümerstatus oder sowohl `MANAGE` als auch `SELECT` (bei Schemaänderungen zusätzlich `MODIFY`).

**Syntax:**

```sql
MASK func_name [ USING COLUMNS ( other_column_name | constant_literal [, ...] ) ]
```

| Parameter | Beschreibung |
|---|---|
| `func_name` | Eine skalare SQL-UDF mit mindestens einem Parameter. Der erste Parameter entspricht 1:1 der maskierten Spalte und muss vom Spaltentyp castbar sein; der Rückgabetyp muss auf den Datentyp der maskierten Spalte castbar sein. |
| `other_column_name` | Weitere Spalten derselben Tabelle, die zusätzlich an die Funktion übergeben werden. Jede muss auf den entsprechenden Funktionsparameter castbar sein. |
| `constant_literal` | Ein konstanter Parameter (`STRING`, numerisch, `BOOLEAN`, `INTERVAL` oder `NULL`), der zum Funktionsparameter passt. |

```sql
CREATE FUNCTION mask_ssn(ssn STRING)
RETURN CASE WHEN is_member('HumanResourceDept') THEN ssn ELSE '***-**-****' END;

CREATE TABLE persons(name STRING, ssn STRING MASK mask_ssn);

INSERT INTO persons VALUES('James', '123-45-6789');
SELECT * FROM persons;
```

Mit `USING COLUMNS`, um eine zweite Spalte (hier die Region) als zusätzliches Funktionsargument einzubeziehen:

```sql
CREATE FUNCTION mask_pii_regional(value STRING, region STRING)
RETURN IF(is_account_group_member(region || '_HumanResourceDept'), value, 'REDACTED');

CREATE TABLE persons(name STRING, address STRING MASK mask_pii_regional
  USING COLUMNS (region), region STRING);

INSERT INTO persons VALUES('James', '160 Spear St, San Francisco', 'US');
SELECT * FROM persons;
```

**Wichtige Hinweise:** Die Maske wird angewendet, sobald die Zeile aus der Datenquelle abgerufen wird — Ausdrücke, Prädikate und Sortierungen werden erst danach ausgeführt. Bei Typkonflikten und deaktiviertem `ANSI_MODE` werden nicht castbare Werte stillschweigend zu `NULL` konvertiert. Column Masks können nicht auf Spalten angewendet werden, die von Generated Columns referenziert werden.

**Vertiefung — Row Filter direkt bei `CREATE TABLE` inline anwenden (`WITH ROW FILTER`)**, anwendbar bei `CREATE TABLE`/`ALTER TABLE`, `CREATE MATERIALIZED VIEW`/`ALTER MATERIALIZED VIEW`, `CREATE STREAMING TABLE`/`ALTER STREAMING TABLE`. Benötigte Privilegien: zum Zuweisen `EXECUTE` auf der Funktion, `USE SCHEMA`, `USE CATALOG`; bei neuen Tabellen zusätzlich `CREATE TABLE`; bei bestehenden Tabellen Eigentümerstatus oder sowohl `MANAGE` als auch `SELECT` (bei Schemaänderungen zusätzlich `MODIFY`).

**Syntax:**

```sql
ROW FILTER func_name ON ( [ column_name | constant_literal [, ...] ] ) [...]
```

| Parameter | Beschreibung |
|---|---|
| `func_name` | Eine skalare SQL-UDF mit Rückgabetyp `BOOLEAN`. Zeilen, für die die Funktion `FALSE` oder `NULL` zurückgibt, werden herausgefiltert. |
| `column_name` | Tabellenspalten, die an `func_name` übergeben werden. Jede Spalte muss auf den entsprechenden Funktionsparameter castbar sein; die Anzahl der Spalten muss zur Funktionssignatur passen. Weicht der Datentyp einer Spalte vom erwarteten Parametertyp ab, erfolgt eine implizite Konvertierung — bei deaktiviertem `ANSI_MODE` kann das zu unerwarteten Ergebnissen führen. |
| `constant_literal` | Konstante Parameter, die auf die Funktionsparameter passen. Unterstützte Typen: `STRING`, numerische Typen (`INTEGER`, `FLOAT`, `DOUBLE`, `DECIMAL`), `BOOLEAN`, `INTERVAL`, `NULL`. |

**Beispiel:**

```sql
CREATE FUNCTION filter_emps(dept STRING) RETURN is_account_group_member(dept);

CREATE TABLE employees(emp_name STRING, dept STRING) WITH ROW FILTER filter_emps ON (dept);

INSERT INTO employees VALUES ('Jones', 'Engineering'), ('Smith', 'Sales');
SELECT * FROM employees;
```

Hier filtert `filter_emps` danach, ob der abfragende Nutzer Mitglied der Gruppe ist, deren Name dem Wert der `dept`-Spalte entspricht — jede Zeile ist also nur für Mitglieder der jeweils passenden Abteilungsgruppe sichtbar.

**Vertiefung — Column Masks auffinden: `INFORMATION_SCHEMA.COLUMN_MASKS`** — enthält Metadaten zu allen Column Masks in Unity Catalog (Runtime 12.2 LTS+, Public Preview). Angezeigt werden nur Spalten, auf die der abfragende Nutzer Zugriff hat.

| Spalte | Typ | Nullable | Bedeutung |
|---|---|---|---|
| `CATALOG_NAME` | STRING | Nein | Catalog, der die Tabelle enthält |
| `SCHEMA_NAME` | STRING | Nein | Schema, das die Tabelle enthält |
| `TABLE_NAME` | STRING | Nein | Name der Tabelle mit der maskierten Spalte |
| `COLUMN_NAME` | STRING | Nein | die maskierte Spalte |
| `MASK_CATALOG` | STRING | Nein | Catalog, der die Mask-Funktion enthält |
| `MASK_SCHEMA` | STRING | Nein | Schema, das die Mask-Funktion enthält |
| `MASK_NAME` | STRING | Nein | Name der Funktion, die die Maske implementiert |
| `MASK_COL_USAGE` | STRING | Ja | kommagetrennte Liste zusätzlicher Spalten, die an die Mask-Funktion übergeben werden (`NULL`, falls keine — entspricht `USING COLUMNS`) |

Constraints: Primary Key über `(CATALOG_NAME, SCHEMA_NAME, TABLE_NAME, COLUMN_NAME)`; Foreign Keys auf die `COLUMNS`-View (dieselben vier Spalten) sowie auf die `ROUTINES`-View (`MASK_CATALOG`, `MASK_SCHEMA`, `MASK_NAME`).

**Beispiel — alle im aktuellen Catalog verwendeten Mask-Funktionen zählen:**

```sql
SELECT mask_catalog, mask_schema, mask_name, count(1)
FROM information_schema.column_masks
GROUP BY ALL
ORDER BY ALL;
```

---

## 48. Service Policies für KI-Assets — Überblick

**Einfach erklärt:** Service Policies regeln, *wie* KI-Services (Modelle, MCP-Services) mit Nutzern und externen Systemen interagieren dürfen — anders als klassische Zugriffskontrolle, die nur regelt, *ob* überhaupt zugegriffen werden darf. Eine Policy trifft pro Interaktion eine von drei Entscheidungen: erlauben, blockieren oder menschliche Freigabe verlangen. Vier eingebaute Policies erkennen z. B. unsichere Inhalte, Jailbreaks, Halluzinationen oder sensible Daten.

**Drei Entscheidungsausgänge:**

| Ergebnis | Bedeutung |
|---|---|
| `ALLOW` | Interaktion läuft normal weiter |
| `DENY` | Liefert HTTP 200 mit Begründung zurück, verhindert erneutes Auslösen in Folgeschritten |
| `ASK` | Interaktion wird bis zur menschlichen Freigabe zurückgehalten (für sensible Operationen) |

**Auswertungszeitpunkte:** `ON CALL` (vor dem Service-Aufruf, prüft die Anfrage) und `ON RESULT` (nach der Service-Antwort, prüft die Antwort). Für eingebaute LLM-as-a-Judge-Policies sendet Databricks den Policy-Prompt und die extrahierte Nachricht an ein Bewertungsmodell, das ein geflagged/nicht-geflagged-Urteil zurückliefert.

**Ausführungsmodell:** Policies werden an Services mit einem **Rang** (Priorität) angehängt. Die Auswertung erfolgt bei `ON CALL` in aufsteigender, bei `ON RESULT` in absteigender Rangfolge. Innerhalb eines Rangs laufen blockierende LLM-as-a-Judge-Policies parallel (Latenzoptimierung); übrige Policies laufen nur sequenziell weiter, wenn die parallelen Policies zugelassen haben. Die Ausführung stoppt sofort beim ersten `DENY`.

**Eingebaute Policies** im Namespace `system.ai`: `system.ai.block_unsafe_content`, `system.ai.block_jailbreak`, `system.ai.block_hallucination`, `system.ai.detect_sensitive_data` (deterministisch, regelbasiert, kann auch redigieren).

**Unterstützte Services:** MCP Services (managed, external, custom), Model Services (gehostete und externe Endpoints), Model Provider Services.

**Fail-Closed-Verhalten:** Fehler während der Auswertung führen zu `DENY` — fehlkonfigurierte Policies blockieren Interaktionen, statt sie durchzulassen.

Keine Code-Beispiele in dieser Datei.

---

## 49. Sensible Daten erkennen (`detect_sensitive_data`)

**Einfach erklärt:** `detect_sensitive_data` ist eine eingebaute, regelbasierte Service Policy, die PII (z. B. Sozialversicherungsnummern, E-Mail-Adressen, Kreditkartennummern) in Anfragen und Antworten von KI-Services erkennt. Sie arbeitet deterministisch mit Regex, Prüfsummen und Kontext-Schlüsselwörtern — nicht mit einem LLM — und ist dadurch sehr schnell und präzise, erkennt aber keine Freitext-Entitäten wie Namen oder Orte.

**Aktionen bei Erkennung:**

| Aktion | Verhalten |
|---|---|
| **Block** | Verweigert die Interaktion; der Aufrufer erhält eine HTTP-200-Antwort mit den ausgelösten Kategorien. |
| **Redact** | Ersetzt erkannte Werte durch Platzhalter-Tokens (z. B. `[US_SSN]`), bevor der Inhalt weitergeleitet wird. |

Policies lassen sich auf Eingabe, Ausgabe oder beides anwenden.

**Unterstützte Kategorien (15 insgesamt):**

| Region | Kategorien |
|---|---|
| **Global** (7) | E-Mail-Adresse, IP-Adresse, MAC-Adresse, VIN, Kreditkarte, IBAN, Telefonnummer |
| **USA** (4) | SSN, ITIN, Reisepass, Bankkontonummer |
| **UK** (2) | NHS-Nummer, National Insurance Number |
| **Indien** (2) | Permanent Account Number, Aadhaar-Nummer |

**Erkennungsmethoden:** Kombination aus Regex-Musterabgleich, Prüfsummen (Luhn, ISO 7064, Mod-11, Verhoeff) und Kontext-Schlüsselwörtern zur Validierung der Treffer.

**Genauigkeit laut Benchmark:** Block-Präzision 0,99 über alle 15 Kategorien; Redaction-Recall 0,96; zusätzliche Latenz deutlich unter 50 ms pro Request.

**Einschränkung:** Die Policy erkennt keine Freitext-Entitäten wie Namen, Orte oder Organisationen — dafür wäre Sprachverständnis statt Musterabgleich nötig.

Keine Code-Beispiele in dieser Datei.

---

## 50. Service Policy erstellen und anhängen

**Einfach erklärt:** Eine Service Policy wird als SQL-UDF in Unity Catalog geschrieben, die ein `event`-VARIANT-Objekt entgegennimmt und `ALLOW`/`DENY`/`ASK` zurückgibt. Danach wird sie über die Unity AI Gateway UI an einen Service (Model, Provider oder MCP) angehängt, mit Zielgruppe, Guardrail-Typ, Phase (`ON CALL`/`ON RESULT`) und Rang konfiguriert.

**Voraussetzungen:** Beta muss vom Account-Admin über die Account-Console-Seite **Previews** aktiviert werden; `CREATE FUNCTION`-Privileg auf dem Zielschema; `MANAGE` auf dem Service-Objekt und `EXECUTE` auf der Policy-Funktion.

**Schritt 1: Policy-Funktion schreiben.** Policy-Funktionen sind SQL-UDFs in Unity Catalog mit folgender Struktur:

```sql
CREATE OR REPLACE FUNCTION <catalog>.<schema>.<function_name>(
  event VARIANT
)
RETURNS VARIANT
LANGUAGE SQL
RETURN <expression>;
```

Die Funktion unterscheidet über `event:type::string` ('request' oder 'response'), auf welche Phase sie zielt.

**Beispiel — GitHub-Push-Operationen blockieren:**

```sql
CREATE OR REPLACE FUNCTION main.governance.block_github_push(
  event VARIANT
)
RETURNS VARIANT
LANGUAGE SQL
RETURN
  CASE
    WHEN event:type::string = 'request'
      AND event:context.tool.name::string = 'push_files'
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', 'GitHub push operations are not permitted by policy.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Beispiel — Freigabe vor destruktiven Operationen verlangen:**

```sql
CREATE OR REPLACE FUNCTION main.governance.ask_before_repo_delete(
  event VARIANT
)
RETURNS VARIANT
LANGUAGE SQL
RETURN
  CASE
    WHEN event:context.tool.name::string = 'delete_repository'
    THEN to_variant_object(named_struct('result', 'ASK', 'reason', 'Deleting a repository requires human approval.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Schritt 2: Über Unity AI Gateway UI anhängen:**

1. Im Workspace-Menü zu **AI Gateway** navigieren.
2. Service auswählen (Tabs **Models**, **Providers** oder **MCPs**).
3. Tab **Policies** öffnen → **New policy** klicken.
4. Konfigurieren: **Name** (Bezeichner der Policy), **Applied to** (Ziel-Principals, Standard: alle Nutzer), **Guardrail type** (eingebaut oder **Custom** — eigene SQL-Funktion wählen), **Phase** (Input Guardrails `ON CALL` oder Output Guardrails `ON RESULT`), **Rank** (niedrigere Ränge werten bei Requests zuerst, bei Responses zuletzt aus).
5. **Create policy** klicken.

**Prüfung:** Anhängen bestätigen über Tab **Policies** des Service; Ergebnisse beobachten — `DENY` liefert strukturierte Fehler, `ASK` pausiert zur Freigabe; Usage- und Inference-Tabellen zur Auswertung nutzen. Die Verbreitung von Policy-Änderungen kann während der Beta bis zu ein bis zwei Minuten dauern.

**Aktuelle Einschränkungen:** Policies liefern nur Entscheidungen zurück — keine Inhaltstransformation; Custom-Funktionen unterstützen nur SQL; Anhängen erfolgt UI-seitig pro einzelnem Service; gilt für alle Account-Nutzer — Catalog-/Schema-Ebene und ABAC-Bedingungen sind (noch) nicht verfügbar.

---

## 51. Service-Policy-Funktionsreferenz

**Einfach erklärt:** Diese Referenz beschreibt die technischen Details der Policy-Funktionen: welche Felder das `event`-Objekt enthält (z. B. Tool-Name, Nachricht, Actor-Kontext), welche Rückgabestruktur erwartet wird, und welche SQL-Funktionen/Operatoren innerhalb einer Policy-Funktion überhaupt erlaubt sind, da Databricks den Funktionskörper zur Laufzeit nach CEL transpiliert.

Service Policies sind SQL-UDFs in Unity Catalog mit fester Signatur:

```sql
CREATE OR REPLACE FUNCTION <catalog>.<schema>.<function_name>(
  event VARIANT
)
RETURNS VARIANT
LANGUAGE SQL
RETURN <expression>;
```

Ausgewertet wird in zwei Phasen: `'request'` (`ON CALL`, vor dem Service-Aufruf) und `'response'` (`ON RESULT`, nach der Antwort).

**Felder des `event`-Parameters:**

| Feld | Gilt für | Zweck |
|---|---|---|
| `event:type` | Alle | `'request'` oder `'response'` |
| `event:target` | Alle | Vollständiger Unity-Catalog-Name des angehängten Service |
| `event:context.actor.run_as` | Alle | Run-As-Identität zur Autorisierung |
| `event:context.actor.context.is_on_behalf_of` | Alle | `true`, wenn Agent/App im Namen des Nutzers handelt |
| `event:context.actor.context.client_id` | Alle | OAuth-Client-ID der handelnden Identität |
| `event:context.actor.context.actor_resource` | Alle | Ressource der handelnden Identität (z. B. Agent) |
| `event:context.actor.context.is_actor_authenticated` | Alle | `true` bei Confidential-Client-Authentifizierung |
| `event:context.tool.name`, `event:context.tool.arguments` | MCP Services | Name und Argumente des aufgerufenen Tools |
| `event:context.message` | Model/Provider Services | Extrahierte letzte Nutzer-/Assistant-Nachricht |
| `event:data` | Model/Provider Services | Vollständiges Request- oder Response-Payload |
| `event:request_data` | Model/Provider Services | Ursprüngliches Request (verfügbar bei `ON RESULT`) |

**Rückgabewert:** Funktionen liefern ein `VARIANT` mit Pflichtfeld `result` und optionalem `reason`:

```sql
to_variant_object(named_struct('result', 'DENY', 'reason', 'GitHub push operations are not permitted by policy.'))
```

Mögliche `result`-Werte: `ALLOW`, `DENY`, `ASK`.

Alternative Umschlagform:

```sql
to_variant_object(named_struct('decision', named_struct('result', 'DENY', 'reason', '...')))
```

**Unterstützte SQL-Funktionen und Operatoren:**

| Kategorie | Funktionen/Operatoren |
|---|---|
| Operatoren | Vergleich, logisch, arithmetisch; `\|\|`, `IN`, `LIKE`, `IS [NOT] NULL` |
| Kontrollfluss | `CASE`, `IF` |
| Casts | `INT`, `BIGINT`, `DOUBLE`, `FLOAT`, `STRING`, `BOOLEAN` (`CAST` oder `::`) |
| String-Funktionen | `CONCAT`, `LENGTH`, `CHAR_LENGTH`, `UPPER`, `LOWER`, `SUBSTRING`, `TRIM`, `LTRIM`, `RTRIM`, `REPLACE`, `STARTSWITH`, `ENDSWITH`, `CONTAINS` |
| Sonstige | `COALESCE`, `NULLIF`, `IFNULL`, `NVL`, `ABS`, `MOD`, `ISNULL`, `ISNOTNULL`, `NAMED_STRUCT`, `TO_VARIANT_OBJECT` |

**Nicht unterstützt:** `ai_query`, Subqueries, `BETWEEN`, Aggregatfunktionen, Lambdas/`EXISTS`, variadische Funktionen.

**Wichtige Hinweise:** Variant-Pfadzugriffe vor dem Vergleich auf skalare Typen casten: `event:type::string = 'request'`. Fehlende Felder lösen Fehler aus (Fail-Closed zu `DENY`). Databricks transpiliert Policy-Bodies zur Laufzeit nach CEL. Nicht unterstützte Konstrukte führen zur Ablehnung beim Anhängen der Policy.

---

## 52. Service-Policy-Beispiele

**Einfach erklärt:** Diese Datei sammelt praktische Beispiel-Policies für typische Anwendungsfälle — von Keyword-Blocklisten über Prompt-Längenlimits bis zu Tool-Allowlists — und unterscheidet zwischen deterministischen SQL-Policies (exakte, regelbasierte Entscheidung) und LLM-as-a-Judge-Policies (natürlichsprachlicher Prompt, den ein Bewertungsmodell klassifiziert).

### Deterministische SQL-Policies

**Anfragen mit bestimmten Schlüsselwörtern blockieren** (z. B. interne Codenamen):

```sql
CREATE OR REPLACE FUNCTION main.governance.block_codenames(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'request'
      AND (CONTAINS(LOWER(event:context.message::string), 'projectfalcon')
        OR CONTAINS(LOWER(event:context.message::string), 'bluewidget')
        OR CONTAINS(LOWER(event:context.message::string), 'codename-atlas'))
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', 'Your request references a restricted internal or competitor codename.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Anfragen zu eingeschränkten Themen blockieren:**

```sql
CREATE OR REPLACE FUNCTION main.governance.deny_restricted_topics(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'request'
      AND (CONTAINS(LOWER(event:context.message::string), 'lawsuit')
        OR CONTAINS(LOWER(event:context.message::string), 'legal advice')
        OR CONTAINS(LOWER(event:context.message::string), 'investment advice'))
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', 'This assistant does not handle legal or investment topics.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Prompt-Länge begrenzen:**

```sql
CREATE OR REPLACE FUNCTION main.governance.deny_oversized_prompt(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'request'
      AND LENGTH(event:context.message::string) > 8000
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', 'Your prompt exceeds the 8000-character limit for this service.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Freigabe verlangen, wenn ein Agent im Namen des Nutzers handelt:**

```sql
CREATE OR REPLACE FUNCTION main.governance.ask_when_agent_writes(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'request'
      AND event:context.actor.context.is_on_behalf_of::boolean = true
      AND event:context.tool.name::string IN ('create_issue', 'push_files', 'merge_pull_request')
    THEN to_variant_object(named_struct('result', 'ASK', 'reason', 'An agent is attempting a write action on your behalf. Please confirm.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Antworten mit internen URLs blockieren:**

```sql
CREATE OR REPLACE FUNCTION main.governance.block_internal_links_in_response(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'response'
      AND (CONTAINS(LOWER(event:context.message::string), 'wiki.internal.example.com')
        OR CONTAINS(LOWER(event:context.message::string), 'admin.example.com'))
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', 'The response was blocked because it referenced an internal-only URL.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Tool-Aufrufe anhand von Argumenten blockieren:**

```sql
CREATE OR REPLACE FUNCTION main.governance.block_protected_repo(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'request'
      AND event:context.tool.arguments.repo::string = 'prod-infra'
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', 'Actions on the prod-infra repository are not permitted through the agent.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Nur genehmigte Tools erlauben (Allowlist):**

```sql
CREATE OR REPLACE FUNCTION main.governance.tool_allowlist(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'request'
      AND event:context.tool.name::string NOT IN ('search_issues', 'get_file_contents', 'list_commits')
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', CONCAT('Tool is not on the approved allowlist for this service: ', event:context.tool.name::string)))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

### LLM-as-a-Judge-Policies

Diese Policies nutzen natürlichsprachliche Prompts, die von einem LLM ausgewertet werden:

- **Assistenten beim Thema halten:** *"Flag the message if it asks for something outside [Produkte, Bestellungen, Abrechnung, Account-Support], such as general coding help, writing essays, unrelated trivia, or using the assistant as a general-purpose chatbot."*
- **Professionellen Ton erzwingen:** *"Flag the response if it is rude, sarcastic, dismissive, condescending, uses profanity, or would embarrass the company if a customer saw it."*
- **Regulierte Beratung blockieren:** *"Flag the response if it provides individualized investment, tax, or legal advice, or a specific recommendation to a person."*

---

## 53. Governed Tags — Überblick

**Einfach erklärt:** Governed Tags sind Metadaten-Labels auf Account-Ebene mit eingebauten Regeln: Administratoren legen fest, welche Tag-Schlüssel "governed" sind, welche Werte pro Tag erlaubt sind, und wer sie zuweisen bzw. verwalten darf. So bleiben Tags konsistent und lassen sich für ABAC, Kostentracking, Auffindbarkeit oder Zertifizierungs-Workflows nutzen — statt dass jeder Nutzer beliebige Freitext-Tags vergibt.

**Was Administratoren steuern können:** bestimmte Tag-Schlüssel als "governed" festlegen; erlaubte Werte pro Tag definieren; festlegen, welche Nutzer/Gruppen Tags zuweisen und Definitionen verwalten dürfen. Das System erzwingt: Nur Nutzer mit passenden Berechtigungen können einem Tag Werte zuweisen — und das auch nur aus einer vordefinierten Menge erlaubter Werte. Neben selbst erstellten Governed Tags pflegt Databricks auch vordefinierte System-Tags.

**Anwendungsfälle:** Datenklassifizierung und Kennzeichnung von Sensibilität; Attribute-Based Access Control (ABAC); Kostenstellen-Tracking und Chargeback; Auffinden und Organisieren von Assets; Datenzertifizierung und Deprecation-Workflows.

**Technische Eckdaten:**

| Grenzwert | Wert |
|---|---|
| Governed Tags pro Account | max. 1.000 |
| Erlaubte Werte pro Tag | max. 500 |
| Länge von Schlüssel/Wert | max. 256 Zeichen (UTF-8) |
| Groß-/Kleinschreibung | wird unterschieden |
| Verbotene Zeichen | `* . / < > % & ? \ =` |

**Automatisierung:** Neben manueller Vergabe (ein Objekt nach dem anderen) unterstützt die Plattform automatisierte Ansätze: Data Classification, benutzerdefinierte Klassifizierer und regelbasierte Tag-Zuweisung.

**Sicherheitshinweis:** Da Tag-Daten als Klartext gespeichert werden: keine Tag-Namen, -Werte oder -Beschreibungen verwenden, die die Sicherheit von Ressourcen kompromittieren könnten.

Keine Code-Beispiele in dieser Datei.

---

## 54. Governed Tags erstellen und verwalten

**Einfach erklärt:** Diese Datei zeigt, wie Governed Tags per Catalog Explorer oder per SQL (`CREATE/ALTER/DROP GOVERNED TAG`) angelegt, bearbeitet und gelöscht werden, sowie wie man Tags über `SET TAG`/`UNSET TAG` konkreten Objekten (Tabellen, Spalten, Schemas, ...) zuweist. Wichtig: Wird ein gelöschtes Governed Tag noch in einer ABAC-Policy referenziert, schlagen alle betroffenen Queries fehl.

**Anforderungen an Schlüssel und Werte:** maximal 256 Zeichen; UTF-8-kodiert, Unicode-fähig; Groß-/Kleinschreibung wird unterschieden (`"Department"` ≠ `"department"`); verboten sind `* . / < > % & ? \ =` sowie ASCII-Steuerzeichen (0–31); dürfen nicht mit Leerzeichen beginnen oder enden.

**Governed Tags erstellen** — benötigtes Privileg: `CREATE` auf Account-Ebene (Account- und Workspace-Admins besitzen es standardmäßig). Über Catalog Explorer: Catalog → Govern → Governed Tags → Create governed tag → Tag-Schlüssel/Beschreibung eingeben → optional erlaubte Werte festlegen → Create.

**Über SQL:**

```sql
CREATE GOVERNED TAG isPii;
CREATE GOVERNED TAG sensitivity_level VALUES ('low', 'medium', 'high');
CREATE GOVERNED TAG pii DESCRIPTION 'Indicates what kind of personal identifiable information the asset contains' VALUES ('ssn', 'ccn', 'dob');
```

**Wichtig:** Wird ein Governed Tag mit einem bereits existierenden **ungoverned** Tag-Schlüssel erstellt, werden automatisch alle bestehenden Zuweisungen mit diesem Schlüssel governt.

**Governed Tags bearbeiten** — benötigtes Privileg: `MANAGE` auf dem Tag.

```sql
ALTER GOVERNED TAG pii SET DESCRIPTION 'Updated description';
ALTER GOVERNED TAG sensitivity_level SET VALUES ('low', 'medium', 'high');
ALTER GOVERNED TAG isPii SET VALUES ();
```

**Governed Tags löschen** — benötigtes Privileg: `MANAGE`. **Warnung:** Wird ein Governed Tag gelöscht, das in einer ABAC-Policy referenziert wird, schlagen **alle** Queries im Geltungsbereich dieser Policy fehl. Das Löschen wandelt das Tag in ein **ungoverned** Tag um — bestehende Zuweisungen bleiben erhalten, verlieren aber die Governance-Einschränkungen.

```sql
DROP GOVERNED TAG isPii;
```

**Vertiefung — `CREATE GOVERNED TAG` / `ALTER GOVERNED TAG` / `DROP GOVERNED TAG` — vollständige Syntax:**

```sql
CREATE GOVERNED TAG tag_key [ DESCRIPTION description ] [ VALUES ( value_name [, ...] ) ]
```

```sql
-- Nur ein Schlüssel, ohne erlaubte Werte (Freitext-Tag)
CREATE GOVERNED TAG isPii;

-- Leere Werteliste explizit angeben
CREATE GOVERNED TAG sensitivity_level VALUES ();
```

```sql
ALTER GOVERNED TAG tag_key { SET DESCRIPTION description | SET VALUES ( value_name [, ...] ) }
```

```sql
-- Alle erlaubten Werte entfernen -> Tag wird wieder werte-frei
ALTER GOVERNED TAG isPii SET VALUES ();
```

```sql
DROP GOVERNED TAG tag_key
```

```sql
DROP GOVERNED TAG isPii;
```

**Vertiefung — `DESCRIBE GOVERNED TAG` und `SHOW GOVERNED TAGS`:**

```sql
{ DESC | DESCRIBE } GOVERNED TAG tag_key [ AS JSON ]
```

```sql
DESCRIBE GOVERNED TAG isPii;
```

```sql
SHOW GOVERNED TAGS [ [ LIKE ] regex_pattern ]
```

```sql
SHOW GOVERNED TAGS;
SHOW GOVERNED TAGS LIKE 'pii*';
```

**Vertiefung — `SET TAG` / `UNSET TAG` — Tag-Zuweisung auf Objekten (inkl. Spalten):** `SET TAG`/`UNSET TAG` weisen einen (governed oder ungoverned) Tag-Schlüssel einem konkreten Objekt zu — Catalog, Schema, Tabelle, View, Spalte, Funktion, Volume oder External Metadata:

```sql
SET TAG ON
  { CATALOG catalog_name |
    COLUMN relation_name.column_name |
    EXTERNAL METADATA external_metadata_name |
    { FUNCTION | PROCEDURE } function_name |
    { SCHEMA | DATABASE } schema_name |
    TABLE relation_name |
    VIEW relation_name |
    VOLUME volume_name }
  tag_key [ = tag_value ]
```

```sql
SET TAG ON CATALOG catalog `cost_center` = `hr`;
UNSET TAG ON CATALOG catalog cost_center;

SET TAG ON TABLE catalog.schema.table cost_center = hr;
UNSET TAG ON TABLE catalog.schema.table cost_center;

-- Spalten-Tag ohne Wert (Boolean-artige Kennzeichnung)
SET TAG ON COLUMN table.ssn pii;
UNSET TAG ON COLUMN table.ssn pii;
```

Zugewiesene Spalten-Tags lassen sich über die `information_schema` abfragen — nützlich, um z. B. alle mit `pii` getaggten Spalten in einem Schema zu finden (Grundlage für `has_tag()`/`has_tag_value()` in ABAC-Policies):

```sql
SELECT catalog_name, schema_name, table_name, tag_name, tag_value
FROM information_schema.column_tags
WHERE tag_name = 'pii' AND schema_name = 'default';
```

---

## 55. Berechtigungen für Governed Tags verwalten

**Einfach erklärt:** Wer Governed Tags erstellen, bearbeiten, zuweisen oder löschen darf, wird über drei Berechtigungstypen gesteuert (`CREATE`, `MANAGE`, `ASSIGN`), die entweder account-weit für alle Tags oder für einzelne Tags vergeben werden können. Berechtigungsänderungen können bis zu 30 Sekunden oder länger brauchen, bis sie wirksam werden.

**Berechtigungstypen:**

| Berechtigung | Zweck | Scope |
|---|---|---|
| `CREATE` | Neue Governed Tags erstellen | nur Account |
| `MANAGE` | Governed Tags bearbeiten, löschen, Berechtigungen zuweisen | Account oder einzelnes Tag |
| `ASSIGN` | Governed Tags auf Unity-Catalog-Objekte anwenden | Account oder einzelnes Tag |

**Wichtige Details:** Account-Admins besitzen standardmäßig alle drei Privilegien. Workspace-Admins besitzen standardmäßig `CREATE` auf Account-Ebene. Nutzer mit `CREATE` erhalten automatisch `MANAGE` auf die von ihnen erstellten Tags. System-Tags können auch mit `MANAGE`-Privileg nicht aktualisiert oder gelöscht werden. Die Verbreitung von Berechtigungsänderungen kann bis zu 30 Sekunden oder länger dauern.

**Berechtigungen zuweisen — auf Account-Ebene** (erfordert `MANAGE` auf Account-Ebene): zu Catalog → Govern → Governed Tags navigieren, Tab **Account Permissions** auswählen, Berechtigungen an Principals vergeben (Nutzer, Service Principals oder Gruppen). Auf einzelnen Tags: analoger Ablauf über den **Permissions**-Tab des jeweiligen Governed Tag.

Keine Code-Beispiele in dieser Datei.

---

## 56. Automatische Tag-Zuweisung (Beta)

**Einfach erklärt:** Statt Tags manuell Objekt für Objekt zu setzen, können Admins Automatisierungen definieren, die Governed Tags anhand von Geschäftsregeln (Bedingungen wie Tag-Wert, Spalten-Tag, Query-Anzahl, Alter, Eigentümer, Namensmuster) automatisch auf Tabellen oder Volumes anwenden oder entfernen — entweder per natürlichsprachlichem Genie-Prompt oder manuell per Formular.

**Anwendungsfälle:** Daten zertifizieren, die Reifekriterien erfüllen; veraltete, ungepflegte Daten als "deprecated" markieren; Sensibilitätsklassifizierungen von Spalten auf Tabellen-Tags hochrollen; Assets kennzeichnen, denen erforderliche Tags fehlen; veraltete Tags bereinigen.

**Erstellungswege:** über natürlichsprachliche Prompts mit Genie, oder manuell über das Formular in Catalog Explorer.

**Voraussetzungen:** `USE CATALOG`, `USE SCHEMA` und `APPLY TAG` auf dem Ziel-Catalog; `MANAGE` auf dem Catalog; `ASSIGN` auf jedem beteiligten Governed Tag.

**Bedingungen (Auswahl):**

| Bedingung | Gilt für | Beispiel |
|---|---|---|
| Tag/Tag-Wert | bestehende Governed Tags | `cost_center` gleich `finance` |
| Spalten-Tag | Tags auf Spalten (nur Tabellen) | eine Spalte trägt `class.email_address` |
| Query-Anzahl | Lese-/Schreibaktivität (nur Tabellen) | Lesezugriffe größer als 100 |
| Zuletzt abgefragt | Tage seit letzter Query (nur Tabellen) | vor mehr als 90 Tagen |
| Erstellt/Aktualisiert | Alter des Assets | aktualisiert in den letzten 30 Tagen |
| Eigentümer | Asset-Eigentümerschaft | Eigentümer ist einer der angegebenen Principals |
| Beschreibung | Dokumentationsstatus | Beschreibung vorhanden/nicht vorhanden |
| Name | Namensmuster | enthält `_staging` |

**Betriebsfunktionen:** Benachrichtigungen (E-Mail-Alerts an Asset-Eigentümer oder festgelegte Empfänger aktivierbar, wenn eine Automatisierung Assets ändert); Ausführungshistorie (alle Testläufe/Dry Runs und echten Ausführungen werden protokolliert — mit Status, Startzeit, Anzahl betroffener Assets und Dauer); Status (Automatisierungen sind entweder "Pending review" oder "Enabled").

**Aktuelle Einschränkungen (Beta):** Nur ein einzelner Catalog pro Automatisierung; zielt entweder auf Tabellen oder Volumes, nicht auf beide gleichzeitig; verarbeitet maximal 500 zutreffende Assets pro Lauf; weist maximal 5 Governed Tags pro Automatisierung zu/entfernt sie; wiederkehrende Läufe sind typischerweise innerhalb von 24 Stunden abgeschlossen; Scope und Aktion lassen sich nach dem Erstellen nicht mehr ändern.

Keine Code-Beispiele in dieser Datei.

---

## 57. KI-generierte Dokumentation (AI-Generated Comments)

**Einfach erklärt:** DatabricksIQ kann automatisch Beschreibungen (Comments) für Unity-Catalog-Objekte wie Tabellen, Spalten oder Schemas vorschlagen — basierend auf Schema und Spaltennamen, nicht auf den eigentlichen Dateninhalten. Das erleichtert das Auffinden von Daten und reduziert manuellen Dokumentationsaufwand, ersetzt aber keine PII-Klassifizierung und muss vor dem Übernehmen geprüft werden.

**Funktionsweise:** Ein von Databricks entwickeltes, custom-gebautes Large Language Model generiert Metadaten-Beschreibungen auf Basis von Tabellenschema und Spaltennamen — die Kommentare sind auf einen geschäftlichen/unternehmerischen Kontext zugeschnitten und wurden anhand von Beispielschemata aus mehreren offenen Datensätzen verschiedener Branchen trainiert bzw. abgestimmt.

**Unterstützte Objekttypen:** Catalogs, Schemas; Tabellen, Views, Materialized Views; Tabellenspalten; Functions, Models, Volumes.

**Benötigte Berechtigungen:** für die meisten Objekte (Catalogs, Schemas, Tabellen, Functions, Models, Volumes) Owner-Status oder `MODIFY`-Privileg; für Views und Materialized Views ausschließlich Owner-Status (kein `MODIFY`-Äquivalent).

**Nutzung im Catalog Explorer — für Tabellen (bzw. andere Objekte):** Objekt im Catalog Explorer öffnen, im „Overview"-Tab bzw. „About this object"-Panel auf **AI generate** klicken; DatabricksIQ schlägt eine „AI Suggested Description" vor; Vorschlag übernehmen, bearbeiten oder verwerfen — auch nachträgliches Anpassen ist jederzeit möglich.

**Für Spalten:** im „Overview"-Tab unterhalb des angezeigten Schemas den Button **AI generate** anklicken; DatabricksIQ generiert Beschreibungen für alle Spalten gleichzeitig; Vorschläge einzeln übernehmen, verwerfen oder anpassen. Die Sprache der generierten Kommentare lässt sich über das Overflow-Menü konfigurieren.

**Einschränkungen und Hinweise:** Sorgfaltspflicht — KI-Modelle sind nicht immer akkurat, generierte Kommentare müssen vor dem Speichern überprüft werden. Nicht für PII-Klassifizierung geeignet — die Funktion ersetzt keine Datenklassifizierung sensibler Daten. Auswirkung auf Pipelines — das Speichern von Kommentaren löst intern `ALTER`-Befehle auf dem betroffenen Objekt aus, was laufende Pipelines beeinträchtigen kann.

Keine Code-Beispiele in dieser Datei.

---

## 58. Discoverability und Tag-Suche

**Einfach erklärt:** Getaggte Objekte lassen sich in Databricks über die Suchleiste mit dem Präfix `tag:<Schlüssel>` bzw. `tag:<Schlüssel>:<Wert>` finden, oder programmatisch über `INFORMATION_SCHEMA`-Tag-Views abfragen (z. B. für Automatisierung, Auditing oder Dashboards). Beide Wege respektieren automatisch die vorhandenen Zugriffsrechte des Nutzers.

**Suchleiste: `tag:`-Syntax:**

| Syntax | Bedeutung |
|---|---|
| `tag:<tag_key>` | sucht nach Objekten, die einen Tag mit diesem Schlüssel tragen — unabhängig vom Wert |
| `tag:<tag_key>:<tag_value>` | sucht nach Objekten mit exakter Schlüssel-**und**-Wert-Übereinstimmung |

Weitere allgemeine Filterpräfixe lassen sich kombinieren, z. B. `type:table owner:me`. Tag-Suche funktioniert für Tabellen, Views, Modelle, Volumes, Funktionen, Dashboards, Genie-Agents und Notebooks. Je mehr Filter kombiniert werden, desto feiner das Ergebnis. Die exakte Übereinstimmung gilt sowohl für den Tag-Schlüssel als auch für den Tag-Wert.

**Praktisches Beispiel:** Um die für die eigene Umgebung gültige Suchanfrage zu ermitteln, lässt sich der Katalogname per SQL abfragen und direkt in die Suchleiste einfügen:

```sql
SELECT concat('catalog:', DA.catalog_name, ' ', 'domain:customer') AS use_in_search_bar
```

Das Ergebnis dieser Query wird kopiert und oben in die Suchleiste eingefügt, um die passenden Objekte zu finden. Wichtig: Der Tag-Teil benötigt zusätzlich das Präfix `tag:` vor dem Schlüssel. Korrekt wäre also `tag:domain:customer`.

**Programmatische Tag-Suche über `INFORMATION_SCHEMA`:** Je nach Objekttyp existiert eine eigene View: `INFORMATION_SCHEMA.CATALOG_TAGS`, `INFORMATION_SCHEMA.SCHEMA_TAGS`, `INFORMATION_SCHEMA.TABLE_TAGS`, `INFORMATION_SCHEMA.COLUMN_TAGS`, `INFORMATION_SCHEMA.VOLUME_TAGS`.

```sql
SELECT *
FROM INFORMATION_SCHEMA.TABLE_TAGS
WHERE TABLE_NAME = 'customers_silver'
```

Wie bei allen `INFORMATION_SCHEMA`-Views gilt automatische Privilegien-Filterung: Es werden nur Tags von Objekten angezeigt, auf die der ausführende Nutzer bereits Zugriff hat.

---

## 59. System Tables — Überblick

**Einfach erklärt:** System Tables sind von Databricks gehostete, read-only Tabellen im `system`-Catalog, die operative Account-Daten sammeln — für Kostenmonitoring, Sicherheits-Audits, Compute-Analysen und Workload-Observability über den gesamten Account hinweg. Daneben liefert `INFORMATION_SCHEMA` reine Metadaten (welche Tabellen/Spalten/Privilegien existieren) mit automatischer Privilegien-Filterung.

**Voraussetzungen:** Der Workspace muss für Unity Catalog aktiviert sein; der Metastore benötigt Unity Catalog Privilege Model Version 1.0; Zugriff ist nur über Unity-Catalog-aktivierte Workspaces möglich — die Tabellen erfassen aber Daten aller Workspaces der jeweiligen Region.

**Berechtigungen:** Account- und Metastore-Admins haben standardmäßig Zugriff. Andere Nutzer benötigen `USE CATALOG` auf dem `system`-Catalog, `USE SCHEMA` auf dem jeweiligen Schema, `SELECT` auf der jeweiligen System-Tabelle.

**Verfügbare Schemas (Auswahl):**

| Schema | Inhalt |
|---|---|
| `system.billing` | Abrechenbare Nutzung, Preisdaten |
| `system.access` | Audit-Logs, Lineage, Netzwerk-Events |
| `system.compute` | Cluster, Warehouses, Nodes, Instance Pools |
| `system.lakeflow` | Jobs, Pipelines, Zerobus-Ingest-Operationen |
| `system.alert` | Alert-Konfigurationen und -Auswertungen |
| `system.serving` | Metadaten von Model-Serving-Endpunkten |
| `system.ai_gateway` | AI-Gateway-Nutzung und -Ausgaben |
| `system.information_schema` | Schema-Metadaten (funktioniert abweichend, siehe unten) |

**Aufbewahrung und Geltungsbereich:** Die meisten Tabellen behalten Daten für 365 Tage (kostenlose Aufbewahrungsfrist). Manche Tabellen (Node-Typen, Preise, Workspaces) werden unbegrenzt aufbewahrt. Workspace-Ereignisse sind regional, Account-Ereignisse global gespeichert.

**Streaming aus System Tables:** Ab Databricks Runtime 16.4 lassen sich System Tables auch als Streaming-Quelle lesen — dabei muss die Option `skipChangeCommits` gesetzt werden, und die VACUUM-Aufbewahrung (Standard 7 Tage) sollte beim Lag-Monitoring berücksichtigt werden:

```python
spark.readStream.option("skipChangeCommits", "true").table("system.billing.usage")
```

**Einschränkung:** Neue Spalten können jederzeit zu System Tables hinzugefügt werden. Stark selektive Query-Prädikate werden empfohlen, um Performance-Fehler zu vermeiden.

**`information_schema`: Metadaten-Abfragen.** `INFORMATION_SCHEMA` ist ein SQL-Standard-Schema, das Metadaten über Objekte in allen Catalogs des Metastore liefert — sowohl account-weit (`system.information_schema`) als auch pro Catalog. Es gilt automatische Privilegien-Filterung: es werden nur Objekte angezeigt, auf die bereits Zugriff besteht.

**Wichtige Views:**

| View | Zweck | Wichtige Spalten |
|---|---|---|
| `TABLES` | Tabellen/Views im Catalog | `table_name`, `table_schema`, `table_catalog`, `table_owner`, `created_by`, `last_altered`, `last_altered_by` |
| `TABLE_PRIVILEGES` | Principals mit Privilegien auf Tabellen/Views | `grantee`, `privilege_type`, `table_name`, `table_schema`, `table_catalog` |
| `COLUMNS` | Spalten von Tabellen/Views | `column_name`, `data_type`, `table_name` |

Weitere Views: `SCHEMATA`, `CATALOGS`, `ROUTINES`, sowie privilegienbezogene Views (`SCHEMA_PRIVILEGES`, `CATALOG_PRIVILEGES`).

**Beispiele:**

```sql
-- In den letzten 24 Stunden geänderte Tabellen finden
SELECT table_name, table_owner, last_altered
FROM system.information_schema.tables
WHERE datediff(now(), last_altered) < 1;
```

```sql
-- Wer hat Zugriff auf diese Tabelle?
SELECT grantee, table_name, privilege_type
FROM system.information_schema.table_privileges
WHERE table_name = "login_data_silver";
```

**Hinweis:** Selektive Filter verwenden, um Timeouts zu vermeiden; Bezeichner klein schreiben für bessere Performance.

---

## 60. Audit Logs, Billing und Lineage per System Tables abfragen

**Einfach erklärt:** Drei besonders wichtige System-Tabellen-Schemas beantworten typische Governance-Fragen: `system.billing.usage` zeigt, wie viel Compute/Storage verbraucht und abgerechnet wurde; `system.access.audit` protokolliert nahezu in Echtzeit, wer wann auf was zugegriffen hat; `system.access.table_lineage`/`column_lineage` zeigen, welche Tabellen/Spalten aus welchen Quellen erzeugt wurden.

**Billing: `system.billing.usage`.** Verfolgt abrechenbare Nutzung account-weit über alle Regionen hinweg — inklusive Korrekturen über `record_type` (`ORIGINAL`, `RETRACTION`, `RESTATEMENT`).

**Wichtige Spalten:** `record_id`, `account_id`, `workspace_id`, `sku_name` (z. B. `STANDARD_ALL_PURPOSE_COMPUTE`), `cloud`, `usage_start_time`, `usage_end_time`, `usage_date`, `custom_tags`, `usage_unit` (z. B. `DBU`), `usage_quantity`, `usage_metadata` (u. a. `job_id`), `identity_metadata` (u. a. `run_as`), `billing_origin_product`, `usage_type` (`COMPUTE_TIME`, `STORAGE_SPACE`, `NETWORK_BYTE`, …).

**DBU** (Databricks Unit) ist die Verarbeitungseinheit, in der Databricks abrechnet — jeder Job-, Query- oder Pipeline-Lauf verbraucht DBUs je nach genutztem Compute und Laufzeit. **SKU** identifiziert, welches Databricks-Produkt/-Tier die DBU-Nutzung erzeugt hat (Jobs Compute, All-Purpose Compute, DBSQL, Serverless, …) — da jede SKU unterschiedlich bepreist ist, lässt sich damit Spend nach Workload-Art aufschlüsseln.

**Beispiel — korrekte stündliche Aggregation inkl. Korrekturen:**

```sql
SELECT
  usage_metadata.job_id,
  usage_start_time,
  usage_end_time,
  SUM(usage_quantity) as usage_quantity
FROM system.billing.usage
GROUP BY ALL
HAVING usage_quantity != 0
```

**Audit-Logs: `system.access.audit`.** Erfasst nahezu in Echtzeit, wer wann auf was zugegriffen hat.

**Wichtige Spalten:** `account_id`, `workspace_id`, `version`, `event_time`, `event_date`, `source_ip_address`, `user_agent`, `session_id`, `user_identity` (Struct), `service_name`, `action_name`, `request_id`, `request_params` (Map), `response` (Struct mit Statuscode/Fehlermeldung), `audit_level`, `event_id`, `identity_metadata` (`run_by`, `run_as`).

**Hinweise:** Die meisten Audit-Logs sind nur in der Region des jeweiligen Workspace verfügbar. Account-weite Audit-Logs tragen `workspace_id = 0`. Für bessere Performance auf `event_date` statt `event_time` filtern.

**Beispiele:**

```sql
-- Wer greift am häufigsten auf diese Tabelle zu?
SELECT user_identity.email, count(*)
FROM system.access.audit
WHERE request_params.table_full_name = "main.uc_deep_dive.login_data_silver"
  AND service_name = "unityCatalog"
  AND action_name = "generateTemporaryTableCredential"
GROUP BY 1 ORDER BY 2 DESC LIMIT 1;

-- Wer hat diese Tabelle gelöscht?
SELECT user_identity.email
FROM system.access.audit
WHERE request_params.full_name_arg = "main.uc_deep_dive.login_data_silver"
  AND service_name = "unityCatalog"
  AND action_name = "deleteTable";

-- Worauf hat dieser Nutzer in den letzten 24 Stunden zugegriffen?
SELECT request_params.table_full_name
FROM system.access.audit
WHERE user_identity.email = "user@example.com"
  AND service_name = "unityCatalog"
  AND action_name = "generateTemporaryTableCredential"
  AND datediff(now(), event_time) < 1;
```

**Lineage: `system.access.table_lineage` und `column_lineage`.** Zwei Lineage-System-Tabellen erlauben programmatische Abfragen der Datenherkunft. Sie behalten ein rollierendes 1-Jahres-Fenster — ältere Events werden automatisch entfernt. Für Lineage über diesen Zeitraum hinaus: Catalog Explorer oder Lineage-API (unbegrenzte Aufbewahrung für Events ab dem 1. September 2024).

**`table_lineage`-Spalten (Auswahl):** `account_id`, `metastore_id`, `workspace_id`, `entity_type` (`NOTEBOOK`, `JOB`, `PIPELINE`, `DASHBOARD_V3`, `DBSQL_QUERY`, oder `NULL`), `entity_id`, `entity_run_id`, `source_table_full_name` (+ `_catalog`/`_schema`/`_name`), `source_path`, `source_type` (`TABLE`, `PATH`, `VIEW`, `MATERIALIZED_VIEW`, `METRIC_VIEW`, `STREAMING_TABLE`), analog `target_*`, `created_by`, `event_time`, `event_date`, `record_id`, `event_id`, `statement_id` (Fremdschlüssel zur Query-History, nur SQL-Warehouse), `entity_metadata`, `direct_access`.

`column_lineage` enthält zusätzlich `source_column_name` und `target_column_name`. **Hinweis:** Enthält keine Events ohne Quelle (z. B. Inserts mit expliziten Literalwerten).

**Event-Klassifizierung:** nur `source_type` gesetzt → Read; nur `target_type` gesetzt → Write; beide gesetzt → Read+Write.

**Beispiel:**

```sql
CREATE OR REPLACE TABLE car_features
AS SELECT *,
  in1+in2 as premium_feature_set
FROM car_features_exterior
JOIN car_features_interior
USING(id, model);
```

erzeugt u. a. folgenden `table_lineage`-Eintrag:

| entity_type | source_table_name | target_table_name | created_by |
|---|---|---|---|
| NOTEBOOK | car_features_exterior | car_features | user@example.com |

und folgenden `column_lineage`-Eintrag:

| source_table_name | target_table_name | source_column_name | target_column_name |
|---|---|---|---|
| car_features_interior | car_features | in1 | premium_feature_set |

**External Tables (per Pfad statt Name referenziert):**

```sql
SELECT *
FROM system.access.table_lineage
WHERE source_path = "s3://mybucket/table1" OR target_path = "s3://mybucket/table1";
```

**Hilfsfunktion, die Tabellenname und -pfad gleichzeitig abdeckt:**

```python
def getLineageForTable(table_name):
  table_path = spark.sql(f"describe detail {table_name}").select("location").head()[0]
  df = spark.read.table("system.access.table_lineage")
  return df.where(
    (df.source_table_full_name == table_name)
    | (df.target_table_full_name == table_name)
    | (df.source_path == table_path)
    | (df.target_path == table_path)
  )
```

**Einschränkung:** Records werden nur erzeugt, wenn sich Lineage tatsächlich ableiten lässt — die Lineage-System-Tabellen decken daher nur eine Teilmenge aller Lese-/Schreibzugriffe ab; die allgemeinen Data-Lineage-Einschränkungen von Unity Catalog gelten auch hier.

---

## 61. Insights-Tab (Catalog Explorer)

**Einfach erklärt:** Der Insights-Tab im Catalog Explorer zeigt zu einer Tabelle, wie oft und von wem sie in den letzten 30 Tagen genutzt wurde, welche Queries/Notebooks/Dashboards sie am häufigsten nutzen und mit welchen anderen Tabellen sie oft gejoint wird. Das hilft, Vertrauen in Daten einzuschätzen und ungenutzte Tabellen für Cleanup zu identifizieren.

**Was der Insights-Tab anzeigt:** ein Diagramm zur Tabellennutzung der letzten 30 Tage; häufige Queries und Notebooks, die auf die Tabelle zugreifen; häufig genutzte Dashboards; häufige Nutzer, die auf die Tabelle zugreifen; andere Tabellen, die häufig zusammen mit dieser Tabelle gejoint werden. Popularität wird dabei unterschiedlich gemessen: Tabellen-Popularität bemisst sich an interaktiven Lesezugriffen, Spalten-Popularität am Anteil der Queries, die die jeweilige Spalte referenzieren.

**Geltungsbereich (Scope):**

| Abschnitt | Scope |
|---|---|
| Tabellennutzungs-Diagramm (30 Tage) | **metastore-weit** — über alle am Metastore angehängten Workspaces hinweg |
| Häufig gejointe Tabellen | **metastore-weit** |
| Häufige Nutzer | **workspace-begrenzt** |
| Häufige Queries | **workspace-begrenzt** — nur gespeicherte Queries im SQL-Editor |
| Häufige Dashboards / Notebooks | **workspace-begrenzt** |

**Benötigte Berechtigungen:** `SELECT`-Privileg auf der Tabelle; `USE SCHEMA`-Privileg auf dem übergeordneten Schema der Tabelle; `USE CATALOG`-Privileg auf dem übergeordneten Catalog der Tabelle; für Query-Ergebnisse zusätzlich `CAN VIEW`-Berechtigung in Databricks SQL. Metastore-Admins verfügen standardmäßig über diese Berechtigungen.

**Nutzen: ungenutzte Tabellen identifizieren.** Der Insights-Tab hilft bei Fragen wie „Kann ich diesen Daten vertrauen?" oder „Welche Nutzer können dazu Auskunft geben?" — und lässt sich damit auch nutzen, um Tabellen zu identifizieren, die von Anwendungen nicht mehr verwendet werden. Solche Tabellen können anschließend zur späteren Bereinigung (Cleanup) getaggt werden.

Keine Code-Beispiele in dieser Datei.

---

## 62. Pseudonymisierung und Anonymisierung von PII

**Einfach erklärt:** Während Row Filter, Column Masks und ABAC steuern, *wer auf Daten zugreifen darf*, verändern Pseudonymisierung und Anonymisierung *die Daten selbst*, um PII zu schützen. Pseudonymisierung (Hashing, Tokenization) ist auf Record-Ebene reversibel — autorisierte Nutzer können re-identifizieren; Anonymisierung (Suppression, Generalization) ist auf Datensatz-Ebene irreversibel. Grundprinzip: Mit genug Zeit und Zusatzdaten lässt sich vieles potenziell re-identifizieren — die Techniken reduzieren das Risiko, eliminieren es aber nicht vollständig.

**Pseudonymisierung — reversibel, Record-Ebene.** Ersetzt PII durch künstliche, aber eindeutige Identifikatoren (Token, Hashes, verschlüsselte Werte). Der Vorgang ist umkehrbar — pseudonymisierte Daten gelten laut GDPR weiterhin als personenbezogene Daten. Autorisierte Nutzer mit Zugriff auf Schlüssel/Hash-Tabelle können re-identifizieren; Data Scientists können mit vollständigen Datensätzen arbeiten, ohne die zugrunde liegenden Klartextwerte einsehen zu können.

**Methode: Hashing.** Eine Hash-Funktion erzeugt aus dem PII-Wert eine zufällig aussehende, deterministische Zeichenkette. Da Hashes deterministisch sind, wird Salting empfohlen — ein zufälliger String wird vor dem Hashen angehängt, um Rainbow-Table-Angriffe zu erschweren. Der Salt-Wert lässt sich über die Databricks-Secrets-API verwalten, sodass er nie im Klartext im Notebook erscheint und nur autorisierte Produktions-Jobs/Nutzer Zugriff darauf haben.

```python
salt = "BEANS"

def salted_hash(id):
    return F.sha2(F.concat(id, F.lit(salt)), 256)
```

`sha2(expr, bitLength)` ist eine SQL/PySpark-Funktion. `bitLength` akzeptiert `0` (Standard, entspricht 256), `224`, `256`, `384` oder `512` und liefert eine hexadezimale Prüfsumme aus der SHA-2-Familie zurück:

```sql
SELECT sha2('Spark', 256);
-- 529bc3b07127ecb7e53a4dcf1991d9152c24537d919178022b2c42657f79a26b
```

**Vorteile:** praktisch irreversibel, Datenverknüpfung über den Hash-Wert weiterhin möglich, erhält die Datenverteilung, kein Systemumbau nötig.
**Nachteile:** höherer Speicherbedarf (Hash-Werte sind länger als die Originaldaten), teilweise Rückschlüsse aus der Werteverteilung möglich, keine echte Rückgewinnung des Originalwerts — problematisch z. B. bei ML-Preprocessing, wenn Teilinformationen (etwa die Domain einer E-Mail-Adresse) separat weiterverarbeitet werden müssen und daher getrennt gehasht werden sollten.

**Methode: Tokenization.** Jeder eindeutige PII-Wert wird durch einen zufälligen Token (z. B. eine UUID) ersetzt; die Zuordnung Token ↔ Originalwert wird in einer sicheren Lookup-/Vault-Tabelle gespeichert. Tokenization ist langsam beim Schreiben, schnell beim Lesen — die dem Endnutzer zugängliche Tabelle enthält nur den kompakten Token.

```python
.withColumn("token", F.expr("uuid()"))
# gespeichert in einer Token-Tabelle, per Join mit dem Original verknüpft
```

**Vorteile:** hoher Schutzgrad, der Token ersetzt den echten Wert 1:1 in nachgelagerten Operationen, schnell beim Lesen.
**Nachteile:** langsam beim Schreiben, benötigt ein robustes eigenes Tokenisierungssystem/Vault; bei Kompromittierung des Vaults sind alle Originalwerte sofort wiederherstellbar.

**Hashing vs. Tokenization im Vergleich:**

| | Hashing | Tokenization |
|---|---|---|
| Rückgewinnung | praktisch irreversibel | vollständig reversibel über den Vault |
| Geschwindigkeit | schnell, kein Lookup nötig | schreiblastig langsam, lesend schnell |
| Speicherbedarf | erhöht (Hash-Länge) | gering (kompakter Token) |
| Schutzgrad | moderat–hoch | hoch |
| Risiko bei Kompromittierung | Rückschlüsse aus Werteverteilung möglich, kein direkter Rückweg | bei Vault-Kompromittierung alle Originalwerte abrufbar |
| Typischer Einsatz | Passwörter, kein Rückführungsbedarf | Zahlungsdaten, kontrollierte Rückführung |

**Anonymisierung — irreversibel, Datensatz-Ebene.** Schützt ganze Datasets (Tabellen, Datenbanken, Kataloge) und verändert personenbezogene Daten irreversibel so, dass Betroffene weder direkt noch indirekt identifizierbar sind — passend für Business-Intelligence-Anwendungsfälle, bei denen Aggregationen und Trends im Vordergrund stehen. In der Praxis werden meist mehrere Techniken kombiniert.

**Methode: Data Suppression.** Bedingte Filter und dynamische Zugriffskontrollen entfernen den Zugriff auf Spalten oder Zeilen, ohne die Reporting-Fähigkeit einzuschränken — z. B. lässt sich eine regionale Aggregation weiterhin erstellen, ohne vollständige Kundennamen/-adressen offenzulegen. Aggregation allein bietet keinen Schutz und kann sensible Daten über Reports/Dashboards offenlegen, wenn z. B. eine Gruppierungsspalte nur sehr wenige Datensätze enthält (kleine Städte, dünn besetzte demografische Gruppen). Ein Filter, der Gruppen mit niedriger Zeilenzahl entfernt, schützt Einzelidentitäten zusätzlich; dynamische Zugriffskontrollen erlauben gruppenbasierte Redaktion/Filterung.

**Methode: Generalization.** Entfernt Präzision aus den Daten, um Re-Identifikation zu erschweren:

- **Categorical Generalization:** kleinere Kategorien zu größeren zusammenfassen (z. B. Stadt → Bundesland/Land), damit dünn besetzte Gruppen nicht auf Einzelpersonen zurückführbar sind.
- **Binning:** z. B. 10-Jahres-Altersbänder oder Gehaltsbänder statt Einzelwerten — Reports bleiben aussagekräftig, ohne den exakten Wert einer Person offenzulegen. Die passende Bin-Größe hängt vom Anwendungsfall ab und sollte mit Domänenexpertise festgelegt werden.
- **IP-Truncation:** das letzte Byte einer IP-Adresse durch `0` ersetzen, um sie in den `/24`-CIDR-Bereich zu bringen.
- **Rounding:** Werte auf eine gröbere Genauigkeit runden (z. B. auf die nächsten 5) — allgemeine Trends bleiben erhalten, da gleichmäßig auf- und abgerundet wird; die höchsten/niedrigsten Gruppen können aber weiterhin Ausreißer offenlegen und ggf. zusätzlich unterdrückt werden müssen.

**Vergleich der Schutztechniken:**

| Technik | Beschreibung | Beispiel | Typischer Einsatz | Vorteile | Nachteile | Schutzgrad |
|---|---|---|---|---|---|---|
| **Data Masking** | Originaldaten mit verändertem Inhalt verdecken (Dynamic Masking) | `gXXX.dXXXX@gmx.de` | operative Nutzbarkeit bei reduzierter Sichtbarkeit | Format bleibt erhalten, Teilinformation bleibt nutzbar | verändert die Datenverteilung, teils aus Nachbarspalten rekonstruierbar, keine Verknüpfung möglich | niedrig–moderat |
| **Pseudo-Anonymisierung** | Werte durch Pseudonyme ersetzen | `charles@gmx.de` | Verlaufsstudien mit Tracking-Bedarf bei geschützter Identität | statistische Verteilung bleibt erhalten, Verknüpfung mehrerer Datasets möglich | Rückschlüsse aus Verteilung möglich, Verknüpfungstabelle muss sicher gespeichert werden | niedrig–moderat |
| **Hashing** | irreversible Transformation | `cf35ddff242..` | Passwort-Speicherung | sicher/irreversibel, Verknüpfung möglich, erhält Verteilung | Rückschlüsse aus Verteilung möglich, keine Rückgewinnung | moderat–hoch |
| **Column Encryption** | spaltenweise Verschlüsselung vor dem Speichern | `skjrk42ndd..` | Schutz einzelner sensibler Spalten | hohe Sicherheit, Einzelwerte/Verteilung beobachtbar | Schlüsselverwaltung nötig, deutlich größerer Speicherbedarf, Verknüpfung schwierig, Verteilung verändert sich | hoch |
| **Tokenization** | Ersetzung durch Token | `fik52tklhn2..` | Kreditkarten-Transaktionen | Token ersetzt Originaldaten 1:1 in Operationen | robustes Tokenisierungssystem nötig, bei Kompromittierung vollständig rückgewinnbar | hoch |

**Best Practices für den Umgang mit PII:**

1. Keine PII zu haben ist immer besser, als PII zu schützen.
2. Rangfolge der Schutzwirkung: Anonymisierung > Pseudonymisierung > Klartext.
3. Eine gesunde Skepsis gegenüber den eigenen angewandten Schutzmaßnahmen bewahren.
4. Stets bedenken, wie sich Datasets kombinieren ließen, um Re-Identifikation zu ermöglichen.
5. Datenteams regelmäßig zu den anwendbaren Datenschutzgesetzen schulen.
6. Nicht jede Art von PII ist gleich sensibel — Schutzmaßnahmen entsprechend abstufen.
7. Privacy-Impact-Assessments (PIA) durchführen.
8. Umgebungen, die PII verarbeiten, konsequent isolieren.

**Praxisbeispiel: Salted Hashing und Tokenization als Pipeline.** Dieser Lakeflow-Declarative-Pipelines-Code erstellt aus einer Quelltabelle mit Nutzerregistrierungsdaten zwei parallele Pseudonymisierungs-Pfade:

```python
from pyspark import pipelines as dp
import pyspark.sql.functions as F

user_reg_source = spark.conf.get("user_reg_source")

# Quelldaten inkrementell mit Auto Loader einlesen
@dp.table
def registered_users():
    return (
        spark.readStream
            .format("cloudFiles")
            .schema("device_id LONG, mac_address STRING, registration_timestamp DOUBLE, user_id LONG")
            .option("cloudFiles.format", "json")
            .load(f"{user_reg_source}")
        )

# --- Pfad 1: Salted Hashing ---
salt = "BEANS"

def salted_hash(id):
    return F.sha2(F.concat(id, F.lit(salt)), 256)

@dp.table
def user_lookup_hashed():
    return (dp
            .read_stream("registered_users")
            .select(
                  salted_hash(F.col("user_id")).alias("alt_id"),
                  "device_id", "mac_address", "user_id")
           )

# --- Pfad 2: Tokenization ---
@dp.table
def registered_users_tokens():
    return (dp
            .readStream("registered_users")
            .select("user_id")
            .distinct()
            .withColumn("token", F.expr("uuid()"))
        )

@dp.table
def user_lookup_tokenized():
    return (dp
            .read_stream("registered_users")
            .join(dp.read("registered_users_tokens"), "user_id", "left")
            .drop("user_id")
            .withColumnRenamed("token", "alt_id")
           )
```

`user_lookup_hashed` und `user_lookup_tokenized` dienen anschließend als einzige Verknüpfung zwischen einer pseudonymen `alt_id` und der echten `user_id` — der Zugriff auf diese Lookup-Tabellen lässt sich getrennt und restriktiv vergeben, sodass andere Tabellen im System nur die pseudonyme ID kennen.

**Praxisbeispiel: Binning-Anonymisierung (Altersbänder).** Die Funktion `age_bins()` berechnet aus einem Geburtsdatum das Alter und ordnet es 10-Jahres-Bändern zu, statt das exakte Alter offenzulegen:

```python
def age_bins(dob_col):
    age_col = F.floor(F.months_between(F.current_date(), dob_col) / 12).alias("age")
    return (
        F.when((age_col < 18), "under 18")
        .when((age_col >= 18) & (age_col < 25), "18-25")
        .when((age_col >= 25) & (age_col < 35), "25-35")
        .when((age_col >= 35) & (age_col < 45), "35-45")
        .when((age_col >= 45) & (age_col < 55), "45-55")
        .when((age_col >= 55) & (age_col < 65), "55-65")
        .when((age_col >= 65) & (age_col < 75), "65-75")
        .when((age_col >= 75) & (age_col < 85), "75-85")
        .when((age_col >= 85) & (age_col < 95), "85-95")
        .when((age_col >= 95), "95+")
        .otherwise("invalid age")
        .alias("age")
    )

@dp.table
def user_age_bins():
    return (
        dp.read("users_bronze")
        .select("user_id", age_bins(F.col("dob")), "gender", "city", "state")
    )
```

Das Ergebnis `user_age_bins` erlaubt Auswertungen nach Altersgruppe, Geschlecht, Stadt und Bundesland, ohne das exakte Geburtsdatum in der Ausgabetabelle zu führen.

**Verwandte Themen:** `08 ABAC/Haeufige Muster.md`, Abschnitt "Konsistentes Hashing / deterministische Pseudonymisierung" — dasselbe `SHA2`-Grundmuster, dort als ABAC-Column-Mask-Funktion. `Lakeflow Pipelines/10 Governance und Zugriff/GDPR.md` — Löschstrategien (Bronze-first, `skipChangeCommits`, Materialized Views) für das "Recht auf Vergessenwerden"; dort gilt ausdrücklich: vollständige Löschung ist Obfuskation/Pseudonymisierung vorzuziehen, wo immer möglich. `Lakeflow Pipelines/05 CDC/Change Data Feed.md` — Propagation von Löschungen (inkl. pseudonymisierter Datensätze) durch nachgelagerte Tabellen.

---

## 63. Verbose Audit Logs (Log Delivery), SCIM API und Cluster-Nutzungsanalyse

**Einfach erklärt:** Neben den in Abschnitt 60 beschriebenen `system.access.audit`-System-Tabellen bietet Databricks (historisch und weiterhin ergänzend) einen zweiten Weg zu Audit-Daten: die **Auslieferung roher Audit-Logs im JSON-Format an einen kundeneigenen Cloud-Storage-Bucket** (z. B. AWS S3), aus dem sich eine eigene Auswertungs-Pipeline bauen lässt — nützlich etwa für SIEM-Integration oder wenn Audit-Daten außerhalb des Databricks-Account-Kontexts konsolidiert werden sollen.

**Aufbau einer Audit-Log-Pipeline nach dem Medaillon-Muster:**

- **Bronze:** rohe, als JSON an den kundeneigenen S3-Bucket gelieferte Audit-Log-Daten werden unverändert eingelesen, mit **Structured Streaming** (Checkpoints zur State-Verwaltung) und **Delta Lake** (Schema-Evolution).
- **Silver:** Bereinigung und Transformation — Nullwerte entfernen, E-Mail-Adressen parsen, Zeitstempel konvertieren.
- **Gold:** ressourcentypspezifische, produktionsreife Tabellen, auf die das gesamte Unternehmen sich verlassen kann.

Für eine tägliche Pseudo-Batch-Verarbeitung eignet sich `triggerOnce` (Structured Streaming); nach Aktualisierungen empfiehlt sich `OPTIMIZE` auf den Zieltabellen.

**SCIM API zur Identitätsklärung.** Ergibt eine Audit-Log-Auswertung einen auffälligen Job oder Cluster (z. B. unautorisierte Cluster-Erstellung), lässt sich über die **SCIM API** die Identität des verantwortlichen Nutzers auflösen — Admins können den Ersteller dann direkt kontaktieren, um den Vorfall zu klären.

**Cluster-Nutzungsanalyse per Audit-Logs (Beispielmetriken):**

- Tägliche Cluster-Erstellungen, gruppiert nach Datum und `cluster_creator` (Filter auf `actionName = "create"`).
- Unterscheidung Job-Cluster vs. interaktive Cluster: Job-Cluster folgen dem Namensmuster `job-<jobId>-run-<runId>`, aus dem sich die `jobId` extrahieren lässt.
- Cluster mit `cluster_creator IS NULL` deuten auf automatisiert (z. B. über Jobs) statt manuell erstellte Cluster hin.
- Überwachung des Autotermination-Status zur Kostenkontrolle.

**Einordnung:** Dieser Ansatz stammt aus einem älteren Blogpost (2020) und beschreibt die manuelle, selbst gebaute Auswertung roher Audit-Log-Dateien — die in Abschnitt 60 dokumentierten `system.access.audit`/`system.billing.usage`-System-Tabellen sind der modernere, von Databricks direkt bereitgestellte Weg zu denselben Fragestellungen (Cluster-Ersteller, Zugriffshistorie) und benötigen keine eigene Pipeline. Für SIEM-Export oder Konsolidierung über mehrere Accounts/Cloud-Umgebungen hinweg bleibt die Log-Delivery an einen eigenen Storage-Bucket aber ein relevantes, ergänzendes Werkzeug.

Keine Code-Beispiele in dieser Datei.

Quelle: https://www.databricks.com/blog/2020/06/02/monitor-your-databricks-workspace-with-audit-logs.html

---

## 64. Verifikationsprotokoll (Databricks-Blog-Abgleich)

Abgleich aller 62 Originaldateien gegen aktuelle **Databricks-Blog-Artikel** (`databricks.com/blog`, teils ergänzt durch `community.databricks.com`), durchgeführt am 2026-09-24 von vier parallelen Rechercheagenten (je ein Themenblock):

### Grundlagen, Objektmodell, Setup, Table ACLs (Themen 1–14)

| Thema | Blog-Quelle | Ergebnis |
|---|---|---|
| Unity-Catalog-Metastore-Setup (manuelle/skriptbasierte Einrichtung, Terraform) | [Enterprise-Scale Governance: Migrating from Hive Metastore to Unity Catalog](https://www.databricks.com/blog/enterprise-scale-governance-migrating-hive-metastore-unity-catalog) | ✅ Bestätigt den in „Unity Catalog einrichten" beschriebenen Ablauf und ergänzt, dass das Setup per Terraform/REST-API automatisiert und über mehrere Business Units templatisiert werden kann. |
| Data Governance mit Unity Catalog als zentrale Plattform | [Unity Catalog Governance Value Levers](https://www.databricks.com/blog/unity-catalog-governance-value-levers); [Unity Catalog Governance in Action](https://www.databricks.com/blog/unity-catalog-governance-action-monitoring-reporting-and-lineage) | ✅ Bestätigt den Governance-Fähigkeiten-Überblick als aktuell gültige Kernpfeiler. |
| Managed vs. External Tables — Storage Lifecycle beim `DROP` | Doku-Seite [Managed versus external assets](https://docs.databricks.com/aws/en/data-governance/unity-catalog/managed-versus-external) (kein dedizierter Blog gefunden) | ⚠️ Kein Blog-Artikel gefunden; die Doku bestätigt aber exakt die im Original beschriebenen Fristen. |
| Legacy Table ACLs / Hive Metastore — Deprecation-Status | Doku-Seite plus Community-Thread [„Hive Metastore End of Life"](https://community.databricks.com/t5/data-engineering/hive-metastore-end-of-life/td-p/136152) | ✅ Bestätigt explizit: „data governance using Hive metastore is deprecated" — deckt sich mit dem Legacy-Hinweis in allen vier Table-ACL-Dateien. |
| ABAC als Weiterentwicklung der Rechteverwaltung | [ABAC row filtering and column masking policies, governed tags, and data classification are now generally available](https://www.databricks.com/blog/abac-row-filtering-and-column-masking-policies-governed-tags-and-data-classification-are-now); [What's new with Unity Catalog at Data + AI Summit 2026](https://www.databricks.com/blog/whats-new-unity-catalog-data-ai-summit-2026) | ✅ Bestätigt und ergänzt die knapp erwähnte ABAC-Fähigkeit: GA seit 13. Mai 2026, plus neue Erweiterungen vom Data + AI Summit 2026. |

### Access Control und Privilegien verwalten (Themen 15–29)

| Thema | Blog-Quelle | Ergebnis |
|---|---|---|
| ABAC als empfohlener zentraler Zugriffskontroll-Mechanismus | [How to scale data governance with Attribute-Based Access Control in Unity Catalog](https://www.databricks.com/blog/how-scale-data-governance-attribute-based-access-control-unity-catalog) | ✅ Bestätigt die Empfehlung: ABAC mit Governed Tags wird gegenüber tabellenweisen Row-/Column-Filtern als skalierbarer Ansatz positioniert. |
| ABAC Row Filtering/Column Masking, Governed Tags, Data Classification | [ABAC ... now generally available](https://www.databricks.com/blog/abac-row-filtering-and-column-masking-policies-governed-tags-and-data-classification-are-now) | ✅ Bestätigt: inzwischen GA statt nur Preview. |
| Admin-Rollen (Account-/Workspace-/Metastore-Admin) | [Databricks Workspace Administration – Best Practices](https://www.databricks.com/blog/2022/08/26/databricks-workspace-administration-best-practices-for-account-workspace-and-metastore-admins.html) | ⚠️ Rollenaufteilung stimmt, Blogpost stammt aber aus 2022 — zusätzlich gegen aktuelle Doku geprüft, kein Widerspruch. |
| Workspace-Catalog-Binding / Isolation als Best Practice | Offizielle Best-Practices-Doku (kein dedizierter Blogpost gefunden) | ⚠️ Keine Blog-Quelle gefunden, aber inhaltlich deckungsgleich mit der Best-Practices-Dokumentation. |
| Credential Vending / Customer-Managed Keys | [Take Control: Customer-Managed Keys for Lakebase Postgres](https://www.databricks.com/blog/take-control-customer-managed-keys-lakebase-postgres) | ⚠️ Kein direkter Blogpost zu Credential Vending; aktueller CMK-Blog behandelt primär Lakebase Postgres statt des allgemeinen Envelope-Encryption-Modells — kein Widerspruch, aber auch keine direkte Bestätigung. |
| GRANT/REVOKE/SHOW GRANTS Kernsyntax | Offizielle Language-Manual-Seiten (keine dedizierten Blogposts) | ✅ Keine Hinweise auf Änderungen; Kernsyntax weiterhin aktuell (Stand September 2026). |

### ABAC (Themen 30–45)

| Thema | Blog-Quelle | Ergebnis |
|---|---|---|
| GA-Status von ABAC Row Filter/Column Mask | [ABAC ... now generally available](https://www.databricks.com/blog/abac-row-filtering-and-column-masking-policies-governed-tags-and-data-classification-are-now) | ⚠️ Bestätigt: GA seit 13. Mai 2026 — die 16 Originaldateien nennen keinen expliziten GA/Preview-Status und sollten entsprechend ergänzt werden. |
| Governed Tags & Data Classification als Gesamtpaket | [How to scale data governance with ABAC](https://www.databricks.com/blog/how-scale-data-governance-attribute-based-access-control-unity-catalog) | ✅ Bestätigt und vertieft die Konzepte aus „Grundkonzepte" und „Secure by Default" — inhaltlich deckungsgleich. |
| Performance von Row Filter/Column Mask | Aktuelle Performance-Doku (referenziert im GA-Blogpost) | ✅ Deckt sich vollständig mit Thema 44 — keine neuen Erkenntnisse. |
| Neuer Policy-Typ: ABAC DENY-Policies (Beta) | [ABAC DENY policies (Beta)](https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/deny-policies) | ⚠️ **Fehlt in den Originaldateien:** vierter Policy-Typ neben Row-Filter/Column-Mask/GRANT, kann `MANAGE ACCESS CONTROL` verweigern, vererbt sich hierarchisch. |
| Metastore-weite ABAC-Policies | September-2026-Release-Notes | ⚠️ **Fehlt in den Originaldateien:** Policies lassen sich inzwischen (Beta) auch auf Metastore-Ebene anhängen — größerer Scope als `CATALOG`/`SCHEMA`/`TABLE`. |
| Cross-Engine ABAC | [Introducing Cross-Engine ABAC](https://www.databricks.com/blog/introducing-cross-engine-abac) | ⚠️ **Neues Feature (Beta, ca. Juni 2026):** ABAC-Durchsetzung auch für externe Engines über die Iceberg-REST-Catalog-API — in den Originaldateien nicht erwähnt. |

**Teilfazit ABAC:** Die inhaltliche Substanz der 16 Originaldateien ist weiterhin korrekt. Auffälligster Nachholbedarf: GA-Status sowie drei neue 2026-Erweiterungen (DENY-Policies, Metastore-Level-Policies, Cross-Engine-ABAC) fehlen komplett.

### Filters/Masks, Service Policies, Governed Tags, Auditing, PII (Themen 46–62)

| Thema | Blog-Quelle | Ergebnis |
|---|---|---|
| Service Policies (AI Gateway) | [What's new in Unity AI Gateway: service policies, guardrails, observability, and cost controls](https://www.databricks.com/blog/whats-new-unity-ai-gateway-service-policies-guardrails-observability-and-cost-controls-ai) | ⚠️ Beta-Status der Originaldateien weiterhin plausibel, Funktionsumfang wächst aber schnell (Contextual Service Policies) — vor Nutzung erneut prüfen. |
| Governed Tags | [ABAC ... now generally available](https://www.databricks.com/blog/abac-row-filtering-and-column-masking-policies-governed-tags-and-data-classification-are-now) | ✅ GA seit 13. Mai 2026. Neu und nicht erwähnt: **Tag Propagation** (Private Preview) — trägt Tags automatisch an nachgelagerte Tabellen/Views weiter. |
| Automatische Tag-Zuweisung / Data Classification | [Find Sensitive Data at Scale with Data Classification in Unity Catalog](https://www.databricks.com/blog/find-sensitive-data-scale-data-classification-unity-catalog) | ⚠️ Zusätzlich zur regelbasierten Automatisierung aus Thema 56 gibt es eine agentenbasierte, GA-Data-Classification über alle Kataloge hinweg — in den Originaldateien nicht behandelt. |
| System Tables / Audit Logs / Lineage | [Improve Lakehouse Security Monitoring using System Tables](https://www.databricks.com/blog/improve-lakehouse-security-monitoring-using-system-tables-databricks-unity-catalog); [Data lineage in Unity Catalog GA](https://www.databricks.com/blog/announcing-general-availability-data-lineage-unity-catalog) | ✅ Bestätigt: Data Lineage GA seit Dezember 2022, System Tables etabliertes zentrales Werkzeug — keine veralteten Angaben gefunden. |
| PII / Pseudonymisierung vs. automatisierte Erkennung | [Find Sensitive Data at Scale](https://www.databricks.com/blog/find-sensitive-data-scale-data-classification-unity-catalog); [LogSentinel: LLM-powered PII detection](https://www.databricks.com/blog/logsentinel-how-databricks-uses-databricks-llm-powered-pii-detection-and-governance) | ⚠️ Manuelle Techniken (Hashing, Tokenization, Suppression, Generalization) bleiben zutreffend; automatisierte, agentenbasierte PII-Erkennung (GA seit Mai 2026) ergänzt sie, ersetzt sie aber nicht. |
| Row Filter/Column Masks vs. ABAC | [ABAC ... now generally available](https://www.databricks.com/blog/abac-row-filtering-and-column-masking-policies-governed-tags-and-data-classification-are-now) | ✅ Bestätigt: die empfohlene Priorisierung (ABAC vor manuellen Filtern) in Thema 46 ist aktuell und korrekt. |

### Gesamtfazit

Alle 62 Originaldateien beschreiben inhaltlich weiterhin korrekte, aktuelle Konzepte, Privilegien und SQL-Syntax — kein Blog-Artikel widerspricht den dokumentierten Kernaussagen. Wiederkehrendes Muster: Mehrere Bereiche haben seit den 2026er-Ankündigungen (Data + AI Summit 2026, ABAC-GA im Mai 2026) einen **GA-Status erreicht oder neue Beta-Funktionen erhalten**, die in den ursprünglich verfassten Dateien noch nicht auftauchen — insbesondere:

- **ABAC-Gesamtpaket** (Row Filter, Column Mask, Governed Tags, Data Classification): GA seit 13. Mai 2026.
- **Drei neue ABAC-Erweiterungen 2026:** DENY-Policies (Beta), Metastore-Level-Policies (Beta), Cross-Engine-ABAC (Beta).
- **Governed Tags:** Tag Propagation (Private Preview).
- **Data Classification:** agentenbasierte, GA-fähige automatische PII-Erkennung über alle Kataloge hinweg.
- **Service Policies:** wachsen schnell weiter (Contextual Service Policies), Beta-Status aber weiterhin plausibel.

Empfehlung: Diese ⚠️-markierten Punkte bei nächster Gelegenheit in die jeweiligen Originaldateien einpflegen.
