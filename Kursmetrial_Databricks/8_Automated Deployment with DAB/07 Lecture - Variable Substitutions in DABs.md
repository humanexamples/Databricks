### A1. Standard-Substitutionen, einfache und komplexe Variablen

Declarative Automation Bundles unterstützen **Substitutionen** und **benutzerdefinierte Variablen**, die beide erlauben, dass Werte dynamisch aufgelöst werden, wenn das Bundle deployed und ausgeführt wird. Referenzieren Sie jede davon mit `${...}`.

**Standard-Substitutionen**

Standardmäßig ist eine Vielzahl von **Variablensubstitutionen** verfügbar:

```
${bundle.name}
${bundle.target}
${workspace.file_path}
${workspace.root_path}
${resources.jobs.<job-name>.id}
${resources.models.<model-name>.name}
${resources.pipelines.<pipeline-name>.name}
```

**Einfache benutzerdefinierte Variablen**

- Sie können **einfache benutzerdefinierte Variablen** in Ihrem Bundle definieren, um das dynamische Abrufen von Werten zu ermöglichen, die für viele Szenarien benötigt werden.
- Benutzerdefinierte Variablen werden in Ihren Bundle-Konfigurationsdateien innerhalb des **variables**-Mappings deklariert.

```yaml
variables:
  my_lab_user_name:
    description: Your user name
    default: labuser23904

  catalog_dev:
    description: Development catalog reference
    default: ${var.my_lab_user_name}_1_dev

  catalog_prod:
    description: Production catalog reference
    default: ${var.my_lab_user_name}_3_prod
```

**Komplexe Variablen**

- Eine benutzerdefinierte Variable wird als Typ **string** angenommen, es sei denn, Sie definieren sie als komplexe Variable.
- Definieren Sie eine benutzerdefinierte Variable, indem Sie den **type** auf `complex` setzen.

```yaml
bundle:
  name: demo08_bundle
...
variables:
  my_cluster:
    description: "My cluster"
    type: complex
    default:
      spark_version: "15.4.x-scala2.11"
      node_type_id: "Standard_DS3_v2"
      num_workers: 2
```

### B3. Lookup-Variablen

Für bestimmte Objekttypen können Sie einen **Lookup** für eine benutzerdefinierte Variable definieren, um die ID des Objekts dynamisch abzurufen.

- **Die neue Variable erstellen** – definiert eine neue benutzerdefinierte Variable – hier `my_cluster_id`.
- **Das Objekt nachschlagen** – verwendet das **lookup**-Mapping, um den Cluster-Namen `myclustername` zu seiner Cluster-ID aufzulösen.

```yaml
...
variables:
  my_cluster_id:
    description: "Get cluster ID using a lookup variable"
    lookup:
      cluster: myclustername
...
```

> **Zusätzliche Notizen:**
>
> - Für bestimmte Objekttypen definieren Sie einen Lookup für eine benutzerdefinierte Variable, um die ID des Objekts abzurufen.
> - Geben Sie den Variablennamen (`my_cluster_id`) an und verwenden Sie dann das `lookup`-Mapping, um zu definieren, was nachgeschlagen werden soll – hier das Cluster namens `myclustername`, dessen ID zum Wert der Variablen wird.
> - Wenn ein Lookup definiert ist, wird immer die ID des Objekts mit dem angegebenen Namen als Wert der Variablen verwendet, was die korrekt aufgelöste ID sichert.

### B4. Lookups für eine Vielzahl von Umgebungskonfigurationen

Sie können Lookups für viele Objekttypen definieren:

`alert`, `cluster_policy`, `cluster`, `dashboard`, `instance_pool`, `job`, `metastore`, `notification_destination`, `pipeline`, `query`, `service_principal`, `warehouse`

## C. Overrides für Zielumgebungen

### C1. Variablen-Overrides für Zielumgebungen

Verwenden Sie das `targets`-Mapping, um den Wert einer Variablen in jeder Umgebung dynamisch zu ändern.

- **targets-Mapping** – Variablenwerte innerhalb jeder Zielumgebung dynamisch mit dem Top-Level-`targets`-Mapping ändern.
- **development** – beim Deployen nach **development** verwendet `target_catalog` den Wert von `catalog_dev`.
- **production** – beim Deployen nach **production** verwendet `target_catalog` den Wert von `catalog_prod`.

```yaml
...
targets:
  development:
    ...
    variables:
      target_catalog: ${var.catalog_dev}
  production:
    ...
    variables:
      target_catalog: ${var.catalog_prod}
```

Ein **Standardwert** für die Variable muss im Top-Level-`variables`-Mapping definiert sein, damit ein Override funktioniert.

> **Zusätzliche Notizen:**
>
> - Benutzerdefinierte Variablen können im gesamten `databricks.yml` verwendet werden, auch innerhalb des `targets`-Mappings, was Ihnen erlaubt, Variablenwerte für jede Zielumgebung dynamisch zu ändern.
> - Beim Deployen nach development verwendet `target_catalog` den Wert von `catalog_dev`; beim Deployen nach production verwendet es den Wert von `catalog_prod`.
> - Wenn für eine Variable kein Override angegeben ist, wird ihr ursprünglicher Wert verwendet.
> - Ein Standardwert für die Variable muss im Top-Level-`variables`-Mapping definiert sein, damit ein Override funktioniert.

## D. Warum Variablen wichtig sind

### D1. Vorteile der Verwendung von Variablen

- **Anpassbar für verschiedene Umgebungen** – Konfigurationen (z. B. Datenbankverbindungen, Dateipfade usw.) für Development-, Staging- und/oder Production-Umgebungen leicht ändern.
- **Wiederverwendbarkeit über Databricks-Projekte hinweg** – Sie können dasselbe Asset-Bundle über mehrere Teams oder Workspaces verwenden, indem Sie nur Variablenwerte anpassen.
- **Einfache Wartung & Updates** – Assets schnell aktualisieren, indem Variablen geändert werden, um Konsistenz zu sichern und Fehler zu reduzieren.

> **Zusätzliche Notizen:**
>
> - Variablen lassen Sie Konfigurationen – Catalogs, Dateipfade und andere Einstellungen – für Development-, Staging- und Production-Umgebungen anpassen.
> - Sie ermöglichen Wiederverwendbarkeit über Databricks-Projekte hinweg: Dasselbe Asset-Bundle kann über mehrere Teams oder Workspaces verwendet werden, indem nur die Variablenwerte angepasst werden.
> - Sie machen Wartung und Updates einfach: Assets und Konfigurationen können schnell aktualisiert werden, wodurch Umgebungen konsistent bleiben und das Fehlerrisiko reduziert wird.

## E. Fazit

- Bundles bieten viele **Standard-Substitutionen**, die Sie mit `${...}` referenzieren können.
- Sie können **einfache**, **komplexe** und **Lookup**-benutzerdefinierte Variablen im `variables`-Mapping definieren.
- **Target-Overrides** geben einer Variablen pro Umgebung einen anderen Wert (ein Default ist erforderlich).
- Variablen machen Bundles **wiederverwendbar, wartbar und anpassbar** über Umgebungen hinweg.

### Nächste Schritte

Im nächsten Demo deployen Sie ein DAB in mehrere Umgebungen unter Verwendung von Variablen und Overrides.

---

&copy; 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
