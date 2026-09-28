**Delta Lake Liquid Clustering** ersetzt **Table Partitioning** und **ZORDER**, um Entscheidungen zum Daten-Layout zu vereinfachen und die Query-Performance zu optimieren. Es bietet die Flexibilität, Clustering-Keys neu zu definieren, ohne bestehende Daten neu schreiben zu müssen, sodass sich das Daten-Layout im Laufe der Zeit an die analytischen Anforderungen anpassen kann.

Databricks empfiehlt Liquid Clustering für **alle neuen Delta-Tabellen**. **Szenarien, die von Clustering profitieren, sind unter anderem:**

- Tabellen, die häufig nach hochkardinalen Spalten gefiltert werden.
- Tabellen mit einer signifikanten Schiefe in der Datenverteilung.
- Tabellen, die schnell wachsen und Wartungs- sowie Tuning-Aufwand erfordern.
- Tabellen mit Anforderungen an gleichzeitige Schreibvorgänge.
- Tabellen mit Zugriffsmustern, die sich im Laufe der Zeit ändern.
- Tabellen, bei denen ein typischer Partition Key zu zu vielen oder zu wenigen Partitionen führen würde.

Weitere Informationen zur Aktivierung von Liquid Clustering finden Sie in der [Dokumentation](https://docs.databricks.com/en/delta/clustering.html#enable-liquid-clustering).

**HINWEIS:** Diese Queries auf der ZORDERED-Tabelle sind auch ohne Clustering bereits recht schnell, da wir einen kleinen Cluster verwenden und die Tabellen nicht extrem groß sind. Es besteht jedoch weiterhin Verbesserungspotenzial.