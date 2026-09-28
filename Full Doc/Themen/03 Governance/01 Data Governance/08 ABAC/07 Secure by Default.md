# Neue Tabellen standardmäßig absichern (Secure by Default)

Muster, um neue Tabellen automatisch zu sperren, bis Data Stewards ihren Inhalt geprüft haben — mittels eines **Control Tags** auf Schema-Ebene.

## Grundidee

Ein Schema-Level-Tag `review_status` mit den erlaubten Werten `pending` und `reviewed`. Jede neue Tabelle im Schema erbt dieses Tag automatisch — ganz ohne zusätzliche Konfiguration pro Tabelle.

## Voraussetzungen

- Databricks Runtime 16.4+ oder Serverless Compute.
- Account-/Workspace-Admin-Rechte, `MANAGE` auf Ziel-Catalog/-Schema.

## Ablauf

1. **Data Classification** auf dem Catalog aktivieren.
2. Governed Tag `review_status` erstellen.
3. Tag mit Wert `pending` auf das Schema anwenden.
4. **Pending-Policy:** eine Column-Mask-Policy, die `system.data_classification.mask_value` auf **jede** Spalte anwendet — unabhängig vom Tag — solange `review_status = pending` gilt.
5. Eine Beispieltabelle (z. B. Mitarbeiterverzeichnis) wird angelegt und erbt automatisch den `pending`-Status → alle Spalten erscheinen maskiert.
6. **Data-Classification-Scan** erkennt sensible Spalten automatisch und vergibt `class.*`-System-Tags (z. B. `class.us_ssn`, `class.email_address`).
7. **Reviewed-Policy:** eine zweite Policy maskiert nur noch `class.*`-getaggte Spalten, sofern `review_status = reviewed` gilt.
8. Nach Prüfung durch einen Data Steward wird das Tabellen-Tag auf `reviewed` gesetzt — das überschreibt das vom Schema geerbte Tag, und nicht-klassifizierte Spalten werden wieder sichtbar.
9. Neue Tabellen im selben Schema erben automatisch wieder den `pending`-Status, ganz ohne zusätzliche Konfiguration.

## Eingebaute Maskierungsfunktion

`system.data_classification.mask_value` maskiert typgerecht: `0` für Integer, `DATE '1970-01-01'` für Datumswerte, SHA-256-Hashes für Strings.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/secure-by-default
