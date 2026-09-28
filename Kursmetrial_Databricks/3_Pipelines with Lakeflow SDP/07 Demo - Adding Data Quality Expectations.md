Datenqualitäts-Expectations, um Qualitäts-Constraints anzuwenden, die Daten beim Durchlaufen von Apache Spark™ Declarative Pipelines validieren. Expectations bieten tiefere Einblicke in Datenqualitätskennzahlen und ermöglichen es, Updates fehlschlagen zu lassen oder Datensätze zu verwerfen, wenn ungültige Datensätze erkannt werden.

**HINWEIS:**  Die Funktion `create_declarative_pipeline` ist eine für diesen Kurs erstellte benutzerdefinierte Funktion, die die Beispiel-Pipeline über die Databricks REST API erstellt. So müssen Sie die Pipeline nicht manuell erstellen und die Pipeline-Assets nicht manuell referenzieren.

```python
%python
create_declarative_pipeline(
    pipeline_name=f'07 - Adding Data Quality Expectations Project - {my_catalog}',
    root_path_folder_name='07 - Adding Data Quality Expectations Project',
    catalog_name=my_catalog,
    schema_name='default',
    source_folder_names=['orders'],
    configuration={'source': source_volume_path}
)
```

2. Führen Sie die folgenden Schritte aus, um das Starter-Projekt der Spark Declarative Pipeline für diese Demonstration zu öffnen:

   a. Klicken Sie in der Hauptnavigationsleiste mit der rechten Maustaste auf **Jobs & Pipelines** und wählen Sie **Open Link in New Tab**.

   b. Wählen Sie unter **Jobs & Pipelines** Ihre Pipeline **07 - Adding Data Quality Expectations Project - labuser**.

   c. Wählen Sie ganz rechts im Bereich **Pipeline details** die Option **Open in Editor** (Feld rechts neben **Source code**), um die Pipeline im **Lakeflow Pipeline Editor** zu öffnen.

   d. Im neuen Tab:
- Wählen Sie den Ordner **orders** (der Hauptordner enthält außerdem den zusätzlichen Ordner **python_excluded** mit der Python-Version)

- Klicken Sie auf **orders_pipeline.sql**.

## C. Die Pipeline `orders_pipeline.sql` mit Datenqualitäts-Expectations erkunden und ausführen

1. Klicken Sie auf die Schaltfläche **Run pipeline**, um die Pipeline zu starten. Wenn Sie aufgefordert werden, Katalog und Schema zu bestätigen, prüfen Sie diese und klicken Sie erneut auf **Run pipeline**, um fortzufahren.

*Fahren Sie, während die Pipeline läuft, mit Schritt 2 fort.*

2. Während die Pipeline ausgeführt wird:

   a. Sehen Sie sich `CREATE OR REFRESH STREAMING TABLE 2_silver_db.orders_silver_demo07` an (Abschnitt **Bronze -> Silver (Contains Data Quality Expectations)**)

   b. Beachten Sie, dass sie **3 Datenqualitäts-Expectations** enthält, die beim Ingestieren der Daten in **orders_silver_demo07** angewendet werden:

| Constraint | Regel | Aktion |
|------------|------|--------|
| `valid_notifications` | `notifications` muss `'Y'` oder `'N'` sein | **Warn** – Zeilen werden behalten, der Verstoß wird protokolliert |
| `valid_date` | `order_timestamp` muss nach `'2021-12-26'` liegen | **Drop Row** – ungültige Zeilen werden entfernt |
| `valid_id` | `customer_id` darf nicht `NULL` sein | **Fail Update** – die Pipeline schlägt bei einem Verstoß fehl |

- Die Spalte **notifications** enthält nur die Werte `Y` oder `N` – daher lösen `N`-Werte eine Warnung aus
- Die Spalte **order_timestamp** enthält Datumswerte vom `2021-12-25` – daher werden diese Zeilen verworfen
- **customer_id** hat in dieser Demo keine Nullwerte – daher läuft die Pipeline erfolgreich durch



- **174 Zeilen** wurden in die Bronze-Tabelle eingelesen
- Nur **148 Zeilen** wurden in die Silber-Tabelle (die Tabelle mit Constraints) eingelesen

2. Stellen Sie sicher, dass Sie sich im unteren Fenster im Tab **Tables** befinden.

   - Wählen Sie **orders_silver_demo07** und dann **Table metrics**

   - Beachten Sie Folgendes in der Tabelle:

| Kennzahl | Wert | Beschreibung |
|--------|-------|-------------|
| **Output records** | 148 | Zeilen, die alle Expectations bestanden haben und in die Tabelle geschrieben wurden |
| **Expectations** | 1 met \| 2 unmet | Gesamtzahl der für die Streaming Table festgelegten Datenqualitäts-Expectations |
| **Dropped** | 26 | Zeilen, die die `DROP ROW`-Expectation nicht bestanden haben (14,9 % Fehlerquote) |
| **Warnings** | 32 | Zeilen, die die `WARN`-Expectation nicht bestanden haben (14,9 % Fehlerquote) |

   - Wählen Sie den Link in der Spalte **Expectations**, um eine detaillierte Aufschlüsselung anzuzeigen:

| Constraint | Aktion | Fehlerquote | Fehlgeschlagene Zeilen |
|------------|--------|--------------|-------------|
| `valid_notifications` | **Allow** (warn) | 22,4 % | 39 |
| `valid_date` | **Drop** | 14,9 % | 26 |

- **HINWEISE:**
  - Wenn sich die `WARN`-Zahlen zwischen der Tabelle und dem Pop-up unterscheiden, liegt das daran, dass die Tabellenansicht überlappende Zeilen dedupliziert, während das Pop-up die Fehler pro Expectation zählt – auch wenn dieselbe Zeile mehrere Expectations verletzt.
  - Die Expectation-Kennzahlen in der UI gelten pro Update-Lauf. Um die Datenqualität über mehrere Läufe hinweg zu analysieren, fragen Sie das Event Log der Pipeline ab (wird später im Kurs behandelt).

#### Checkpoint
![](https://files.training.databricks.com/binder/prod_main/build-data-pipelines-with-apache-spark-declarative-pipelines-en_us-3.2.0/images/20260724T200107Z/Build Data Pipelines with Apache Spark Declarative Pipelines/Includes/images/data-quality-expectations/quality-expectations-run.png)



