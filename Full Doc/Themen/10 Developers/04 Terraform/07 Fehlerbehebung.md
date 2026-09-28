# Fehlerbehebung

Bekannte Provider-Installationsfehler und deren Lösung sowie Logging-Aktivierung für den Databricks-Terraform-Provider. Teil der [Terraform](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Fehler: Failed to install provider](#install-fehler)
2. [Fehler: Failed to query available provider packages](#query-fehler)
3. [Logging aktivieren](#logging)
4. [Quelle](#quelle)

---

## <a id="install-fehler">1. Fehler: Failed to install provider</a>

**Problem:** Bei `terraform init` ohne eingecheckte `terraform.lock.hcl`-Datei erscheint die Meldung „Failed to install provider" — der Fehler kann auf fehlende SHA-256-Hashes für bestimmte Provider-Versionen verweisen.

**Ursache:** Die Terraform-Konfiguration verweist auf veraltete Databricks-Provider-Referenzen.

**Lösung:**

1. Provider-Referenzen in allen `.tf`-Dateien von `databrickslabs/databricks` auf `databricks/databricks` aktualisieren. Ein automatisiertes Python-Skript steht zur Verfügung:
   ```bash
   python3 -c "$(curl -Ls https://dbricks.co/updtfns)"
   ```
2. Den State-Provider-Replacement-Befehl ausführen:
   ```bash
   terraform state replace-provider databrickslabs/databricks databricks/databricks
   ```
3. Änderungen mit `terraform init` validieren.

## <a id="query-fehler">2. Fehler: Failed to query available provider packages</a>

**Problem:** `terraform init` ohne `terraform.lock.hcl`-Datei erzeugt die Meldung „Failed to query available provider packages".

**Ursache:** veraltete Databricks-Terraform-Provider-Referenzen in der Konfiguration.

**Lösung:** dieselben Schritte wie unter „Failed to install provider" (Abschnitt 1) befolgen.

## <a id="logging">3. Logging aktivieren</a>

Die Umgebungsvariable `TF_LOG` auf `DEBUG` oder ein anderes unterstütztes Terraform-Log-Level setzen. Um die Ausgabe in eine Datei zu leiten, `TF_LOG_PATH` konfigurieren:

```bash
TF_LOG=DEBUG TF_LOG_PATH=tf.log terraform apply -no-color
```

## <a id="quelle">4. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/terraform/troubleshoot

**Stand:** 2026-08-21.
