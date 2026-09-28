# Multi-Domain Column Masking mit Sensitivitätsstufen

Kombiniert domänenbewusste Column-Masks mit regionsbasierter Row-Filterung — über zwei zusammenwirkende Governed Tags.

## Zwei Tags im Zusammenspiel

- **`domain`** — welches Team eine Spalte besitzt (`hr`, `finance`, `marketing`).
- **`sensitivity`** — Maskierungsintensität (`internal`, `confidential`).

Jede Spalte trägt genau einen `domain`-Wert und einen `sensitivity`-Wert — dadurch trifft pro Nutzer genau **eine** Policy auf jede Spalte zu.

## Ablauf

1. **Governed Tags erstellen:** `region` (nur Schlüssel), `domain` (drei Werte), `sensitivity` (zwei Werte).
2. **Beispieldaten:** Tabelle `employee_records` mit Spalten aus HR, Finance und Marketing.
3. **Tags anwenden:** jede sensible Spalte erhält sowohl `domain`- als auch `sensitivity`-Tag — z. B. die SSN-Spalte: `domain='hr'`, `sensitivity='confidential'`.
4. **UDFs erstellen:**
   - `region_filter()` — vergleicht die Region der Zeile.
   - `partial_mask()` — liefert ersten Buchstaben plus `***`.
   - `redact()` — liefert `***REDACTED***`.
5. **Policies erstellen:** sechs Column-Mask-Policies (eine je Domain-Sensitivity-Kombination) und zwei Row-Filter-Policies, die die UDFs über `AND`-Bedingungen in `MATCH COLUMNS` auf getaggte Spalten anwenden.

## Durchsetzungsmuster über `EXCEPT`

Der zentrale Mechanismus: Jede Policy zielt auf "alle Account-Nutzer" **außer** die jeweils zuständige Domain-Gruppe. Nutzer, die mehreren Domain-Gruppen angehören, sehen dadurch automatisch die unmaskierten Daten aller ihrer Domänen, während alle anderen die entsprechend der Sensitivitätsstufe maskierten Werte sehen.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/multi-domain
