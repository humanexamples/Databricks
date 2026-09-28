# Classic Compute für Jobs

Databricks empfiehlt Serverless Compute für die meisten Job-Workloads, da es die Infrastruktur automatisch verwaltet. Für nicht-kompatible Workloads: Classic Compute.

## Jobs vs. All-Purpose Compute

All-Purpose Compute wird für Jobs **nicht empfohlen** — unterschiedliche Abrechnungssätze, anderes Auto-Termination-Verhalten, Ressourcenkonkurrenz zwischen Teams und andere Konfigurationsoptimierung. Ausnahmen: iterative Entwicklung und kurzlebige, häufige Jobs — hier ist Serverless die bevorzugte Alternative.

## Access Mode

Databricks empfiehlt **Standard Access Mode** für Jobs. Standardeinstellung ist „Auto", sofern Cluster-Policies das nicht überschreiben. Bei Kompatibilitätsfehlern und passenden Berechtigungen lässt sich auf **Dedicated Access Mode** wechseln.

## Compute-Policies

Workspace-Admins sollten job-spezifische Compute-Policies einrichten. Databricks stellt eine Standard-Policy bereit, die Admins mit anderen Nutzern teilen können.

## Quelle

- https://docs.databricks.com/aws/en/jobs/run-classic-jobs
