# Häufige Stolpersteine

Checkliste wiederkehrender Fehlerquellen beim Vergeben von Unity-Catalog-Privilegien — jeder Punkt ist an anderer Stelle in diesem Kapitel bzw. in [04 Access Control](../04%20Access%20Control/) ausführlich belegt.

1. **`SELECT` allein reicht nicht.** Ohne `USE CATALOG` auf dem Catalog und `USE SCHEMA` auf dem Schema bleibt ein `SELECT`-Grant auf einer Tabelle wirkungslos (siehe [Berechtigungskonzepte.md](../04%20Access%20Control/Berechtigungskonzepte.md) und [Schluesselprivilegien im Detail.md](Schluesselprivilegien%20im%20Detail.md)).
2. **`WRITE FILES` ohne `READ FILES` schlägt fehl.** Schreibversuche auf einer External Location, bei der nur `WRITE FILES` (nicht zusätzlich `READ FILES`) vergeben ist, enden mit `PERMISSION_DENIED`.
3. **`MODIFY` setzt `SELECT` auf derselben Tabelle voraus** — nicht nur die Elternprivilegien `USE CATALOG`/`USE SCHEMA`.
4. **`ALL PRIVILEGES` ist kein Freifahrtschein.** Es deckt weder `MANAGE`, `READ METADATA`, `EXTERNAL USE SCHEMA` noch `EXTERNAL USE LOCATION` ab — diese vier müssen immer explizit vergeben werden.
5. **`MANAGE` ist nicht gleichbedeutend mit Ownership.** Ein Nutzer mit `MANAGE` kann Rechte verwalten und Eigentümerschaft übertragen, besitzt aber nicht automatisch `SELECT`/`MODIFY`/etc. — er müsste sich diese explizit selbst zuweisen.
6. **External-Location-Rechte wirken nicht auf Nachbar-/Elternpfade.** Ein Grant auf `.../raw-data` erlaubt keinen Zugriff auf `.../raw-data/../` oder `.../json-data` daneben (siehe [Grant-Rezepte fuer haeufige Szenarien.md](Grant-Rezepte%20fuer%20haeufige%20Szenarien.md), Rezept e).
7. **Views/Functions/Models: Eigentumsübertragung an beliebige Dritte nur durch Metastore-Admins.** Normale Owner bzw. `MANAGE`-Inhaber dürfen die Eigentümerschaft nur an sich selbst oder eine eigene Gruppe übertragen (siehe [Eigentuemerschaft (OWNER TO).md](Eigentuemerschaft%20%28OWNER%20TO%29.md)).
8. **`samples`-Catalog ist nicht änderbar.** `GRANT`/`REVOKE` auf dem mitgelieferten `samples`-Catalog werden nicht unterstützt.

## Verwandte, aber getrennte Governance-Mechanismen

`GRANT`/`REVOKE` ist nicht der einzige Zugriffssteuerungs-Mechanismus in Databricks — folgende Themen wirken zusammen oder werden oft damit verwechselt:

- **Row Filters und Column Masks** — zeilen-/spaltenweise Einschränkung des Datenzugriffs, siehe [07 Filters und Masks](../07%20Filters%20und%20Masks/).
- **Attribute-Based Access Control (ABAC)** — taggesteuertes Policy-System, das auch dynamisch Privilegien vergeben kann, siehe [08 ABAC](../08%20ABAC/).
- **Workspace-Catalog-Bindung** — schränkt den Zugriff auf einen Catalog auf bestimmte Workspaces ein, unabhängig von individuellen `GRANT`-Privilegien, siehe [04 Access Control/Workspace-Catalog-Bindung.md](../04%20Access%20Control/Workspace-Catalog-Bindung.md).
- **Lakeflow-Jobs-Berechtigungen** — ein separates System (Job-ACLs plus Run-as-Identität), das steuert, wer einen Job sehen/ausführen/verwalten darf; wirkt zusätzlich zu, nicht anstelle von, Unity-Catalog-Privilegien der Run-as-Identität, siehe [Lakeflow Jobs/06 Berechtigungen und Monitoring/Privilegien.md](../../../Data%20Management/Data%20Engineering/Lakeflow%20Jobs/06%20Berechtigungen%20und%20Monitoring/Privilegien.md).

## Quelle

- Zusammenfassung bereits an anderer Stelle in diesem Kapitel belegter Fakten.
