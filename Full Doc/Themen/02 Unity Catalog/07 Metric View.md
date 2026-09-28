### Metric View

Eine **Metric View** ist ein schreibgeschütztes Objekt, das eine Menge wiederverwendbarer Metrikdefinitionen auf Basis einer oder mehrerer Tabellen, Views oder SQL-Abfragen festlegt. Nutzer fragen eine Metric View wie eine Standard-View ab.

Das Berechtigungsmodell für Metric Views entspricht dem von Standard-Views. Nutzer benötigen `SELECT` und die passenden [Nutzungsprivilegien](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#usage-privileges), um die Metric View abzufragen. Die Privilegien des Metric-View-Eigentümers werden zur Laufzeit verwendet, um die zugrunde liegenden Datenquellen aufzulösen.

Weitere Informationen zu Metric Views siehe [Unity Catalog Metric Views](https://docs.databricks.com/aws/en/uc-semantics/metric-views/).
