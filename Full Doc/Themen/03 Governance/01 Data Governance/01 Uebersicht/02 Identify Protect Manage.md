# Data-Privacy-Rahmenwerk: Identify, Protect, Manage

Aus privatem Kursmaterial übernommen, nicht gegen eine eigene offizielle Databricks-Konzeptseite verifiziert — ein nützlicher Ordnungsrahmen, um zu verorten, welche der in diesem Ordner beschriebenen Databricks-Fähigkeiten welches Datenschutz-Problem lösen. Datenschutz lässt sich in drei Phasen gliedern: **Identify**, **Protect**, **Manage**.

## 1. Identify — sensible Daten erkennen

Bevor irgendetwas geschützt werden kann, braucht es ein klares Bild davon, welche sensiblen Daten existieren, wo sie entstehen und wo sie verwendet werden.

- **Data Discovery** — organisationsweite Bestandsaufnahme personenbezogener/sensibler Daten.
- **Data Classification** — Einstufung nach Sensibilität (PII, Finanzdaten, Gesundheitsdaten, …), die festlegt, welche Schutzmaßnahmen und Compliance-Vorgaben gelten (siehe `08 ABAC/Grundkonzepte.md` zu Governed Tags als Klassifizierungs-Mechanismus).
- **Data Mapping** — Nachvollziehen, wie Daten durch die Organisation fließen: Speicherort, Zugriffsberechtigte, Bewegung zwischen Systemen (siehe `11 Auditing und System Tables/Audit Logs, Billing und Lineage.md`).

## 2. Protect — Schutzmaßnahmen abwägen

Sobald bekannt ist, was vorhanden und wie sensibel es ist, wird entschieden, wie (oder ob) es geschützt wird — ein Abwägen zwischen Nutzbarkeit und Risiko.

- **Technische Schutzmaßnahmen** — Verschlüsselung, Zugriffskontrollen, Firewalls (siehe `04 Access Control/Sicherheitsmodell und Verschluesselung.md`).
- **Data Minimization** — Datenerhebung auf das für den jeweiligen Geschäftszweck Notwendige beschränken.
- *(außerhalb des Databricks-Funktionsumfangs)* Consent Management, Privacy by Design.

Konkret stellt sich hier oft die Frage: anonymisieren oder pseudonymisieren — und falls pseudonymisiert wird, wie sichergestellt wird, dass sich der Schutz nicht leicht umkehren lässt (siehe `12 PII und Pseudonymisierung/Pseudonymisierung und Anonymisierung.md`).

## 3. Manage — Rechte laufend durchsetzen

Datenschutz ist kein einmaliger Akt, sondern muss aktiv gepflegt werden — insbesondere wenn Betroffene ihre Rechte ausüben.

- **Data Governance** — Richtlinien und Prozesse für den gesamten Lebenszyklus personenbezogener Daten (siehe die übrigen Kapitel dieses Ordners).
- **Compliance Management** — laufende Einhaltung von GDPR, CCPA, HIPAA usw. (siehe `Lakeflow Pipelines/10 Governance und Zugriff/GDPR.md` für die technische Umsetzung des „Rechts auf Vergessenwerden").
- **Ongoing Monitoring & Auditing** — regelmäßige Überprüfung anhand sich ändernder Bedrohungen/Vorgaben (siehe `11 Auditing und System Tables/`).
- *(außerhalb des Databricks-Funktionsumfangs)* Data Subject Access Requests (DSARs), Incident Response.

## Quelle

- Private Kursnotizen, nicht dokuverifiziert.
