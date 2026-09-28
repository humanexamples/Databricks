# Discoverability und Tag-Suche

Wie sich Tags (siehe [Uebersicht.md](Uebersicht.md)) nutzen lassen, um Datenobjekte in Unity Catalog aufzufinden — über die Suchleiste in der Databricks-UI sowie programmatisch über `INFORMATION_SCHEMA`-Views. Basierend auf einer privaten Kursnotiz sowie der offiziellen Databricks-Dokumentation (jeweils am Ende referenziert).

## Suchleiste: `tag:`-Syntax

Die Suchleiste am oberen Rand der Databricks-UI unterstützt Filterpräfixe, mit denen sich Suchanfragen einschränken lassen. Für Tags gibt es zwei Formen:

| Syntax | Bedeutung |
|---|---|
| `tag:<tag_key>` | sucht nach Objekten, die einen Tag mit diesem Schlüssel tragen — unabhängig vom Wert |
| `tag:<tag_key>:<tag_value>` | sucht nach Objekten mit exakter Schlüssel-**und**-Wert-Übereinstimmung |

Weitere allgemeine Filterpräfixe lassen sich kombinieren, z. B. `type:table owner:me`. Tag-Suche funktioniert für Tabellen, Views, Modelle, Volumes, Funktionen, Dashboards, Genie-Agents und Notebooks. Je mehr Filter kombiniert werden, desto feiner das Ergebnis — mehrere Tags in einer Suchanfrage grenzen die Treffermenge weiter ein.

**Abweichung von der Kursnotiz:** Die private Kursnotiz verwendet als Beispiel die Syntax `domain:customer` (bzw. `catalog:<name> domain:customer`), also ohne das Präfix `tag:` vor dem Tag-Schlüssel. Die aktuelle offizielle Dokumentation verlangt jedoch explizit das Präfix `tag:` vor Schlüssel (und optional Wert) — korrekt wäre demnach `tag:domain:customer`. Es ist nicht auszuschließen, dass sich die Such-Syntax seit Erstellung der Kursnotiz geändert hat; für aktuelle Databricks-Workspaces gilt jedenfalls die `tag:`-Präfix-Form.

Die exakte Übereinstimmung gilt sowohl für den Tag-Schlüssel als auch für den Tag-Wert.

### Beispiel aus der Kursnotiz (Nicht-Databricks-Quelle: privates Kursmaterial)

Um die für die eigene Umgebung gültige Suchanfrage zu ermitteln, lässt sich der Katalogname per SQL abfragen und direkt in die Suchleiste einfügen:

```sql
SELECT concat('catalog:', DA.catalog_name, ' ', 'domain:customer') AS use_in_search_bar
```

Das Ergebnis dieser Query wird kopiert und oben in die Suchleiste eingefügt, um die passenden Objekte zu finden (nach aktueller Doku-Syntax wäre der Tag-Teil als `tag:domain:customer` zu ergänzen).

## Programmatische Tag-Suche über `INFORMATION_SCHEMA`

Alternativ lassen sich Tags direkt per SQL über die `INFORMATION_SCHEMA`-Tag-Views abfragen — nützlich für Automatisierung, Auditing oder Dashboards. Je nach Objekttyp existiert eine eigene View:

- `INFORMATION_SCHEMA.CATALOG_TAGS`
- `INFORMATION_SCHEMA.SCHEMA_TAGS`
- `INFORMATION_SCHEMA.TABLE_TAGS`
- `INFORMATION_SCHEMA.COLUMN_TAGS`
- `INFORMATION_SCHEMA.VOLUME_TAGS`

```sql
SELECT *
FROM INFORMATION_SCHEMA.TABLE_TAGS
WHERE TABLE_NAME = 'customers_silver'
```

Wie bei allen `INFORMATION_SCHEMA`-Views (siehe [System Tables Uebersicht.md](../11%20Auditing%20und%20System%20Tables/System%20Tables%20Uebersicht.md)) gilt automatische Privilegien-Filterung: Es werden nur Tags von Objekten angezeigt, auf die der ausführende Nutzer bereits Zugriff hat.

## Quellen

- https://docs.databricks.com/aws/en/search/
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-information-schema
- Private Kursnotiz (Suchleisten-Beispiel, `concat`-Query)
