## Secret

Innerhalb eines [Schemas](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#schema) ist ein **Secret** ein sicherbares Objekt, das einen sensiblen Wert speichert, etwa eine Zugangsdaten oder ein API-Token. Secrets erlauben es, den Zugriff auf sensible Werte in Unity Catalog zu regeln und sie in Code oder aus anderen Unity-Catalog-Objekten heraus zu referenzieren, ohne den Wert offenzulegen. Secrets sind Teil des Drei-Ebenen-Namespace (`catalog.schema.secret`).

Die folgende Tabelle fasst wichtige Details zu Secrets zusammen:

| Detail | Beschreibung |
| :---------------- | :----------------------------------------------------------- |
| Nutzungsprivilegien | Um ein Secret zu verwenden, benötigt ein Nutzer `USE CATALOG` auf dem übergeordneten Katalog und `USE SCHEMA` auf dem übergeordneten Schema ([Nutzungsprivilegien](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#usage-privileges)), zusätzlich zum relevanten Secret-Level-Privileg. |
| Secret-Privilegien | `CREATE SECRET` erlaubt einem Nutzer, Secrets in einem Schema anzulegen. `READ SECRET` erlaubt das Abrufen eines Secret-Werts. `WRITE SECRET` erlaubt das Aktualisieren eines Secret-Werts. `REFERENCE SECRET` erlaubt es einem Unity-Catalog-Objekt, ein Secret zu referenzieren, ohne dessen Wert dem Nutzer offenzulegen. |
| Vererbung | Auf Katalog- oder Schema-Ebene vergebene Secret-Privilegien gelten für alle aktuellen und künftigen Secrets in diesem Katalog bzw. Schema. Siehe [Privilegienvererbung](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#inheritance). |

Weitere Informationen zu Secrets in Unity Catalog siehe [Secrets in Unity Catalog](https://docs.databricks.com/aws/en/security/secrets/unity-catalog-secrets).
