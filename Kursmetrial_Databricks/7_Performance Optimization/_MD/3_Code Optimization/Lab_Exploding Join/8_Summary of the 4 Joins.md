# 8_Zusammenfassung der 4 Joins

## Zusammenfassung der 4 Joins

| Join-Strategie                        | Ausführungszeit | Memory Spill | Größter Shuffle Write | Anmerkungen                                                        |
| :------------------------------------ | :--------------- | :----------- | :--------------------- | :------------------------------------------------------------------ |
| D. Exploding Join                     | ~60 Sekunden      | ~928 MiB     | 1334,8 MiB              | Zuerst wird die **transactions**-Tabelle mit der **store**-Tabelle gejoint (exploding join) |
| E. Anzahl der shuffles erhöhen        | ~50 Sekunden      | ~273,7 MiB   | 680,5 MiB               | Derselbe join wie zuvor, 8 partitions angegeben                     |
| F. Reihenfolge des joins ändern       | ~40 Sekunden      | 0            | 19,1 MiB                | Die Join-Reihenfolge geändert, sodass **transactions** zuerst mit **countries** gejoint wird |
| G. Analyze und broadcast join         | ~20 Sekunden      | 0            | 383,6 KiB               | Databricks analysieren und die Standard-Broadcast-Konfigurationen verwenden lassen. Obwohl die Query etwa gleich lange dauerte, wurde der shuffle drastisch reduziert. |

