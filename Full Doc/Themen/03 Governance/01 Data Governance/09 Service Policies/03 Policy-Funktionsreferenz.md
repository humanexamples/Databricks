# Service-Policy-Funktionsreferenz

Service Policies sind SQL-UDFs in Unity Catalog mit fester Signatur:

```sql
CREATE OR REPLACE FUNCTION <catalog>.<schema>.<function_name>(
  event VARIANT
)
RETURNS VARIANT
LANGUAGE SQL
RETURN <expression>;
```

Ausgewertet wird in zwei Phasen: `'request'` (`ON CALL`, vor dem Service-Aufruf) und `'response'` (`ON RESULT`, nach der Antwort).

## Felder des `event`-Parameters

| Feld | Gilt für | Zweck |
|---|---|---|
| `event:type` | Alle | `'request'` oder `'response'` |
| `event:target` | Alle | Vollständiger Unity-Catalog-Name des angehängten Service |
| `event:context.actor.run_as` | Alle | Run-As-Identität zur Autorisierung |
| `event:context.actor.context.is_on_behalf_of` | Alle | `true`, wenn Agent/App im Namen des Nutzers handelt |
| `event:context.actor.context.client_id` | Alle | OAuth-Client-ID der handelnden Identität |
| `event:context.actor.context.actor_resource` | Alle | Ressource der handelnden Identität (z. B. Agent) |
| `event:context.actor.context.is_actor_authenticated` | Alle | `true` bei Confidential-Client-Authentifizierung |
| `event:context.tool.name`, `event:context.tool.arguments` | MCP Services | Name und Argumente des aufgerufenen Tools |
| `event:context.message` | Model/Provider Services | Extrahierte letzte Nutzer-/Assistant-Nachricht |
| `event:data` | Model/Provider Services | Vollständiges Request- oder Response-Payload |
| `event:request_data` | Model/Provider Services | Ursprüngliches Request (verfügbar bei `ON RESULT`) |

## Rückgabewert

Funktionen liefern ein `VARIANT` mit Pflichtfeld `result` und optionalem `reason`:

```sql
to_variant_object(named_struct('result', 'DENY', 'reason', 'GitHub push operations are not permitted by policy.'))
```

**Mögliche `result`-Werte:** `ALLOW`, `DENY`, `ASK`.

Alternative Umschlagform:

```sql
to_variant_object(named_struct('decision', named_struct('result', 'DENY', 'reason', '...')))
```

## Unterstützte SQL-Funktionen und Operatoren

| Kategorie | Funktionen/Operatoren |
|---|---|
| Operatoren | Vergleich, logisch, arithmetisch; `\|\|`, `IN`, `LIKE`, `IS [NOT] NULL` |
| Kontrollfluss | `CASE`, `IF` |
| Casts | `INT`, `BIGINT`, `DOUBLE`, `FLOAT`, `STRING`, `BOOLEAN` (`CAST` oder `::`) |
| String-Funktionen | `CONCAT`, `LENGTH`, `CHAR_LENGTH`, `UPPER`, `LOWER`, `SUBSTRING`, `TRIM`, `LTRIM`, `RTRIM`, `REPLACE`, `STARTSWITH`, `ENDSWITH`, `CONTAINS` |
| Sonstige | `COALESCE`, `NULLIF`, `IFNULL`, `NVL`, `ABS`, `MOD`, `ISNULL`, `ISNOTNULL`, `NAMED_STRUCT`, `TO_VARIANT_OBJECT` |

**Nicht unterstützt:** `ai_query`, Subqueries, `BETWEEN`, Aggregatfunktionen, Lambdas/`EXISTS`, variadische Funktionen.

## Wichtige Hinweise

- Variant-Pfadzugriffe vor dem Vergleich auf skalare Typen casten: `event:type::string = 'request'`.
- Fehlende Felder lösen Fehler aus (Fail-Closed zu `DENY`).
- Databricks transpiliert Policy-Bodies zur Laufzeit nach CEL.
- Nicht unterstützte Konstrukte führen zur Ablehnung beim Anhängen der Policy.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/service-policies/policy-function-reference
