# 08 - Erkundung des Projekt-Setups

Erkunden Sie die isolierten Kataloge innerhalb des Projekts.

Ihre Umgebung wurde mit den folgenden Katalogen und Dateien konfiguriert:

- Katalog: **unique_catalog_name_1_dev**
  - Schema: **default**
    - Volume: **health**
      - *dev_health.csv* : kleine Teilmenge der Prod-Daten, anonymisierte *PII*, 7.500 Zeilen

- Katalog: **unique_catalog_name_2_stage**
  - Schema: **default**
    - Volume: **health**
      - *stage_health.csv* : Teilmenge der Prod-Daten, 35.000 Zeilen

- Katalog: **unique_catalog_name_3_prod**
  - Schema: **default**
    - Volume: **health**
      - *2025-01-01_health.csv*
      - *2025-01-02_health.csv*
      - *2025-01-03_health.csv*
      - CSV-Dateien werden täglich zu diesem Cloud-Speicherort hinzugefügt. Sehen Sie sich Ihre Kataloge für diesen Kurs manuell an.

