[← Übersicht](00%20Uebersicht.md)

# Fall 12 – Zeitfenster- / gefilterte Ingestion

**A) `read_files()` / `COPY INTO` – nach Änderungszeit**

```sql
SELECT * FROM read_files('/Volumes/catalog/schema/landing/', format => 'json',
                         modifiedAfter  => date_sub(current_date(), 7),
                         modifiedBefore => current_date());
```

**B) Nach Dateinamen-Muster**

- `read_files(..., pathGlobFilter => '*.json')` bzw. `useStrictGlobber => true`
- `COPY INTO … PATTERN = 'folder1/file_[a-g].csv'`

**C) Nur bestimmte Unterordner** – Pfad-Präfix oder Glob (siehe [Fall 10D](10%20Mehrere%20Quellordner%20%28Multiplex%29.md)).

**D) Korrupte / fehlende Dateien tolerieren**

```sql
read_files(..., ignoreCorruptFiles => true, ignoreMissingFiles => true)
```

```sql
COPY INTO … FORMAT_OPTIONS ('ignoreCorruptFiles' = 'true')
```

---
[← Vorheriger Fall](11%20Schema%20aendert%20sich%20ueber%20die%20Zeit.md) · [Übersicht](00%20Uebersicht.md) · [Nächster Fall →](13%20Verarbeitete%20Dateien%20aufraeumen.md)
