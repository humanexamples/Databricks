## External Metadata

Innerhalb eines [Metastores](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#metastore) ist ein **External-Metadata**-Objekt ein sicherbares Objekt, das benutzerdefinierte Data-Lineage-Beziehungen für Systeme festlegt, die außerhalb der nativen Lineage-Nachverfolgung von Unity Catalog operieren.

Um ein External-Metadata-Objekt anzulegen, benötigt ein Nutzer das `CREATE EXTERNAL METADATA`-Privileg auf dem Unity-Catalog-Metastore. Um Lineage-Beziehungen auf dem Objekt hinzuzufügen oder zu ändern, benötigt der Nutzer `MODIFY` auf dem External-Metadata-Objekt, zusätzlich zu den passenden Privilegien auf allen in der Beziehung referenzierten Unity-Catalog-Objekten.

Weitere Informationen zu External Metadata siehe [Lineage in Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-lineage).
