## Volume

Innerhalb eines [Schemas](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#schema) ist ein **Volume** ein sicherbares Objekt für unstrukturierte Daten im Cloud-Speicher. Volumes können verwaltet (managed, Speicherort von Unity Catalog bestimmt) oder extern (external, Speicherpfad selbst angegeben) sein. Anders als Tabellen und Views unterstützen Volumes keine SQL-Abfrageoperationen — sie bieten dateibasierten Lese- und Schreibzugriff auf Daten im Cloud-Speicher. Databricks kennt folgende Volume-Typen:

- **Managed Volumes** sind Volumes, bei denen der Speicherort von Unity Catalog bestimmt wird. Wichtig: Die Daten selbst liegen weiterhin in deinem Cloud-Account. Databricks empfiehlt Managed Volumes, damit Unity Catalog automatisch den gesamten Datenzugriff regelt.
- **External Volumes** sind Volumes, bei denen du den Speicherort selbst angibst. External Volumes eignen sich, wenn externer Systemzugriff außerhalb von Databricks benötigt wird — dabei ist zu beachten, dass externe Systeme die Unity-Catalog-Governance umgehen können.

Die folgende Tabelle fasst wichtige Details zu Volumes zusammen:

| Detail | Beschreibung |
| :-------------------- | :----------------------------------------------------------- |
| Nutzungsprivilegien | Um auf Dateien in einem Volume zuzugreifen, benötigt ein Nutzer `USE CATALOG` auf dem übergeordneten Katalog und `USE SCHEMA` auf dem übergeordneten Schema ([Nutzungsprivilegien](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#usage-privileges)), zusätzlich zu `READ VOLUME` oder `WRITE VOLUME` auf dem Volume. |
| Lese- und Schreibzugriff | `READ VOLUME` gewährt die Fähigkeit, in einem Volume gespeicherte Dateien und Verzeichnisse zu lesen; `WRITE VOLUME` gewährt die Fähigkeit, Dateien hinzuzufügen, zu ändern oder zu löschen. |
| Vererbung | Auf Schema- oder Katalog-Ebene vergebenes `READ VOLUME` und `WRITE VOLUME` gilt für alle aktuellen und künftigen Volumes in diesem Schema bzw. Katalog. Siehe [Privilegienvererbung](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#inheritance). |

Weitere Informationen zu Volumes siehe [Was sind Unity-Catalog-Volumes?](https://docs.databricks.com/aws/en/volumes/).

Volumes ermöglichen die Governance über nicht-tabellarische Datensätze und repräsentieren ein logisches Speichervolumen an einem Cloud-Objektspeicherort. Sie bieten Funktionen zum Zugriff auf, zur Speicherung, Governance und Organisation von Dateien.

Während Tabellen Governance über tabellarische Datensätze bieten, ergänzen Volumes die Governance um nicht-tabellarische Datensätze. Volumes können verwendet werden, um Dateien in **_jedem_** Format zu speichern und darauf zuzugreifen, einschließlich strukturierter, semi-strukturierter und unstrukturierter Daten.

Beim Zugriff auf Daten in Volumes wird der von Unity Catalog bereitgestellte Pfad verwendet, der stets diesem Format folgt: `/Volumes/catalog_name/schema_name/volume_name/`.

```python
-- Führen Sie den folgenden Befehl aus, um eine Liste der Volumes in einem bestimmten Schema anzuzeigen.
SHOW VOLUMES IN catalog_name.schema_name;
```

```python
-- Verwenden Sie die DESCRIBE VOLUME-Anweisung, um die Metadaten eines Volumes zurückzugeben.
DESCRIBE VOLUME myvolume;
```

```python
-- Verwenden Sie die LIST-Anweisung, um die verfügbaren Dateien in einem Verzeichnis aufzulisten.
LIST '/Volumes/catalog_name/schema_name/volume_name/'

-- ADLS 2
LIST 'abfss://container-name@storage-account-name.dfs.core.windows.net/path/to/data'

-- S3
LIST 's3://bucket-name/path/to/data'

-- GCS
LIST 'gs://bucket-name/path/to/data'
```

```python
spark.sql(f"LIST '{my_vol_path}/bright_home_orders'").display()
```

```python
CREATE VOLUME IF NOT EXISTS trigger_storage_location
```

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### CREATE VOLUME

Legt ein Managed oder External Volume an. Bei External Volumes wird der Speicherpfad explizit angegeben.

```sql
-- External Volume mit eigenem Speicherort
CREATE EXTERNAL VOLUME my_catalog.my_schema.my_external_volume
  LOCATION 's3://my-bucket/my-location/my-path'
  COMMENT 'This is my example external volume on S3';

-- Managed Volume mit vollqualifiziertem Namen
CREATE VOLUME my_catalog.my_schema.my_volume;
```

Quelle: [CREATE VOLUME](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-volume)

### ALTER VOLUME

Ändert Namen, Besitzer oder Tags eines bestehenden Volumes.

```sql
ALTER VOLUME my_volume RENAME TO new_name_volume;
ALTER VOLUME my_volume SET TAGS ('tag1' = 'val1', 'tag2' = 'val2');
```

Quelle: [ALTER VOLUME](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-volume)

### DROP VOLUME

Löscht ein Volume (nur die Metadaten-Registrierung; bei External Volumes bleiben die zugrunde liegenden Dateien im Cloud-Speicher erhalten).

```sql
DROP VOLUME IF EXISTS my_catalog.my_schema.my_volume;
```

Quelle: [DROP VOLUME](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-volume)

### DESCRIBE VOLUME

Zeigt Metadaten eines Volumes an, u. a. Owner, Speicherort und Volume-Typ (`MANAGED`/`EXTERNAL`).

```sql
DESCRIBE VOLUME my_external_volume;
```

Quelle: [DESCRIBE VOLUME](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-volume)

### SHOW VOLUMES

Listet die für den Nutzer sichtbaren Volumes auf, optional eingeschränkt auf ein Schema oder gefiltert per `LIKE`-Muster.

```sql
SHOW VOLUMES IN machine_learning;
SHOW VOLUMES LIKE 'a*';
```

Quelle: [SHOW VOLUMES](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-volumes)

### LIST

Listet Dateien unter einem Pfad auf (z. B. innerhalb eines Volumes oder eines Cloud-Speicherorts), optional mit expliziter Credential und Ergebnisbegrenzung.

```sql
LIST 's3://us-east-1-dev/some_dir' WITH (CREDENTIAL aws_some_dir) LIMIT 2;
```

Quelle: [LIST](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-list)
