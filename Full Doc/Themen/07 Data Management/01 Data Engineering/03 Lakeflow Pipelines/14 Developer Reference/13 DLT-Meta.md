# DLT-Meta

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Anwendungsfälle](#anwendungsfaelle)
3. [Funktionsweise](#funktionsweise)
4. [Nutzen](#nutzen)
5. [Support-Status](#support)
6. [Quellen](#quellen)

---

## <a id="ueberblick">1. Überblick</a>

`dlt-meta` ist ein "metadatengetriebenes Metaprogrammierungs-Framework, konzipiert für die Zusammenarbeit mit Lakeflow-Pipelines" (*"a metadata-driven metaprogramming framework designed to work with Lakeflow pipelines"*). Es automatisiert die Erstellung von Bronze- und Silver-Datenpipelines, indem es Python-Code aus JSON- und YAML-Metadatendateien generiert.

---

## <a id="anwendungsfaelle">2. Anwendungsfälle</a>

Laut Doku zwei zentrale Anwendungsfälle:

1. Effizientes Ingestion und Bereinigen einer großen Zahl von Tabellen,
2. Durchsetzung einheitlicher Data-Engineering-Standards über mehrere Pipelines hinweg.

---

## <a id="funktionsweise">3. Funktionsweise</a>

Das System folgt einem vierstufigen Prozess:

1. Metadatendateien erstellen, die Quellen, Ausgaben, Qualitätsregeln und Verarbeitungsanforderungen spezifizieren.
2. `dlt-meta` kompiliert diese zu einer `DataflowSpec`.
3. Die Engine generiert Bronze-Tabellen-Pipelines.
4. Die Engine generiert Silver-Tabellen-Pipelines mit den passenden Transformationen.

---

## <a id="nutzen">4. Nutzen</a>

Der metadatengetriebene Ansatz reduziert laut Doku den Pflegeaufwand: *"maintaining metadata, rather than the code, requires less overhead, and reduces errors"* — die Pflege von Metadaten statt Code verursacht weniger Aufwand und reduziert Fehler.

---

## <a id="support">5. Support-Status</a>

`dlt-meta` ist ein Open-Source-Explorationsprojekt von Databricks Labs. Die Doku stellt ausdrücklich klar: Databricks unterstützt es nicht offiziell und bietet keine Service-Level-Agreements (*"Databricks does not support it or provide service-level agreements (SLAs)"*). Implementierungsdetails, Tutorials und Einstiegsanleitungen finden sich in der offiziellen GitHub-Dokumentation des Projekts.

---

## <a id="quellen">6. Quellen</a>

- Create pipelines with dlt-meta (Überblick, Anwendungsfälle, Funktionsweise, Support-Status): https://docs.databricks.com/aws/en/ldp/developer/dlt-meta

**Stand:** 2026-08-19.
