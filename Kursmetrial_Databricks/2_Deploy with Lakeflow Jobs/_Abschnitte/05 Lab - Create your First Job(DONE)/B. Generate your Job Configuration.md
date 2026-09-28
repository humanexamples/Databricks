## B. Ihre Job-Konfiguration generieren
1. Führen Sie die folgende Zelle aus, um die Werte auszugeben, die Sie in den nachfolgenden Schritten zur Konfiguration Ihres Jobs verwenden. Achten Sie darauf, den richtigen Job-Namen und die richtigen Dateien anzugeben.

**HINWEIS:** Das Objekt `DA.print_job_config` ist spezifisch für den Databricks-Academy-Kurs. Es gibt die Informationen aus, die Sie zum Erstellen des Jobs benötigen.

```python
DA.print_job_config(job_name_extension="Lab_05_Bank_Job", 
                    file_paths='/Task Files/Lesson 05 Files',
                    Files=[
                            '5.1 - Ingesting Banking Data',
                            '5.2 - Creating Borrower Details Table',
                            '5.3 - Creating Loan Details Table'
                        ])
```
