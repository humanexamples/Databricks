# Air-Gapped-Umgebungen

Bundles ohne Internetzugriff über den Databricks-CLI-Docker-Container nutzen. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Schritt 1: Docker-Container-Image herunterladen](#download)
3. [Schritt 2: Bundle-Befehle über Docker ausführen](#ausfuehren)
4. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick</a>

„Bundles hängen von externen Bibliotheken und Tools ab, um korrekt zu funktionieren." Ist kein Internetzugriff verfügbar, muss Docker genutzt werden, um Bundles in isolierten Netzwerkumgebungen zu verwalten.

## <a id="download">2. Schritt 1: Docker-Container-Image herunterladen</a>

Das Databricks-CLI-Docker-Image ist über das Databricks-CLI-GitHub-Repository verfügbar und unterstützt sowohl ARM64- als auch AMD64-Architekturen.

**Neueste Version:**

```bash
docker pull ghcr.io/databricks/cli:latest
```

**Bestimmte Version (Beispiel):**

```bash
docker pull ghcr.io/databricks/cli:v0.218.0
```

## <a id="ausfuehren">3. Schritt 2: Bundle-Befehle über Docker ausführen</a>

Zwei Ansätze nach dem Herunterladen des Containers:

### Direkte Ausführung

Befehle sofort ausführen, ohne in die Container-Shell zu wechseln:

```bash
docker run -v /my-bundle:/my-bundle -e DATABRICKS_HOST=... \
-e DATABRICKS_TOKEN=... --workdir /my-bundle \
ghcr.io/databricks/cli:latest bundle deploy
```

Wichtige Flags: `-v` zum Mounten des Bundle-Verzeichnisses, `-e` für Umgebungsvariablen (Authentifizierungs-Credentials), `--workdir` zum Setzen des Arbeitsverzeichnisses.

### Interaktive Ausführung

Eine interaktive Terminal-Sitzung innerhalb des Containers starten:

```bash
docker run -v /my-bundle:/my-bundle -e DATABRICKS_HOST=... \
-e DATABRICKS_TOKEN=... -it --entrypoint /bin/sh \
--workdir /my-bundle ghcr.io/databricks/cli:latest
```

Nach dem Start der Sitzung Befehle direkt ausführen:

```bash
/my-bundle # databricks bundle deploy
```

Dieser Ansatz erlaubt „bidirektionale" Synchronisation — lokale Bearbeitungen spiegeln sich sofort im Container wider, ohne den Docker-Befehl erneut ausführen zu müssen.

## <a id="quelle">4. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/bundles/airgapped-environment

**Stand:** 2026-08-21.
