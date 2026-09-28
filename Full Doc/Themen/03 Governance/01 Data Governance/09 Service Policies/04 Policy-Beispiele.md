# Service-Policy-Beispiele

Zwei Kategorien von Policies: **deterministische SQL-Policies** (regelbasierte, exakte Entscheidung) und **LLM-as-a-Judge-Policies** (ein Bewertungsmodell wendet eine natürlichsprachliche Klassifikation an).

## Deterministische SQL-Policies

**Anfragen mit bestimmten Schlüsselwörtern blockieren** (z. B. interne Codenamen):

```sql
CREATE OR REPLACE FUNCTION main.governance.block_codenames(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'request'
      AND (CONTAINS(LOWER(event:context.message::string), 'projectfalcon')
        OR CONTAINS(LOWER(event:context.message::string), 'bluewidget')
        OR CONTAINS(LOWER(event:context.message::string), 'codename-atlas'))
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', 'Your request references a restricted internal or competitor codename.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Anfragen zu eingeschränkten Themen blockieren:**

```sql
CREATE OR REPLACE FUNCTION main.governance.deny_restricted_topics(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'request'
      AND (CONTAINS(LOWER(event:context.message::string), 'lawsuit')
        OR CONTAINS(LOWER(event:context.message::string), 'legal advice')
        OR CONTAINS(LOWER(event:context.message::string), 'investment advice'))
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', 'This assistant does not handle legal or investment topics.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Prompt-Länge begrenzen:**

```sql
CREATE OR REPLACE FUNCTION main.governance.deny_oversized_prompt(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'request'
      AND LENGTH(event:context.message::string) > 8000
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', 'Your prompt exceeds the 8000-character limit for this service.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Freigabe verlangen, wenn ein Agent im Namen des Nutzers handelt:**

```sql
CREATE OR REPLACE FUNCTION main.governance.ask_when_agent_writes(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'request'
      AND event:context.actor.context.is_on_behalf_of::boolean = true
      AND event:context.tool.name::string IN ('create_issue', 'push_files', 'merge_pull_request')
    THEN to_variant_object(named_struct('result', 'ASK', 'reason', 'An agent is attempting a write action on your behalf. Please confirm.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Antworten mit internen URLs blockieren:**

```sql
CREATE OR REPLACE FUNCTION main.governance.block_internal_links_in_response(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'response'
      AND (CONTAINS(LOWER(event:context.message::string), 'wiki.internal.example.com')
        OR CONTAINS(LOWER(event:context.message::string), 'admin.example.com'))
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', 'The response was blocked because it referenced an internal-only URL.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Tool-Aufrufe anhand von Argumenten blockieren:**

```sql
CREATE OR REPLACE FUNCTION main.governance.block_protected_repo(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'request'
      AND event:context.tool.arguments.repo::string = 'prod-infra'
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', 'Actions on the prod-infra repository are not permitted through the agent.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Nur genehmigte Tools erlauben (Allowlist):**

```sql
CREATE OR REPLACE FUNCTION main.governance.tool_allowlist(event VARIANT)
RETURNS VARIANT
LANGUAGE SQL
RETURN CASE
    WHEN event:type::string = 'request'
      AND event:context.tool.name::string NOT IN ('search_issues', 'get_file_contents', 'list_commits')
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', CONCAT('Tool is not on the approved allowlist for this service: ', event:context.tool.name::string)))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

## LLM-as-a-Judge-Policies

Diese Policies nutzen natürlichsprachliche Prompts, die von einem LLM ausgewertet werden:

- **Assistenten beim Thema halten:** *"Flag the message if it asks for something outside [Produkte, Bestellungen, Abrechnung, Account-Support], such as general coding help, writing essays, unrelated trivia, or using the assistant as a general-purpose chatbot."*
- **Professionellen Ton erzwingen:** *"Flag the response if it is rude, sarcastic, dismissive, condescending, uses profanity, or would embarrass the company if a customer saw it."*
- **Regulierte Beratung blockieren:** *"Flag the response if it provides individualized investment, tax, or legal advice, or a specific recommendation to a person."*

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/service-policies/policy-examples
