# Tutorial: Datei-Pipelines

Referenz zum Tutorial für Datei-verarbeitende (medallion-artige) Pipelines mit dem `FILE`-Typ und KI-Funktionen, basierend auf `https://docs.databricks.com/aws/en/ldp/tutorial-file-pipelines`.

## Abschnittsübersicht

1. [Was baut man in diesem Tutorial?](#einleitung)
2. [Voraussetzungen](#voraussetzungen)
3. [Schritt 1: Bronze — Verträge als FILE-Referenzen einlesen](#schritt1)
4. [Schritt 2: Silver — Parsen und Klassifizieren](#schritt2)
5. [Schritt 3: Gold — Strukturierte Felder extrahieren](#schritt3)
6. [Quellen](#quellen)

---

## <a id="einleitung">1. Was baut man in diesem Tutorial?</a>

Das Tutorial zeigt den Aufbau einer Medaillon-Pipeline ("medallion pipeline") mit Lakeflow-Pipelines, die unstrukturierte Dokumente Ende-zu-Ende verarbeitet: Bronze (rohe, verwaltete `FILE`-Referenzen), Silver (geparste und klassifizierte Dokumente) und Gold (extrahierte Felder je Vertragstyp).

Konkret wird gelernt:

- Vertrags-PDFs aus einem Volume inkrementell als verwaltete `FILE`-Referenzen mit Auto Loader einzulesen.
- Jedes Dokument mit der Funktion `ai_parse_document` zu parsen und mit `ai_classify` zu klassifizieren.
- Strukturierte Felder für jeden Vertragstyp mit der Funktion `ai_extract` zu extrahieren.

## <a id="voraussetzungen">2. Voraussetzungen</a>

- In einem Databricks-Workspace mit aktiviertem Unity Catalog angemeldet sein.
- Der `FILE`-Typ muss für den Workspace aktiviert sein. Workspace-Admins können ihn über die Seite **Previews** aktivieren, indem sie **Manage Databricks previews** auswählen.
- Berechtigungen, Tabellen in einem Schema sowie eine Pipeline zu erstellen.
- Ein beschreibbares Unity-Catalog-Volume für den `FileSpace` der Bronze-Tabelle.
- Den Preview-Channel verwenden.

Diese Voraussetzungen zeigen deutlich: Der `FILE`-Datentyp sowie die KI-Funktionen `ai_parse_document`, `ai_classify` und `ai_extract` befinden sich zum Zeitpunkt dieses Tutorials im Preview-Status und müssen explizit aktiviert werden.

## <a id="schritt1">3. Schritt 1: Bronze — Verträge als FILE-Referenzen einlesen</a>

Contract-PDFs werden per Auto Loader (`cloudFiles`-Format `file`) aus einem Volume inkrementell als verwaltete `FILE`-Referenzen (`FILE MANAGED`) eingelesen. Die Zieltabelle referenziert dabei über die Tabelleneigenschaft `databricks.filespace-preview` einen eigenen Volume-Pfad als "FileSpace" für die eigentlichen Dateiinhalte.

```sql
CREATE OR REFRESH STREAMING TABLE raw_contracts (
  path STRING,
  size BIGINT,
  modification_time TIMESTAMP,
  file FILE MANAGED)
TBLPROPERTIES ('databricks.filespace-preview' = '/Volumes/my_catalog/my_schema/filespace/')
AS SELECT *
  FROM STREAM read_files(
    '/Volumes/samples/sec/contracts/',
    format => 'file');
```

```python
from pyspark import pipelines as dp

@dp.table(
  name="raw_contracts",
  schema="path STRING, size BIGINT, modification_time TIMESTAMP, file FILE MANAGED",
  table_properties={"databricks.filespace-preview": "/Volumes/my_catalog/my_schema/filespace/"})
def raw_contracts():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "file")
      .load("/Volumes/samples/sec/contracts/")
  )
```

## <a id="schritt2">4. Schritt 2: Silver — Parsen und Klassifizieren</a>

Zunächst wird jedes Dokument mit `ai_parse_document` geparst:

```sql
CREATE OR REFRESH MATERIALIZED VIEW parsed_contracts AS
  SELECT
    path,
    ai_parse_document(file) AS parsed
  FROM raw_contracts;
```

```python
@dp.materialized_view(name="parsed_contracts")
def parsed_contracts():
  return (
    spark.read.table("raw_contracts")
      .selectExpr("path", "ai_parse_document(file) AS parsed")
  )
```

Anschließend wird jedes erfolgreich geparste Dokument (geprüft über `is_variant_null(parsed:error_status)`) mit `ai_classify` einem von fünf Vertragstypen zugeordnet:

```sql
CREATE OR REFRESH MATERIALIZED VIEW classified_contracts AS
  SELECT
    path,
    parsed,
    ai_classify(
      parsed,
      '["affiliate_agreement", "marketing_agreement", "consulting_agreement", "hosting_agreement", "escrow_agreement"]',
      map('version', '2.1')
    ):response[0].value::STRING AS contract_type
  FROM parsed_contracts
  WHERE is_variant_null(parsed:error_status);
```

```python
@dp.materialized_view(name="classified_contracts")
def classified_contracts():
  return (
    spark.read.table("parsed_contracts")
      .filter("is_variant_null(parsed:error_status)")
      .selectExpr(
        "path",
        "parsed",
        """ai_classify(
             parsed,
             '["affiliate_agreement", "marketing_agreement", "consulting_agreement", "hosting_agreement", "escrow_agreement"]',
             map('version', '2.1')
           ):response[0].value::STRING AS contract_type""")
  )
```

## <a id="schritt3">5. Schritt 3: Gold — Strukturierte Felder extrahieren</a>

Für Verträge des Typs `consulting_agreement` werden über `ai_extract` gezielt strukturierte Felder (Firmenname, Berater, Vergütung, Datum) aus dem geparsten Dokument extrahiert und in eine flache Gold-Tabelle überführt.

```sql
CREATE OR REFRESH MATERIALIZED VIEW consulting_agreements AS
  WITH extracted AS (
    SELECT
      path,
      ai_extract(
        parsed,
        '["company_name", "consultant_name", "compensation_amount", "effective_date"]',
        map('version', '2.1')
      ) AS fields
    FROM classified_contracts
    WHERE contract_type = 'consulting_agreement'
  )
  SELECT
    path,
    fields:response.company_name.value::STRING AS company_name,
    fields:response.consultant_name.value::STRING AS consultant_name,
    fields:response.compensation_amount.value::STRING AS compensation_amount,
    fields:response.effective_date.value::STRING AS effective_date
  FROM extracted;
```

```python
@dp.materialized_view(name="consulting_agreements")
def consulting_agreements():
  return (
    spark.read.table("classified_contracts")
      .filter("contract_type = 'consulting_agreement'")
      .selectExpr(
        "path",
        """ai_extract(
             parsed,
             '["company_name", "consultant_name", "compensation_amount", "effective_date"]',
             map('version', '2.1')
           ) AS fields""")
      .selectExpr(
        "path",
        "fields:response.company_name.value::STRING AS company_name",
        "fields:response.consultant_name.value::STRING AS consultant_name",
        "fields:response.compensation_amount.value::STRING AS compensation_amount",
        "fields:response.effective_date.value::STRING AS effective_date")
  )
```

**Ergänzung (2026-08-20):** Für die übrigen vier klassifizierten Vertragstypen baut das Tutorial selbst keine Gold-Tabelle, benennt aber im Abschnitt "Explore on your own" konkrete Extraktionsfelder, mit denen sich das `consulting_agreements`-Muster (Filter auf `contract_type` + `ai_extract`) analog fortsetzen lässt:

| Vertragstyp | Vorgeschlagene Felder |
|---|---|
| `affiliate_agreement` | `party_1_name`, `party_2_name`, `commission_rate`, `payment_frequency` |
| `marketing_agreement` | `party_1_name`, `party_2_name`, `effective_date`, `territory` |
| `hosting_agreement` | `provider_name`, `customer_name`, `effective_date`, `term_length` |
| `escrow_agreement` | `owner_name`, `licensee_name`, `escrow_agent_name`, `software_name` |

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/tutorial-file-pipelines
