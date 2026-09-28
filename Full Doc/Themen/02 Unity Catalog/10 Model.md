### Model

Ein **Model** ist ein versioniertes oder unversioniertes, in Unity Catalog gespeichertes KI-Modell. Ein Model ist ein Container, der mehrere Versionen enthalten kann. Wird das Model mit MLflow trainiert, werden die Artefakte und Metadaten jedes Trainingslaufs darin als **Modellversionen** gespeichert.

Das Berechtigungsmodell für registrierte Modelle entspricht dem von Functions. Folgende zusätzliche Privilegien gelten speziell für Models:

- `APPLY TAG`: Erlaubt das Hinzufügen und Bearbeiten von Tags auf einem Model und seinen Versionen. Der Nutzer benötigt zusätzlich `USE CATALOG` auf dem übergeordneten Katalog und `USE SCHEMA` auf dem übergeordneten Schema.
- `CREATE MODEL VERSION`: Erlaubt einem Nutzer, neue Versionen eines Models zu registrieren, ohne die Fähigkeit zu gewähren, das Model auszuführen, zu ändern oder mit Tags zu versehen. Der Nutzer benötigt zusätzlich `USE CATALOG` auf dem übergeordneten Katalog und `USE SCHEMA` auf dem übergeordneten Schema.

Das Anlegen eines Models erfordert das `CREATE MODEL`-Privileg auf dem übergeordneten Schema oder Katalog. Wird `CREATE MODEL` auf einem Katalog vergeben, können Models in jedem Schema dieses Katalogs angelegt werden.

Weitere Informationen zu Models siehe [Modell-Lebenszyklus in Unity Catalog verwalten](https://docs.databricks.com/aws/en/machine-learning/manage-model-lifecycle/).
