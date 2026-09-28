# ABAC — Voraussetzungen, Kontingente, Einschränkungen

## Compute-Anforderungen

Eine der folgenden Konfigurationen ist nötig:

- Serverless Compute
- Standard Compute mit Databricks Runtime 16.4+
- Dedicated Compute mit Databricks Runtime 16.4+ und aktivierter feingranularer Zugriffskontroll-Filterung

Standard- und Dedicated Compute mit Runtime-Versionen vor 16.4 können **nicht** auf ABAC-geschützte Tabellen zugreifen.

## Governed Tags erforderlich

ABAC-Policies benötigen **Governed Tags** (keine ungoverned Tags). Diese werden auf Account-Ebene definiert, mit eigenen Zugriffskontrollen dafür, wer sie erstellen, zuweisen und verwalten darf. Nach dem Zuweisen oder Ändern eines Tags kann es einige Minuten dauern, bis die Änderung wirksam wird.

## Kontingente

| Ressource | Limit |
|---|---|
| Policies pro Metastore | 10.000 |
| Policies pro Catalog oder Schema | 100 |
| Policies pro Tabelle | 50 |
| Principals pro Policy (`TO`- und `EXCEPT`-Klauseln zusammen) | 20 |
| Spaltenbedingungen pro `MATCH COLUMNS`-Klausel | 3 |

## Wichtige Einschränkungen

- **Views:** ABAC-Policies lassen sich nicht direkt auf Views anwenden. Fragt ein Nutzer jedoch eine View ab, die auf Tabellen mit ABAC-Policies verweist, werden diese Policies dennoch berücksichtigt.
- **Time Travel & Cloning:** ABAC-Policies lassen sich nicht gegen historische Snapshots auswerten — diese Operationen schlagen auf geschützten Tabellen fehl.
- **Materialized Views/Streaming Tables:** Policies werden mit der Identität des Pipeline-Eigentümers ausgewertet — das kann Daten dauerhaft maskieren.
- **Mehrere Policies:** Pro Tabelle und Nutzer kann sich zur Laufzeit nur **ein** eindeutiger Row Filter auflösen, um Konflikte zu vermeiden.
- **AI-Search-Indizes:** ABAC-Policies auf Quelltabellen gelten nicht für daraus erzeugte Indizes.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/requirements
