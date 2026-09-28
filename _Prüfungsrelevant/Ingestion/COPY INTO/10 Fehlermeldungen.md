[← Übersicht](00%20Uebersicht.md)

# Fehlermeldungen rund um COPY INTO

Jeder Fehler steht mit kurzer Erklärung da. Wo es hilft, folgt ein Beispiel, das ihn auslöst oder behebt.

---

## Syntax (`COPY_INTO_SYNTAX_ERROR`, SQLSTATE 42601)

Der Befehl kann nicht geparst werden. Es gibt drei Unterfälle.

**`CREDENTIAL_SYNTAX`:** Credentials gehören an die Quelle, nur als `WITH (CREDENTIAL ...)`.

**`ENCRYPTION_SYNTAX`:** Die Verschlüsselung gehört an die Quelle, nur als `WITH (ENCRYPTION ...)`.

**`VALIDATE_INVALID_ROWS`:** `VALIDATE ... ROWS` braucht eine positive ganze Zahl.

```sql
COPY INTO t FROM '/Volumes/main/raw/landing/x' FILEFORMAT = CSV VALIDATE 0 ROWS;   -- Fehler
COPY INTO t FROM '/Volumes/main/raw/landing/x' FILEFORMAT = CSV VALIDATE 10 ROWS;  -- ok
```

---

## Zieltabelle

**`DELTA_MISSING_DELTA_TABLE_COPY_INTO`** (42P01): Die Tabelle existiert nicht. Lege sie vorher an.

```sql
CREATE TABLE IF NOT EXISTS main.bronze.orders;
```

**`DELTA_COPY_INTO_TARGET_FORMAT`** (0AKDD): Das Ziel muss eine Delta-Tabelle sein.

**`COPY_INTO_SCHEMA_MISMATCH_WITH_TARGET_TABLE`** (42KDG): Das Schema der Daten passt nicht zur Tabelle. Die Meldung zeigt den Unterschied. Lösung: die Daten korrigieren oder die Schema-Evolution einschalten.

```sql
COPY_OPTIONS ('mergeSchema' = 'true')
```

**`COPY_INTO_COLUMN_ARITY_MISMATCH`** (21S01): In die Tabelle kann nicht geschrieben werden, weil die Zahl der Spalten nicht passt. „Arity“ bedeutet Spaltenzahl.

---

## Quelle und Format

**`COPY_INTO_SOURCE_FILE_FORMAT_NOT_SUPPORTED`** (0A000): Das Format muss CSV, JSON, AVRO, ORC, PARQUET, TEXT oder BINARYFILE sein. **Eine Delta-Tabelle als Quelle** ist nicht erlaubt, weil nach `OPTIMIZE` Daten doppelt geladen werden könnten. Die Prüfung lässt sich mit `spark.databricks.delta.copyInto.formatCheck.enabled = false` abschalten.

```sql
SET spark.databricks.delta.copyInto.formatCheck.enabled = false;
```

**`COPY_INTO_SOURCE_SCHEMA_INFERENCE_FAILED`** (42KD9): Im Quellordner gibt es keine lesbare Datei des angegebenen Formats. Prüfe Pfad und `FILEFORMAT`.

---

## Credentials und Verschlüsselung

- **`COPY_INTO_CREDENTIALS_NOT_ALLOWED_ON`** (0A000): Quell-Credentials gehen nur mit `s3`, `s3n`, `s3a`, `wasbs` und `abfss`.
- **`COPY_INTO_CREDENTIALS_REQUIRED`** (42601): Der Credential fehlen Pflichtschlüssel.
- **`COPY_INTO_ENCRYPTION_NOT_ALLOWED_ON`** (0A000): Verschlüsselung geht nur mit `s3`, `s3n`, `s3a` und `abfss`.
- **`COPY_INTO_ENCRYPTION_NOT_SUPPORTED_FOR_AZURE`** (0A000): Unter Azure geht Verschlüsselung nur mit ADLS Gen2 (`abfss://`).
- **`COPY_INTO_ENCRYPTION_REQUIRED`** / **`..._WITH_EXPECTED`** (42601): Ein Pflichtschlüssel der Verschlüsselung fehlt oder hat den falschen Wert, zum Beispiel `TYPE = 'AWS_SSE_C'`.

---

## Parallelität und Transaktionen

- **`COPY_INTO_DUPLICATED_FILES_COPY_NOT_ALLOWED`** (25000): Ein paralleler `COPY INTO` hat dieselben Dateien schon committet. Später erneut versuchen.
- **`COPY_INTO_NON_BLIND_APPEND_NOT_ALLOWED`** (25000): Ein `COPY INTO`, das nicht nur anhängt, darf nicht parallel zu anderen Transaktionen laufen.
- **`TRANSACTION_CONCURRENT_COPY_INTO`** (25000): In einer Transaktion wurde ein paralleler `COPY INTO` auf dieselbe Tabelle erkannt. Die Transaktion wiederholen.

---

## Interner Zustand

- **`COPY_INTO_ROCKSDB_MAX_RETRY_EXCEEDED`** (25000): Der Zustand konnte nicht geladen werden. Die maximale Zahl an Versuchen ist erreicht.
- **`COPY_INTO_STATE_INTERNAL_ERROR`** (55019), Unterfall **`MULTIPLE_STATES_NOT_ALLOWED`**: Im Delta-Log-Snapshot wurden mehrere `COPY INTO`-Zustände gefunden, erwartet ist genau einer. Später erneut versuchen.
- **`DELTA_VACUUM_COPY_INTO_STATE_FAILED`** (22000): `VACUUM` hat die Datendateien gelöscht, das Aufräumen des `COPY INTO`-Zustands ist aber fehlgeschlagen.

---

## Funktionen

- **`COPY_INTO_FEATURE_INCOMPATIBLE_SETTING`** (42613): Eine `COPY INTO`-Funktion verträgt sich nicht mit einer bestimmten Einstellung.
- **`COPY_INTO_UNSUPPORTED_FEATURE`** (0A000): Eine `COPY INTO`-Funktion wird nicht unterstützt.
