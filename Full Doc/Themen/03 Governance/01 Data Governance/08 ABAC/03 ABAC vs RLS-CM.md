# ABAC vs. tabellenbezogene Row Filter/Column Masks

## Grundunterschied

**Tabellenbezogene Row Filter/Column Masks** wenden Sensibilitätskontrollen direkt auf einzelne Tabellen an, über `ALTER TABLE`. **ABAC-Policies** werden auf Catalog-, Schema- oder Tabellenebene angehängt und matchen Tabellen/Spalten dynamisch anhand von Governed Tags.

## Vergleich

| Aspekt | ABAC | Tabellenbezogen |
|---|---|---|
| **Scope/Skalierung** | Gilt für alle Tabellen im Policy-Scope; neue getaggte Tabellen automatisch erfasst | Einzeln konfiguriert; jede Tabelle braucht eigenes Setup |
| **Dynamisches Matching** | Über `has_tag()` / `has_tag_value()` | Kein dynamisches Matching — Filter/Masken sind fest an bestimmte Tabellen gebunden |
| **Governance-Kontrolle** | Catalog-/Schema-Eigentümer setzen Policies durch; Tabelleneigentümer können nicht übersteuern | Tabelleneigentümer verwalten direkt und können Einschränkungen ändern/entfernen |
| **Syntax** | `CREATE POLICY ... ON CATALOG/SCHEMA/TABLE` | `ALTER TABLE ... SET ROW FILTER` / `ALTER TABLE ... ALTER COLUMN ... SET MASK` |

## Wann was verwenden?

**ABAC wählen, wenn:** organisationsweite Konsistenz über viele Tabellen benötigt wird, der Datenbestand wächst, und eine Aufgabentrennung zwischen Policy-Autoren und Data Stewards besteht.

**Tabellenbezogene Filter/Masken wählen, wenn:** einzelne Tabellen spezifische, nicht verallgemeinerbare Logik benötigen, Tabelleneigentümer die Einschränkungen direkt verwalten sollen, oder die Tabellenmenge klein und stabil ist.

## Koexistenz

Beide Ansätze können auf derselben Tabelle wirken — pro Spalte darf zur Laufzeit aber nur **ein** eindeutiger Row Filter und **eine** eindeutige Column Mask gelten. Werden unterschiedliche Funktionen verwendet, entsteht ein Konflikt.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/abac-vs-rls-cm
