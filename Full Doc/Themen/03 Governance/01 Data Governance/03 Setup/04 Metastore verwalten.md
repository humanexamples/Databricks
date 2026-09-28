# Metastore verwalten

## Automatische Workspace-Zuweisung

Account-Admins können die automatische Metastore-Zuweisung für neu erstellte Workspaces derselben Region aktivieren. Dabei werden automatisch Workspace-Catalogs erstellt und Nutzern die nötigen Privilegien zur Objekterstellung erteilt.

## Managed Storage hinzufügen

Speicher auf Metastore-Ebene lässt sich in drei Schritten ergänzen:

1. Einen S3-Bucket in derselben Region wie der Metastore anlegen.
2. Eine External Location in Unity Catalog einrichten — per AWS Quickstart (empfohlen) oder manuell.
3. Den Speicherpfad als Account-Administrator zur Metastore-Konfiguration hinzufügen.

**Voraussetzung:** Mindestens ein Workspace muss bereits an den Unity-Catalog-Metastore angebunden sein.

## Speicher entfernen

Wird Speicher auf Metastore-Ebene entfernt, erhalten bestehende Catalogs ohne eigenen Speicher-Root den Cloud-Speicherort des Metastore. Dabei kann automatisch eine neue External Location namens `prior_metastore_root_location` entstehen.

## Weitere Admin-Aufgaben

- **Metastore-Admins zuweisen** — für die Zugriffsverwaltung über Workspaces hinweg.
- **Metastore löschen** — unumkehrbare Aktion, die alle verwalteten Objekte betrifft; Daten von External Tables bleiben erhalten.

**Wichtig:** Managed-Table-Daten und -Metadaten benötigen nach dem Löschen eines Metastore 30 Tage, bevor sie automatisch entfernt werden.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-metastore
