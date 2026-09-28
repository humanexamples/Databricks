# Managed vs. External Assets

Unity Catalog registriert alle schützbaren Objekte mit zentralisierter Governance. Für Datenobjekte (Tabellen und Volumes) gibt es zwei Betriebsmodelle:

- **Managed Assets:** Unity Catalog steuert sowohl die Governance-Protokolle als auch den Lebenszyklus der zugrunde liegenden Dateien.
- **External Assets:** Unity Catalog übernimmt nur die Governance — Speicherort und Lebenszyklus bleiben in der Verantwortung des Nutzers bzw. externer Systeme.

Wichtig laut Doku: *"Bei der Registrierung eines Managed Asset behalten Sie die volle Eigentümerschaft an Ihren Daten — die Datendateien verbleiben immer in Ihrem Cloud-Account."*

## Vergleich

| Eigenschaft | Managed | External |
|---|---|---|
| Speicherort | Von Unity Catalog festgelegt (im eigenen Cloud-Account) | Vom Nutzer festgelegt |
| Datei-Lebenszyklus | Von Unity Catalog verwaltet (Optimierung, Organisation, Löschung) | Vom Nutzer verwaltet |
| Verhalten bei `DROP` | Datendateien werden nach 8-tägiger Aufbewahrungsfrist endgültig gelöscht | Datendateien bleiben unverändert bestehen |
| Dateneigentümerschaft | Ja | Ja |

## Geltungsbereich

Diese Unterscheidung gilt **ausschließlich für Tabellen und Volumes**. Andere schützbare Objekte wie Views, Modelle und Funktionen haben keine Managed-/External-Varianten.

## Begriffsklärung

Der Begriff "managed" wird in der Unity-Catalog-Doku mit unterschiedlichen Bedeutungen verwendet — Governance-Zugriffskontrolle, Festlegung des Speicherorts, Steuerung des Datenlebenszyklus, oder ein konkretes Privileg. Der jeweilige Kontext entscheidet über die genaue Bedeutung.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/managed-versus-external
