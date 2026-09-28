```python
%run ./Classroom-Setup-Common
```

---

```python
## Kurskatalog und Schemanamen für den Benutzer anzeigen.
DA.display_config_values(
  [
    ('Lab catalog reference: DA.catalog_name', DA.catalog_name)
  ]
)

set_default_catalog = spark.sql(f'USE CATALOG {DA.catalog_name}')
```
