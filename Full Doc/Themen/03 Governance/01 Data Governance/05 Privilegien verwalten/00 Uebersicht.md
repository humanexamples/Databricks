# Privilegien verwalten — Überblick

## Wer darf Privilegien verwalten?

Anfangs haben Nutzer **keinen** Zugriff auf Daten in einem Metastore. Standardmäßig besitzen Databricks-Account-Admins, Workspace-Admins und Metastore-Admins Privilegien zur Verwaltung von Unity Catalog.

Objekteigentümer besitzen alle Privilegien auf ihrem Objekt und können diese an andere weitergeben. Privilegien können vergeben werden von:

- dem Eigentümer des Objekts,
- dem Eigentümer des übergeordneten Catalogs oder Schemas,
- einem Nutzer mit `MANAGE`-Privileg auf dem Objekt,
- einem Metastore-Admin.

## Grants anzeigen

Nutzer mit `MANAGE`-Privileg können alle Grants auf einem Objekt einsehen. **Aktuelle Einschränkung:** Nutzer mit `MANAGE`-Privileg auf einem Objekt können nicht alle Grants für dieses Objekt im `INFORMATION_SCHEMA` einsehen.

## Themen in diesem Kapitel

Die konzeptionelle Grundlage (Objekthierarchie, vollständige Privilegien-Referenztabelle, Vererbung) findet sich in [04 Access Control](../04%20Access%20Control/). Dieses Kapitel behandelt die praktische Anwendung:

1. **Vollständige `GRANT`/`REVOKE`/`SHOW GRANTS`-Syntax** — siehe [GRANT, REVOKE und SHOW GRANTS.md](GRANT%2C%20REVOKE%20und%20SHOW%20GRANTS.md)
2. **Verhalten einzelner Schlüsselprivilegien** (`ALL PRIVILEGES`, `MANAGE`, `READ FILES`/`WRITE FILES` u. a.) — siehe [Schluesselprivilegien im Detail.md](Schluesselprivilegien%20im%20Detail.md)
3. **Fertige Grant-Kombinationen für typische Szenarien** (Leserecht, Tabellen anlegen, Volume-Zugriff, `COPY INTO` u. a.) — siehe [Grant-Rezepte fuer haeufige Szenarien.md](Grant-Rezepte%20fuer%20haeufige%20Szenarien.md)
4. **Eigentümerschaft übertragen** (`ALTER ... OWNER TO`) — siehe [Eigentuemerschaft (OWNER TO).md](Eigentuemerschaft%20%28OWNER%20TO%29.md)
5. **Prinzipal-Referenzierung** (Nutzer, Gruppen, Service Principals, Backtick-Regel) — siehe [Prinzipal-Typen.md](Prinzipal-Typen.md)
6. **Standardrechte ohne expliziten Grant** — siehe [Standardrechte ohne expliziten Grant.md](Standardrechte%20ohne%20expliziten%20Grant.md)
7. **Checkliste häufiger Fehlerquellen** — siehe [Haeufige Stolpersteine.md](Haeufige%20Stolpersteine.md)
8. **Admin-Rollen** — siehe [Admin-Privilegien.md](Admin-Privilegien.md)
9. **Zugriff anfragen (Request for Access)** — siehe [Access Request Destinations.md](Access%20Request%20Destinations.md)

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/
