## 2_3_Data Isolation

![image-20260710091921711](../../../../assets/image-20260710091921711.png)

- Für das Thema Data Isolation ist es wichtig, die Datenhierarchie von Unity Catalog zu verstehen und zu berücksichtigen. Sie ist mit einem Metastore und dessen Zuordnung zu einem dreistufigen Namespace, der deine Daten-Assets organisiert, sehr leicht nachvollziehbar.
- In dieser Session betrachten wir den „Metastore“, Kataloge und Volumes.

------

![image-20260710092042857](../../../../assets/image-20260710092042857.png)

**Metastore**s

- Der Metastore ist der oberste Container für Metadaten in Databricks Unity Catalog und organisiert Datenobjekte hierarchisch nach dem dreistufigen Namespace.
- Account-Administratoren können **einen Metastore pro Region** erstellen und ihn **mehreren Workspaces in dieser Region** zuweisen.
- Ein Workspace ist die Arbeitsumgebung für eine Gruppe von Nutzern.
- Metastores bieten **standardmäßig regionale Isolation**, wobei der physische Speicher jedes Metastores in der Regel von anderen Metastores im selben Account getrennt ist.
- Aber **Data Isolation sollte auf Katalogebene beginnen**, der höchsten Ebene in der Datenhierarchie (Katalog > Schema > Tabelle/View/Volume).

------

**Katalog**e

- Wie erwähnt sind Kataloge als **primäre Einheit der Data Isolation** vorgesehen.
- Sie bilden oft Organisationseinheiten oder Phasen des Software-Entwicklungslebenszyklus ab, z. B. getrennte Kataloge für Produktions- und Entwicklungsdaten.
- Kataloge können **auf Metastore-Ebene oder getrennt vom übergeordneten Metastore gespeichert** werden, wobei getrennter Speicher die bevorzugte Option ist.
- Sie können an bestimmte Workspaces gebunden werden, sodass bestimmte Datentypen nur in dafür vorgesehenen Umgebungen verarbeitet werden.
- Kataloge sind ein idealer Ort, um vererbte Berechtigungen zu setzen, was eine effiziente und granulare Zugriffskontrolle ermöglicht.

------

**Volumes**

- Volumes können jede Art von Daten speichern, einschließlich strukturierter, halbstrukturierter und unstrukturierter Formate.
- Volumes bieten Möglichkeiten, um Dateien abzurufen, zu speichern, zu verwalten (governance) und zu organisieren – z. B. Bibliotheken, Konfigurationen und Checkpoint-Ordner.
- Sie bieten Governance über nicht-tabellarische Datensätze und ergänzen die Governance, die Tabellen für tabellarische Daten bieten.
- Wichtig zu verstehen: Die in Volumes gespeicherten Daten können nicht als Tabellen registriert oder wie eine Tabelle behandelt werden.
- Sie können entweder managed (an von Unity Catalog verwalteten Speicherorten gespeichert) oder external (auf Verzeichnisse in External Locations registriert) sein.

------

**Daten physisch trennen**

![image-20260710092944819](../../../../assets/image-20260710092944819.png)

Eine Organisation kann verlangen, dass Daten bestimmter Typen in bestimmten Accounts oder Buckets in ihrem Cloud-Tenant gespeichert werden.

Unity Catalog bietet die Möglichkeit, Speicherorte auf Metastore-, Katalog- oder Schema-Ebene zu konfigurieren, um solche Anforderungen zu erfüllen.

Darüber hinaus

bietet Unity Catalog dir die Möglichkeit, zwischen zentralisierten und verteilten Governance-Modellen zu wählen.

Im zentralisierten Governance-Modell sind deine Governance-Administratoren Owner des Metastores und können die Ownership jedes Objekts übernehmen sowie Berechtigungen gewähren und entziehen.

In einem verteilten Governance-Modell ist der Katalog oder eine Gruppe von Katalogen die Data Domain. Der Owner dieses Katalogs kann alle Assets erstellen und besitzen und die Governance innerhalb dieser Domain verwalten. Die Owner einer bestimmten Domain können unabhängig von den Ownern anderer Domains agieren.

Unabhängig davon, ob du den Metastore oder Kataloge als deine Data Domain wählst, empfiehlt Databricks dringend, eine Gruppe als Metastore-Admin oder Katalog-Owner festzulegen.

------

**External Locations und Storage Credentials**

![image-20260710093140694](../../../../assets/image-20260710093140694.png)

External Locations und Storage Credentials in Databricks Unity Catalog spielen eine entscheidende Rolle bei der Data Isolation:

- External Locations verknüpfen Unity-Catalog-Storage-Credentials mit Cloud-Object-Storage-Containern. Sie ermöglichen es Unity Catalog, im Namen der Nutzer Daten in deinem Cloud-Tenant zu lesen und zu schreiben.
- Für eine verbesserte Data Isolation können External Locations und Storage Credentials an bestimmte Workspaces gebunden werden.
- External Locations bieten eine starke Kontrolle und Nachvollziehbarkeit des Speicherzugriffs.
- Um zu verhindern, dass Unity-Catalog-Zugriffskontrollen umgangen werden, beschränke den direkten Nutzerzugriff auf Container, die als External Locations verwendet werden.

------

**Das Sicherheitsmodell von Unity Catalog**

![image-20260710093347998](../../../../assets/image-20260710093347998.png)

Nachdem wir alle zentralen Konzepte rund um Unity Catalog besprochen haben, werfen wir einen letzten Blick auf sein Sicherheitsmodell in Aktion. Beginnen wir mit einer Tour durch den Lebenszyklus einer Query, um zu sehen, wie Unity Catalog Zugriffskontrolle auf sichere und zugleich performante Weise bereitstellt.

(DIE FOLIE ENTHÄLT ANIMATIONEN; EINE FÜR JEDEN DER FOLGENDEN SCHRITTE)

1. [KLICK] Die Geschichte beginnt damit, dass ein Principal eine Query absetzt. Queries können über All-Purpose-Cluster abgesetzt werden, wenn Nutzer Python- oder SQL-Workloads interaktiv ausführen. Im Fall eines Jobs oder einer Pipeline, die als Service Principal läuft, würde dies typischerweise über einen Job-Cluster laufen. Alternativ setzen Datenanalysten Queries in Databricks SQL über ein SQL Warehouse ab, oder die Query stammt aus einem BI-Tool, das mit einem SQL Warehouse verbunden ist. In jedem Fall beginnt die zuständige Compute-Ressource mit der Verarbeitung der Query.
2. [KLICK] Die Anfrage wird an Unity Catalog weitergeleitet, der sie protokolliert und die Query gegen alle Sicherheitsbeschränkungen validiert, die innerhalb des Metastores definiert sind, mit dem die Compute-Ressource verknüpft ist.
3. [KLICK] Für jedes in der Query referenzierte Objekt nimmt Unity Catalog die passende Cloud-Credential an, die dieses Objekt regelt und von einem Cloud-Administrator bereitgestellt wird. Bei Managed Tables wäre das der mit dem Metastore verknüpfte Cloud-Storage. Bei Dateien oder External Tables wäre das eine External Location, die durch eine Storage Credential geregelt wird.
4. [KLICK] Wiederum für jedes in der Query referenzierte Objekt generiert Unity Catalog ein scoped, temporäres Token, das einem Client den direkten Zugriff auf die Daten aus dem Storage ermöglicht, und gibt dieses Token zusammen mit einer Zugriffs-URL zurück. So kann der Cluster bzw. das SQL Warehouse direkt, aber sicher auf Daten zugreifen.
5. [KLICK] Der Cluster bzw. das SQL Warehouse fordert die Daten mit der von Unity Catalog zurückgegebenen URL und dem Token direkt vom Cloud-Storage an.
6. [KLICK] Die Daten werden vom Cloud-Storage zurückübertragen. Dieser Anfrageprozess wird für jedes von der Query referenzierte Objekt wiederholt.
7. [KLICK] Mit Zugriff auf Daten auf Partitionsebene wird das „Last-Mile“-Filtern auf Zeilen- oder Spaltenbasis auf dem Cluster bzw. dem SQL Warehouse angewendet.
8. [KLICK] Schließlich wird das gefilterte Ergebnis an den Aufrufer zurückgegeben.

------

**Daten- und Workload-Isolation**

Eine weitere Möglichkeit, deine Daten zu isolieren, besteht darin, ein geeignetes Cluster-Profil und den Einsatz von Workspaces zu nutzen.

Hier haben wir eine Abbildung mit zwei Workspaces: Der erste hat zwei Cluster – einen für einen Single User, der an einem POC arbeitet, und einen mit Shared Access, damit dein Team an aktiven Projekten arbeiten kann. Der zweite Workspace hat einen SQL-Warehouse-Cluster, der die Zusammenarbeit über dein Team hinweg ermöglicht.

Isoliere einfach nach deinen Anforderungen

1. Single-User-Cluster bieten Datenschutz
2. Multi-User-Cluster, die Nutzer mit unterschiedlichen Berechtigungen sicher unterstützen, z. B. Shared Access Mode oder SQL Warehouses
3. Mehrere Workspaces isolieren Gruppen, die nicht zusammenarbeiten

![image-20260710093906918](../../../../assets/image-20260710093906918.png)

------

**Verschlüsselung standardmäßig**

Du kannst dich darauf verlassen, dass Databricks Verschlüsselungsmaßnahmen einsetzt, um Daten bei allen Übertragungen zu schützen:

- Data in transit: Der gesamte Datenverkehr zwischen Nutzern und der Control Plane, zwischen Control Plane und Compute Plane sowie zu AWS-APIs wird mit TLS/SSL-Protokollen verschlüsselt.
- Data at rest: AES-256-Verschlüsselung wird für Daten verwendet, die in Azure Storage und Amazon-EBS-Volumes gespeichert sind.
- Control-Plane-Daten: Es wird Envelope Encryption verwendet, bei der der Data Encryption Key (DEK) mit einem Customer-Managed Key (CMK) verschlüsselt und dann erneut mit einem von Databricks verwalteten Schlüssel verschlüsselt wird.

https://www.databricks.com/trust/security-features/data-protection-with-cus
tomer-managed-keys

![image-20260710094059703](../../../../assets/image-20260710094059703.png)

------

**Zugriff auf PII verwalten**

Auch wenn Databricks über umfangreiche Access Control Lists verfügt, ist das physische Trennen privater Daten in Storage-Container mit eingeschränktem Zugriff über die gesamte Organisation hinweg ein wichtiger zusätzlicher Schritt. Selbst wenn du dich für die Gewährung von Datenzugriff in Databricks nicht ausdrücklich auf das Cloud-Identity-and-Access-Management verlässt, ist es entscheidend, die Berechtigungen in der Cloud korrekt gesetzt zu haben.

Da Cluster und angehängte Storage-Volumes ephemer sind, bleiben zwischengespeicherte (cached) Daten nach Abschluss eines Jobs nicht erhalten. Wenn du personenbezogene Informationen speicherst, begrenzt das Entfernen natürlicher Schlüssel, die zur Nutzeridentität zurückführen könnten, die Anzahl der Stellen, an denen du Daten löschen musst, und stellt sicher, dass sie nicht mehr identifizierbar sind.

Wenn du Daten für Analysten verfügbar machst, können Views verwendet werden, um Spalten entweder dynamisch zu maskieren oder durch Aggregation zu de-identifizieren.

- Zugriff auf Speicherorte mit Cloud-Berechtigungen steuern
- Menschlichen Zugriff auf Rohdaten begrenzen
- Zeilen- und Spaltenfilterung in Unity Catalog
- Datensätze bei der Ingestion pseudonymisieren
- Table ACLs zur Verwaltung von Nutzerberechtigungen verwenden
- Dynamic Views für Datenschwärzung konfigurieren
- Identifizierende Details aus demografischen Views entfernen

------

**Neue Best Practices**

Gehen wir nun die neuen von Databricks empfohlenen „Best Practices“ durch:

1. Vermeide den direkten Zugriff auf Object Stores. Unity Catalog sollte jeglichen Datenzugriff vermitteln und einen umfassenden Audit-Trail aller Zugriffsanfragen führen. Dieser zentralisierte Ansatz sorgt für bessere Kontrolle und Sichtbarkeit des Datenzugriffs.
2. Minimiere die Verwendung von Keys: Weniger Keys im Umlauf verringern das Risiko von Sicherheitsverletzungen. Die zentralisierte Zugriffskontrolle von Unity Catalog macht mehrere Access Keys überflüssig.
3. Eliminiere Credentials in Code oder Secret Scopes: Mit Unity Catalog werden sensible Credentials nicht mehr in Code oder Secret Scopes gespeichert. Nutze stattdessen Databricks Secrets.
4. Migriere weg vom Hive Metastore: Hive Metastores gelten als weniger sicher. Alle neuen Daten-Assets sollten innerhalb von Unity Catalog erstellt und verwaltet werden.
5. Nutze für Modell-Assets Unity Catalog: Speichere alle Modell-Assets in Schemas in Unity Catalog statt in workspace-lokalen Model Registries. Dieser Ansatz bietet bessere Governance und Sharing-Möglichkeiten über Workspaces hinweg.
6. Vermeide die Nutzung von DBFS: Das Databricks File System (DBFS) sollte in Unity-Catalog-fähigen Workspaces vermieden werden. Nutze stattdessen Volumes, um unstrukturierte Daten wie Checkpoints, Bibliotheken und Konfigurationsdateien zu speichern.

![image-20260710094539241](../../../../assets/image-20260710094539241.png)

Hier ist ein Link zu weiteren Best Practices:

https://docs.databricks.com/en/data-governance/unity-catalog/best-practices.html

------

**Kunden-Use-Case – SEEK**

PII-Erkennung im großen Maßstab auf dem Lakehouse

![image-20260710094735858](../../../../assets/image-20260710094735858.png)

Hier haben wir einen Erfolgsfall von SEEK, Australiens größtem Online-Jobmarktplatz. Dieser Marktplatz verarbeitet Millionen von Lebensläufen mit sensiblen Bewerberinformationen.

- Ihr Ziel ist es, ein nahezu echtzeitfähiges Datenüberwachungssystem zu schaffen, das Lücken aufdeckt, Dashboards bereitstellt und Tickets für Data Custodians auslöst, um Probleme zu beheben.
- SEEK hat ein eigenes Framework auf Basis von HuggingFace-Transformern entwickelt, um PII sowohl in strukturierten als auch in unstrukturierten Daten zu erkennen und zu anonymisieren.
- Ihr PII-Erkennungsmodul umfasst:
  - Angepasste Recognizer für bestimmte Kontexte
  - Optical Character Recognition (OCR), um PII in hochgeladenen Dokumenten wie Pässen zu erkennen
  - Integration mit MLflow für Modell-Versionierung und API-Erstellung
  - Echtzeit-Warnungen, um zu verhindern, dass Nutzer sensible Informationen übermitteln
- Das System nutzt Unity Catalog für die Nachverfolgung der Data Lineage und die Durchsetzung der Zugriffskontrolle.

Ihr Ansatz zielt darauf ab, Data Governance von einem manuellen Prozess zu einem KI-gesteuerten, automatisierten System zu transformieren, das den Datenschutz und das Risikomanagement verbessert – schau sie dir also an.
