# 4_Lab Queries Summary (geschätzte durchschnittliche Ausführungszeiten unten, die tatsächlichen Ausführungszeiten variieren)

Sehen Sie sich die Queries für jede der folgenden Tabellen an und vergleichen Sie einige der Query-Statistiken.

#### D1. Query nach UniqueCarrier

**HINWEISE:** Für die Spalte **UniqueCarrier** wurde keine Speicheroptimierung festgelegt, sodass bei jedem Query für jede Tabelle alle Dateien gelesen wurden. Jedes Query hatte ähnliche Cloud-Storage-Response-Größen und Ausführungszeiten.

| Tabelle                        | Query                        | Dateien gesamt | Gelesene Dateien | Übersprungene Dateien | Query-Dauer (variiert) | cloud storage request count total | cloud storage response size total |
| :----------------------------- | :--------------------------- | :---------- | :--------- | :----------- | :------------------------- | :-------------------------------- | :-------------------------------- |
| **ZORDER by FlightNum**        | `WHERE UniqueCarrier = 'TW'` | 31          | 31         | 0            | ~12 s                      | 149                               | 1068 MiB                          |
| **CLUSTER BY id**              | `WHERE UniqueCarrier = 'TW'` | 128         | 128        | 0            | ~10 s                      | 316                               | 1047.8 MiB                        |
| **CLUSTER BY (id, FlightNum)** | `WHERE UniqueCarrier = 'TW'` | 144         | 144        | 0            | ~10 s                      | 374                               | 997.6 MiB                         |

#### D2. Query nach FlightNum

**HINWEISE:** Beachten Sie, dass bei den Tabellen, die **FlightNum** in eine Speicheroptimierungstechnik einbezogen, viele Dateien durch Pruning ausgeschlossen wurden, was die Effizienz erhöhte und die Ausführungszeiten verkürzte.

Die Tabelle, die nur nach **id** geclustert war, lief langsamer, und die Cloud-Storage-Response-Größe war deutlich größer.

| Tabelle                        | Query                    | Dateien gesamt | Gelesene Dateien | Übersprungene Dateien | Query-Dauer (variiert) | cloud storage request count total | cloud storage response size total |
| :----------------------------- | :----------------------- | :---------- | :--------- | :----------- | :------------------------- | :-------------------------------- | :-------------------------------- |
| **ZORDER by FlightNum**        | `WHERE FlightNum = 1890` | 31          | 1          | 30           | ~2 s                       | 6                                 | 53.MiB                            |
| **CLUSTER BY id**              | `WHERE FlightNum = 1890` | 128         | 128        | 0            | ~10 s                      | 275                               | **1871.3 MiB**                    |
| **CLUSTER BY (id, FlightNum)** | `WHERE FlightNum = 1890` | 144         | 12         | 132          | ~2 s                       | 32                                | 146.3 MiB                         |

#### D3. Query nach id

**HINWEISE:** Beachten Sie, dass bei den Tabellen, die **id** in eine Speicheroptimierungstechnik einbezogen (beide liquid clustered Tabellen), viele Dateien durch Pruning ausgeschlossen wurden, was die Effizienz erhöhte — auch bei der Tabelle, die sowohl nach **id** als auch nach **FlightNum** geclustert ist.

Sie können außerdem erkennen, dass die Cloud-Storage-Response-Größe jeder der geclusterten Tabellen deutlich kleiner war als bei der nach **FlightNum** z-geordneten Tabelle.

Beachten Sie zudem, dass die z-geordnete Tabelle extrem lange zur Fertigstellung benötigte und die Cloud-Storage-Response-Größe beim Abfragen der Spalte **id** in der Tabelle **flights** deutlich größer war.

| Tabelle                        | Query                      | Dateien gesamt | Gelesene Dateien | Übersprungene Dateien | Query-Dauer (variiert) | cloud storage request count total | cloud storage response size total |
| :----------------------------- | :------------------------- | :---------- | :--------- | :----------- | :------------------------- | :-------------------------------- | :-------------------------------- |
| **ZORDER by FlightNum**        | `WHERE id = 1125281431554` | 31          | 31         | 31           | **~28 s**                  | **267**                           | **4.7 GiB**                       |
| **CLUSTER BY id**              | `WHERE id = 1125281431554` | 128         | 1          | 127          | ~2 s                       | 4                                 | 54.5 MiB                          |
| **CLUSTER BY (id, FlightNum)** | `WHERE id = 1125281431554` | 144         | 10         | 134          | ~2 s                       | 29                                | 370.9 MiB                         |

