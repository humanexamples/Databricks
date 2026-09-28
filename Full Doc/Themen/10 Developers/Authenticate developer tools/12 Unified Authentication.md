# Databricks Unified Authentication

Ein einheitlicher Weg, Authentifizierung über alle Databricks-Werkzeuge und -SDKs hinweg zu konfigurieren und zu automatisieren. Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Unterstützte Werkzeuge und SDKs](#tools)
3. [Auswertungsreihenfolge der Authentifizierung](#reihenfolge)
4. [Empfohlener Ansatz](#empfehlung)
5. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick</a>

„Databricks Unified Authentication bietet einen konsistenten Weg, Authentifizierung als Teil der OAuth-Autorisierung zu konfigurieren und zu automatisieren." Entwickler definieren ihre Credentials **einmal** und verwenden sie über mehrere Werkzeuge hinweg — keine separate Credential-Verwaltung pro Werkzeug.

## <a id="tools">2. Unterstützte Werkzeuge und SDKs</a>

- Databricks CLI
- Databricks Terraform Provider
- Databricks Connect
- Databricks-Erweiterung für Visual Studio Code
- Databricks SDK for Python
- Databricks SDK for Java
- Databricks SDK for Go

Alle unterstützen die Konfiguration über **Umgebungsvariablen** und **Konfigurationsprofile**. Terraform sowie die SDKs für Python, Java und Go erlauben zusätzlich die **direkte Konfiguration im Code**.

## <a id="reihenfolge">3. Auswertungsreihenfolge der Authentifizierung</a>

### 3a. Reihenfolge der Authentifizierungstypen

Werkzeuge und SDKs versuchen die Methoden nacheinander, bis eine erfolgreich ist:

1. **Personal Access Tokens (Legacy)**
2. **OAuth Machine-to-Machine (M2M)**
3. **OAuth User-to-Machine (U2M)**

### 3b. Reihenfolge der Credential-Suche

Für jede Methode wird in dieser Reihenfolge nach Credentials gesucht:

1. **SDK-`Config`-Felder** (Konfiguration direkt im Code — nur SDKs)
2. **Umgebungsvariablen** (plattformspezifische Variablen)
3. **Konfigurationsprofil** (`DEFAULT`-Profil der `.databrickscfg`-Datei)

> Diese einheitliche Reihenfolge gilt laut Doku **uniform** für alle oben genannten Werkzeuge und SDKs — es gibt keine abweichenden Sequenzen pro Werkzeug.

## <a id="empfehlung">4. Empfohlener Ansatz</a>

Best Practice:

1. Ein **eigenes Konfigurationsprofil** in `.databrickscfg` anlegen.
2. Die benötigten Authentifizierungsfelder eintragen (siehe [13 Umgebungsvariablen und Felder.md](13%20Umgebungsvariablen%20und%20Felder.md)).
3. Die Umgebungsvariable **`DATABRICKS_CONFIG_PROFILE`** auf den Profilnamen setzen.

Das maximiert die Portabilität über verschiedene Umgebungen hinweg.

## <a id="quelle">5. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/auth/unified-auth
- https://docs.databricks.com/aws/en/dev-tools/sdk-python (SDK-Config-Felder/Umgebungsvariablen/Profil-Reihenfolge für das Python-SDK im Detail; vollständige Referenz siehe [Databricks SDK für Python.md](../07%20Databricks%20SDK%20fuer%20Python.md))

**Stand:** 2026-09-01.
