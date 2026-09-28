# Pseudonymisierung und Anonymisierung von PII

Techniken, um personenbezogene Daten (PII) vor der Weiterverarbeitung zu schützen — als Ergänzung zu Row Filtern, Column Masks und ABAC (siehe `07 Filters und Masks/` und `08 ABAC/`), die den *Zugriff* auf Daten steuern, während die hier beschriebenen Techniken die *Daten selbst* verändern.

**Grundprinzip:** Mit ausreichend Zeit und Zugriff auf zusätzliche Daten lässt sich ein Großteil der Daten unabhängig von der gewählten Methode potenziell re-identifizieren. Pseudonymisierung und Anonymisierung reduzieren das Risiko und die Sichtbarkeit für die meisten Nutzer eines Datasets, eliminieren es aber nicht vollständig.

Die folgenden Konzepte, Vor-/Nachteile und der Vergleich sind aus privatem Kursmaterial übernommen und **nicht gegen eine eigene offizielle Databricks-Konzeptseite verifiziert** — es existiert keine dedizierte Doku-Seite zu Pseudonymisierungs-/Anonymisierungsstrategien; nur die verwendete SQL-Funktion `sha2()` sowie das Muster "konsistentes Hashing" in `08 ABAC/Haeufige Muster.md` sind offiziell dokumentiert.

## Pseudonymisierung — reversibel, Record-Ebene

Ersetzt PII durch künstliche, aber eindeutige Identifikatoren (Token, Hashes, verschlüsselte Werte). Der Vorgang ist **umkehrbar** — pseudonymisierte Daten gelten laut GDPR weiterhin als personenbezogene Daten. Autorisierte Nutzer mit Zugriff auf Schlüssel/Hash-Tabelle können re-identifizieren; Data Scientists können mit vollständigen Datensätzen arbeiten, ohne die zugrunde liegenden Klartextwerte einsehen zu können.

### Methode: Hashing

Eine Hash-Funktion erzeugt aus dem PII-Wert eine zufällig aussehende, deterministische Zeichenkette. Da Hashes deterministisch sind, wird **Salting** empfohlen — ein zufälliger String wird vor dem Hashen angehängt, um Rainbow-Table-Angriffe zu erschweren. Der Salt-Wert lässt sich über die Databricks-Secrets-API verwalten, sodass er nie im Klartext im Notebook erscheint und nur autorisierte Produktions-Jobs/Nutzer Zugriff darauf haben.

```python
salt = "BEANS"

def salted_hash(id):
    return F.sha2(F.concat(id, F.lit(salt)), 256)
```

`sha2(expr, bitLength)` ist eine dokumentierte SQL/PySpark-Funktion — `bitLength` akzeptiert `0` (Standard, entspricht 256), `224`, `256`, `384` oder `512` und liefert eine hexadezimale Prüfsumme aus der SHA-2-Familie zurück:

```sql
SELECT sha2('Spark', 256);
-- 529bc3b07127ecb7e53a4dcf1991d9152c24537d919178022b2c42657f79a26b
```

**Vorteile:** praktisch irreversibel, Datenverknüpfung über den Hash-Wert weiterhin möglich, erhält die Datenverteilung, kein Systemumbau nötig.
**Nachteile:** höherer Speicherbedarf (Hash-Werte sind länger als die Originaldaten), teilweise Rückschlüsse aus der Werteverteilung möglich, keine echte Rückgewinnung des Originalwerts — problematisch z. B. bei ML-Preprocessing, wenn Teilinformationen (etwa die Domain einer E-Mail-Adresse) separat weiterverarbeitet werden müssen und daher getrennt gehasht werden sollten.

### Methode: Tokenization

Jeder eindeutige PII-Wert wird durch einen zufälligen Token (z. B. eine UUID) ersetzt; die Zuordnung Token ↔ Originalwert wird in einer sicheren Lookup-/Vault-Tabelle gespeichert. Tokenization ist **langsam beim Schreiben, schnell beim Lesen** — die dem Endnutzer zugängliche Tabelle enthält nur den kompakten Token.

```python
.withColumn("token", F.expr("uuid()"))
# gespeichert in einer Token-Tabelle, per Join mit dem Original verknüpft
```

**Vorteile:** hoher Schutzgrad, der Token ersetzt den echten Wert 1:1 in nachgelagerten Operationen, schnell beim Lesen.
**Nachteile:** langsam beim Schreiben, benötigt ein robustes eigenes Tokenisierungssystem/Vault; bei Kompromittierung des Vaults sind alle Originalwerte sofort wiederherstellbar.

### Hashing vs. Tokenization im Vergleich

| | Hashing | Tokenization |
|---|---|---|
| Rückgewinnung | praktisch irreversibel | vollständig reversibel über den Vault |
| Geschwindigkeit | schnell, kein Lookup nötig | schreiblastig langsam, lesend schnell |
| Speicherbedarf | erhöht (Hash-Länge) | gering (kompakter Token) |
| Schutzgrad | moderat–hoch | hoch |
| Risiko bei Kompromittierung | Rückschlüsse aus Werteverteilung möglich, kein direkter Rückweg | bei Vault-Kompromittierung alle Originalwerte abrufbar |
| Typischer Einsatz | Passwörter, kein Rückführungsbedarf | Zahlungsdaten, kontrollierte Rückführung |

## Anonymisierung — irreversibel, Datensatz-Ebene

Schützt ganze Datasets (Tabellen, Datenbanken, Kataloge) und verändert personenbezogene Daten **irreversibel** so, dass Betroffene weder direkt noch indirekt identifizierbar sind — passend für Business-Intelligence-Anwendungsfälle, bei denen Aggregationen und Trends im Vordergrund stehen. In der Praxis werden meist mehrere Techniken kombiniert.

### Methode: Data Suppression

Bedingte Filter und dynamische Zugriffskontrollen entfernen den Zugriff auf Spalten oder Zeilen, ohne die Reporting-Fähigkeit einzuschränken — z. B. lässt sich eine regionale Aggregation weiterhin erstellen, ohne vollständige Kundennamen/-adressen offenzulegen. Aggregation allein bietet keinen Schutz und kann sensible Daten über Reports/Dashboards offenlegen, wenn z. B. eine Gruppierungsspalte nur sehr wenige Datensätze enthält (kleine Städte, dünn besetzte demografische Gruppen). Ein Filter, der Gruppen mit niedriger Zeilenzahl entfernt, schützt Einzelidentitäten zusätzlich; dynamische Zugriffskontrollen (siehe `08 ABAC/`) erlauben gruppenbasierte Redaktion/Filterung.

### Methode: Generalization

Entfernt Präzision aus den Daten, um Re-Identifikation zu erschweren — je nach Datentyp auf unterschiedliche Weise:

- **Categorical Generalization:** kleinere Kategorien zu größeren zusammenfassen (z. B. Stadt → Bundesland/Land), damit dünn besetzte Gruppen nicht auf Einzelpersonen zurückführbar sind.
- **Binning:** z. B. 10-Jahres-Altersbänder oder Gehaltsbänder statt Einzelwerten — Reports bleiben aussagekräftig, ohne den exakten Wert einer Person offenzulegen. Die passende Bin-Größe hängt vom Anwendungsfall ab und sollte mit Domänenexpertise festgelegt werden.
- **IP-Truncation:** das letzte Byte einer IP-Adresse durch `0` ersetzen, um sie in den `/24`-CIDR-Bereich zu bringen.
- **Rounding:** Werte auf eine gröbere Genauigkeit runden (z. B. auf die nächsten 5) — allgemeine Trends bleiben erhalten, da gleichmäßig auf- und abgerundet wird; die höchsten/niedrigsten Gruppen können aber weiterhin Ausreißer offenlegen und ggf. zusätzlich unterdrückt werden müssen.

## Vergleich der Schutztechniken (Zusammenfassung, aus Kursmaterial)

| Technik | Beschreibung | Beispiel | Typischer Einsatz | Vorteile | Nachteile | Schutzgrad |
|---|---|---|---|---|---|---|
| **Data Masking** | Originaldaten mit verändertem Inhalt verdecken (Dynamic Masking) | `gXXX.dXXXX@gmx.de` | operative Nutzbarkeit bei reduzierter Sichtbarkeit | Format bleibt erhalten, Teilinformation bleibt nutzbar | verändert die Datenverteilung, teils aus Nachbarspalten rekonstruierbar, keine Verknüpfung möglich | niedrig–moderat |
| **Pseudo-Anonymisierung** | Werte durch Pseudonyme ersetzen | `charles@gmx.de` | Verlaufsstudien mit Tracking-Bedarf bei geschützter Identität | statistische Verteilung bleibt erhalten, Verknüpfung mehrerer Datasets möglich | Rückschlüsse aus Verteilung möglich, Verknüpfungstabelle muss sicher gespeichert werden | niedrig–moderat |
| **Hashing** | irreversible Transformation | `cf35ddff242..` | Passwort-Speicherung | sicher/irreversibel, Verknüpfung möglich, erhält Verteilung | Rückschlüsse aus Verteilung möglich, keine Rückgewinnung | moderat–hoch |
| **Column Encryption** | spaltenweise Verschlüsselung vor dem Speichern | `skjrk42ndd..` | Schutz einzelner sensibler Spalten | hohe Sicherheit, Einzelwerte/Verteilung beobachtbar | Schlüsselverwaltung nötig, deutlich größerer Speicherbedarf, Verknüpfung schwierig, Verteilung verändert sich | hoch |
| **Tokenization** | Ersetzung durch Token | `fik52tklhn2..` | Kreditkarten-Transaktionen | Token ersetzt Originaldaten 1:1 in Operationen | robustes Tokenisierungssystem nötig, bei Kompromittierung vollständig rückgewinnbar | hoch |

## Best Practices für den Umgang mit PII (aus Kursmaterial)

1. Keine PII zu haben ist immer besser, als PII zu schützen.
2. Rangfolge der Schutzwirkung: Anonymisierung > Pseudonymisierung > Klartext.
3. Eine gesunde Skepsis gegenüber den eigenen angewandten Schutzmaßnahmen bewahren.
4. Stets bedenken, wie sich Datasets kombinieren ließen, um Re-Identifikation zu ermöglichen.
5. Datenteams regelmäßig zu den anwendbaren Datenschutzgesetzen schulen.
6. Nicht jede Art von PII ist gleich sensibel — Schutzmaßnahmen entsprechend abstufen.
7. Privacy-Impact-Assessments (PIA) durchführen.
8. Umgebungen, die PII verarbeiten, konsequent isolieren (siehe `Sicherheitsmodell und Verschluesselung.md`).

## Praxisbeispiel: Salted Hashing und Tokenization als Pipeline

Aus privatem Kursmaterial übernommen (kurseigene Übung), aber echter, lauffähiger Lakeflow-Declarative-Pipelines-Code — kein fiktives SDK. Erstellt aus einer Quelltabelle mit Nutzerregistrierungsdaten zwei parallele Pseudonymisierungs-Pfade:

```python
from pyspark import pipelines as dp
import pyspark.sql.functions as F

user_reg_source = spark.conf.get("user_reg_source")

# Quelldaten inkrementell mit Auto Loader einlesen
@dp.table
def registered_users():
    return (
        spark.readStream
            .format("cloudFiles")
            .schema("device_id LONG, mac_address STRING, registration_timestamp DOUBLE, user_id LONG")
            .option("cloudFiles.format", "json")
            .load(f"{user_reg_source}")
        )

# --- Pfad 1: Salted Hashing ---
salt = "BEANS"

def salted_hash(id):
    return F.sha2(F.concat(id, F.lit(salt)), 256)

@dp.table
def user_lookup_hashed():
    return (dp
            .read_stream("registered_users")
            .select(
                  salted_hash(F.col("user_id")).alias("alt_id"),
                  "device_id", "mac_address", "user_id")
           )

# --- Pfad 2: Tokenization ---
@dp.table
def registered_users_tokens():
    return (dp
            .readStream("registered_users")
            .select("user_id")
            .distinct()
            .withColumn("token", F.expr("uuid()"))
        )

@dp.table
def user_lookup_tokenized():
    return (dp
            .read_stream("registered_users")
            .join(dp.read("registered_users_tokens"), "user_id", "left")
            .drop("user_id")
            .withColumnRenamed("token", "alt_id")
           )
```

`user_lookup_hashed` und `user_lookup_tokenized` dienen anschließend als einzige Verknüpfung zwischen einer pseudonymen `alt_id` und der echten `user_id` — der Zugriff auf diese Lookup-Tabellen lässt sich getrennt und restriktiv vergeben, sodass andere Tabellen im System nur die pseudonyme ID kennen.

## Praxisbeispiel: Binning-Anonymisierung (Altersbänder)

Ebenfalls aus privatem Kursmaterial, echter Pipeline-Code. Die Funktion `age_bins()` berechnet aus einem Geburtsdatum das Alter und ordnet es 10-Jahres-Bändern zu, statt das exakte Alter offenzulegen:

```python
def age_bins(dob_col):
    age_col = F.floor(F.months_between(F.current_date(), dob_col) / 12).alias("age")
    return (
        F.when((age_col < 18), "under 18")
        .when((age_col >= 18) & (age_col < 25), "18-25")
        .when((age_col >= 25) & (age_col < 35), "25-35")
        .when((age_col >= 35) & (age_col < 45), "35-45")
        .when((age_col >= 45) & (age_col < 55), "45-55")
        .when((age_col >= 55) & (age_col < 65), "55-65")
        .when((age_col >= 65) & (age_col < 75), "65-75")
        .when((age_col >= 75) & (age_col < 85), "75-85")
        .when((age_col >= 85) & (age_col < 95), "85-95")
        .when((age_col >= 95), "95+")
        .otherwise("invalid age")
        .alias("age")
    )

@dp.table
def user_age_bins():
    return (
        dp.read("users_bronze")
        .select("user_id", age_bins(F.col("dob")), "gender", "city", "state")
    )
```

Das Ergebnis `user_age_bins` erlaubt Auswertungen nach Altersgruppe, Geschlecht, Stadt und Bundesland, ohne das exakte Geburtsdatum in der Ausgabetabelle zu führen.

## Verwandte Themen

- `08 ABAC/Haeufige Muster.md`, Abschnitt "Konsistentes Hashing / deterministische Pseudonymisierung" — dasselbe `SHA2`-Grundmuster, dort als dokuverifizierte ABAC-Column-Mask-Funktion.
- `Lakeflow Pipelines/10 Governance und Zugriff/GDPR.md` — Löschstrategien (Bronze-first, `skipChangeCommits`, Materialized Views) für das "Recht auf Vergessenwerden"; dort gilt ausdrücklich: **vollständige Löschung ist Obfuskation/Pseudonymisierung vorzuziehen**, wo immer möglich.
- `Lakeflow Pipelines/05 CDC/Change Data Feed.md` — Propagation von Löschungen (inkl. pseudonymisierter Datensätze) durch nachgelagerte Tabellen.

## Quellen

- https://docs.databricks.com/aws/en/sql/language-manual/functions/sha2 (Funktionsreferenz `sha2()`)
- https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/common-patterns (Muster "konsistentes Hashing", dokuverifiziert in `08 ABAC/Haeufige Muster.md`)
- Konzeptueller Rahmen (Pseudonymisierung/Anonymisierung, Vergleichstabelle, Best Practices, Pipeline-Beispiele): private Kursnotizen, nicht gegen eine eigene offizielle Databricks-Konzeptseite verifiziert
