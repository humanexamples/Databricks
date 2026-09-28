3 verschiedenen Ansätzen verbergen können:

* Views 
* Dynamic Views
* Row Filter und Column Masks für Tabellen (eingeführt in 2024)



Das Sicherheitsmodell von Unity Catalog unterstützt zwei unterschiedliche Muster zur Verwaltung von Datenzugriffsberechtigungen:

1. Massenhafte Erteilung von Berechtigungen durch Nutzung der Berechtigungsvererbung von Unity Catalog.

1. Explizite Erteilung von Berechtigungen für bestimmte Objekte. Dieses Muster ist recht sicher, erfordert jedoch mehr Aufwand bei der Einrichtung und Verwaltung.

### 1. Geerbte Berechtigungen

Wie wir gesehen haben, sind sicherbare Objekte in Unity Catalog hierarchisch aufgebaut und folgen einem Drei-Ebenen-Namespace. Berechtigungen werden nach unten vererbt, und die Nutzung dieser Funktion erleichtert das Einrichten von Standardzugriffsregeln für Ihre Daten. 

Mithilfe der Berechtigungsvererbung erstellen wir eine Berechtigungskette, die es jedem ermöglicht, auf die View **customers_gold_view** und andere Objekte im selben Katalog und Schema zuzugreifen.

```sql

  GRANT USE CATALOG ON CATALOG ${DA.catalog} TO `account users`;
  GRANT USE SCHEMA,SELECT ON CATALOG ${DA.catalog}.example TO `account users`

```
Im Grunde verschiebt dies `USE SCHEMA` und `SELECT` eine Ebene tiefer, sodass Empfänger nur Zugriff auf alle zutreffenden Objekte im neu erstellten Schema haben.


1. Unten sehen Sie eine *Beispiel*-Abfrage, um Berechtigungen für Folgendes zu erteilen:

  - Die Möglichkeit, Ihren durch **${DA.catalog_name}** angegebenen Katalog zu nutzen/darauf zuzugreifen.

  - Die Möglichkeit, beliebige Schemas innerhalb Ihres Katalogs zu nutzen/darauf zuzugreifen.

  - Die Möglichkeit, SELECT-Operationen (Daten lesen) in Ihrem Katalog durchzuführen.

  - Dies ermöglicht es Mitgliedern der Gruppe *account users*, Daten innerhalb des Katalogs und seiner Schemas zu durchsuchen und abzufragen.

**HINWEIS: Das Abfrageergebnis liefert einen UNAUTHORIZED_ACCESS-Fehler. Warum? Sie müssen der Eigentümer des Katalogs sein, um solche Berechtigungen zu erteilen, und Sie sind nicht der Eigentümer des Katalogs. **

```python
spark.sql(f'GRANT USE CATALOG, USE SCHEMA, SELECT ON CATALOG 
          TO `account users`')
```

2. Führen Sie die `DESCRIBE CATALOG`-Anweisung aus, um Informationen über den Katalog anzuzeigen. Betrachten Sie die Ergebnisse. Beachten Sie, dass Sie den *Owner* eines Katalogs einsehen können. In diesem Beispiel sind Sie nicht der Eigentümer des Katalogs und haben nicht die Möglichkeit, Berechtigungen zu erteilen.

```python
r = spark.sql(f'DESCRIBE CATALOG {DA.catalog_name}')
display(r)
```

### C3. Berechtigungen in Unity Catalog überprüfen

#### C3.2 Berechtigungen mit Code überprüfen
1. Sie können auch den [`SHOW GRANTS`-Befehl](https://docs.databricks.com/en/sql/language-manual/security-show-grant.html) verwenden, um die Berechtigungen für Ihren Katalog zu überprüfen. Dieser Befehl ist eine vielseitige SQL-Anweisung, die verwendet wird, um Berechtigungen für verschiedene Datenbankobjekte anzuzeigen. In diesem Fall wenden wir ihn auf einen Katalog mit folgender Syntax an: 
```
SHOW GRANTS [ principal ] ON securable_object
```

Führen Sie die untenstehende Zelle aus und betrachten Sie die Ergebnisse.

```python
r = spark.sql(f'SHOW GRANTS ON CATALOG {DA.catalog_name}')
display(r)
```

### C4. Explizite Berechtigungen für Schema oder Objekte erteilen

1. Zeigen Sie die Berechtigungen für das Schema **pii_data** innerhalb Ihres Katalogs an. Beachten Sie, dass nur Sie Zugriff auf dieses Schema haben.

```sql
SHOW GRANTS ON SCHEMA pii_data;
```

2. Zeigen Sie die Berechtigungen für die View **customers_gold_view** innerhalb des Schemas **pii_data** Ihres Katalogs an. Beachten Sie, dass nur Sie Zugriff auf diese View haben.

```sql
SHOW GRANTS ON VIEW customers_gold_view;
```

3. Mithilfe expliziter Berechtigungsvergabe auf Schemaebene erstellen wir eine Berechtigungskette, die es jedem ermöglicht, auf die View **customers_gold_view** zuzugreifen.

Sie müssen jedoch anderen Benutzern Zugriff auf den Katalog gewähren, damit diese auf die darin enthaltenen Objekte zugreifen können. 

```python
## Diese Berechtigung ermöglicht es Benutzern, auf den angegebenen Katalog zuzugreifen und mit ihm zu interagieren, sodass sie Schemas darin sehen und abfragen können.
## Die Erteilung von Berechtigungen für Ihren Katalog funktioniert in diesem Lab nicht - auskommentiert
##
## spark.sql(f'GRANT USE CATALOG ON CATALOG {DA.catalog_name} TO `account users`')
##

## Diese Berechtigung ermöglicht es der Gruppe account users, auf das Schema pii_data im angegebenen Katalog zuzugreifen und mit ihm zu interagieren.
spark.sql(f'GRANT USE SCHEMA ON SCHEMA {DA.catalog_name}.pii_data TO `account users`')

## Diese Berechtigung ermöglicht es der Gruppe account users, Daten aus der View customers_gold_view im Schema pii_data des angegebenen Katalogs abzufragen (SELECT).
spark.sql(f'GRANT SELECT ON VIEW {DA.catalog_name}.pii_data.customers_gold_view TO `account users`')
```

Mit diesen Berechtigungen (sofern Sie die Berechtigung hätten, vollständigen Zugriff zu erteilen) würde die Abfrage weiterhin erfolgreich ausgeführt werden, wenn jemand anderes die View erneut abfragt, da alle entsprechenden Berechtigungen vorhanden sind; wir haben lediglich einen ganz anderen Ansatz gewählt, um sie einzurichten.

Dies scheint komplizierter zu sein. Eine Anweisung von vorhin wurde durch drei ersetzt, und dies bietet nur Zugriff auf eine einzige View. 

Diesem Muster folgend, müssten wir für jede zusätzliche Tabelle oder View, auf die wir Zugriff gewähren möchten, einen zusätzlichen `SELECT`-Grant durchführen. Aber diese Komplikation bringt den Vorteil der Sicherheit mit sich. Jetzt kann der Benutzer nur die *gold*-View lesen, aber nichts anderes. Es besteht keine Möglichkeit, dass er versehentlich Zugriff auf ein anderes Objekt erhält. Dies ist also sehr explizit und sicher, aber man kann sich vorstellen, dass es bei vielen Tabellen und Views sehr umständlich wäre.

### 2. Explizite Berechtigungen überprüfen

```sql
SHOW GRANTS ON SCHEMA pii_data;
SHOW GRANTS ON VIEW pii_data.customers_gold_view;
```

```python
# Beachten Sie, dass `account users` keinen Zugriff hat, 
# um Berechtigungen für den Katalog zu erteilen.
r = spark.sql(f'SHOW GRANTS ON CATALOG {DA.catalog_name}')
display(r)
```

### C6. Berechtigungen widerrufen

```sql
REVOKE USAGE ON SCHEMA pii_data FROM `account users`;
REVOKE SELECT ON VIEW pii_data.customers_gold_view FROM `account users`;
```

```sql
SHOW GRANTS ON SCHEMA pii_data;
SHOW GRANTS ON VIEW pii_data.customers_gold_view;
```

### C7. Views versus Tabellen

Angenommen jedoch, jemand anderes würde versuchen, direkt auf die Tabelle **customers_silver** zuzugreifen. Dies könnte erreicht werden, indem **customers_gold_view** in der vorherigen Abfrage durch **customers_silver** ersetzt wird.

Mit den expliziten Berechtigungen würde die Abfrage fehlschlagen. Wie funktioniert dann die Abfrage gegen die View **customers_gold_view**? Weil der **Eigentümer** der View über entsprechende Berechtigungen für die Tabelle **customers_silver** verfügt (durch Eigentümerschaft). Diese Eigenschaft führt zu interessanten Anwendungen von Views in der Tabellensicherheit, die wir im nächsten Abschnitt behandeln.

## D. Schutz von Spalten und Zeilen

Databricks bietet mehrere Optionen zum Schutz von Spalten und Zeilen. In diesem Abschnitt verwenden wir die Tabelle **customers_silver** als Quelle, um **Dynamic Views** zu erstellen und **Row Filtering und Column Masks** anzuwenden, um sensible Daten zu schützen:
- Dynamic View: **customers_gold_dynamic_view**
- Tabelle: **customers_silver_with_row_filter_and_column_masks** mit `ROW_FILTER` und `MASK COLUMN`

### D2. Dynamic Views

* Spaltenwerte teilweise zu verbergen oder vollständig zu schwärzen
* Zeilen basierend auf bestimmten Kriterien auszulassen

Die Zugriffskontrolle mit **Dynamic Views** **durch die Verwendung von Funktionen** :
* `current_user()`: gibt die E-Mail-Adresse des Benutzers zurück, der die View abfragt

* `is_account_group_member()`: gibt TRUE zurück, wenn der Benutzer, der die View abfragt, Mitglied der angegebenen Gruppe ist.

  ```sql
  SELECT is_account_group_member('supervisors')
  ```

* `is_member()`: gibt TRUE zurück, wenn der Benutzer, der die View abfragt, Mitglied der angegebenen workspace-lokalen Gruppe ist. (Databricks rät im Allgemeinen von der Verwendung der Funktion `is_member()` in Produktionsumgebungen ab, da sie sich auf workspace-lokale Gruppen bezieht und somit eine Workspace-Abhängigkeit in einen Metastore einführt.)

Angenommen, wir möchten, dass jeder aggregierte Datentrends aus der Tabelle **customers_silver** sehen kann, aber wir möchten keine Kunden-PII-Daten für alle offenlegen. Spaltenschwärzungen werden mithilfe von `CASE`-Anweisungen durchgeführt, und die Zeilenfilterung erfolgt durch Anwendung der Bedingung als `WHERE`-Klausel.

```sql
CREATE OR REPLACE VIEW customers_gold_dynamic_view AS
SELECT 
  CASE WHEN        -- Schwärzt die Spalte customer_id, wenn der Benutzer kein Supervisor ist
    is_account_group_member('supervisors') THEN customer_id 
    ELSE 9999999
  END AS customer_id,
  state, 
  avg(units_purchased) as average_units_purchased, 
  loyalty_segment
FROM customers_silver
WHERE
  CASE WHEN          -- Filtert Zeilen mit loyalty_segment 3 oder höher heraus, wenn der Benutzer kein Supervisor ist
    is_account_group_member('supervisors') THEN TRUE  -- Wenn wahr, alle Zeilen zurückgeben
    ELSE loyalty_segment < 3                          -- Wenn falsch, Zeilen kleiner als 3 zurückgeben
  END
GROUP BY customer_id, state, loyalty_segment
ORDER BY customer_id;
```

## E. Row Filters und Column Masks (Eingeführt in 2024) 

Diese neu eingeführte Funktion ermöglicht es Dateneigentümern, Spalten zu maskieren und Zeilen auf ähnliche Weise wie Dynamic Views zu verbergen - ohne ein weiteres Datenobjekt erstellen zu müssen.

### E1. Row Filters

**Row Filters** ermöglichen es Ihnen, einen Filter auf eine Tabelle anzuwenden, sodass Abfragen nur Zeilen zurückgeben, die die Filterkriterien erfüllen. Sie implementieren einen Row Filter als SQL-benutzerdefinierte Funktion (UDF). Python- und Scala-UDFs werden ebenfalls unterstützt, jedoch nur, wenn sie in einer SQL-UDF eingebettet sind.

```sql
DROP FUNCTION IF EXISTS loyalty_row_filter;

CREATE OR REPLACE FUNCTION loyalty_row_filter(loyalty_segment STRING)
RETURNS BOOLEAN
RETURN IF(is_account_group_member('supervisors'), true, loyalty_segment < 3);
```

```sql
-- Löscht die Tabelle, falls sie für Demozwecke bereits existiert
DROP TABLE IF EXISTS customers_silver_with_row_filter_and_column_masks;

-- Erstellt eine neue Tabelle und wendet den Row Filter an
CREATE OR REPLACE TABLE customers_silver_with_row_filter_and_column_masks AS 
SELECT 
  customer_id,
  state, 
  avg(units_purchased) as average_units_purchased, 
  loyalty_segment
FROM customers_silver
GROUP BY customer_id, state, loyalty_segment
ORDER BY customer_id;


-- Zeigt die neue Tabelle an
SELECT count(*) AS TotalRows
FROM customers_silver_with_row_filter_and_column_masks;
```

```sql
ALTER TABLE customers_silver_with_row_filter_and_column_masks 
SET ROW FILTER loyalty_row_filter ON (loyalty_segment);
```

### E2. Column Mask

**Column Masks** ermöglichen es Ihnen, eine Maskierungsfunktion auf eine Tabellenspalte anzuwenden.  Column Masks sind Ausdrücke, die als SQL-UDFs oder als Python- oder Scala-UDFs geschrieben werden, die in einer SQL-UDF eingebettet sind. Um Column Masks anzuwenden, erstellen Sie eine UDF und wenden Sie diese mithilfe einer `ALTER TABLE`-Anweisung auf eine Tabellenspalte an.

```sql
DROP FUNCTION IF EXISTS redact_customer_id;

CREATE OR REPLACE FUNCTION redact_customer_id(customer_id BIGINT)
RETURN CASE WHEN is_account_group_member('supervisors') 
  THEN customer_id 
  ELSE 9999999
END;
```

```sql
ALTER TABLE customers_silver_with_row_filter_and_column_masks
  ALTER COLUMN customer_id 
  SET MASK redact_customer_id;
```

## F. Dynamic Views vs. Row Filters - Diskussion

- Dynamic Views, Row Filters und Column Masks ermöglichen es Ihnen alle, komplexe Logik auf Tabellen anzuwenden und ihre Filterentscheidungen zur Laufzeit der Abfrage zu verarbeiten.

- Verwenden Sie **Dynamic Views**, wenn Sie Transformationslogik wie Filter und Masken **auf schreibgeschützte Tabellen** anwenden müssen und es akzeptabel ist, dass Benutzer die Dynamic Views unter anderen Namen referenzieren. 

- Verwenden Sie Row Filters und Column Masks, wenn Sie bestimmte Daten filtern oder Ausdrücke darüber berechnen möchten, **den Benutzern aber weiterhin Zugriff auf die Tabellen unter ihren ursprünglichen Namen geben möchten.**

## G. Tagging 
Tags sind Attribute mit Schlüsseln und optionalen Werten, die auf sicherbare Objekte in Unity Catalog angewendet werden können, um sie zu organisieren und zu kategorisieren.

- Zu den unterstützten Objekten für das Tagging gehören Kataloge, Schemas, Tabellen, Spalten, Volumes, Views, registrierte Modelle und Modellversionen.

- Tags vereinfachen die Suche und das Auffinden von Tabellen und Views mithilfe der Workspace-Suchfunktion.

- Sie können bis zu 20 Tags pro Objekt zuweisen, mit einer Schlüssellänge von bis zu 255 Zeichen und einer Wertlänge von bis zu 1000 Zeichen.

- Tags können über die Catalog-Explorer-Benutzeroberfläche oder SQL-Befehle (für Databricks Runtime 13.3+) hinzugefügt und verwaltet werden.

- Tags können für Datenklassifizierung, Sicherheit, Lifecycle-Management, Compliance und Projektmanagement verwendet werden.

**HINWEIS:** Denken Sie daran, dass Tags auch für die oben genannten anderen Objekte gesetzt werden kann (Kataloge, Schemas, Spalten usw.):

```sql
-- TABELLEN-TAGS
ALTER TABLE customers_silver 
SET TAGS (
  'quality'='silver',
  'domain'='customer'
  );


-- SPALTEN-TAGS
ALTER TABLE customers_silver 
  ALTER COLUMN customer_id SET TAGS ("compliance" = "GDPR");
```

Tagging über Catalog Explorer: Im Tab **Overview** finden Sie den Bereich "Tagging" auf der rechten Seite des Panels. Beachten Sie die Tags, die wir in der vorherigen Zelle definiert haben.

## H. Auffindbarkeit

Unity Catalog bietet robuste Funktionen zur Datenerkennung, mit denen Benutzer einfach nach Datenassets in ihrer Organisation suchen und diese finden können. 

Es gibt zwei Möglichkeiten, Tags für die Auffindbarkeit zu nutzen:

1. **Suchleiste:** Verwenden Sie eine Syntax wie `tag:value`. In unserem Beispiel sollte dies `domain:customer` sein. Je mehr Tags hinzugefügt werden, desto feiner werden die Ergebnisse.

![Discoverability](https://files.training.databricks.com/binder/prod_main/databricks-data-privacy-en_us-2.1.2/images/20260819T030319Z/Databricks Data Privacy/Includes/images/search_bar.png)

2. **Abfragen:** Alternativ können Sie die untenstehende Abfrage ausführen, die `INFORMATION_SCHEMA.TABLE_TAGS` mit einer Filterung nach der Tabelle `customers_silver` nutzt.
   Beachten Sie die folgenden Tabellen, um Tags aus den verschiedenen Objekten abzurufen:

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

## I. Lineage

 Im Tab **Lineage** können wir Elemente identifizieren, die mit dem ausgewählten Objekt in Beziehung stehen:

* Bei ausgewähltem **Upstream** sehen wir Objekte, die zu diesem Objekt geführt haben oder die dieses Objekt verwendet. Dies ist nützlich, um die Quelle Ihrer Daten nachzuverfolgen.
* Bei ausgewähltem **Downstream** sehen wir Objekte, die dieses Objekt verwenden. Dies ist nützlich für die Durchführung von Auswirkungsanalysen.
* Der Lineage-Graph bietet eine Visualisierung der Lineage-Beziehungen.

Sie können auf die Lineage einer Tabelle im Catalog Explorer zugreifen, indem Sie Ihre Tabelle auswählen: Im Tab _"lineage"_ gibt es eine Schaltfläche _"see lineage graph"_, um die unten gezeigten Ergebnisse anzuzeigen. 

![Lineage](https://files.training.databricks.com/binder/prod_main/databricks-data-privacy-en_us-2.1.2/images/20260819T030319Z/Databricks Data Privacy/Includes/images/lineage.png)

## J. KI-generierte Dokumentation

KI-generierte Dokumentation für Unity Catalog ermöglicht die automatische Erstellung von Beschreibungen für Tabellen und Spalten. Die Funktion nutzt ein speziell entwickeltes Large Language Model (LLM), um Metadaten basierend auf Tabellenschemas und Spaltennamen zu generieren.

- Verfügbar für Kataloge, Schemas, Tabellen, Spalten, Funktionen, Modelle und Volumes.
- Spart Zeit und reduziert den manuellen Aufwand bei der Dokumentation von Datenassets.
- Verbessert die Suchfunktion innerhalb von Databricks-Workspaces.
- Benutzer benötigen entsprechende Berechtigungen (Objekteigentümer oder MODIFY-Privileg), um KI-generierte Kommentare anzuzeigen, zu bearbeiten und zu speichern.


### J1. Tabellen
1. Wir generieren automatisch prägnante und informative Tabellen- und Spaltenkommentare für Unity Catalog mithilfe von DatabricksIQ. 

    Suchen Sie im Catalog Explorer nach der Tabelle "customers_silver" und im Tab "Overview" schlägt DatabricksIQ eine "_AI Suggested Description_" vor. Sie können diese nach Bedarf bearbeiten und anpassen oder die Empfehlung übernehmen. Es ist auch möglich, die Beschreibung später bei Bedarf

![AI Generated Table Description](https://files.training.databricks.com/binder/prod_main/databricks-data-privacy-en_us-2.1.2/images/20260819T030319Z/Databricks Data Privacy/Includes/images/table_ai_desc.png)


### J2. Spalten

1. Ebenso wie bei der Tabellenbeschreibung finden Sie unter dem Tab "Overview", unterhalb der Darstellung des Schemas, eine Schaltfläche "AI Generate". Nach dem Klicken generiert DatabricksIQ eine Beschreibung für jede Spalte, wie im untenstehenden Bild gezeigt. Sie können diese ebenfalls zurücksetzen oder nach Bedarf anpassen.


![AI Generated Column Description](https://files.training.databricks.com/binder/prod_main/databricks-data-privacy-en_us-2.1.2/images/20260819T030319Z/Databricks Data Privacy/Includes/images/table_column_ai_desc.png)

## K. Insights
Sie können den **Tab Insights** im Catalog Explorer verwenden, **um die häufigsten aktuellen Abfragen und Benutzer einer beliebigen in Unity Catalog registrierten Tabelle anzuzeigen**. Der Tab Insights berichtet über häufige Abfragen und Benutzerzugriffe der letzten 30 Tage.

Sie benötigen die folgenden **Berechtigungen**, um häufige Abfragen und Benutzerdaten im Tab Insights anzuzeigen.
* **SELECT**-Privileg für die Tabelle.
* **USE SCHEMA**-Privileg für das übergeordnete Schema der Tabelle.
* **USE CATALOG**-Privileg für den übergeordneten Katalog der Tabelle.

Metastore-Administratoren verfügen standardmäßig über diese Berechtigungen.

Im Tab Insights für eine Tabelle können Sie Folgendes einsehen: 
1. Häufig verwendete Abfragen und Notebooks
1. Häufig verwendete Dashboards
1. Häufige Benutzer
1. Andere Tabellen, die häufig mit der betreffenden Tabelle verbunden (gejoint) werden

**Der Tab Insights kann auch dabei helfen, Tabellen zu identifizieren, die von Anwendungen nicht mehr verwendet werden. Diese Tabellen können dann für eine zukünftige Bereinigung getaggt werden.**
