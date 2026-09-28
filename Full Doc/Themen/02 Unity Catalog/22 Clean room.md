## Clean Room

Innerhalb eines [Metastores](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#metastore) ist ein **Clean Room** ein sicherbares Objekt, das eine sichere Umgebung für die Zusammenarbeit mit anderen Organisationen an gemeinsam genutzten Daten bereitstellt, ohne dass eine der beiden Parteien der anderen ihre zugrunde liegenden Daten offenlegt.

Um einen Clean Room anzulegen, benötigt ein Nutzer das `CREATE CLEAN ROOM`-Privileg auf dem Unity-Catalog-Metastore.

Das `EXECUTE CLEAN ROOM TASK`-Privileg erlaubt einem Nutzer, Notebooks innerhalb des Clean Rooms auszuführen und Clean-Room-Details einzusehen. Das `MODIFY CLEAN ROOM`-Privileg erlaubt einem Nutzer, den Clean Room zu aktualisieren, einschließlich des Hinzufügens oder Entfernens von Daten-Assets, Notebooks und Kommentaren.

Weitere Informationen zu Clean Rooms siehe [Was sind Databricks Clean Rooms?](https://docs.databricks.com/aws/en/clean-rooms/).
