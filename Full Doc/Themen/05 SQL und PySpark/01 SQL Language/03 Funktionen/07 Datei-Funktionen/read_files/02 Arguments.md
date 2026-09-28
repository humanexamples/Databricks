# `read_files` — Arguments

- **`path`**: ein `STRING` mit der URI des Speicherorts der Daten. Unterstützt das Lesen aus Azure Data Lake Storage (`'abfss://'`), S3 (`'s3://'`) und Google Cloud Storage (`'gs://'`). Kann Globs enthalten.
- **`option_key`**: der Name der zu konfigurierenden Option. Enthält der Name einen Punkt (`.`), muss er in Backticks (`` ` ``) stehen.
- **`option_value`**: ein konstanter Ausdruck, auf den die Option gesetzt wird. Akzeptiert Literale und skalare Funktionen.
