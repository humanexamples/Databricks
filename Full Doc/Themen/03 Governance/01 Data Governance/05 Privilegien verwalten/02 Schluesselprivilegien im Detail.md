# Schlüsselprivilegien im Detail

Ergänzt die tabellarische Referenz in [04 Access Control/Privilegien-Referenz.md](../04%20Access%20Control/Privilegien-Referenz.md) um die genauen Verhaltensregeln, Abhängigkeiten und Ausnahmen einzelner Privilegien — verifiziert gegen AWS- und Azure-Doku (wortgleich).

## `ALL PRIVILEGES`

Ein besonderes Privileg, das einem Nutzer erlaubt, alle Fähigkeiten auf dem Securable-Objekt und dessen Kindobjekten auszuüben — impliziert alle für einen Objekttyp zutreffenden Privilegien, ohne dass jedes einzeln explizit gewährt wird.

- **Anzeige:** Beim Auflisten von Berechtigungen über die API oder `SHOW GRANTS` für einen Nutzer mit `ALL PRIVILEGES` wird nur `ALL PRIVILEGES` zurückgegeben, nicht die einzelnen implizierten Privilegien wie `SELECT` oder `MODIFY`.
- **Dynamik:** `ALL PRIVILEGES` wird zum Zeitpunkt der Zugriffsprüfung neu ausgewertet, nicht zum Zeitpunkt des Grants — künftig neu hinzukommende Privilegien für den Objekttyp sind automatisch mit eingeschlossen.
- **Ausnahme:** umfasst nicht `EXTERNAL USE SCHEMA`, `EXTERNAL USE LOCATION`, `MANAGE` oder `READ METADATA` (siehe [GRANT, REVOKE und SHOW GRANTS.md](GRANT%2C%20REVOKE%20und%20SHOW%20GRANTS.md)).

## `OWNERSHIP` (Eigentümerschaft)

Objekt-Owner können automatisch alle Fähigkeiten auf dem eigenen Objekt ausüben. Ownership wird **nicht** nach unten vererbt — Objekt-Owner besitzen jedoch automatisch die Fähigkeit, alle Kindobjekte zu verwalten. Beispiel: Der Owner eines Catalogs besitzt nicht automatisch die Kind-Schemas, kann sie aber verwalten. Der ursprüngliche Ersteller eines Objekts wird automatisch dessen Owner (ausführliche Syntax zur Übertragung siehe [Eigentuemerschaft (OWNER TO).md](Eigentuemerschaft%20%28OWNER%20TO%29.md)).

## `MANAGE` — ähnlich, aber nicht gleich Ownership

Erlaubt einem Nutzer, Privilegien auf einem Objekt zu verwalten, dessen Ownership zu übertragen und es zu löschen, **ohne** dessen Owner zu sein.

**Entscheidender Unterschied:** Nutzern mit `MANAGE` werden nicht automatisch alle Privilegien auf dem Objekt gewährt — jedes einzelne Privileg muss separat gewährt werden. Allerdings können sich Nutzer mit `MANAGE` diese Privilegien explizit **selbst** zuweisen.

**Vererbung von `MANAGE` selbst:** Wird `MANAGE` auf einem Container-Objekt gewährt, erhält der Nutzer `MANAGE` auch auf allen Kindobjekten. Wird beispielsweise `MANAGE` auf einem Catalog gewährt, wird es dadurch auch explizit auf allen Kind-Schemas und -Tables gewährt.

`MANAGE` ist **nicht** in `ALL PRIVILEGES` enthalten und muss stets explizit vergeben werden.

## `CREATE TABLE`, `CREATE SCHEMA`, `CREATE VOLUME`

Für alle drei gilt dasselbe Muster: Das Erstell-Privileg allein reicht nicht.

- `CREATE SCHEMA`: Nutzer muss zusätzlich `USE CATALOG` auf dem Catalog besitzen.
- `CREATE TABLE`: Nutzer muss zusätzlich `USE CATALOG` auf dem Catalog **und** `USE SCHEMA` auf dem Schema besitzen, in dem die Table/View angelegt wird.
- `CREATE VOLUME`: identisches Muster — `USE CATALOG` **und** `USE SCHEMA` auf den jeweiligen Elternobjekten zusätzlich nötig.

## `SELECT` / `MODIFY`

- `SELECT`: erlaubt das Selektieren aus Table, View oder Materialized View. Nutzer muss zusätzlich `USE CATALOG` auf dem Catalog und `USE SCHEMA` auf dem Schema besitzen.
- `MODIFY`: erlaubt Einfügen, Aktualisieren und Löschen von Daten in einer Table. Nutzer muss zusätzlich `SELECT` auf **derselben** Table, `USE SCHEMA` auf dem Schema und `USE CATALOG` auf dem Catalog besitzen. **`MODIFY` setzt also `SELECT` auf derselben Tabelle voraus.**

## `READ VOLUME` / `WRITE VOLUME`

Beide erfordern zusätzlich `USE SCHEMA` auf dem übergeordneten Schema und `USE CATALOG` auf dem übergeordneten Catalog. `WRITE VOLUME` erlaubt das Hinzufügen, Entfernen oder Ändern von Dateien/Verzeichnissen in einem Volume; `READ VOLUME` das Lesen.

## `READ FILES` / `WRITE FILES` (External Location)

**Wichtige Abhängigkeit:** `WRITE FILES` erfordert, dass `READ FILES` **ebenfalls** auf derselben External Location gewährt ist — Schreiboperationen auf Cloud-Object-Storage beinhalten Metadaten-Prüfungen und Pfad-Validierungen, die Lesezugriff voraussetzen. Ein Principal mit nur `WRITE FILES` erhält beim Schreibversuch einen `PERMISSION_DENIED`-Fehler.

Databricks rät explizit von direktem Dateizugriff über External Locations ab: Lesezugriff auf Daten im Cloud-Object-Storage sollte stattdessen über Volumes und das `READ VOLUME`-Privileg verwaltet werden (analog für `WRITE FILES`/`WRITE VOLUME`).

## `CREATE EXTERNAL TABLE`

Erlaubt das Anlegen von External Tables direkt im eigenen Cloud-Tenant, unter Verwendung einer External Location oder eines Storage Credentials. Databricks empfiehlt, dieses Privileg auf einer External Location statt auf einem Storage Credential zu vergeben, da es pfadgebunden ist — das ermöglicht mehr Kontrolle darüber, wo Nutzer External Tables im Cloud-Tenant anlegen können.

## `EXECUTE`

Erlaubt das Aufrufen einer Function oder das Laden eines registrierten Models für Inferenz. Bei Functions gewährt `EXECUTE` außerdem die Möglichkeit, Function-Definition und -Metadaten einzusehen. Nutzer muss zusätzlich `USE CATALOG` auf dem Catalog und `USE SCHEMA` auf dem Schema besitzen.

## `MANAGE` vs. `READ METADATA` als „Kind-Privileg"

`READ METADATA` ist ein Kind-Privileg von `MANAGE`. Wie `MANAGE` ist es nicht in `ALL PRIVILEGES` enthalten und muss explizit gewährt werden. Es erlaubt, sämtliche eigentümersichtbaren Metadaten eines Objekts einzusehen (inkl. Grants, Row-Filter, Column-Masks, ABAC-Policies), aber **nicht**, das Objekt zu ändern oder seine Daten zu lesen.

## Quellen

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/privileges
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-privileges
