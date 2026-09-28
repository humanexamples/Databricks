# ABAC GRANT-Policies (Beta)

GRANT-Policies vergeben Unity-Catalog-Privilegien **dynamisch** anhand passender Governed Tags — statt über feste Grants pro Objekt.

## Scope und Geltungsbereich

- Werden nur an **Catalogs oder Schemas** angehängt, nicht an Einzelobjekte.
- Vergeben Privilegien für die Objekttypen `MODEL`, `MODEL_SERVICE`, `MODEL_PROVIDER_SERVICE`, `MCP_SERVICE`, `AGENT_SERVICE`.
- Unterstützte Privilegien je Objekttyp: `APPLY_TAG`, `EXECUTE`, `READ_METADATA`.

## `CREATE POLICY`-Syntax

```sql
CREATE [OR REPLACE] POLICY policy_name
ON { CATALOG catalog_name | SCHEMA schema_name }
[COMMENT description]
TO principal [, ...]
[EXCEPT principal [, ...]]
GRANT privilege [, ...] FOR MODELS
[WHEN condition]
```

## Beispiele

```sql
CREATE POLICY grant_production_model_access
ON SCHEMA production.ml_models
COMMENT 'Grant EXECUTE on production MLflow models'
TO `analysts`
GRANT EXECUTE FOR MODELS
WHEN has_tag_value('lifecycle', 'production');
```

```sql
CREATE POLICY grant_anthropic_foundation_models
ON SCHEMA system.ai
COMMENT 'Grant EXECUTE on Anthropic foundation models'
TO `data_scientists`
EXCEPT `contractors`
GRANT EXECUTE FOR MODELS
WHEN has_tag_value('ai.model_creator', 'anthropic');
```

## Zugriffslogik

Die effektiven Privilegien sind die **Vereinigung** aus direkten Grants und zutreffenden GRANT-Policies. Ein Principal erhält Zugriff, wenn eine der Bedingungen gilt:

- eine GRANT-Policy listet ihn in `TO` (und nicht in `EXCEPT`) und die Tag-Bedingung trifft zu, **oder**
- ein direkter `GRANT` existiert auf Objekt, Schema oder Catalog.

## Verwaltung

```sql
SHOW [EFFECTIVE] POLICIES ON { CATALOG | SCHEMA } securable_name;
DESCRIBE POLICY policy_name ON { CATALOG | SCHEMA } securable_name;
DROP POLICY IF EXISTS policy_name ON SCHEMA schema_name;
```

## System-Tags für Foundation-Modelle

Modelle in `system.ai` tragen vorab Tags wie `ai.model_creator` (z. B. `anthropic`, `openai`, `google`, `meta`) und `ai.model_family` (z. B. `claude-opus`, `gpt`, `gemini`, `qwen`).

## Wichtige Einschränkungen

- `CREATE MODEL` und `CREATE MODEL_VERSION` werden nicht unterstützt.
- `USE CATALOG`/`USE SCHEMA` bleiben als Voraussetzung direkte Grants.
- `ALL_PRIVILEGES`, `MANAGE`, `MODIFY` werden nicht unterstützt.
- SQL-Erstellung ist auf Modelle beschränkt — für andere Typen Catalog Explorer oder REST-API nutzen.
- `SHOW GRANTS` zeigt policy-vergebene Privilegien **nicht** an.
- Delta Sharing ist mit GRANT-Policies auf Modellen nicht kompatibel.

## Best Practices

- Gruppen statt Einzelnutzer in `TO`/`EXCEPT` verwenden.
- Policies auf dem engstmöglichen Scope anhängen, der die Ziele abdeckt.
- GRANT-Policies von direkten Grants für dasselbe Privileg trennen.
- Direkte Grants nur für die Voraussetzungen `USE CATALOG`/`USE SCHEMA` reservieren.

## Voraussetzung

SQL-Operationen erfordern klassisches Compute mit Databricks Runtime 18 LTS oder höher.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/grant-policies
