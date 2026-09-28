# Externe Python-Abhängigkeiten verwalten

## Abschnittsübersicht

1. [Empfohlene Ansätze](#ansaetze)
2. [Python-Bibliotheken über Environment-Einstellungen hinzufügen](#hinzufuegen)
3. [Wichtige Einschränkungen](#einschraenkungen)
4. [Quellen](#quellen)

---

## <a id="ansaetze">1. Empfohlene Ansätze</a>

Databricks nennt zwei primäre Muster für den Umgang mit externen Abhängigkeiten:

1. **Environment-Einstellungen**: *"Use the **Environment** settings to add packages to the pipeline environment for all source files in a pipeline."* — Pakete werden über die Environment-Einstellungen für alle Quelldateien einer Pipeline hinzugefügt.
2. **Import von Workspace-Dateien**: Module aus in Workspace-Dateien abgelegtem Quellcode importieren.

---

## <a id="hinzufuegen">2. Python-Bibliotheken über Environment-Einstellungen hinzufügen</a>

Konfiguration externer Python-Bibliotheken über die UI:

1. Pipeline-Editor öffnen, **Settings** auswählen.
2. Unter **Pipeline environment** auf das Bearbeiten-Symbol klicken.
3. **Add dependency** auswählen und den Paketnamen eingeben.
4. Version fixieren (Beispielformat: `simplejson==3.19.*`).

Die Doku ergänzt: *"You can also install a Python wheel package from a Unity Catalog volume, by specifying its path, such as `/Volumes/my_catalog/my_schema/my_ldp_volume/ldpfns-1.0-py3-none-any.whl`."* — ein Python-Wheel-Paket lässt sich also auch direkt aus einem Unity-Catalog-Volume über dessen Pfad installieren.

---

## <a id="einschraenkungen">3. Wichtige Einschränkungen</a>

**JVM-Bibliotheken-Restriktion:** *"Pipelines support only SQL and Python. You cannot use JVM libraries in a pipeline."* Die Doku betont, dass dies zu "unvorhersehbarem Verhalten" (*"unpredictable behavior"*) führt.

**Python-Prozess-Neustart:** Pipelines unterstützen `dbutils.library.restartPython()` nicht. Abhängigkeiten müssen über die Environment-Einstellungen deklariert werden, statt sie zur Laufzeit zu installieren.

**Init-Skripte:** Während Classic Compute clusterweite Init-Skripte unterstützt, tun dies serverlose Pipelines nicht. Databricks empfiehlt, Environment-Einstellungen gegenüber Init-Skripten zu priorisieren, um Probleme bei Runtime-Upgrades zu reduzieren.

---

## <a id="quellen">4. Quellen</a>

- Manage Python dependencies for Lakeflow pipelines (Environment-Einstellungen, Wheel-Installation aus Unity-Catalog-Volume, JVM-/Init-Skript-Einschränkungen): https://docs.databricks.com/aws/en/ldp/developer/external-dependencies

**Stand:** 2026-08-19.
