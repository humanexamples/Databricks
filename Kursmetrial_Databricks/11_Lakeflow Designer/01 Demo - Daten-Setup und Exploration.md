![DB Academy](./Includes/images/common/db-academy.png)

# Demo - Daten-Setup und Exploration

## Überblick

In dieser Demo erkunden Sie die Quelldaten für den Lakeflow-Designer-Workflow, den Sie im nächsten Notebook erstellen werden.

Sie verwenden Catalog Explorer, um drei Bronze-Tabellen (sessions, participants, feedback) zu untersuchen, und werfen einen Blick in eine CSV-Datei, die Sie später über Lakeflow Designer hochladen werden.

Am Ende kennen Sie die Struktur, die Details und die Join-Schlüssel jedes Datensatzes und verstehen die Medallion-Architektur, den **Bronze -> Silber -> Gold**-Workflow, den Sie als Nächstes aufbauen.

## Lernziele

Am Ende dieser Demo können Sie:

- Mit Catalog Explorer durch Schemas navigieren und Beispieldaten sowie Tabellenmetadaten einsehen.
- Die Details und Join-Schlüssel für jede Bronze-Tabelle identifizieren.
- Verschachtelte Daten (ein `array<struct>`) erkennen und erklären, warum sie in Silber abgeflacht werden müssen.
- Die Medallion-Architektur beschreiben, die Sie in Lakeflow Designer aufbauen werden.

## PFLICHT - COMPUTE-UMGEBUNG AUSWÄHLEN

> **Serverless Compute auswählen**
>
> Wählen Sie vor Beginn dieses Notebooks die unten aufgeführte erforderliche Compute-Umgebung aus.
>
> - **Serverless Compute, Version 5**
>
> ![Serverless auswählen](./Includes/images/common/select-serverless.png)
>
> So wählen Sie eine Umgebungsversion aus:
> [AWS](https://docs.databricks.com/aws/en/compute/serverless/dependencies#-select-an-environment-version) |
> [Azure](https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/dependencies#-select-an-environment-version) |
> [GCP](https://docs.databricks.com/gcp/en/compute/serverless/dependencies#-select-an-environment-version)
>
> **HINWEIS:** Dieses Notebook erfordert **SQL und Python** und wurde mit **Serverless V5** getestet. All-Purpose Compute funktioniert eventuell, es wird aber nicht garantiert, dass es sich gleich verhält oder alle gezeigten Funktionen unterstützt.

## A. Classroom-Setup

1. Führen Sie die untenstehende Zelle aus. Sie wird:

    - Ihren persönlichen Katalog mit dem Namen **labuser_UNIQUE_ID** erstellen (oder verwenden).
    - Das Schema **designer_meeting** erstellen.
    - Die erforderlichen Bronze-Tabellen erstellen.

```text
%run ./Includes/Classroom-Setup-1
```

2. Führen Sie die untenstehende Zelle aus und bestätigen Sie, dass die folgenden Tabellen in Ihrem Schema **labuser_UNIQUE_ID.designer_meeting** erstellt wurden:
    - **feedback_bronze**
    - **participants_bronze**
    - **sessions_bronze**

```sql
SHOW TABLES IN designer_meeting;
```

## B. Szenario-Überblick

### B1. Überblick über die Medallion-Architektur

**Medallion-Architektur** – schrittweise Verfeinerung der Daten durch die Schichten Bronze, Silber und Gold.

| Schicht | Beschreibung | Merkmale |
|---|---|---|
| **Bronze** | Roh, wie eingelesen | Quelldateien und Streams; Schema bleibt erhalten; vollständige Historie wird aufbewahrt |
| **Silber** | Bereinigt, vereinheitlicht | Validiert und typisiert; verknüpft und dedupliziert; bereit für die Modellierung |
| **Gold** | Business-ready | Aggregierte Kennzahlen; für Analysen kuratiert; treibt BI und KI an |

> **Jede Schicht steigert Qualität und Wert.** Bronze erfasst die Quelle der Wahrheit, Silber bereinigt und vereinheitlicht sie zur Wiederverwendung, und Gold liefert die vertrauenswürdigen, analysebereiten Tabellen, die Dashboards, Berichte und KI antreiben.

<details>
<summary>Weitere Hinweise (aufklappen)</summary>

#### Warum ein mehrschichtiger Ansatz?

- Die Datenqualität verbessert sich mit jedem Schritt, sodass nachgelagerte Nutzer immer mit der Version arbeiten, die ihren Anforderungen entspricht.
- Jede Schicht hat eine klare Aufgabe, wodurch Datenflüsse leichter zu debuggen, zu verwalten und weiterzuentwickeln sind.
- Die erneute Verarbeitung ist sicher: Wird ein Fehler in der Silber- oder Gold-Logik gefunden, können Sie ausgehend von Bronze neu aufbauen, ohne erneut von der Quelle abzurufen.

#### Bronze: roh, wie eingelesen

- Die Landing Zone für Daten aus Dateien, Datenbanken, APIs oder Streams.
- Nah am Originalformat gespeichert. Das Schema bleibt erhalten, fehlerhafte Datensätze werden behalten statt verworfen.
- Verwenden Sie Bronze, wenn Sie eine originalgetreue Historie dessen benötigen, was wann eingetroffen ist.
- Typische Operationen: Ingest mit Auto Loader, neue Dateien anhängen, Ingestion-Zeitstempel hinzufügen.

#### Silber: bereinigt und vereinheitlicht

- Die Arbeitsschicht, in der Daten vertrauenswürdig werden.
- Typen werden erzwungen, Duplikate entfernt, Schlüssel standardisiert und Tabellen zu einem stimmigen Modell verknüpft.
- Verwenden Sie Silber, wenn Sie eine verlässliche Grundlage für Analysten, Data Scientists und nachgelagerte Workflows benötigen.
- Typische Operationen: Typen casten, fehlerhafte Zeilen verwerfen oder isolieren, nach Schlüsseln deduplizieren, Referenzdaten verknüpfen.

#### Gold: business-ready

- Die Serving-Schicht, konzipiert für den Konsum.
- Tabellen werden aggregiert, modelliert und nach der Geschäftsfrage benannt, die sie beantworten.
- Verwenden Sie Gold, wenn Sie schnelle, governte, leicht verständliche Tabellen für Dashboards, Berichte und KI möchten.
- Typische Operationen: Gruppieren und Aggregieren, KPIs berechnen, Star-Schemas oder Feature-Tabellen erstellen.

#### Wie es zu Lakeflow Designer passt

- In diesem Workshop sind die Bronze-Tabellen bereits für Sie erstellt.
- Sie werden Silber-Transformationen in Lakeflow Designer erstellen, um die Daten zu bereinigen und zu verknüpfen.
- Anschließend erstellen Sie Gold-Tabellen, die reale Fragen zu Sessions, Teilnehmern und Feedback beantworten.

</details>

### B2. Szenario

**Das Szenario: wöchentliche Event-Betriebsdaten**

Ein Team für virtuelle Events veranstaltet wöchentlich "Hands on Workshop (HOW)"-Deep-Dive-Sessions und sammelt dabei jede Woche vier Rohdatensätze. Ihre Aufgabe ist es, aus diesen Rohdaten etwas zu machen, das das Business tatsächlich nutzen kann.

| Tabelle / Datei | Quelle | Spalten | Granularität | Zeilen |
|---|---|---|---|---|
| **sessions_bronze** | Delta-Tabelle aus der Event-Plattform | meeting_uuid, how_name, event_date, presenter, topic_category, difficulty_level, planned_duration_minutes | Eine Zeile pro Session | 41 |
| **participants_bronze** | Delta-Tabelle aus der Event-Plattform | meeting_uuid, id, join_time, leave_time | Eine Zeile pro Teilnehmer und Session | 3.139 |
| **feedback_bronze** | Delta-Tabelle, enthält verschachteltes JSON | meeting_uuid, responses (JSON-Array); verschachtelte Felder: answer, question, question_id, respondent_id | Eine Zeile pro Session | 40 Sessions, ca. 3.000 verschachtelte Antworten |
| **participant_lookup.csv** | CSV-Datei von HR (Sie laden diese über Lakeflow Designer hoch) | id, email, department, job_title, region | Eine Zeile pro Teilnehmer | 598 |

**Ihre Aufgabe:**

- Heute sind diese Daten **Bronze**: roh, gemischte Datentypen, verschachtelte Arrays, keine Verknüpfungen zwischen den Tabellen.
- Erstellen Sie **Silber**-Tabellen, die bereinigt, typisiert und verknüpfbar sind.
- Erstellen Sie **Gold**-KPIs, die reale Geschäftsfragen zu Teilnahme, Bewertungen und Engagement beantworten.
- Erledigen Sie das alles **ohne Code**, mit Lakeflow Designer.

## C. Vorschau der Tabellen mit Catalog Explorer

Eine der großen Stärken von Databricks ist, dass Sie Daten erkunden können, **ohne Code zu schreiben**. Wir führen die gesamte Tabellenerkundung in diesem Abschnitt über die Oberfläche von Catalog Explorer durch.

Machen wir uns mit dem Inhalt jeder Tabelle vertraut, bevor wir unsere visuelle Datenaufbereitung in Lakeflow Designer aufbauen.

### C1. Catalog Explorer in einem neuen Tab öffnen

1. Wählen Sie in der Workspace-Seitenleiste das Symbol **Catalog** ![Catalog-Symbol](./Includes/images/common/catalog-icon.png).

2. Klicken Sie mit der rechten Maustaste auf Ihren Katalog **labuser_UNIQUE_ID** und wählen Sie **Open in Catalog Explorer**.
   - Wenn Sie dieses Notebook und Catalog Explorer nebeneinander offen halten, lässt sich der Rest des Abschnitts leichter verfolgen.

3. Wählen Sie in Catalog Explorer das Schema **designer_meeting** aus.

4. Bestätigen Sie, dass Sie drei Tabellen sehen:
   - **feedback_bronze**
   - **participants_bronze**
   - **sessions_bronze**

5. Wählen Sie oben in Catalog Explorer über die Warehouse-Auswahl ein SQL-Warehouse aus.

6. Lassen Sie **Catalog Explorer** geöffnet.

### C2. sessions_bronze erkunden

Diese Tabelle enthält **eine Zeile pro Session**. Sie zeigt, worum es in jeder Session ging, wann sie stattfand, wer präsentiert hat und wie lange sie geplant war.

**In Catalog Explorer:**

1. Klicken Sie auf **sessions_bronze**.

2. Klicken Sie auf den Tab **Sample Data**, um die Tabelle in der Vorschau anzuzeigen.

3. Achten Sie beim Betrachten der Beispieldaten auf Folgendes:

   | Spalte | Worauf zu achten ist |
   |---|---|
   | **meeting_uuid** | Der Primärschlüssel. Jede andere Tabelle verknüpft sich über diese Spalte zurück. |
   | **how_name**, **presenter**, **topic_category**, **difficulty_level** | Sessiontitel, Presenter und Gruppierungsfelder. |
   | **event_date** | Sieht aus wie ein Datum, ist aber als **String** gespeichert. Das korrigieren wir in Silber. |
   | **_rescued_data** | Leer. Dies ist die Auto-Loader-Spalte, die fehlerhafte Zeilen erfasst. Wir entfernen sie in Silber. |

4. Stellen Sie nun folgende Frage zu den Daten, um sie zu erkunden:

   > Wie viele Sessions gibt es pro topic_category?

5. Databricks generiert das SQL und führt es für Sie aus. Lesen Sie das Ergebnis.

**HINWEIS:** Erkunden Sie die Daten gerne weiter, wenn Sie zusätzliche Details wünschen.

### C3. participants_bronze erkunden

Diese Tabelle enthält **eine Zeile pro Teilnehmer und Session**. Es handelt sich um das Anwesenheitsprotokoll.

**In Catalog Explorer:**

1. Navigieren Sie zu **participants_bronze** > **Sample Data**.

2. Achten Sie beim Betrachten der Beispieldaten auf Folgendes:

   | Spalte | Worauf zu achten ist |
   |---|---|
   | **meeting_uuid** | Verknüpft sich zurück zu **sessions_bronze**. |
   | **id** | Die Teilnehmer-ID. Verknüpft sich mit der Participant-Lookup-CSV, die Sie später hochladen. |
   | **join_time**, **leave_time** | Sehen aus wie Zeitstempel, sind aber als **Strings** gespeichert. Wir casten sie in Silber. |
   | **_rescued_data** | Leer. Dies ist die Auto-Loader-Spalte, die fehlerhafte Zeilen erfasst. Wir entfernen sie in Silber. |

3. Stellen Sie nun folgende Fragen zu den Daten, um sie zu erkunden:

> Prüfen Sie die Daten auf NULL-IDs und zeigen Sie alle Zeilen an.

> **Warnung – Datenprobleme**
>
> #### Problem 1 – NULL-IDs
> Die Quelldaten enthalten **20** Zeilen mit einer `NULL`-id (keine Teilnehmeridentität). Wir entfernen diese in Silber, da sie sich mit keinem Teilnehmer- oder Feedback-Datensatz verknüpfen lassen.

> Berechnen Sie die Gesamtdauer in Minuten, die jeder Teilnehmer in der Session war. Die Spalten join_time und leave_time enthalten Datums- und Zeitwerte, die als Text gespeichert sind, zum Beispiel 2025-11-03T12:04:27.000+00:00. Wandeln Sie diese Textwerte vor der Berechnung der Dauer in Zeitstempel um. Behalten Sie die ursprünglichen Werte von join_time und leave_time bei und sortieren Sie aufsteigend nach Dauer. Verwenden Sie kein benutzerdefiniertes Datetime-Muster.

> **Warnung – Datenprobleme**
>
> #### Problem 2 – Ungültige Join-Zeit
> Beachten Sie, dass die ersten 23 Zeilen einen negativen Wert für **duration_in_minutes** aufweisen.
>
> Dies liegt an einem Problem in unseren Quelldaten (die **leave_time** wurde für diese Teilnehmer früher erfasst als die **join_time**).
>
> Wir berücksichtigen dies während unserer **Bronze -> Silber**-Datenaufbereitung. Wir wandeln **duration_in_minutes** für diese Zeilen in `NULL` um, damit wir die Teilnehmer in unserem Szenario behalten können, ohne nachgelagerte Durchschnittswerte zu verzerren.
>
> ##### Beispielausgabe (kann bei KI-Generierung variieren)
>
> | participant_id | meeting_uuid | duration_in_minutes |
> |---|---|---:|
> | `+vnj6eUbRXil6g+A5UQ2Aw==` | `4iUQF0z3Rs+SG6H6Ap0cdQ==` | -38479020 |
> | `O2f4GoghTqu89VTtEkJTKw==` | `MUVmi3YYTNyigYwwrmD4VQ==` | -38479020 |
> | `iayLedmCQ2evbeN3EaBgvw==` | `6uqID4Q6RNOs9BF+ysV86Q==` | -38479020 |
> | `...` | `...` | `...` |

### C4. feedback_bronze erkunden (eine STRING-Spalte, die ein JSON-Array von Objekten enthält)

Diese Tabelle ist anders. Jede Zeile ist eine Session, und die Spalte **responses** enthält **jede Umfrageantwort** für diese Session als verschachtelte Daten.

**In Catalog Explorer:**

1. Klicken Sie auf **feedback_bronze**.

2. Klicken Sie auf den Tab **Sample Data**, um die Tabelle in der Vorschau anzuzeigen. Klicken Sie dann auf den kleinen Erweiterungspfeil bei einer **responses**-Zelle, um in eine Zeile hineinzuschauen.

3. Achten Sie beim Betrachten der Beispieldaten auf Folgendes:

   | Spalte | Worauf zu achten ist |
   |---|---|
   | **meeting_uuid** | Identifiziert, zu welcher Session dieses Feedback gehört. Verknüpft sich zurück zu **sessions_bronze**. |
   | **responses** | Eine String-Spalte, die ein JSON-Array von Objekten enthält. Jedes Objekt im Array hat 4 Felder: **answer**, **question**, **question_id**, **respondent_id**. |
   | Zeilenanzahl | Nur **40 Zeilen**, eine pro Session. Aber jede Zeile enthält Dutzende verschachtelter Antworten. |
   | Was wir in Silber tun werden | Die responses abflachen, sodass jede einzelne Antwort zu einer eigenen Zeile wird. |

   Die Spalte **responses** enthält **5 unterschiedliche Fragen**:

   | Frage | Antworttyp |
   |---|---|
   | Rate the session content. | Numerisch (1–5) |
   | Rate the speaker. | Numerisch (1–5) |
   | What did you like about the content in this session? | Freitext |
   | What could have been improved? | Freitext |
   | What additional topics would you like to get a deep dive on? | Freitext |

### C5. Vorschau der Participant-Lookup-CSV

> **Hinweis**
>
> Wir stellen die CSV-Datei mit dem Kursinhalt bereit, aber stellen Sie sich für den Workshop vor, **dass diese Datei bei Ihnen auf dem Laptop liegt, aus einer anderen internen Quelle**.
>
> Im nächsten Notebook laden Sie sie über die Datei-Upload-Oberfläche von Lakeflow Designer hoch, genauso wie Sie sie von Ihrem lokalen Rechner hochladen würden.

Die letzte Tabelle wird aus einer **von HR bereitgestellten CSV-Datei** erstellt.

- Diese Datei befindet sich im Ordner `participant_lookup`. Wir simulieren später den Upload in Lakeflow Designer.

1. Navigieren Sie im Hauptordner zum Ordner `participant_lookup` > `how_participant_lookup_week_1.csv`.

**Kurzinfo zur Participant-Lookup-CSV-Datei:**

| Eigenschaft | Wert |
|---|---|
| Quelle | CSV-Datei im Workspace (Sie laden sie als Nächstes über Lakeflow Designer hoch) |
| Granularität | Eine Zeile pro Teilnehmer |
| Join-Schlüssel | **id** -> **participants_bronze.id** |
| Spalten | **id**, **email**, **department**, **job_title**, **region** |
| Trennzeichen | Komma |
| Zeilenanzahl | 598 |

## D. Projektüberblick

Jetzt, da Sie die Daten kennen, folgt hier der Medallion-Workflow, den Sie im nächsten Notebook mit **Lakeflow Designer** aufbauen werden.

### Der visuelle Workflow, den Sie erstellen werden

- Eine lokale CSV-Datei wird in ein Volume importiert.
- Bronze wird zu **Silber** bereinigt.
- Aus Silber werden zwei Gold-Tabellen abgeleitet. Eine Bonus-Tabelle mit KI-Unterstützung wird als Hausaufgabe angeboten.

**Manueller Datei-Upload in ein Volume**

| Element | Beschreibung |
|---|---|
| CSV-Datei: `how_participant_lookup_week_1.csv` | Hochgeladenes Teilnehmerverzeichnis |

> **Upstream-Workflow · läuft nach Zeitplan — Quell-Workflow, verwaltet von einem anderen Team**
>
> Ein anderes Team lädt die Meeting-Quelldaten nach Zeitplan als Bronze-Tabellen ein und aktualisiert die Tabellen mit neuen Sessions, Teilnehmern und Feedback. Sie halten Silber und Gold aktuell.

Sowohl die hochgeladene CSV-Datei als auch der Upstream-Workflow speisen die folgende Bronze-Schicht:

**Bronze-Schicht**

| Tabelle | Beschreibung |
|---|---|
| **participant_lookup_bronze** | Lookup, eingelesen aus der CSV |
| **sessions_bronze** | Rohe Session-Metadaten, eine Zeile pro Session |
| **participants_bronze** | Anwesenheitsprotokoll, eine Zeile pro Teilnehmer und Session |
| **feedback_bronze** | Umfrageantworten, gespeichert als JSON-Array pro Session |

*(wird bereinigt zu)*

**Silber-Schicht**

| Tabelle | Beschreibung |
|---|---|
| **participant_lookup_silver** | E-Mail und Region in Teile aufgesplittet |
| **sessions_silver** | Datum typisiert, how_name in session_name umbenannt |
| **participants_silver** | Zeitstempel typisiert, duration_in_minutes hinzugefügt |
| **feedback_silver** | JSON entpackt (exploded), eine Zeile pro Antwort |

*(verknüpfen und aggregieren ↓)*

**Gold-Schicht**

| Tabelle | Beschreibung |
|---|---|
| **gold_session_summary** | Session-Metadaten mit Teilnahme-Kennzahlen |
| **gold_feedback_summary** | Durchschnittliche Bewertungen auf Session-Ebene |
| **gold_feedback_sentiment** *(Bonus / Hausaufgabe)* | Freitextantworten, getaggt mit ai_sentiment |

---

© Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).
