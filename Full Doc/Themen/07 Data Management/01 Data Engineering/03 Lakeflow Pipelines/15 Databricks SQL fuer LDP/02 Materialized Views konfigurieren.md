# Standalone Materialized Views konfigurieren

Dieses Dokument beschreibt, wie sich bestehende Standalone Materialized Views beschreiben, aktualisieren, mit Zugriffsrechten versehen und in ihrem Runtime-Channel konfigurieren lassen.

## Abschnittsübersicht

1. [Eine Materialized View beschreiben](#beschreiben)
2. [Die Definition aktualisieren](#aktualisieren)
3. [Zugriffskontrolle](#zugriffskontrolle)
4. [Owner ändern](#owner)
5. [Runtime-Channel festlegen](#channel)
6. [Verhalten bei Verlust des Quellzugriffs](#quellzugriff)
7. [Quellen](#quellen)

---

## <a id="beschreiben">1. Eine Materialized View beschreiben</a>

Spalteninformationen und Datentypen lassen sich per `DESCRIBE`-Anweisung abrufen; erweiterte Metadaten (Owner, Speicherort, Erstellungszeit, Refresh-Status) über `DESCRIBE EXTENDED`. Alternativ steht der Catalog Explorer als UI-basierter Weg zur Verfügung, um Details einer Materialized View einzusehen.

## <a id="aktualisieren">2. Die Definition aktualisieren</a>

Um die Abfragedefinition einer Materialized View zu ändern, wird erneut eine `CREATE OR REPLACE MATERIALIZED VIEW`-Anweisung mit demselben Namen ausgeführt. Dies löst einen vollständigen Refresh mit der aktualisierten Definition aus.

```sql
CREATE OR REPLACE MATERIALIZED VIEW sales
TBLPROPERTIES ('pipelines.channel' = 'preview') AS ...
```

## <a id="zugriffskontrolle">3. Zugriffskontrolle</a>

Materialized Views unterstützen laut Doku umfangreiche Zugriffskontrollen, um Data Sharing zu ermöglichen, ohne potenziell private Daten offenzulegen ("Materialized views support rich access controls to support data-sharing while avoiding exposing potentially private data"). Ein Materialized-View-Owner oder ein Nutzer mit dem `MANAGE`-Privileg kann `SELECT`-Privilegien an andere Nutzer vergeben. Nutzer mit `SELECT`-Zugriff auf die Materialized View benötigen keinen `SELECT`-Zugriff auf die von der View referenzierten Tabellen.

Der `privilege_type` kann laut Doku `SELECT` oder `REFRESH` sein.

### Privilegien vergeben

```sql
GRANT <privilege_type> ON <mv_name> TO <principal>;
```

Beispiel:

```sql
CREATE MATERIALIZED VIEW mv_name AS SELECT * FROM source_table;
GRANT SELECT ON mv_name TO read_only_user;
GRANT SELECT ON mv_name TO refresh_user;
GRANT REFRESH ON mv_name TO refresh_user;
```

### Privilegien entziehen

```sql
REVOKE privilege_type ON <mv_name> FROM principal;
```

Beispiel:

```sql
REVOKE SELECT ON mv_name FROM read_only_user;
```

## <a id="owner">4. Owner ändern</a>

Der Owner-Wechsel erfolgt laut Doku ausschließlich über UI-Schritte im Catalog Explorer; ein SQL-Codebeispiel dafür wird auf der Seite nicht angegeben.

## <a id="channel">5. Runtime-Channel festlegen</a>

Materialized Views nutzen standardmäßig den "current"-Channel der zugrunde liegenden Pipeline. Über `TBLPROPERTIES ('pipelines.channel' = 'preview')` lässt sich stattdessen der Preview-Channel aktivieren (siehe Codebeispiel in Abschnitt 2).

## <a id="quellzugriff">6. Verhalten bei Verlust des Quellzugriffs</a>

**Wichtiger Hinweis:** Verliert der Owner den Zugriff auf die Quelltabellen, behalten Nutzer weiterhin Lesezugriff auf die Materialized View — Refreshes schlagen jedoch fehl, und die View wird zunehmend veraltet ("stale").

---

## <a id="quellen">7. Quellen</a>

1. Configure standalone materialized views (AWS): https://docs.databricks.com/aws/en/ldp/dbsql/materialized-configure
