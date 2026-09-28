# Data Governance mit Unity Catalog

Unity Catalog ist die **einheitliche Governance-Schicht für Daten und KI** in Databricks. Sie ermöglicht es, Zugriff zu kontrollieren, Assets zu entdecken, Lineage nachzuverfolgen, sensible Daten zu klassifizieren und Datenqualität zu überwachen.

Unity Catalog verwaltet dabei nicht nur Tabellen und Volumes, sondern auch Modelle, Funktionen und andere KI-Assets als "securable objects" (schützbare Objekte). KI-Laufzeit-Governance (z. B. AI Gateway) und Sicherheitsthemen wie Authentifizierung/Verschlüsselung werden in eigenen Doku-Bereichen behandelt.

## Einstieg

Drei grundlegende Ressourcen werden empfohlen:

1. **Was ist Unity Catalog?** — Objektmodell und Governance-Ansatz
2. **Erste Schritte mit Unity Catalog** — Einrichtung und erste Assets
3. **Unity-Catalog-Best-Practices** — empfohlene Konfiguration und Verwaltung

## Governance-Fähigkeiten im Überblick

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

## Quelle

- https://docs.databricks.com/aws/en/data-governance/
