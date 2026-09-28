# Managed-Ingestion-Pipelines Troubleshooting

Diese Seite bietet allgemeine Hinweise zur Fehlerbehebung bei Managed-Ingestion-Pipelines in Lakeflow Connect; für Connector-spezifische Probleme gibt es separate Ressourcen.

## Allgemeine Fehlerbehebung

Schlägt ein Pipeline-Lauf fehl, sollte zunächst der fehlgeschlagene Schritt geprüft werden, um festzustellen, ob die Fehlermeldung ausreichend Details liefert. Die UI zeigt Pipeline-Event-Logs an; Cluster-Logs lassen sich auf der Pipeline-Detailseite über **Update details** und dann **Logs** aufrufen und herunterladen.

## Spaltenauswahl mit Declarative Automation Bundles

**Problem:** Die Spaltenauswahl-Funktion ist bei der Pipeline-Erstellung mit Declarative Automation Bundles nicht verfügbar.

**Lösung:** Die Databricks-CLI-Version prüfen. Versionen unter v0.251.0 müssen neu installiert werden.

## Einschränkungen beim Bearbeiten von Pipelines

Pipelines, die über Declarative Automation Bundles oder die CLI erstellt oder geändert wurden, können nicht unterstützte Konfigurationsfelder enthalten. Bei einem Bearbeitungsversuch in der UI erscheint eine Warnung, dass der visuelle Modus nicht verfügbar ist – stattdessen wird der Code-Editor-Modus empfohlen. Zwischen den Modi (Wizard, YAML, JSON) lässt sich über Buttons am oberen Rand des Editors wechseln.

**Hinweis:** Bundle-verwaltete Pipelines sollten direkt in der Bundle-Definitionsdatei bearbeitet werden, da UI-Änderungen bei der nächsten Bereitstellung überschrieben werden.

## Fehler CANNOT_WRITE_TO_INACTIVE_TABLES

**Fehlermeldung:** „Table 'XYZ' is marked as inactive and cannot be written to.“

Tritt auf, wenn eine Pipeline versucht, in eine Zieltabelle zu schreiben, die nach dem Löschen der Quelltabelle als inaktiv markiert wurde.

**Lösungen:**

- Einen Full Refresh ausführen, wenn die Verarbeitung nach einer neu erstellten Quelltabelle fortgesetzt werden soll.
- Die inaktive Zieltabelle löschen und aus der Pipeline entfernen, wenn das Löschen der Quelle beabsichtigt war.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/troubleshoot  
**Stand:** 2026-08-07
