# Databricks Sandbox

> Quelle: <https://docs.databricks.com/aws/en/compute/serverless/sandbox>
> **Beta**

> *"Databricks Sandbox is a compute environment for humans and agents, accessible over SSH (Secure Shell), running in the Databricks serverless compute plane."*

Ermöglicht persistente Entwicklungsumgebungen und das Ausführen von **Coding-Agents** in einer leichtgewichtigen, isolierten Umgebung — ohne lokale Rechnerressourcen.

## Fähigkeiten

- **Persistenter Entwicklungszugriff:** SSH-erreichbare Sandboxes, die zwischen Sitzungen verfügbar bleiben
- **Agent-Ausführung:** Coding-Agents direkt über die Databricks CLI ausführen oder Desktop-IDEs (Cursor, Claude, Codex) verbinden
- **Ephemere Umgebungen:** kurzlebige Instanzen für Experimente und Sub-Agent-Tasks
- **Nebenläufige Sitzungen:** mehrere SSH-Verbindungen teilen dasselbe Dateisystem und denselben State

## Warum Databricks Sandbox?

- **Databricks-native Governance:** läuft in der Serverless Compute Plane; Daten bleiben innerhalb der Workspace-Governance-Grenze. Integration mit **AI Gateway** für governte LLM-Inferenz und MCP-Aufrufe.
- **Für Agents gebaut:** Start in Sekunden; persistenter Speicher im Home-Verzeichnis über Sitzungen hinweg; mehrere nebenläufige SSH-Sitzungen auf geteiltem Dateisystem.

## Voraussetzungen

1. Databricks CLI lokal installieren
2. Mit `databricks auth login` authentifizieren

## Sandbox erstellen

```bash
databricks sandbox create      # Sandbox erstellen
databricks sandbox register    # optional: SSH-Keys registrieren
databricks sandbox ssh         # SSH zur Standard-Sandbox
```

Die CLI installiert und authentifiziert sich automatisch innerhalb der Sandbox.

## Isolations- & Sicherheitsmodell

### Datenpersistenz

> *"Storage during Beta is not persistent and may be deleted."*

- Home-Verzeichnis (`/home/sandbox-agent`): bis zu **100 GB**, persistiert unbegrenzt
- Nicht-Home-Speicher: bis zu **10 GB**, gelöscht beim Stoppen der Sandbox
- Alle nebenläufigen Sitzungen greifen auf dasselbe Dateisystem zu

> **Warnung:** *"Data stored in your home directory will be deleted when the beta period is over."*

### Ressourcen

- **Tech-Specs:** 4 Cores, 16 GB RAM, bis zu 100 GB Speicher (aktuell nicht anpassbar)
- **Limits:** max. **40 Sandboxes pro Nutzer**, **100 pro Workspace**
- **IP-Stabilität:** öffentliche IP-Adressen können sich jederzeit ändern

### Netzwerk / Filesystem / Prozesse

- Sandbox läuft in der Serverless Compute Plane (Workspace-Level-Governance), **integriert aber noch nicht mit Serverless Egress Controls**.
- Getrennte Speicherzonen: persistentes Home-Verzeichnis vs. ephemerer Temp-Speicher.
- *"There is no native way to persist environments outside of the home directory, or to customize your environment at startup time."* — Pakete/Konfiguration können jedoch **im** Home-Verzeichnis persistiert werden.

> **Einschränkung:** *"Do not use Databricks Sandbox in a workspace with (SEG) enabled"* — Serverless Egress Controls werden noch nicht unterstützt.

## Verfügbare Regionen (14 AWS-Regionen)

`ap-northeast-1`, `ap-northeast-2`, `ap-south-1`, `ap-southeast-1`, `ap-southeast-2`, `ca-central-1`, `eu-central-1`, `eu-west-1`, `eu-west-2`, `eu-west-3`, `sa-east-1`, `us-east-1`, `us-east-2`, `us-west-2`

## Kosten (erwartet)

- **Runtime-Compute:** stündliche Abrechnung während des Betriebs (Raten TBD)
- **Persistenter Speicher:** Home-Verzeichnis-Speicher laufend abgerechnet, auch bei Pause
- **Temp-Speicher:** in Runtime-Compute enthalten
- **Datentransfer:** bestehende Ratenstruktur

## Einschränkungen

- Keine Serverless-Egress-Control-Integration
- Feste Instanzgröße (4 Cores, 16 GB)
- Max. 40 Sandboxes/Nutzer, 100/Workspace
- Öffentliche IPs können wechseln
- Beta-Datenlöschung nach Programmende
- Begrenzte Environment-Anpassung

## Hinweise

- *"Databricks Sandbox is for running coding agents in a lightweight, sandboxed environment"* — abzugrenzen von IDE-getriebener Entwicklung über SSH-Tunnel.
- Beim SSH in die Sandbox konfiguriert Databricks gängige Coding-Harnesses (Claude, Codex) automatisch für die Nutzung des **AI Gateway**, sofern dieses für den Workspace konfiguriert ist.
