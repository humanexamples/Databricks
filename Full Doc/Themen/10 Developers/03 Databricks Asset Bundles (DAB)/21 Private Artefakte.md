# Private Artefakte

Wie sich Artefakte aus privaten Quellen (z. B. JFrog Artifactory oder andere private Repositories) in ein Bundle einbinden lassen, wenn ein direkter Download durch Databricks selbst nicht möglich ist. Ergänzt [22 Bibliotheksabhaengigkeiten.md](22%20Bibliotheksabhaengigkeiten.md) um den privaten Sonderfall. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Ausgangslage](#ausgangslage)
2. [Workflow](#workflow)
3. [Wahl des Referenzierungswegs](#wahl)
4. [Alternative: notebook-scoped Installation](#alternative)
5. [Quelle](#quelle)

---

## <a id="ausgangslage">1. Ausgangslage</a>

Stammt eine Abhängigkeit aus einer privaten Quelle (privates PyPI-Repository, JFrog Artifactory o. Ä.), kann Databricks sie nicht automatisch zur Deploy-Zeit herunterladen — das Artefakt muss vorher lokal beschafft werden.

**Zentraler Mechanismus:** Setzt man `artifact_path` in der Bundle-Konfiguration auf einen Unity-Catalog-Volumes-Pfad, „lädt das Bundle automatisch alle im Bundle referenzierten Artefakte nach Unity Catalog hoch".

## <a id="workflow">2. Workflow</a>

**Schritt 1 — lokal herunterladen:**

```bash
pip download -d dist my-wheel==1.0
```

Für authentifizierte Quellen:

```bash
export PYPI_TOKEN=<YOUR TOKEN>
pip download -d dist my-package==1.0.0 --index-url https://$PYPI_TOKEN@<package-index-url> --no-deps
```

**Schritt 2 — optional nach Unity Catalog hochladen:**

```bash
databricks fs cp my-wheel-1.0-*.whl dbfs:/Volumes/myorg_test/myorg_volumes/packages
```

**Schritt 3 — in der Bundle-Konfiguration referenzieren:**

*Lokale Referenz:*

```yaml
libraries:
  - whl: ../dist/my-wheel-1.0-*.whl
```

*Unity-Catalog-Referenz:*

```yaml
libraries:
  - whl: /Volumes/myorg_test/myorg_volumes/packages/my-wheel-1.0-py3-none-any.whl
```

## <a id="wahl">3. Wahl des Referenzierungswegs</a>

- **Lokale Referenz** nutzen, wenn Artefakte direkt in den Workspace-Storage deployt werden.
- **Unity-Catalog-Pfad** nutzen für zentrale Verwaltung und Teilen über mehrere Workspaces hinweg.

## <a id="alternative">4. Alternative: notebook-scoped Installation</a>

„Bei Nutzung von Notebooks lässt sich ein Python-Wheel aus einem privaten Repository innerhalb eines Notebooks installieren, das dann als `notebook_task` in den Job des Bundles eingebunden wird" — umgeht die Bundle-Artefakt-Mechanik vollständig, auf Kosten expliziter Versionskontrolle im Bundle selbst.

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/bundles/artifact-private

**Stand:** 2026-08-26.
