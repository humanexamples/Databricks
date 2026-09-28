# Direct Deployment Engine

Die neue, Go-SDK-basierte Deployment-Engine für Bundles als Alternative zur klassischen Terraform-Engine — schneller, mit erweiterter Validierung und zusätzlichem Ressourcen-Support. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Vorteile der Direct-Engine](#vorteile)
3. [Migration bestehender Bundles](#migration)
4. [Direct Deployment für neue Bundles konfigurieren](#konfigurieren)
5. [Wichtige Verhaltensunterschiede](#unterschiede)
6. [Exklusiv unterstützte Ressourcen](#exklusiv)
7. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick</a>

Die Direct Deployment Engine ist ein neuerer Ansatz für Bundles, der vom ursprünglichen Terraform-basierten System wegführt: „Databricks-CLI-Versionen 0.279.0 und höher unterstützen zwei unterschiedliche Deployment-Engines: `terraform` und `direct`."

## <a id="vorteile">2. Vorteile der Direct-Engine</a>

Aufbauend auf dem Databricks Go SDK:

- **Performance:** Deployments laufen „bis zu 40 % schneller".
- **Erweiterte Validierung:** liefert „detaillierte Diffs von Änderungen über `bundle plan -o json`" mit Feld-genauen Berichten, was eine Aktion ausgelöst hat.
- **Plan-Wiederholbarkeit:** Nutzer können „einen zuvor erstellten Plan ausführen und so sicherstellen, dass nur genehmigte Aktionen die Produktion erreichen."
- **Vereinfachte Infrastruktur:** vermeidet „Probleme mit Firewalls, Proxys und benutzerdefinierten Provider-Registries."
- **Erweiterter Ressourcen-Support:** umfasst „Catalogs, External Locations, AI-Search-Endpoints und Genie Spaces."
- **Immutable-Deployment-Option:** Assets lassen sich „in einen unveränderlichen, schreibgeschützten Ordner zum Manipulationsschutz deployen."

## <a id="migration">3. Migration bestehender Bundles</a>

### Schritt 1 — Terraform-Deployment abschließen

```bash
databricks bundle deploy -t my_target
```

### Schritt 2 — Migrationsbefehl ausführen

```bash
databricks bundle deployment migrate -t my_target
```

Die Migration konvertiert die Terraform-State-Datei (`terraform.tfstate`) in die JSON-State-Datei der Direct-Engine (`resources.json`).

### Schritt 3 — Verifikation

```bash
databricks bundle plan -t my_target
```

Bei erfolgreicher Verifikation abschließen mit:

```bash
databricks bundle deploy -t my_target
```

Bei Fehlschlag die neue State-Datei entfernen:

```bash
rm .databricks/bundle/my_target/resources.json
```

## <a id="konfigurieren">4. Direct Deployment für neue Bundles konfigurieren</a>

**Methode 1 — YAML-Einstellung:**

```yaml
bundle:
  engine: direct
```

**Methode 2 — Umgebungsvariable:**

```bash
DATABRICKS_BUNDLE_ENGINE=direct databricks bundle deploy -t my_target
```

Sind beide gesetzt, „hat die Konfiguration Vorrang" vor der Umgebungsvariable.

## <a id="unterschiede">5. Wichtige Verhaltensunterschiede</a>

### State-Diff-Berechnung

Die Direct-Engine trennt lokale Konfiguration vom Remote-State. Sie vergleicht die lokale Bundle-Konfiguration gegen vorherige Deployment-Snapshots — „Ressourcenfelder, die von der Implementierung nicht behandelt werden, lösen keinen Inkonsistenz-Fehler aus."

### Entfernte Konfigurationsfelder

Wichtiger Unterschied: Werden Felder aus der Konfiguration entfernt, „setzt die Direct-Engine den Wert auf den Standardwert der Ressource zurück" — während Terraform zuvor deployte Werte beibehält. Um Werte zu erhalten, müssen sie „explizit in der Konfiguration gesetzt werden, statt sich auf den zuvor deployten Wert zu verlassen."

### Auflösung von Ressourcen-Substitutionen

Substitutionsreferenzen wie `${resources.jobs.my_job.id}` folgen einem zweistufigen Prozess: zuerst Auflösung aus der lokalen Konfiguration, dann — falls dort nicht verfügbar — aus dem Remote-State.

## <a id="exklusiv">6. Exklusiv unterstützte Ressourcen</a>

Folgende Ressourcen erfordern die Direct Deployment Engine und sind mit der Terraform-Engine nicht kompatibel:

- Unity-Catalog-Catalogs
- Unity-Catalog-External-Locations
- Unity-Catalog-Secrets
- Genie Spaces
- Instance Pools
- AI-Search-Endpoints

Zusätzlich ist das Feld `lifecycle.started` (zum Deployen von Ressourcen im gestarteten Zustand für Apps, Clusters und SQL Warehouses) exklusiv der Direct-Engine vorbehalten.

## <a id="quelle">7. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/bundles/direct

**Stand:** 2026-08-21.
