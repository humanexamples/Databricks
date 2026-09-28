# Häufige Muster für Row Filter und Column Masks

Elf wiederkehrende Implementierungsmuster.

## 1. Cast-kompatible Maskierungsfunktionen

Jeder `CASE`-Zweig muss einen Typ liefern, der zum Zieltyp passt oder dorthin castbar ist — z. B. eine `DOUBLE`-Spalte maskieren und in jedem Zweig `DOUBLE` zurückgeben.

## 2. Numerischen Überlauf vermeiden

Rechenoperationen innerhalb der Maskierungsfunktion (z. B. `score + 1000`) können bei schmalen Zieltypen wie `TINYINT` zu einem Cast-Überlauf führen, wenn das Ergebnis den Wertebereich überschreitet.

## 3. `VARIANT`-basierte Maskierung für mehrere Typen

Eine einzige Funktion für `INT`, `DOUBLE` und `DECIMAL` über `VARIANT`-Rückgabetyp:

```sql
CREATE FUNCTION mask_numeric(val VARIANT) RETURNS VARIANT DETERMINISTIC
RETURN 0::VARIANT;
```

## 4. Struct-Spalten-Maskierung mit `VARIANT` (Runtime 18.1+)

Maskiert einzelne Struct-Felder selektiv, über `schema_of_variant()` zur Formerkennung und `to_variant_object()`/`named_struct()` zur Schwärzung.

## 5. Tag-basierte Zugriffskontrolle

Ein `classification:unverified`-Tag blockiert den Zugriff, bis Data Stewards die Klassifizierung aktualisieren — löst automatische Policy-Übergänge aus (siehe `Secure by Default.md`).

## 6. Teilweise Offenlegung ohne Regex

String-Operationen statt Regex für bessere Performance:

```sql
CONCAT('***-**-', RIGHT(ssn, show_last))
```

## 7. Konsistentes Hashing / deterministische Pseudonymisierung

Erzeugt identische Hashes über Tabellen hinweg, mit Versionsparameter zur Unterstützung von Key-Rotation:

```sql
SHA2(CONCAT(val, CAST(version AS STRING)), 256)
```

## 8. Maskierung anhand von Identitätsattributen

```sql
NOT has_identity_attribute_value('department', 'HR')
```

Schränkt den Zugriff für alle Nutzer außerhalb der HR-Abteilung ein.

## 9. Row-Filterung mit reinen Spalten-Prädikaten

Ermöglicht Predicate Pushdown durch einfache Boolean-Logik:

```sql
array_contains(split(allowed, ','), lower(region))
```

## 10. Row-Filterung über mehrere Spalten

Kombiniert mehrere Spaltenbedingungen über separate `MATCH COLUMNS`-Klauseln, die beide Spalten an eine gemeinsame UDF übergeben — für zusammenhängende Attribute.

## 11. Zugriffsregeln über Lookup-Tabellen

Referenziert externe Tabellen für dynamischen Zugriff:

```sql
EXISTS (SELECT 1 FROM access_rules WHERE principal = session_user())
```

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/common-patterns
