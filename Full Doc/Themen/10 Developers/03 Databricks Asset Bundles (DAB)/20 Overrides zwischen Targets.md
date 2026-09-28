# Overrides zwischen Targets

Die genauen Merge-/Override-Regeln, wenn dieselbe Einstellung sowohl im Top-Level-Mapping als auch innerhalb eines `targets`-Eintrags definiert wird — für Artifacts, Cluster und Job-Tasks. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Grundprinzip](#grundprinzip)
2. [Artifact-Overrides](#artifacts)
3. [Cluster-Overrides](#cluster)
4. [Job-Task-Overrides](#tasks)
5. [Wichtige Regeln](#regeln)
6. [Quelle](#quelle)

---

## <a id="grundprinzip">1. Grundprinzip</a>

„Ist eine Einstellung sowohl im Top-Level-Mapping als auch im `targets`-Mapping für dieselbe Ressource definiert, hat die Einstellung im `targets`-Mapping Vorrang."

## <a id="artifacts">2. Artifact-Overrides</a>

```yaml
artifacts:
  my-artifact:
    type: whl
    path: ./my_package
targets:
  dev:
    artifacts:
      my-artifact:
        path: ./my_other_package
```

**Ergebnis:** Das `dev`-Target nutzt `./my_other_package` statt des Basis-Pfads `./my_package`.

## <a id="cluster">3. Cluster-Overrides</a>

**Für Jobs:** Zuordnung über `job_cluster_key` zwischen Basis- und Target-Ebene. Nicht-konfliktbehaftete Einstellungen werden zusammengeführt, konfliktbehaftete Einstellungen entscheidet das Target.

**Für Pipelines:** Zuordnung über `label: default | maintenance`.

**Beispiel — Merge nicht-konfliktbehafteter Felder:**

```yaml
resources:
  jobs:
    my-job:
      job_clusters:
        - job_cluster_key: my-cluster
          new_cluster:
            spark_version: 13.3.x-scala2.12
targets:
  development:
    resources:
      jobs:
        my-job:
          job_clusters:
            - job_cluster_key: my-cluster
              new_cluster:
                node_type_id: i3.xlarge
                num_workers: 1
```

**Ergebnis:** Das Target führt `node_type_id` und `num_workers` mit dem Basis-`spark_version` zusammen — alle drei Felder gelten im `development`-Target.

**Beispiel — konfliktbehaftete Felder:**

```yaml
resources:
  jobs:
    my-job:
      job_clusters:
        - job_cluster_key: my-cluster
          new_cluster:
            spark_version: 13.3.x-scala2.12
            num_workers: 1
targets:
  development:
    resources:
      jobs:
        my-job:
          job_clusters:
            - job_cluster_key: my-cluster
              new_cluster:
                spark_version: 12.2.x-scala2.12
                num_workers: 2
```

**Ergebnis:** Die Target-Werte (`12.2.x-scala2.12`, `2`) überschreiben die Basiskonfiguration vollständig.

## <a id="tasks">4. Job-Task-Overrides</a>

Zuordnung über `task_key`. Nicht-konfliktbehaftete Einstellungen werden zusammengeführt, bei Konflikten gewinnen die Target-Werte.

```yaml
resources:
  jobs:
    my-job:
      tasks:
        - task_key: my-task
          new_cluster:
            spark_version: 13.3.x-scala2.12
targets:
  development:
    resources:
      jobs:
        my-job:
          tasks:
            - task_key: my-task
              new_cluster:
                node_type_id: i3.xlarge
                num_workers: 1
```

**Ergebnis:** Die zusammengeführte Konfiguration enthält alle drei Parameter (`spark_version`, `node_type_id`, `num_workers`).

## <a id="regeln">5. Wichtige Regeln</a>

- **Zuordnung über passende Keys erforderlich:** Artifacts über den Artifact-Bezeichner, Cluster über `job_cluster_key` bzw. `label`, Tasks über `task_key` — ohne übereinstimmenden Key entsteht kein Merge, sondern ein zusätzlicher Eintrag.
- **Merge vs. Replace:** Nicht-konfliktbehaftete Einstellungen werden kombiniert; konfliktbehaftete Einstellungen werden vom Target-Wert vollständig ersetzt (nicht feldweise weiter aufgelöst).
- **Validierung:** `databricks bundle validate` zeigt das tatsächlich zusammengeführte Ergebnis an — vor jedem Deployment empfehlenswert, um Override-Effekte zu verifizieren.

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/bundles/overrides

**Stand:** 2026-08-26.
