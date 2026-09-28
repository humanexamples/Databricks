## B. Den Starter-Job erstellen und erkunden

Führen Sie die folgende Zelle aus, um den Starter-Job für dieses Lab automatisch zu erstellen. Dieser Starter-Job enthält alle in **05 Lab - Create your First Job** erledigten Tasks:

- ./Task Files/Lesson 05 Files/5.1 - Ingesting Banking Data
- ./Task Files/Lesson 05 Files/5.2 - Creating Borrower Details Table
- ./Task Files/Lesson 05 Files/5.3 - Creating Loan Details Table

```python
job_tasks = [
        {
            'task_name': 'ingesting_master_data',
            'file_path': '/Task Files/Lesson 05 Files/5.1 - Ingesting Banking Data',
            'depends_on': None
        },
        {
            'task_name': 'creating_borrower_details_table',
            'file_path': '/Task Files/Lesson 05 Files/5.2 - Creating Borrower Details Table',
            'depends_on': [{'task_key':'ingesting_master_data'}]
        },
        {
            'task_name': 'creating_loan_details_table',
            'file_path': '/Task Files/Lesson 05 Files/5.3 - Creating Loan Details Table',
            'depends_on': [{'task_key':'ingesting_master_data'}]
        }
    ]

myjob = DAJobConfig(job_name=f"Lab_10_Bank_Job_{DA.schema_name}",
                        job_tasks=job_tasks,
                        job_parameters=[])
```
