# Tabellen in Databricks – Übersicht

Databricks unterstützt mehrere Tabellentypen und Speicherformate. Diese Seite gibt einen Überblick über alle Möglichkeiten.

## Tabellentypen

Databricks kennt vier Haupttypen von Tabellen:

- **Unity Catalog Managed Tables** für Delta Lake und Apache Iceberg. Databricks verwaltet hier Daten und Metadaten vollständig.
- **Temporäre Tabellen** in Databricks SQL und im Databricks Runtime. Sie existieren nur innerhalb einer Sitzung.
- **External Tables** (externe Tabellen). Die Daten liegen in externem Cloud-Speicher.
- **Foreign Tables** (Fremdtabellen). Der Zugriff erfolgt über Lakehouse Federation auf externe Systeme.

## Speicherformate

Databricks unterstützt zwei offene Tabellen-Speicherformate:

- **Delta Lake**: das Standardformat. Es bietet ACID-Transaktionen, Time Travel und Schema-Durchsetzung.
- **Apache Iceberg**: ein Open-Source-Format mit erweitertem Metadaten-Management.

## Tabellenverwaltung

Zur Verwaltung von Tabellen gehören folgende Themen:

- Tabelleneinschränkungen (Constraints)
- Schema-Durchsetzung
- Tabellen-Partitionierung
- Speicherüberwachung
- Migration von externen zu verwalteten Tabellen
- Externe Partitionserkennung

## Einordnung dieser Seite

Diese Seite ist eine reine Übersichtsseite. Sie enthält keine eigenen Code-Beispiele. Details zu den einzelnen Tabellentypen finden sich auf den jeweiligen Unterseiten dieses Kursordners.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/  
**Stand:** 2026-08-06
