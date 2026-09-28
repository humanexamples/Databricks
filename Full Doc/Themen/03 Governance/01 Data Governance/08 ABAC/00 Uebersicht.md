# Attribute-Based Access Control (ABAC) — Überblick

ABAC ist ein Zugriffskontrollmodell in Unity Catalog, bei dem der Zugriff durch die Auswertung von **Attributen** schützbarer Objekte bestimmt wird — statt durch manuell auf einzelne Objekte vergebene Grants.

## Kernkomponenten

- **Governed Tags & Policies:** Attribute werden über Governed Tags dargestellt und über Policies umgesetzt, die auf Hierarchieebenen (Catalog, Schema, Tabelle) angehängt werden und dynamisch ausgewertet werden.
- **Unterstützte Policy-Typen:**
  - **Row-Filter-Policies**
  - **Column-Mask-Policies**
  - **GRANT-Policies** (Beta) — dynamische Privilegienvergabe

Diese gelten für Tabellen, Materialized Views und Streaming Tables.

## Themen in diesem Kapitel

1. Grundkonzepte (Tags, Policies, UDFs, Scope, Vererbung, Auswertung)
2. Policy-Erstellung und -Verwaltung (Catalog Explorer, SQL, REST-APIs)
3. GRANT-Policies
4. Policy-Auswertung und Audit-Logging
5. Häufige Filter- und Maskierungsmuster
6. Best-Practice-Empfehlungen
7. Performance-Eigenschaften
8. ABAC im Vergleich zu tabellenbezogenen Alternativen
9. Voraussetzungen, Kontingente und Einschränkungen

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/
