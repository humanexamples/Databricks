# ABAC — Best Practices

Acht zentrale Empfehlungen für den produktiven Einsatz von ABAC-Policies.

## 1. Attribute und Namensgebung standardisieren

Eine konsistente Tag-Taxonomie teamübergreifend etablieren. Statt überlappender Tags: ein einziges kontrolliertes Set — z. B. ein `sensitivity`-Tag mit Werten wie `public`, `internal`, `confidential`, `restricted`.

## 2. Kontrollieren, wer Tags setzen darf

**Tagging ist eine Sicherheitsgrenze in ABAC.** Das Erstellen und Ändern von Tags über die Governed-Tags-Konfiguration auf autorisierte Data Stewards oder Governance-Admins beschränken. Tag-Änderungen regelmäßig über System-Tabellen auditieren.

## 3. Fallback-Regeln für unklassifizierte Daten festlegen

Neuen Objekten standardmäßig restriktive Tags zuweisen (z. B. `classification:unverified`), bis sie geprüft wurden. Policies erstellen, die den Zugriff auf ungetaggte oder ungeprüfte Objekte einschränken.

## 4. Policies auf dem höchstmöglichen Scope definieren

Policies möglichst auf Catalog- oder Schema-Ebene statt auf Tabellenebene anhängen — dadurch erhalten neue Tabellen automatisch die passenden bestehenden Policies anhand ihrer Tags.

## 5. Policy Sprawl vermeiden

**ABAC ist darauf ausgelegt, die Anzahl an Zugriffsregeln zu reduzieren, nicht zu erhöhen.** Mit breiten Policies beginnen statt separater Regeln für Randfälle. Überlappende Policies regelmäßig überprüfen und konsolidieren.

## 6. Direkte Grants und ABAC-GRANT-Policies gemeinsam auditieren

Die effektiven Privilegien eines Nutzers ergeben sich aus direkten Grants **und** ABAC-GRANT-Policies — beide Quellen gemeinsam prüfen, um unbeabsichtigte Berechtigungen zu vermeiden.

## 7. `TO`/`EXCEPT` für Principal-Zuordnung bevorzugen

Die Klauseln `TO` und `EXCEPT` einer Policy nutzen, um zutreffende Nutzer/Gruppen festzulegen — die UDF-Logik selbst einfach halten.

## 8. Dynamische Policy-Auswertung einplanen

`SHOW EFFECTIVE POLICIES` nutzen, um zu verstehen, was auf eine konkrete Tabelle zutrifft, und das eigene Governance-Modell klar dokumentieren.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/best-practices
