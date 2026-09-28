# Berechtigungen für Governed Tags verwalten

Governed-Tag-Berechtigungen steuern, wer Tags erstellen, bearbeiten, zuweisen und löschen darf. Sie gelten auf zwei Ebenen: **Account-weit** (für alle Tags) oder auf **einzelnen Tags**.

## Berechtigungstypen

| Berechtigung | Zweck | Scope |
|---|---|---|
| `CREATE` | Neue Governed Tags erstellen | nur Account |
| `MANAGE` | Governed Tags bearbeiten, löschen, Berechtigungen zuweisen | Account oder einzelnes Tag |
| `ASSIGN` | Governed Tags auf Unity-Catalog-Objekte anwenden | Account oder einzelnes Tag |

## Wichtige Details

- Account-Admins besitzen standardmäßig alle drei Privilegien.
- Workspace-Admins besitzen standardmäßig `CREATE` auf Account-Ebene.
- Nutzer mit `CREATE` erhalten automatisch `MANAGE` auf die von ihnen erstellten Tags.
- **System-Tags** können auch mit `MANAGE`-Privileg nicht aktualisiert oder gelöscht werden.
- Die Verbreitung von Berechtigungsänderungen kann **bis zu 30 Sekunden oder länger** dauern.

## Berechtigungen zuweisen

**Auf Account-Ebene** (erfordert `MANAGE` auf Account-Ebene):

1. Zu **Catalog** → **Govern** → **Governed Tags** navigieren.
2. Tab **Account Permissions** auswählen.
3. Berechtigungen an Principals vergeben (Nutzer, Service Principals oder Gruppen).

**Auf einzelnen Tags:** analoger Ablauf, über den **Permissions**-Tab des jeweiligen Governed Tag.

## Quelle

- https://docs.databricks.com/aws/en/admin/governed-tags/manage-permissions
