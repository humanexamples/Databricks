## Service

Innerhalb eines [Schemas](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#schema) ist ein **Service** ein sicherbares Objekt, das ein governance-unterworfenes, aufrufbares KI-Asset repräsentiert. Services erlauben es, Zugriff auf KI-Traffic mit denselben Privilegien zu steuern, die auch für Daten verwendet werden. Unity Catalog unterstützt folgende Service-Typen, aktuell in [Beta](https://docs.databricks.com/aws/en/release-notes/release-types):

- **Model Services** stellen LLM-Endpunkte bereit, die sich aufrufen und Workspace-übergreifend teilen lassen. Siehe [LLMs und Agenten auf Databricks abfragen](https://docs.databricks.com/aws/en/agents/query-llms).
- **MCP Services** registrieren MCP-Server, sodass sich steuern lässt, welche Tools Agenten nutzen. Siehe [Agenten mit MCP Services an Drittanbieter-Tools anbinden](https://docs.databricks.com/aws/en/agents/mcp-tools/mcp-services).

Die folgende Tabelle fasst wichtige Details zu Services zusammen:

| Detail | Beschreibung |
| :----------------------------- | :----------------------------------------------------------- |
| Nutzungsprivilegien | Um einen Service aufzurufen, benötigt ein Nutzer `USE CATALOG` auf dem übergeordneten Katalog und `USE SCHEMA` auf dem übergeordneten Schema ([Nutzungsprivilegien](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#usage-privileges)), zusätzlich zu `EXECUTE` auf dem Service. |
| Das `CREATE SERVICE`-Privileg | Das Anlegen eines Service erfordert das `CREATE SERVICE`-Privileg auf dem übergeordneten Schema oder Katalog. |
| Das `EXECUTE`-Privileg | `EXECUTE` auf einem Service zu vergeben erlaubt einem Nutzer, ihn aufzurufen — dasselbe Privileg, das auch für Functions und Models verwendet wird. |

Weitere Informationen zur Governance von KI-Services siehe [KI-Governance in Unity Catalog](https://docs.databricks.com/aws/en/ai-gateway/).
