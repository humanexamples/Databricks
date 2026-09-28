## Feature

Public Preview

Das sicherbare Objekt Feature befindet sich in Public Preview.

Innerhalb eines [Schemas](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#schema) ist ein **Feature** ein sicherbares Objekt in Unity Catalog, das die gespeicherte Definition eines Machine-Learning-Features repräsentiert: seine Quelldaten, seine Berechnungslogik und die zur Berechnung verwendeten Zeitfenster. Als governance-unterworfene, maßgebliche Quelle für ein Feature lässt sich eine einzelne Definition über Training, Materialisierung und Serving hinweg wiederverwenden, wobei Unity Catalog die Lineage zu seinen Quelldaten und den nutzenden Modellen nachverfolgt.

Die Definition eines Features ist eine reine Metadatenoperation: Es werden keine Feature-Daten berechnet, bevor das Feature materialisiert wird.

Weitere Informationen zu Features siehe [Feature Views](https://docs.databricks.com/aws/en/machine-learning/feature-store/feature-views).

Die folgende Tabelle fasst wichtige Details zu Features zusammen:

| Detail | Beschreibung |
| :--------------- | :----------------------------------------------------------- |
| Nutzungsprivilegien | Um ein Feature zu lesen, benötigt ein Nutzer `USE CATALOG` auf dem übergeordneten Katalog und `USE SCHEMA` auf dem übergeordneten Schema ([Nutzungsprivilegien](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#usage-privileges)), zusätzlich zu `READ FEATURE` auf dem Feature. |
| Anlege-Zugriff | Um ein Feature in einem Schema anzulegen, benötigt ein Nutzer das `CREATE FEATURE`-Privileg auf dem Schema, zusammen mit `USE CATALOG` auf dem übergeordneten Katalog und `USE SCHEMA` auf dem Schema. |
| Lesezugriff | `READ FEATURE` gewährt die Fähigkeit, die Metadaten und materialisierten Daten eines Features zu lesen und das Feature für Modell-Inferenz und -Training zu nutzen. |
| Vererbung | Auf Schema- oder Katalog-Ebene vergebenes `READ FEATURE` gilt für alle aktuellen und künftigen Features in diesem Schema bzw. Katalog. Siehe [Privilegienvererbung](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#inheritance). |
