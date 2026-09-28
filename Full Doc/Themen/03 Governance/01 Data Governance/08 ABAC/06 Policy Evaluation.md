# Policy Evaluation — Auswertung und Laufzeitverhalten

Wie Row-Filter- und Column-Mask-Policies bei der Query-Ausführung ausgewertet und durchgesetzt werden.

## Zweistufiger Auswertungsprozess

Die Zugriffskontrolle läuft in zwei Stufen ab: **Policy Evaluation** in Unity Catalog und **Policy Enforcement** in der Databricks Runtime — beide bestimmen gemeinsam, wie die Kontrollen anhand von Nutzeridentität und Gruppenmitgliedschaften auf eine konkrete Query angewendet werden.

## Fail-Closed-Sicherheitsmodell

Kann eine Prüfung nicht abgeschlossen werden, verweigert das System den Zugriff standardmäßig, statt ihn zu gewähren. Das gilt für nicht unterstützte Compute-Versionen, inkompatible Operationen und fehlende Policy-Abhängigkeiten.

## Anforderungen

- ABAC-Policies benötigen **Databricks Runtime 16.4 oder höher**, oder Serverless Compute. Ältere Runtimes werden vom Zugriff auf geschützte Tabellen blockiert.
- Bestimmte Workflows — Time-Travel-Queries, Klon-Operationen, Pipeline-Refreshes, AI-Search-Indexierung — erfordern, dass die betroffenen Principals explizit in einer `EXCEPT`-Klausel gelistet sind, um die Policy-Durchsetzung zu umgehen.

## Absicherung bei fehlenden Abhängigkeiten

| Szenario | Verhalten |
|---|---|
| Governed Tag gelöscht | Queries schlagen fehl mit `INVALID_PARAMETER_VALUE.UC_ABAC_UNKNOWN_TAG_POLICY` |
| Getaggte Spalte soll gelöscht werden | Blockiert, sofern das Tag nicht zuvor von autorisierten Nutzern entfernt wurde |
| Funktion gelöscht | Fehler `UC_DEPENDENCY_DOES_NOT_EXIST` |

## Konfliktauflösung

Pro Tabelle und Nutzer darf zur Query-Zeit nur **ein** eindeutiger Row Filter gelten — analog für Column Masks. Mehrere widersprüchliche Policies lösen einen Fehler aus und blockieren den Zugriff.

`SHOW EFFECTIVE POLICIES` und die `INFORMATION_SCHEMA`-Tabellen helfen, Konflikte zu diagnostizieren.

## Type Casting

Databricks castet Eingabe und Ausgabe von Column-Mask-Funktionen automatisch, um Typkonsistenz sicherzustellen — inklusive Struct-zu-`VARIANT`-Konvertierung ab Runtime 18.1.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/policy-evaluation
