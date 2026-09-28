# Datenzugriff für die Ingestion konfigurieren

Diese Seite richtet sich an Administratoren und beschreibt, wie der Zugriff auf Daten in einem Amazon-S3-Bucket eingerichtet wird, damit Databricks-Nutzer diese Daten mit `COPY INTO` in Tabellen laden können.

## Empfohlene Methoden

1. Unity-Catalog-Volume (empfohlener Weg)
2. Unity-Catalog External Location mit Storage Credential
3. AWS Instance Profile auf Compute-Ressourcen
4. Temporäre AWS-Zugangsdaten

## Voraussetzungen

- Daten in einem S3-Bucket im eigenen AWS-Konto
- Passende Berechtigungen: `READ VOLUME` für Volumes bzw. `READ FILES` für External Locations
- Workspace-Admin-Rechte für die Konfiguration eines Instance Profile
- Ein Databricks-SQL-Warehouse
- Grundkenntnisse der Databricks-SQL-Oberfläche

## Konfiguration

Für jede der vier Methoden existiert eine eigene, detaillierte Anleitung. Databricks empfiehlt: Erstellen Sie ein Unity-Catalog-Volume als bevorzugten Weg.

## Bereinigung

Nach Abschluss der Übungen können folgende Ressourcen entfernt werden:

- AWS-CLI Named Profiles
- IAM-Benutzer und -Policies
- S3-Buckets
- SQL-Warehouses (um unnötige Kosten zu vermeiden)

## Nächste Schritte

Nach der Konfiguration lässt sich `COPY INTO` verwenden, um Daten aus S3 nach Databricks zu laden. Für jede Zugriffsmethode existiert eine eigene Anleitung.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/configure-data-access  
**Stand:** 2026-08-07
