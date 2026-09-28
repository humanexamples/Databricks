# Row Filters und Column Masks — Überblick

## Row Filter

Schränken ein, welche **Zeilen** ein Nutzer sehen kann. Eine SQL-UDF wird zur Query-Zeit für jede Zeile ausgewertet — Zeilen, für die die Funktion `FALSE` zurückgibt, werden aus dem Ergebnis ausgeschlossen. Nützlich für Row-Level-Security, z. B. Einschränkung nach Region oder Abteilung.

## Column Mask

Steuert, welche **Werte** in bestimmten Spalten sichtbar sind. Die Maske ist eine SQL-UDF, die den Spaltenwert als Eingabe nimmt und entweder den Originalwert oder eine maskierte Version zurückgibt. Pro Spalte lässt sich genau eine Maske anwenden.

## Empfohlener Ansatz

Databricks empfiehlt primär **ABAC-Policies** (siehe `08 ABAC/`): Sie werden auf Catalog- oder Schema-Ebene angehängt und gelten automatisch für Tabellen und Spalten anhand von Governed Tags — das ist konsistenter als manuell gepflegte Filter auf Einzeltabellen. Alternativ lassen sich dynamische Views verwenden, die Basistabellen beim Teilen kuratierter oder transformierter Daten mit Filterlogik umschließen: Eine normale SQL-`VIEW` kapselt die Basistabelle(n) und filtert/maskiert zeilen- bzw. spaltenweise über die Funktion `is_account_group_member()` (kontoweite Gruppenzugehörigkeit) in `WHERE`- oder `CASE`-Ausdrücken. Ein eigenes Privileg gibt es dafür nicht — der Schutz ergibt sich rein daraus, dass Nutzer `SELECT` nur auf die View erhalten, nicht auf die Basistabelle. Von der veralteten Funktion `is_member()` (nur Workspace-Gruppen, Hive-Metastore-Kompatibilität) wird für Unity-Catalog-Daten abgeraten.

## Performance-Hinweise

- Einfache UDFs statt komplexer Queries verwenden.
- Anzahl unterschiedlicher Column Masks auf großen Tabellen begrenzen.
- Anzahl der UDF-Argumente reduzieren.
- Row Filter mit vielen `AND`-Bedingungen vermeiden.
- Deterministische Ausdrücke verwenden, die keine Fehler werfen.
- SQL-UDFs gegenüber Python-UDFs bevorzugen.

## Wichtige Einschränkungen

- Views können keine Row-Level-Security erhalten.
- Iceberg-REST-Catalogs werden nicht unterstützt.
- Delta-Lake-APIs werden nicht unterstützt.
- OpenSharing-Provider können Tabellen mit Table-Level-Schutz nicht teilen.
- Time Travel funktioniert nicht in Kombination mit diesen Mechanismen.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks/
