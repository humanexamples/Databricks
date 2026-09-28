# Prozedural vs. deklarative Datenverarbeitung

Databricks unterstützt zwei grundlegende Programmierparadigmen für die Datenverarbeitung: prozedural und deklarativ. Diese Seite erklärt den Unterschied und hilft bei der Wahl des passenden Ansatzes.

## Kernunterschied

- **Prozedural:** Sie legen explizit fest, *wie* eine Aufgabe erledigt wird – durch eine genaue Abfolge von Operationen.
- **Deklarativ:** Sie beschreiben, *was* erreicht werden soll – das System entscheidet selbst, wie es die Aufgabe am besten ausführt.

## Prozedurale Verarbeitung

**Merkmale:**

- Explizite, Schritt-für-Schritt-Ausführungsreihenfolge
- Nutzt Kontrollstrukturen (Schleifen, Bedingungen, Funktionen)
- Ermöglicht feingranulares Ressourcenmanagement
- Ist eine Unterform der imperativen Programmierung

**Typische Einsatzbereiche:**

- Individuelle ETL-Pipelines mit prozeduraler Logik
- Low-Level-Performance-Optimierungen in Batch- und Streaming-Workloads
- Altsysteme oder bestehende imperative Skripte

**Umsetzung in Databricks:** Apache Spark und Lakeflow Jobs bieten prozedurale Ausführungs-Frameworks.

## Deklarative Verarbeitung

**Merkmale:**

- Abstrahiert die Ausführungsdetails
- Das System übernimmt die automatische Optimierung
- Reduziert Komplexität durch weniger explizite Kontrollstrukturen
- Umfasst domänenspezifische und funktionale Paradigmen

**Typische Einsatzbereiche:**

- SQL-basierte Transformationen
- High-Level-Datenverarbeitungs-Frameworks
- Skalierbare verteilte Workloads

**Umsetzung in Databricks:** Lakeflow-Pipelines nutzen Apache Spark Declarative Pipelines (SDP), um zuverlässige und wartbare Stream-Processing-Pipelines einfacher erstellbar zu machen.

## Entscheidungshilfe

Wählen Sie **prozedural**, wenn feingranulare Kontrolle oder komplexe Geschäftsregeln mit manueller Optimierung erforderlich sind.

Wählen Sie **deklarativ**, wenn einfache Entwicklung, Wartung und eingebaute Systemoptimierungen im Vordergrund stehen.

---
**Quelle:** https://docs.databricks.com/aws/en/data-engineering/procedural-vs-declarative  
**Stand:** 2026-08-07
