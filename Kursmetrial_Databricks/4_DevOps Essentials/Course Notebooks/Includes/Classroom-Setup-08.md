```python
%run ./Classroom-Setup-Common
```

---

```python
## Die DA-Schlüssel für die Kataloge des Benutzers erstellen
DA.create_DA_keys()

## Kurskatalog und Schemanamen für den Benutzer anzeigen.
DA.display_config_values(
  [
    ('DEV catalog reference: DA.catalog_dev', DA.catalog_dev),
    ('STAGE catalog reference: DA.catalog_stage', DA.catalog_stage),
    ('PROD catalog reference: DA.catalog_prod', DA.catalog_prod)
   ]
)
```
