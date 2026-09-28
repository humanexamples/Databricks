# Predictive Optimization — Aktivierung, Vererbung und Berechtigungen

## 1. Vererbungsmodell

PO wird **von oben nach unten** vererbt. Jede Ebene kann die Einstellung der übergeordneten Ebene überschreiben.

```
Account (Standard für alle Metastores)
  └─ Catalog   (erbt vom Account, überschreibbar)
       └─ Schema  (erbt vom Catalog, überschreibbar)
            └─ Tabelle (erbt vom Schema, überschreibbar)
```

| Wert | Bedeutung |
|---|---|
| `ENABLE` | PO explizit **ein** für dieses Objekt (und alles darunter, das `INHERIT` hat) |
| `DISABLE` | PO explizit **aus** für dieses Objekt (und alles darunter, das `INHERIT` hat) |
| `INHERIT` | Einstellung der übergeordneten Ebene übernehmen (Standard) |

> **Falle:** Ein explizites `DISABLE` auf Catalog-, Schema- oder Tabellenebene **bleibt bestehen**, auch wenn PO später auf Account-Ebene aktiviert wird. Man muss es aktiv auf `ENABLE` oder `INHERIT` zurücksetzen.
>
> Umgekehrt gilt dasselbe: Wird PO auf Account-Ebene **deaktiviert**, bleibt es für Kataloge und Schemas mit explizitem `ENABLE` **aktiv**.

---

## 2. Aktivierung auf Account-Ebene

Account Admin: **Account Console → Settings → Feature enablement → Predictive optimization** → *Enabled* (bzw. *Disabled*).

Metastores in Regionen ohne PO-Unterstützung werden dabei nicht aktiviert.

## 3. Aktivierung auf Catalog-, Schema- und Tabellenebene

```sql
ALTER CATALOG [catalog_name] { ENABLE | DISABLE | INHERIT } PREDICTIVE OPTIMIZATION;
ALTER { SCHEMA | DATABASE } schema_name { ENABLE | DISABLE | INHERIT } PREDICTIVE OPTIMIZATION;
ALTER TABLE table_name { ENABLE | DISABLE | INHERIT } PREDICTIVE OPTIMIZATION;
```

**Beispiele:**

```sql
-- Für den ganzen Produktionskatalog einschalten
ALTER CATALOG prod ENABLE PREDICTIVE OPTIMIZATION;

-- Sandbox-Schema ausnehmen (z. B. Kosten sparen)
ALTER SCHEMA prod.sandbox DISABLE PREDICTIVE OPTIMIZATION;

-- Einzelne Tabelle wieder dem Schema folgen lassen
ALTER TABLE prod.sales.orders INHERIT PREDICTIVE OPTIMIZATION;
```

---

## 4. Erforderliche Berechtigungen

| Ebene | Erforderliches Privileg |
|---|---|
| Account | **Account Admin** |
| Catalog | Catalog Owner **oder** `MANAGE` |
| Schema | Schema Owner **oder** `MANAGE` |
| Tabelle | Table Owner **oder** `MANAGE` |

> `MODIFY` oder `SELECT` reichen **nicht**, um PO umzuschalten.

---

## <a id="status">5. Status prüfen</a>

```sql
DESCRIBE CATALOG EXTENDED prod;
DESCRIBE SCHEMA  EXTENDED prod.sales;
DESCRIBE TABLE   EXTENDED prod.sales.orders;
```

Die Ausgabe enthält ein Feld **„Predictive Optimization"** mit dem wirksamen Status (`ENABLE`/`DISABLE`) und dem Hinweis, ob er **explizit gesetzt** oder **geerbt** ist (und von welchem übergeordneten Objekt). So erkennt man, **auf welcher Ebene** eine Einstellung wirkt.

---

## 6. Typische Szenarien

| Ziel | Vorgehen |
|---|---|
| PO überall, außer für Test-Schemas | Account `ENABLE`, Test-Schemas `DISABLE` |
| PO nur für einen Katalog | Account `DISABLE`, Katalog `ENABLE` |
| Eine teure, selten genutzte Tabelle ausnehmen | `ALTER TABLE … DISABLE PREDICTIVE OPTIMIZATION` |
| Nach einem Test alles wieder zentral steuern | Untergeordnete Objekte auf `INHERIT` zurücksetzen |

## Quellen

- [Predictive optimization for Unity Catalog managed tables](https://docs.databricks.com/aws/en/optimizations/predictive-optimization)
- [ALTER CATALOG](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-catalog) · [ALTER SCHEMA](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-schema) · [ALTER TABLE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-table)
