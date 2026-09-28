# Service Policy erstellen und anhängen

## Voraussetzungen

- Beta muss vom Account-Admin über die Account-Console-Seite **Previews** aktiviert werden.
- `CREATE FUNCTION`-Privileg auf dem Zielschema.
- `MANAGE` auf dem Service-Objekt und `EXECUTE` auf der Policy-Funktion.

## Schritt 1: Policy-Funktion schreiben

Policy-Funktionen sind SQL-UDFs in Unity Catalog mit folgender Struktur:

```sql
CREATE OR REPLACE FUNCTION <catalog>.<schema>.<function_name>(
  event VARIANT
)
RETURNS VARIANT
LANGUAGE SQL
RETURN <expression>;
```

Die Funktion unterscheidet über `event:type::string` ('request' oder 'response'), auf welche Phase sie zielt.

**Beispiel — GitHub-Push-Operationen blockieren:**

```sql
CREATE OR REPLACE FUNCTION main.governance.block_github_push(
  event VARIANT
)
RETURNS VARIANT
LANGUAGE SQL
RETURN
  CASE
    WHEN event:type::string = 'request'
      AND event:context.tool.name::string = 'push_files'
    THEN to_variant_object(named_struct('result', 'DENY', 'reason', 'GitHub push operations are not permitted by policy.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

**Beispiel — Freigabe vor destruktiven Operationen verlangen:**

```sql
CREATE OR REPLACE FUNCTION main.governance.ask_before_repo_delete(
  event VARIANT
)
RETURNS VARIANT
LANGUAGE SQL
RETURN
  CASE
    WHEN event:context.tool.name::string = 'delete_repository'
    THEN to_variant_object(named_struct('result', 'ASK', 'reason', 'Deleting a repository requires human approval.'))
    ELSE to_variant_object(named_struct('result', 'ALLOW', 'reason', ''))
  END;
```

## Schritt 2: Über Unity AI Gateway UI anhängen

1. Im Workspace-Menü zu **AI Gateway** navigieren.
2. Service auswählen (Tabs **Models**, **Providers** oder **MCPs**).
3. Tab **Policies** öffnen → **New policy** klicken.
4. Konfigurieren:
   - **Name:** Bezeichner der Policy.
   - **Applied to:** Ziel-Principals (Standard: alle Nutzer).
   - **Guardrail type:** eingebaut oder **Custom** (eigene SQL-Funktion wählen).
   - **Phase:** Input Guardrails (`ON CALL`) oder Output Guardrails (`ON RESULT`).
   - **Rank:** niedrigere Ränge werten bei Requests zuerst, bei Responses zuletzt aus.
5. **Create policy** klicken.

## Prüfung

- Anhängen bestätigen: Tab **Policies** des Service prüfen.
- Ergebnisse beobachten: `DENY` liefert strukturierte Fehler, `ASK` pausiert zur Freigabe; Usage- und Inference-Tabellen zur Auswertung nutzen.

**Hinweis:** Die Verbreitung von Policy-Änderungen kann während der Beta bis zu ein bis zwei Minuten dauern.

## Aktuelle Einschränkungen

- Policies liefern nur Entscheidungen zurück — keine Inhaltstransformation.
- Custom-Funktionen unterstützen nur SQL.
- Anhängen erfolgt UI-seitig pro einzelnem Service.
- Gilt für alle Account-Nutzer; Catalog-/Schema-Ebene und ABAC-Bedingungen sind (noch) nicht verfügbar.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/service-policies/create-service-policy
