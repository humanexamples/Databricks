# Directory Listing Mode konfigurieren

Der Directory Listing Mode ist der Standard-Dateierkennungsansatz von Auto Loader. Auto Loader erkennt neue Dateien, indem es das Eingabeverzeichnis auflistet – zusätzlich zum Cloud-Speicherzugriff sind keine weiteren Berechtigungskonfigurationen nötig.

## Funktionsweise

Das System optimiert die Dateierkennung, indem es abgeflachte Antworten vom Speicher erhält, statt alle Unterverzeichnisse nacheinander aufzulisten. Statt z. B. rund 8.761 API-Aufrufe zu benötigen, um Dateien in einer nach Datum/Uhrzeit hierarchisch organisierten Verzeichnisstruktur zu finden, reduziert Auto Loader dies durch effizientes Batch-Abrufen erheblich.

Cloud-Speicheranbieter liefern unterschiedlich viele Ergebnisse pro API-Aufruf:

- **S3:** 1.000 Ergebnisse
- **ADLS:** 5.000 Ergebnisse
- **GCS:** 1.024 Ergebnisse

## Empfehlung

Databricks empfiehlt, vom Directory Listing Mode wegzumigrieren: Für die meisten Workloads wird stattdessen File Notification Mode mit File Events auf External Locations empfohlen. Das ist besonders bei Continuous-Triggern wichtig, da Directory Listing Mode kontinuierlich das gesamte Verzeichnis auflistet und die `LIST`-API-Kosten deutlich erhöhen kann.

## Lexikalische Reihenfolge von Dateien

Für optimale Performance sollten neue Dateien Präfixe haben, die lexikografisch größer sind als bestehende Dateien.

**Versionierte Dateien** (z. B. Delta-Lake-Transaktionslogs, AWS DMS):

```python
database_schema_name/table_name/LOAD00000001.csv
database_schema_name/table_name/LOAD00000002.csv
```

**Datumspartitionierte Dateien:**

```python
<base-path>/2021/12/01/10:11:23-randomString.json
<base-path>/year=2021/month=12/day=04/hour=08/minute=22/randomString.csv
```

Wichtige Anforderung bei Datumspartitionierung: Monate, Tage, Stunden und Minuten müssen links mit Nullen aufgefüllt werden, um die lexikalische Reihenfolge sicherzustellen.

## Incremental Listing (veraltet)

Diese Funktion wird nicht mehr empfohlen: Incremental Listing garantiert keine Verarbeitungsreihenfolge der Dateien und sollte nicht für geordnete Dateiaufnahme verwendet werden.

## Quellpfad ändern

Ab Databricks Runtime 11.3 LTS lässt sich der Eingabepfad des Verzeichnisses ändern, während im Directory Listing Mode dasselbe Checkpoint-Verzeichnis beibehalten wird.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/directory-listing-mode  
**Stand:** 2026-08-07
