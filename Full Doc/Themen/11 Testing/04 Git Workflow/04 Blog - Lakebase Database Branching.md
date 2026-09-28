# Blog: Lakebase Database Branching

Kuratierte Zusammenfassung von drei Databricks-Blogartikeln zu Copy-on-Write-Database-Branching mit Lakebase (Databricks' verwaltetem Postgres): eine Kunden-Fallstudie (Glaspoort), die technische Grundlage, und ein dreiteiliges Playbook für evolutionäre Datenbankentwicklung im Team-Maßstab. Teil der [Testing](../Uebersicht.md)-Reihe. Thematisch nur lose mit Databricks-Notebook-/Pipeline-Testing verwandt (Postgres-Branching statt Data-Lakehouse), aber explizit angefragt — daher hier dokumentiert. Blog-Inhalte, keine normative Referenzdokumentation.

## Abschnittsübersicht

1. [Glaspoort: Datenbank-Branching als CI/CD-Muster](#glaspoort)
2. [Datenbank-Branching in Postgres mit Lakebase](#technische-grundlage)
3. [Evolutionäre Datenbankentwicklung mit Database Branching (Teil 3)](#evolutionaer)
4. [Quelle](#quelle)

---

## <a id="glaspoort">1. Glaspoort: Datenbank-Branching als CI/CD-Muster</a>

Glaspoort, ein niederländisches Glasfaser-Infrastrukturunternehmen, implementierte eine Datenbank-Branching-Strategie mit Databricks Lakebase, die Anwendungscode-Workflows widerspiegelt — Datenbankänderungen laufen über Pull Requests, CI/CD-Gates und gesteuerte Promotion.

**Kernproblem:** **Environment Drift** (langlebige Dev-/Acceptance-Branches driften von Production ab) und die **„Reset Tax"** — Lakebase-Branches lassen sich nicht zurücksetzen, wenn sie Kind-Branches haben, was Löschen, Neu-Verdrahtung von Connection Strings und erneutes Anwenden von Grants erzwingt. Dadurch wird Refresh so teuer, dass Teams ihn vermeiden, was den Drift perpetuiert.

**Lösung — flache Topologie ab Production:** statt hierarchischem Stacking (Production → Dev → Acceptance) verzweigen Dev und Acceptance direkt und gleichrangig von Production — „jeder langlebige Umgebungs-Branch ist ein Kind von Production, nicht von einer anderen Umgebung." Eliminiert die Reset-Einschränkung vollständig.

**Per-PR-CI/CD-Flow:** jeder Pull Request erzeugt einen temporären `pr-xxxx`-Branch ab Production (TTL: 1 Stunde) → CI spielt alle Datenbank-Migrationen erneut ein (übersprungen, wenn ein Git-Diff-Check keine Migrationsänderungen zeigt) → das neue Anwendungs-Image wird gegen den frisch migrierten Branch getestet (Dual Validation) → bei Merge wiederholt sich der gesamte Prozess erneut ab dem aktuellen Production-Stand → manuelle Freigabe-Gates in Azure DevOps orchestrieren die Promotion Dev → Acceptance → Production, wobei jedes Gate Migrationen erneut gegen den Ziel-Branch abspielt.

**Migrationen als Source of Truth:** Branches werden nie zurückgemerged — die maßgebliche Aufzeichnung ist die geordnete Sequenz der Migrationen selbst, nicht irgendeine langlaufende Datenbankinstanz: „Fehlt einem aufgefrischten Branch eine Änderung, wendet der nächste Migrations-Replay sie erneut an."

**Zwei evaluierte Promotion-Modelle:** (1) Merge nach CI-Erfolg (gewählt — optimiert Entwicklergeschwindigkeit, Trade-off: Hotfixes können die Warteschlange nicht ohne Parallel-Pipeline umgehen) vs. (2) Merge erst nach CD durch alle Umgebungen (optimiert Unabhängigkeit/Hotfix-Pfade, Trade-off: Teammitglieder warten auf Acceptance-Freigabe).

**Ergebnisse:** Iterationszyklen zehnfach beschleunigt, kleine Teams liefern Features in Tagen statt Monaten; „Wer hat Acceptance kaputtgemacht?"-Diskussionen verschwanden vollständig.

## <a id="technische-grundlage">2. Datenbank-Branching in Postgres mit Lakebase</a>

**Kernkonzept:** statt vollständiger Duplizierung (`pg_dump`, Minuten bis Stunden je nach Datenbankgröße) nutzt Lakebase Copy-on-Write-Technologie, um isolierte Umgebungen in Sekunden zu erstellen.

**Architektonische Grundlage:** vollständige Trennung von Compute und Storage. „Alle Daten werden in eine verteilte, versionierte Storage-Engine geschrieben, die jede Änderung als neue Version aufzeichnet, statt bestehende Daten zu überschreiben." Da Storage versioniert ist, können mehrere Branches sicher auf identische zugrunde liegende Daten verweisen; unabhängiges Compute bedeutet, dass jeder Branch einen eigenen, autonom skalierenden Postgres-Prozess ausführt.

**Vorteile gegenüber traditionellem Kopieren:** Geschwindigkeit (Branch-Erstellung dauert Sekunden, unabhängig von der Datenbankgröße); Storage-Effizienz („Storage-Kosten proportional zu Änderungen, nicht zur Gesamtdatenmenge — ein Branch, der 50 MB in einer 500-GB-Datenbank ändert, nutzt etwa 50 MB zusätzlichen Storage"); Isolation und Aktualität (unabhängige Connection Strings/Compute-Endpoints); Kosten (Idle-Branches skalieren Compute automatisch auf null).

**Praktische Workflows:** Entwickler-Isolation (jeder Ingenieur erhält eine eigene, produktionsrealistische Umgebung); PR-basierte Branches (automatisch bei PR-Öffnung erstellt, bei Merge/Schließung gelöscht); CI/CD-Testisolation (jeder Testlauf erhält eine frische, isolierte Datenbank); Point-in-Time Recovery (Branch von jedem historischen Zeitpunkt innerhalb des Restore-Fensters — „der gesamte Prozess dauert Sekunden, nicht die Stunden oder Tage, die traditionelles PITR benötigt"); KI-Agent-Integration (Agenten provisionieren Datenbanken programmatisch über die Lakebase-API für die Dauer einer Aufgabe).

## <a id="evolutionaer">3. Evolutionäre Datenbankentwicklung mit Database Branching (Teil 3)</a>

Abschluss einer dreiteiligen Serie, die Copy-on-Write-Database-Branching in Lakebase anhand der Entwicklerfigur „Jen" aus dem Essay „Evolutionary Database Design" (2003) im Jahr 2026 durchspielt.

**Tier-Topologie:** ersetzt traditionelle Multi-Instanz-Umgebungen durch eine einheitliche Branch-Hierarchie. **Tiers** fungieren als Eltern-Branches in Promotion-Hierarchien (Production, Staging etc.), **Features** sind ephemere, von Tiers abstammende Branches, die Teams nach Gebrauch aufräumen. Kernprinzip: „die Parent-of-Kette ist die Promotion-Hierarchie." Sechs traditionelle Umgebungsinstanzen kollabieren zu „einem Lakebase-Elternteil mit einer parent-verknüpften Hierarchie langlaufender Branches."

**Practice #10 — Governance einmal entworfen, pro Branch geerbt:** Berechtigungsmodelle, Unity-Catalog-Policies (Masking, Row Filters) und Audit-Erfassung werden einmalig auf dem Trunk entworfen und automatisch von Kind-Branches geerbt. „Rollen deklarieren; die Policy erzwingt."

**DBA-Rollenentwicklung zum Platform Engineer:** das ursprüngliche Verhältnis von einem Vollzeit-DBA je ~100 Personen bleibt gültig, verwaltet nun aber Metadaten-Operationen statt Infrastruktur-Provisionierung. Agenten treiben die Skalierung zusätzlich: Neon berichtet von einer halben Million Branches täglich, 80 % davon von Agenten erstellt — manuelles Ticket-Gating wird damit unmöglich. Sechs-Entwickler-Teams generieren typischerweise 30+ operative Tickets je Sprint in traditionellen Modellen; Branch-native Modelle senken dies auf unter 5 hochwertige Policy-Reviews, DBA-Aufwand von 20+ auf unter 5 Wochenstunden, mittlere Recovery-Zeit von 4+ Stunden auf unter 30 Minuten.

**Practice #11 — Agenten als Team-Praktizierende:** Agenten greifen nur auf Branches zu, nie direkt auf Production, und folgen denselben Workflow-Regeln wie menschliche Entwickler. Vier Absicherungen machen agentengenerierten Code wartbar: Guardrails über das Berechtigungsmodell („Das Substrat verweigert"); benannte Refactorings aus dem 70+-Katalog von databaserefactoring.com; ein SCM-State-Machine-Workflow mit fünf blockierenden Zuständen (`scaffold-complete, feature-claimed, pr-ready, ci-green, merged`); menschliches PR-Review mit sichtbaren Schema-Diffs.

**SCM-Workflow-State-Machine:** implementiert im Lakebase App Dev Kit über dokumentierte CLI-Befehle (`lakebase-scm-claim-feature-branch`, `-prepare-pr`, `-wait-ci`, `-merge`), die Vorbedingungen validieren, Übergänge durchführen und den Zustand in `.lakebase/workflow-state.json` schreiben. „Ein Feature-Branch mit falschem Eltern-Tier wird abgelehnt; ein Merge-Versuch vor grüner CI wird verweigert."

**TDD als Opt-in-Schicht:** ergänzt die verpflichtende SCM-Baseline zwischen den Zuständen `feature-claimed` und `pr-ready` mit einem zweiten State Machine (Spec-Author, Architect-Reviewer, Test-Strategist, Scrum-Master, Driver/Navigator-Agenten im RED-GREEN-REFACTOR-Paarmodus) — adressiert das Risiko, dass Agenten Tests löschen, um CI-Checks zu bestehen.

**Fazit:** die Methodik der evolutionären Datenbankentwicklung aus 2003 bleibt 2026 gültig — der Unterschied ist die technische Fähigkeit. Copy-on-Write-Branching entfernt die Einschränkung, die „jeder bekommt eine eigene Datenbankinstanz" zwanzig Jahre lang aspirational hielt.

## <a id="quelle">4. Quelle</a>

- https://www.databricks.com/blog/branching-databases-code-cicd-pattern-lakebase-production-glaspoort
- https://www.databricks.com/blog/database-branching-postgres-git-style-workflows-databricks-lakebase
- https://www.databricks.com/blog/enabling-evolutionary-database-development-database-branching-lakebase-part-3

**Stand:** 2026-08-21.
