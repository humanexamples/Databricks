## Tags

Tags sind Schlüssel-Wert-Paare (oder reine Schlüssel ohne Wert), die sich auf Unity-Catalog-Objekten anbringen lassen, um sie zu klassifizieren, auffindbar zu machen und in Policies (z. B. ABAC, siehe [ABAC/01 Grundkonzepte.md](../03%20Governance/01%20Data%20Governance/08%20ABAC/01%20Grundkonzepte.md)) referenzierbar zu machen.

### Unterstützte Objekte

Tags lassen sich anbringen auf: **Catalogs, Schemas, Tabellen, Tabellenspalten, Volumes, Views, Funktionen, registrierte Modelle, Modellversionen** sowie **External-Metadata-Objekte** (Public Preview). Zusätzlich unterstützt: Dashboards, Genie-Agenten, Databricks Apps und Notebooks.

### Schlüssel- und Wert-Vorgaben

| Eigenschaft | Regel |
|---|---|
| Groß-/Kleinschreibung | wird unterschieden (`"Sales"` ≠ `"sales"`) |
| Maximale Schlüssellänge | 256 Zeichen |
| Maximale Wertlänge | 256 Zeichen |
| Verbotene Zeichen im Schlüssel | `. , - = / :` |
| Leerzeichen | weder im Schlüssel noch im Wert am Anfang oder Ende erlaubt |

**Zuweisungslimits:**

- Maximal **50 Tags** pro schützbarem Objekt.
- Maximal **1.000 Spalten-Tags** pro Tabelle (über alle Spalten hinweg summiert).
- Spalten-Tagging erfordert einen einzelnen `ALTER TABLE`-Befehl je Spalte — eine Batch-Zuweisung über mehrere Spalten hinweg wird nicht unterstützt.
- Die Tag-Suche verlangt exakte Übereinstimmung der Suchbegriffe.

### Governed Tags vs. System Tags

**Governed Tags:** Account-weit über Regeln durchgesetzte Tags — werden in der UI mit einem Schloss-Symbol angezeigt, benötigen eine explizite `ASSIGN`-Berechtigung zur Zuweisung und dürfen nur Werte aus der zugehörigen Policy annehmen. Wird ein Governed Tag mit einem bereits existierenden ungoverned Schlüssel angelegt, werden alle bestehenden Zuweisungen mit diesem Schlüssel automatisch governt. Ausführlich behandelt in [Governance/Data Governance/10 Governed Tags](../03%20Governance/01%20Data%20Governance/10%20Governed%20Tags/01%20Governed%20Tags%20verwalten.md).

**System Tags:** eine besondere Kategorie von Governed Tags, die **von Databricks vordefiniert** wird — mit unveränderlichen Definitionen, kontrollierten Zuweisungsberechtigungen und einem Schraubenschlüssel-Symbol in der UI. Nutzer können die Sichtbarkeit von System Tags beim Zuweisen ein-/ausblenden.

### Tag-Vererbung in ABAC-Policies

Bei der Auswertung von ABAC-Policies kaskadieren Tags implizit an untergeordnete Objekte — ein Catalog-Tag gilt automatisch für alle darunterliegenden Schemas und Tabellen. **Ausnahme:** Tags vererben sich **nicht** auf Spaltenebene.

### Berechtigungen

Um Tags auf Unity-Catalog-Objekten hinzuzufügen, muss ein Nutzer entweder Eigentümer des Objekts sein oder folgende Privilegien besitzen:

- `APPLY TAG` auf dem Objekt selbst.
- `USE SCHEMA` auf dem übergeordneten Schema.
- `USE CATALOG` auf dem übergeordneten Catalog.

Für Governed Tags zusätzlich erforderlich: die `ASSIGN`-Berechtigung auf dem jeweiligen Tag.

### SQL-Syntax

**Ab Databricks Runtime 16.1+ (bevorzugter Ansatz):**

```sql
SET TAG ON CATALOG catalog `cost_center` = `hr`;
UNSET TAG ON CATALOG catalog cost_center;
```

**Ab Databricks Runtime 13.3+ (Alternative, z. B. für Spalten-Tags):**

```sql
ALTER TABLE schema.table ALTER COLUMN column_name SET TAGS ('key' = 'value');
```

Für die übrigen Objekttypen existiert die äquivalente `ALTER <OBJEKTTYP> ... SET TAGS (...)`/`UNSET TAGS (...)`-Syntax (siehe die jeweiligen Objektdateien in diesem Ordner, z. B. [02 Catalog.md](02%20Catalog.md), [08 Volume.md](08%20Volume.md)).

### Spalten mit Governed Tags löschen

Bevor eine Spalte mit einem Governed Tag gelöscht werden kann, muss das Tag zunächst entfernt werden — diese Reihenfolge verhindert potenzielle Datenlecks:

1. `UNSET TAG ON COLUMN` für jedes Governed Tag der Spalte ausführen.
2. Spalte über `ALTER TABLE ... DROP COLUMN` löschen.

### Tags auf registrierten Modellen

Für registrierte Modelle und Modellversionen steht **keine SQL-Syntax** zur Tag-Verwaltung zur Verfügung — hierfür müssen der Catalog Explorer oder der MLflow-Client (API) genutzt werden.

### Information-Schema-Views

Tag-Metadaten lassen sich über folgende Views abfragen:

| View | Inhalt |
|---|---|
| `INFORMATION_SCHEMA.CATALOG_TAGS` | Tags auf Catalogs |
| `INFORMATION_SCHEMA.SCHEMA_TAGS` | Tags auf Schemas |
| `INFORMATION_SCHEMA.TABLE_TAGS` | Tags auf Tabellen |
| `INFORMATION_SCHEMA.COLUMN_TAGS` | Tags auf Tabellenspalten |
| `INFORMATION_SCHEMA.VOLUME_TAGS` | Tags auf Volumes |

```sql
SELECT catalog_name, schema_name, table_name, tag_name, tag_value
FROM information_schema.column_tags
WHERE tag_name = 'pii' AND schema_name = 'default';
```

### Sicherheitshinweis

**Wichtig:** Tag-Daten werden als Klartext gespeichert und können global repliziert werden. Persönliche oder sensible Informationen dürfen daher **nicht** in Tag-Namen, -Werten oder -Beschreibungen abgelegt werden.

### Quelle

- https://docs.databricks.com/aws/en/database-objects/tags
