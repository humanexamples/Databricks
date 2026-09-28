# Administration und private Netzwerke

Behandelt das Aktivieren/Deaktivieren von Git Folders per API sowie zwei Wege, private/On-Premises-Git-Server anzubinden: den klassischen Git-Server-Proxy und Serverless Private Git (PrivateLink-basiert). Teil der [Git Folders (Repos)](01%20Grundlagen.md)-Reihe.

## Abschnittsübersicht

1. [Git Folders per API aktivieren/deaktivieren](#enable-disable)
2. [Git-Server-Proxy: wann benötigt](#proxy-bedarf)
3. [Git-Server-Proxy: Architektur und Einrichtung](#proxy-einrichtung)
4. [Git-Server-Proxy: Einschränkungen](#proxy-einschraenkungen)
5. [Serverless Private Git: Vorteile](#serverless-vorteile)
6. [Serverless Private Git: Einrichtung](#serverless-einrichtung)
7. [Serverless Private Git: Konfigurationsdatei](#serverless-config)
8. [Serverless Private Git: Einschränkungen](#serverless-einschraenkungen)
9. [Quelle](#quelle)

---

## <a id="enable-disable">1. Git Folders per API aktivieren/deaktivieren</a>

„Databricks Git Folders sind standardmäßig für neue Workspaces aktiviert." Workspace-Admins verwalten dies auf zwei Wegen.

**Methode 1 — Notebook:** Ein Notebook „Enable a Databricks Git folder" lässt sich direkt in den Workspace importieren und bietet einen interaktiven Weg, das Feature umzuschalten.

**Methode 2 — Databricks CLI:**

```bash
# Aktivieren
databricks workspace-conf set-status --json '{"enableProjectTypeInWorkspace": "true"}'

# Deaktivieren
databricks workspace-conf set-status --json '{"enableProjectTypeInWorkspace": "false"}'
```

Zentraler Konfigurationsparameter: `enableProjectTypeInWorkspace` (boolescher Wert).

## <a id="proxy-bedarf">2. Git-Server-Proxy: wann benötigt</a>

Der Proxy wird benötigt, wenn der Git-Server „privat, On-Premises oder hinter einer Firewall ist, etwa GitHub Enterprise Server, Bitbucket Server, GitLab Self-Managed oder Azure DevOps Server." Cloud-gehostete Dienste wie GitHub.com und GitLab.com benötigen ihn nicht.

## <a id="proxy-einrichtung">3. Git-Server-Proxy: Architektur und Einrichtung</a>

**Architektur:** Der Proxy leitet Git-Befehle von der Databricks-Control-Plane an einen Proxy-Cluster in der Compute Plane des Workspace weiter. Dieser Cluster empfängt Git-Befehle und leitet sie an den privaten Git-Server weiter, ohne die Sicherheitsarchitektur zu kompromittieren.

**Voraussetzungen:** Git-Folders-Feature aktiviert; Git-Server erreichbar aus der VPC des Workspace; HTTPS und PATs auf dem Git-Server aktiviert; Workspace-Admin-Zugriff zum Erstellen von Compute-Ressourcen.

**Schritt 1 — Git-Server-Instanz vorbereiten:** eine statische Outbound-IP-Adresse für den Proxy-Cluster über ein NAT-Gateway routen; diese IP zur Allowlist des Git-Servers hinzufügen; den Git-Server für HTTPS-Verbindungen konfigurieren.

**Schritt 2 — Enablement-Notebook ausführen:** das Databricks-bereitgestellte Notebook (auf GitHub verfügbar) ausführen — erstellt eine Single-Node-Compute-Ressource namens „Databricks Git Proxy" (ohne Auto-Termination) und aktiviert die Feature Flags für das Git-Request-Proxying.

**Schritt 3 — Konfiguration validieren:** ein Repository vom privaten Git-Server über den Proxy klonen, um die Funktionsfähigkeit zu bestätigen.

**Schritt 4 — Nutzer-Credentials konfigurieren:** Nutzer konfigurieren ihre Git-Credentials; keine weiteren Repository-Erstellungsschritte nötig.

**Sicherheitskonfiguration:** `CAN ATTACH TO`-Berechtigungen für alle Workspace-Nutzer vom Proxy-Cluster entfernen, um unautorisierte Workload-Ausführung zu verhindern.

**Troubleshooting-Umgebungsvariablen:**

| Variable | Zweck |
|---|---|
| `GIT_PROXY_ENABLE_SSL_VERIFICATION` | auf `false` setzen für selbstsignierte Zertifikate |
| `GIT_PROXY_CA_CERT_PATH` | Pfad zur CA-Zertifikatsdatei |
| `GIT_PROXY_HTTP_PROXY` | HTTPS-URL für den Netzwerk-Firewall-Proxy |
| `GIT_PROXY_CUSTOM_HTTP_PORT` | benutzerdefinierte Git-Server-Portnummer |

## <a id="proxy-einschraenkungen">4. Git-Server-Proxy: Einschränkungen</a>

- SSH-Transport wird nicht unterstützt — nur HTTPS funktioniert.
- GPG-Commit-Signierung wird nicht unterstützt.
- Jeder Workspace benötigt einen eigenen Proxy-Cluster.
- Der gesamte Git-Folders-Traffic läuft über den Proxy, auch für öffentliche Repositories.

## <a id="serverless-vorteile">5. Serverless Private Git: Vorteile</a>

„Databricks Serverless Private Git erlaubt es, einen Databricks-Workspace über Serverless Compute und PrivateLink mit einem privaten Git-Server zu verbinden." Das Feature befindet sich in Public Preview; Compute- und Netzwerkkosten fallen an, wenn Serverless-Ressourcen sich mit externen Systemen verbinden.

**Vorteile gegenüber dem Git-Server-Proxy:**

1. **Ressourceneffizienz:** Serverless Compute wird nur bei eingehenden Git-Requests bezogen und bleibt sonst inaktiv — im Gegensatz zu Proxy-Clustern, die dauerhaft laufen müssen.
2. **Sicherheit:** nutzt PrivateLink für sichere Verbindungen zu privaten Git-Instanzen.

## <a id="serverless-einrichtung">6. Serverless Private Git: Einrichtung</a>

**Voraussetzungen:** VPC-Endpoint-Service für den privaten Git-Server hinter einem Network Load Balancer (NLB); administrativer Zugriff zum Erstellen von AWS-Interface-VPC-Endpoints in der Databricks Network Connectivity Configuration (NCC).

**Schritte:**

1. VPC-Endpoint-Service für den Zugriff auf den privaten Git-Server konfigurieren.
2. Einen AWS-Interface-VPC-Endpoint je Git-Server in der Databricks-NCC erstellen.
3. Eine Network Connectivity Configuration je Workspace etablieren (eine einzelne NCC kann mehrere Git-Server mit derselben Konfiguration bedienen).
4. Private-Endpoint-Regeln zur NCC hinzufügen.
5. Mindestens zehn Minuten nach dem NCC-Setup warten.
6. Serverless Private Git in den Workspace-Einstellungen aktivieren.
7. Eine Git-Operation ausführen — UI-Indikatoren bestätigen die Aktivierung.

**Hinweis:** Nach der Konfiguration hat Serverless Private Git Vorrang vor dem klassischen Git-Proxy und Enterprise Private Git — laufende Git-Proxy-Cluster sollten pausiert werden.

## <a id="serverless-config">7. Serverless Private Git: Konfigurationsdatei</a>

Datei `/Workspace/.git_settings/config.json` anlegen:

```json
{
  "default": { },
  "remotes": [ ]
}
```

**Felder im `default`-Abschnitt:**

| Feld | Typ | Pflicht | Standard | Zweck |
|---|---|---|---|---|
| `sslVerify` | boolean | Nein | `true` | SSL-Zertifikatsvalidierung |
| `caCertPath` | string | Nein | `""` | Workspace-Pfad zum benutzerdefinierten CA-Zertifikat |
| `httpProxy` | string | Nein | `""` | HTTP-Proxy-Routing |
| `customHttpPort` | integer | Nein | unspezifiziert | benutzerdefinierter Git-Server-HTTP-Port |

**Felder im `remotes`-Abschnitt** (je Eintrag `urlPrefix` erforderlich): dieselben Felder wie oben, zusätzlich `urlPrefix` (string, Pflicht) für das Matching der Git-Remote-URL.

**Minimalbeispiel:**

```json
{
  "default": {
    "sslVerify": false
  }
}
```

**Umfassendes Beispiel:**

```json
{
  "default": {
    "sslVerify": true,
    "caCertPath": "/Workspace/my_ca_cert.pem",
    "httpProxy": "https://git-proxy-server.company.com",
    "customHttpPort": "8080"
  },
  "remotes": [
    {
      "urlPrefix": "https://my-private-git.company.com/",
      "caCertPath": "/Workspace/my_ca_cert_2.pem"
    },
    {
      "urlPrefix": "https://another-git-server.com/project.git",
      "sslVerify": false
    }
  ]
}
```

**Anforderungen:** allen Git-Nutzern View-Berechtigung auf die Konfigurationsdatei und referenzierte CA-Zertifikate gewähren; Änderungen benötigen bis zu einer Minute; der `default`-Abschnitt muss mindestens teilweise vorhanden sein; der `remotes`-Abschnitt ist optional, jeder Eintrag benötigt `urlPrefix`; unbekannte Felder werden ignoriert, nicht angegebene Felder nutzen Standardwerte.

**Sicherheitsempfehlung:** Bei aktivierter Serverless-Egress-Kontrolle sicherstellen, dass die Netzwerk-Policies den vollqualifizierten Domainnamen (FQDN) des Git-Servers in den erlaubten Internet-Zielen enthalten.

## <a id="serverless-einschraenkungen">8. Serverless Private Git: Einschränkungen</a>

- Serverless-Proxy-Logs sind nicht verfügbar.
- Auf Serverless-unterstützte Regionen beschränkt.
- Ein einzelner VPC-Endpoint-Service kann nicht mehrere Regionen bedienen — zusätzliches NLB- und Endpoint-Setup je Region erforderlich.
- Maximal eine NCC je Workspace.
- Die NCC unterliegt regionalen und Workspace-Attachment-Grenzen.

## <a id="quelle">9. Quelle</a>

- https://docs.databricks.com/aws/en/repos/enable-disable-repos-with-api
- https://docs.databricks.com/aws/en/repos/git-proxy
- https://docs.databricks.com/aws/en/repos/serverless-private-git

**Stand:** 2026-08-21.
