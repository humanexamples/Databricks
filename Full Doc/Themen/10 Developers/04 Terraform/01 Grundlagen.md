# Grundlagen

Kernfähigkeiten des Databricks-Terraform-Providers, Einstiegsvoraussetzungen, Aufbau einer Beispielkonfiguration und Testing-Ansätze. Teil der [Terraform](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Kernfähigkeiten](#kernfaehigkeiten)
2. [Einstiegsvoraussetzungen](#voraussetzungen)
3. [Beispielkonfiguration](#beispiel)
4. [Testing-Ansätze](#testing)
5. [Quelle](#quelle)

---

## <a id="kernfaehigkeiten">1. Kernfähigkeiten</a>

Der Provider unterstützt die Provisionierung von: Databricks-Workspaces; Clustern und Jobs; Notebooks und Workspace-Ressourcen; Datenzugriffs-Konfigurationen; Unity-Catalog-Setups.

## <a id="voraussetzungen">2. Einstiegsvoraussetzungen</a>

1. **Terraform CLI** — von der offiziellen Terraform-Website herunterladen.
2. **Projektverzeichnis** — ein dediziertes Verzeichnis für Konfigurationsdateien (z. B. `mkdir terraform_demo`).
3. **Provider-Abhängigkeit** — Konfigurationsblock mit `source = "databricks/databricks"`.
4. **Authentifizierungs-Setup** — Credentials gemäß Databricks-Provider-Dokumentation konfigurieren.

## <a id="beispiel">3. Beispielkonfiguration</a>

Die Doku beschreibt eine schrittweise Beispielkonfiguration bestehend aus:

- **`me.tf`** — ruft Informationen zum aktuellen Nutzer ab.
- **`notebook.tf`** — definiert eine Notebook-Ressource mit Pfad, Sprache und Quelle.
- **`cluster.tf`** — erstellt Cluster mit Node-Typ- und Spark-Version-Angaben.
- **`job.tf`** — richtet Jobs ein, die Notebooks auf Clustern ausführen.
- **`*.auto.tfvars`-Dateien** — spezifizieren Variablenwerte je Ressourcentyp.

Vollständiges End-to-End-Beispiel siehe [03 Cluster, Notebook und Job bereitstellen.md](03%20Cluster%2C%20Notebook%20und%20Job%20bereitstellen.md).

## <a id="testing">4. Testing-Ansätze</a>

- **Integrationstests:** `command = apply` nutzen, um tatsächliche Ressourcen zu deployen und zu verifizieren.
- **Unit Tests:** `command = plan` oder Mock-Provider nutzen, um ohne Deployment zu testen.

## <a id="quelle">5. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/terraform/

**Stand:** 2026-08-21.
