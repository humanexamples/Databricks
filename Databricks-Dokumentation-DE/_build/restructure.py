# -*- coding: utf-8 -*-
"""Patches all build_XX_YY.py scripts to output into the new 7-Section structure
instead of the old 9-folder structure, then the caller re-runs them."""
import re, os

BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE"

# old folder name -> (new section folder name, section subtitle label)
FOLDER_MAP = {
    "00 Überblick": ("Section 1 - Databricks Intelligence Plattform", "Section 1 &middot; Databricks Intelligence Plattform"),
    "01 Datenaufnahme mit Lakeflow Connect": ("Section 2 - Data Ingestion and Loading", "Section 2 &middot; Data Ingestion and Loading"),
    "02 Orchestrierung mit Lakeflow Jobs": ("Section 4 - Working with Lakeflow Jobs", "Section 4 &middot; Working with Lakeflow Jobs"),
    "03 Deklarative Pipelines - Grundlagen": ("Section 3 - Data Transformation and Modelling", "Section 3 &middot; Data Transformation and Modelling"),
    "04 Deklarative Pipelines - Fortgeschritten": ("Section 3 - Data Transformation and Modelling", "Section 3 &middot; Data Transformation and Modelling"),
    "05 Data Governance und Datenschutz": ("Section 7 - Governance and Security", "Section 7 &middot; Governance and Security"),
    "06 Performance-Optimierung": ("Section 6 - Troubleshooting, Monitoring and Optimization", "Section 6 &middot; Troubleshooting, Monitoring and Optimization"),
    "07 DevOps und CI-CD": ("Section 5 - Implementing CI-CD", "Section 5 &middot; Implementing CI-CD"),
    "08 Automatisiertes Deployment mit Asset Bundles": ("Section 5 - Implementing CI-CD", "Section 5 &middot; Implementing CI-CD"),
}

# explicit filename renumbering where old prefixes must be stripped/merged
FILENAME_MAP = {
    "00 Databricks Data-Engineering-Plattform und Lakeflow im Ueberblick.pdf": "01 Databricks Data-Engineering-Plattform und Lakeflow im Ueberblick.pdf",
    "02-1 Grundlagen - Jobs, Tasks und Komponenten.pdf": "01 Grundlagen - Jobs, Tasks und Komponenten.pdf",
    "02-2 Jobs erstellen, planen und automatisieren.pdf": "02 Jobs erstellen, planen und automatisieren.pdf",
    "02-3 Bedingte und iterative Tasks.pdf": "03 Bedingte und iterative Tasks.pdf",
    "02-4 Monitoring, Fehlerbehandlung und Repair.pdf": "04 Monitoring, Fehlerbehandlung und Repair.pdf",
    "02-5 Lakeflow Jobs in Produktion - Best Practices und modulare Orchestrierung.pdf": "05 Lakeflow Jobs in Produktion - Best Practices und modulare Orchestrierung.pdf",
    "03-1 Konzepte - Flows, Streaming Tables und Materialized Views.pdf": "01 Konzepte - Flows, Streaming Tables und Materialized Views.pdf",
    "03-2 Pipelines entwickeln - Pipeline-Editor und Einstellungen.pdf": "02 Pipelines entwickeln - Pipeline-Editor und Einstellungen.pdf",
    "03-3 Datenqualitaet mit Expectations.pdf": "03 Datenqualitaet mit Expectations.pdf",
    "03-4 Streaming Joins und Produktivbetrieb.pdf": "04 Streaming Joins und Produktivbetrieb.pdf",
    "03-5 Change Data Capture Grundlagen - AUTO CDC und SCD Type 1.pdf": "05 Change Data Capture Grundlagen - AUTO CDC und SCD Type 1.pdf",
    "04-1 Multi-Flow-Pipelines und Liquid Clustering.pdf": "06 Multi-Flow-Pipelines und Liquid Clustering.pdf",
    "04-2 Multiplex Streaming, Delta Sinks und Iceberg-UniForm.pdf": "07 Multiplex Streaming, Delta Sinks und Iceberg-UniForm.pdf",
    "04-3 CDC vertieft - SCD Type 1 vs Type 2 mit AUTO CDC INTO.pdf": "08 CDC vertieft - SCD Type 1 vs Type 2 mit AUTO CDC INTO.pdf",
    "04-4 Erweiterte Datenqualitaetspruefungen und Quarantaene-Muster.pdf": "09 Erweiterte Datenqualitaetspruefungen und Quarantaene-Muster.pdf",
    "04-5 Praxisbeispiel - Multi-Source E-Commerce-Pipeline.pdf": "10 Praxisbeispiel - Multi-Source E-Commerce-Pipeline.pdf",
    "05-1 Unity-Catalog-Sicherheitsmodell (ACLs, Lineage, Discoverability).pdf": "01 Unity-Catalog-Sicherheitsmodell (ACLs, Lineage, Discoverability).pdf",
    "05-2 Row Filters, Column Masks & Dynamic Views.pdf": "02 Row Filters, Column Masks & Dynamic Views.pdf",
    "05-3 PII-Schutz - Pseudonymisierung & Anonymisierung.pdf": "03 PII-Schutz - Pseudonymisierung & Anonymisierung.pdf",
    "05-4 Change Data Feed - Aenderungen nachverfolgen & propagieren.pdf": "04 Change Data Feed - Aenderungen nachverfolgen & propagieren.pdf",
    "05-5 Compliance - DSGVO,CCPA & Datenloeschung.pdf": "05 Compliance - DSGVO,CCPA & Datenloeschung.pdf",
    "06-1 Spark-Architektur und Adaptive Query Execution.pdf": "01 Spark-Architektur und Adaptive Query Execution.pdf",
    "06-2 Datenlayout - Data Skipping, Z-Ordering, Partitionierung.pdf": "02 Datenlayout - Data Skipping, Z-Ordering, Partitionierung.pdf",
    "06-3 Liquid Clustering und Predictive Optimization.pdf": "03 Liquid Clustering und Predictive Optimization.pdf",
    "06-4 Skew, Shuffle und Spill erkennen und beheben.pdf": "04 Skew, Shuffle und Spill erkennen und beheben.pdf",
    "06-5 Serialisierung und UDF-Performance.pdf": "05 Serialisierung und UDF-Performance.pdf",
    "06-6 Cluster-Auswahl - Photon, Spot-Instanzen und Serverless Compute.pdf": "06 Cluster-Auswahl - Photon, Spot-Instanzen und Serverless Compute.pdf",
    "01 Grundlagen - databricks.yml und CLI-Lifecycle.pdf": "06 Grundlagen - databricks.yml und CLI-Lifecycle.pdf",
    "02 Multi-Environment-Deployments - Targets und Variablen.pdf": "07 Multi-Environment-Deployments - Targets und Variablen.pdf",
    "03 CI-CD mit Asset Bundles - Tests und Pipelines kombiniert.pdf": "08 CI-CD mit Asset Bundles - Tests und Pipelines kombiniert.pdf",
    "04 Asset Bundles in VS Code.pdf": "09 Asset Bundles in VS Code.pdf",
    # 07 DevOps files keep their 01-05 numbers unchanged in Section 5
}

SUBTITLE_RE = re.compile(r'Themenordner \d+ &middot; [^&]+&middot;')

def patch_file(path):
    src = open(path, encoding="utf-8").read()
    changed = False

    def repl_out_pdf(m):
        nonlocal changed
        full_old_path = m.group(1)
        old_folder = None
        old_filename = None
        for folder in FOLDER_MAP:
            prefix = BASE + "\\" + folder + "\\"
            if full_old_path.startswith(prefix):
                old_folder = folder
                old_filename = full_old_path[len(prefix):]
                break
        if old_folder is None:
            print("  WARN: could not map path:", full_old_path)
            return m.group(0)
        new_folder, _ = FOLDER_MAP[old_folder]
        new_filename = FILENAME_MAP.get(old_filename, old_filename)
        new_path = BASE + "\\" + new_folder + "\\" + new_filename
        changed = True
        return 'out_pdf=r"' + new_path + '"'

    src = re.sub(r'out_pdf=r"([^"]+)"', repl_out_pdf, src)

    def repl_subtitle(m):
        nonlocal changed
        full_match_start = m.start()
        # find which folder this subtitle belongs to by looking at the nearest out_pdf before it (already patched to NEW folder,
        # so instead we derive the section label from render_pdf call by matching against original subtitle text)
        return m.group(0)  # placeholder, real replacement done below per-known mapping

    # Subtitle patch: map by matching the old topic name still embedded before &middot; Quelle
    for folder, (new_folder, label) in FOLDER_MAP.items():
        old_topic = folder.split(" ", 1)[1] if folder[:2].isdigit() else folder
        # old topic name as used in original subtitle strings (folder name minus leading number)
        pattern = re.compile(r'Themenordner \d+ &middot; ' + re.escape(old_topic) + r' &middot;')
        if pattern.search(src):
            src = pattern.sub(label + " &middot;", src)
            changed = True

    if changed:
        open(path, "w", encoding="utf-8").write(src)
    return changed

if __name__ == "__main__":
    for fn in sorted(os.listdir(BUILD_DIR)):
        if fn.startswith("build_") and fn.endswith(".py"):
            path = os.path.join(BUILD_DIR, fn)
            did = patch_file(path)
            print(fn, "-> patched" if did else "-> unchanged")
