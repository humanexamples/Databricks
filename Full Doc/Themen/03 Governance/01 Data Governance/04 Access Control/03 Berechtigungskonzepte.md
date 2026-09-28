# Berechtigungskonzepte

## Securable Objects

Unity Catalog organisiert Daten in einem hierarchischen dreistufigen Namespace: `catalog`.`schema`.`tabelle`. Jede Ebene ist ein eigenes schützbares Objekt, auf dem Zugriffskontrolle greift.

![Unity-Catalog-Objekthierarchie](images/object-hierarchy.png)

## Container-Objekte

Catalogs und Schemas sind Container-Objekte, die Kindobjekte enthalten:

- Auf Containern vergebene Privilegien gelten automatisch für alle aktuellen und künftigen Kindobjekte.
- Der Zugriff auf Kindobjekte erfordert die passenden `USE CATALOG`- bzw. `USE SCHEMA`-Privilegien auf den übergeordneten Containern.
- Container-Eigentümer können alle Kindobjekte automatisch verwalten.

## Wichtige Privilegien im Überblick

| Privileg | Bedeutung |
|---|---|
| `SELECT` | Lesezugriff auf Tabellen/Views |
| `MODIFY` | Schreibzugriff auf Tabellen |
| `USE CATALOG` / `USE SCHEMA` | Navigationsrechte, erforderlich für den Zugriff auf Kindobjekte |
| `CREATE TABLE` / `CREATE SCHEMA` | Rechte zur Objekterstellung |
| `MANAGE` | Volle Kontrolle inkl. Privilegienverwaltung und Übertragung der Eigentümerschaft |
| `BROWSE` | Metadaten-Entdeckung ohne Datenzugriff |

Für die meisten Operationen sind Privilegien auf mehreren Hierarchieebenen nötig — z. B. benötigt man für die meisten Operationen auf Tabellen, Views, Volumes oder Funktionen: `USE CATALOG` auf dem übergeordneten Catalog, `USE SCHEMA` auf dem übergeordneten Schema **und** das jeweilige Operationsprivileg selbst.

**Kontrollgrenze für Catalog-/Schema-Owner:** `USE CATALOG` bildet eine wichtige Zugriffskontrollgrenze. Selbst wenn ein Table-Owner einem Nutzer `SELECT` auf einer Table gewährt, bleibt der Zugriff wirkungslos, solange dieser Nutzer nicht zusätzlich `USE CATALOG` auf dem übergeordneten Catalog (und analog `USE SCHEMA` auf dem Schema) besitzt. Da nur Catalog- bzw. Schema-Owner (oder Inhaber von `MANAGE`) diese Usage-Privilegien vergeben können, behalten sie so die Kontrolle darüber, wer tatsächlich auf ihre Objekte zugreifen kann — unabhängig davon, was einzelne Table-Owner großzügig vergeben.

**Ausnahme `BROWSE`:** Wer stattdessen `BROWSE` auf dem Catalog bzw. Schema besitzt, kann Objekte entdecken und Metadaten einsehen, ganz ohne `USE CATALOG`/`USE SCHEMA`. `BROWSE` gewährt aber keinen Datenzugriff, nur Metadaten-Sichtbarkeit und die Möglichkeit, Zugriff anzufragen.

## Eigentümerschaft (Ownership)

Jedes schützbare Objekt hat genau einen Eigentümer (Nutzer, Service Principal oder Gruppe). Eigentümer besitzen automatisch alle Fähigkeiten auf ihrem Objekt und können Kindobjekte verwalten — benötigen dafür aber explizite Grants auf diesen Kindobjekten.

**Wichtige Unterscheidung:** Eigentümerschaft vererbt sich **nicht** nach unten an Kindobjekte. Eigentümer erhalten jedoch automatisch `MANAGE`-Fähigkeiten auf alle Kindobjekte, ohne dass explizite Grants nötig sind.

## Privilegien-Vererbung

Auf einem übergeordneten Objekt vergebene Privilegien kaskadieren automatisch an alle aktuellen und künftigen Kindobjekte. **Ausnahme:** Grants auf Metastore-Ebene vererben sich nicht — sie steuern stattdessen Operationen mit Metastore-Geltungsbereich, z. B. `CREATE CATALOG`.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts
