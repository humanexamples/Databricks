# Spark Submit (Legacy, Deprecated, Entfernung Mitte 2026 geplant)

Der Spark-Submit-Task ist ein veralteter Ansatz zur Konfiguration von JARs als Tasks. **Deprecated, Entfernung Mitte 2026 geplant** — für neue Implementierungen den JAR-Task-Typ nutzen (siehe `JAR-Task.md`).

## Einschränkungen

- Läuft nur auf neuen Clustern.
- JAR-Dateien müssen an kompatiblen Orten oder Maven-Repositories liegen.
- JAR-Dateien in Volumes sind nicht zugänglich.
- Cluster-Autoscaling wird nicht unterstützt.
- Cluster-Auto-Termination wird nicht unterstützt — Anwendungen müssen `System.exit` beim Abschluss explizit aufrufen.
- `dbutils` wird nicht unterstützt.
- Unity-Catalog-aktivierte Cluster benötigen Dedicated Access Mode — Standard Access Mode ist inkompatibel.
- Structured-Streaming-Jobs benötigen `max_concurrent_runs = 1` und den Cron-Ausdruck `"* * * * * ?"` (jede Minute); Streaming-Tasks müssen als letztes in der Job-Sequenz stehen.

## Konfiguration

1. Tab **Tasks** → **Add task**.
2. Task-Namen eingeben.
3. Typ **Spark Submit**.
4. Compute konfigurieren.
5. Argumente/Konfiguration im **Parameters**-Feld als JSON-Array von Strings:

```json
["--class", "org.apache.spark.mainClassName", "dbfs:/Filestore/libraries/jar_path.jar"]
```

**Hinweise:**

- Die ersten drei Argumente identifizieren Main-Class und JAR-Pfad.
- `master`, `deploy-mode` und `executor-cores` lassen sich nicht überschreiben.
- `--jars` und `--py-files` für abhängige Bibliotheken, `--conf` für Spark-Konfigurationen — beide unterstützen DBFS- und S3-Pfade (ebenso `--files`).
- Standardmäßig wird der gesamte verfügbare Speicher genutzt (abzüglich Databricks-Service-Reserven) — anpassbar über `--driver-memory` und `--executor-memory`.

6. **Save task**.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/spark-submit-legacy
