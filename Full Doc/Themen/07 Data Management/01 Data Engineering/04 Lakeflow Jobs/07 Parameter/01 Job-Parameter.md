# Job-Parameter konfigurieren

Job-Parameter sind Key-Value-Paare, die Jobs mit statischen oder dynamischen Standardwerten parametrisieren — bei neuen Läufen optional überschreibbar. Parameter-Schlüssel dürfen nur Unterstriche, Bindestriche, Punkte und alphanumerische Zeichen enthalten. Werte sind Strings oder dynamische Wertreferenzen.

Job-Parameterwerte können auch beliebiges gültiges JSON sein, einschließlich Arrays (siehe `Task-Parameter.md` zur Nutzung von JSON-Array-Parametern in Tasks).

## Hinzufügen/Bearbeiten

1. **Jobs & Pipelines** in der Sidebar.
2. Optional Filter **Jobs**/**Owned by me**.
3. Job über den Namenslink auswählen.
4. Job-Details-Sidebar → **Edit parameters**.
5. Parameter über **Key**/**Value**-Felder hinzufügen/ändern.
6. Papierkorb-Icon zum Entfernen.
7. **Save**.

Über **{ }** lassen sich verfügbare dynamische Wertreferenzen zur Einfügung in Value-Felder anzeigen.

## Weitergabe an Tasks (Pushdown)

Unterschiedliche Task-Typen erhalten Job-Parameter über unterschiedliche Mechanismen. Teilen sich Job- und Task-Parameter denselben Schlüssel, hat der Job-Parameter bei Key-Value-Parameter-Tasks Vorrang. JSON-Array-Parameter-Tasks benötigen dagegen die explizite Referenz `{{job.parameters.<name>}}`.

## Mit anderen Parametern ausführen

Konfigurierte Job-Parameter lassen sich bei „Run now with different parameters" überschreiben/ergänzen — ebenso bei der Reparatur fehlgeschlagener/übersprungener Tasks.

## Quelle

- https://docs.databricks.com/aws/en/jobs/job-parameters
