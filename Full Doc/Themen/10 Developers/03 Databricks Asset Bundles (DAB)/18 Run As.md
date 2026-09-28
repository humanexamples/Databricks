# Die `run_as`-Einstellung

Trennt die Deployment-Identität (wer das Bundle deployt) von der Ausführungsidentität (wer die deployten Ressourcen tatsächlich ausführt). Bereits kurz erwähnt in [07 Deployment-Modi und Authentifizierung.md](07%20Deployment-Modi%20und%20Authentifizierung.md), Abschnitt 2 — hier im Detail. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Syntax und Geltungsbereich](#syntax)
2. [Unterstützte Identitäten](#identitaeten)
3. [Ressourcen-Support je nach Identitätskonstellation](#ressourcen-support)
4. [Best Practices](#best-practices)
5. [Quelle](#quelle)

---

## <a id="syntax">1. Syntax und Geltungsbereich</a>

`run_as` lässt sich an zwei Stellen konfigurieren:

- **Top-Level:** gilt für alle Bundle-Ressourcen.
- **Innerhalb eines Targets:** gilt nur für dieses Deployment-Ziel.

```yaml
bundle:
  name: example
  run_as:
    service_principal_name: 'ID-here'
```

## <a id="identitaeten">2. Unterstützte Identitäten</a>

| Feld | Format |
|---|---|
| `user_name` | E-Mail-Adresse |
| `service_principal_name` | Application-ID |

**Einschränkung für Nicht-Admins:** Nicht-administrative Nutzer können dieses Feld **nur auf ihre eigene E-Mail-Adresse** setzen.

## <a id="ressourcen-support">3. Ressourcen-Support je nach Identitätskonstellation</a>

| Konstellation | Unterstützte Ressourcen |
|---|---|
| Deployer-Identität und `run_as`-Identität sind **identisch** | alle Bundle-Ressourcen |
| Deployer-Identität und `run_as`-Identität **unterscheiden sich** | **nur** Jobs und Pipelines |

**Nicht unterstützt:** `run_as` wird für **Model-Serving-Endpoints nicht unterstützt** — sind solche Ressourcen in einem Bundle mit konfiguriertem `run_as` definiert, tritt ein Fehler auf.

## <a id="best-practices">4. Best Practices</a>

Für Production-Targets werden **Service Principals** empfohlen (siehe auch die Production-Modus-Empfehlung in [07 Deployment-Modi und Authentifizierung.md](07%20Deployment-Modi%20und%20Authentifizierung.md), Abschnitt 2):

- stellt über `CAN_USE`-Berechtigungen eine korrekte Autorisierung sicher,
- entkoppelt Ausführungsrechte von Deployment-Rechten,
- ermöglicht strengere Berechtigungskonfiguration für Production-Workflows.

Service Principals erscheinen als Application-IDs, abrufbar über die Workspace-Admin-Einstellungen.

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/bundles/run-as

**Stand:** 2026-08-26.
