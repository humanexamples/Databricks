# Secrets Utility (`dbutils.secrets`)

Befehle zum Speichern und Zugreifen auf sensible Credentials, ohne sie im Notebook-Code offenzulegen. Teil der [Databricks Utils](00%20Uebersicht.md)-Reihe.

## Befehlsübersicht

| Befehl | Signatur | Beschreibung |
|---|---|---|
| `get` | `get(scope: String, key: String): String` | liefert die String-Repräsentation eines Secret-Werts |
| `getBytes` | `getBytes(scope: String, key: String): byte[]` | liefert die Bytes-Repräsentation eines Secret-Werts |
| `list` | `list(scope: String): Seq` | listet Metadaten aller Secrets innerhalb eines Scopes (`SecretMetadata`-Objekte) |
| `listScopes` | `listScopes: Seq` | listet alle verfügbaren Secret-Scopes (`SecretScope`-Objekte) |
| `help` | `help()` / `help("<command-name>")` | zeigt verfügbare Befehle bzw. befehlsspezifische Dokumentation |

## Beispiele

```python
dbutils.secrets.get(scope="my-scope", key="my-key")
# Out[14]: '[REDACTED]'

dbutils.secrets.getBytes(scope="my-scope", key="my-key")
# Out[1]: b'a1!b2@c3#'

dbutils.secrets.list("my-scope")
# Out[10]: [SecretMetadata(key='my-key')]

dbutils.secrets.listScopes()
# Out[14]: [SecretScope(name='my-scope')]

dbutils.secrets.help()
dbutils.secrets.help("get")
```

## Zugriffsrechte und Redaction

**Wer lesen darf:** „Administratoren, Secret-Ersteller und Nutzer mit entsprechend erteilter Berechtigung können Databricks-Secrets lesen."

**Ausgabe-Redaction:** Secret-Werte, die in Notebooks angezeigt würden, werden von Databricks maskiert (angezeigt als `[REDACTED]`). Die Doku warnt jedoch ausdrücklich: „Es ist nicht möglich zu verhindern", dass autorisierte Nutzer die tatsächlichen Secret-Werte auslesen — Redaction schützt nur die Notebook-Ausgabe, nicht den Zugriff selbst.

**Verfügbarkeit:** Alle Befehle in Python, R und Scala nutzbar, sofern nicht anders angegeben.

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/databricks-utils#secrets-utility-dbutilssecrets

**Stand:** 2026-08-26.
