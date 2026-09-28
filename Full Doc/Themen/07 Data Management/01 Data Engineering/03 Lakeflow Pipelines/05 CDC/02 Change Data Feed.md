# Change Data Feed (CDF) im Kontext von CDC

Change Data Feed (CDF) verfolgt **Row-Level-Änderungen zwischen Versionen** einer Delta-Lake- oder Apache-Iceberg-v3-Tabelle — inklusive Metadaten, ob eine Zeile eingefügt, aktualisiert oder gelöscht wurde. CDF ist ein Delta-Lake-Feature auf einer **einzelnen Tabelle**; es unterscheidet sich damit klar von `AUTO CDC INTO` (siehe Abgrenzung unten und [01 CDC-Grundlagen.md](01%20CDC-Grundlagen.md)).

**Vollständige CDF-Referenz** (Automatic vs. Legacy CDF, Aktivierung/Deaktivierung, Ausgabeschema, Batch-/Streaming-Lesen, `table_changes()`-Funktionsreferenz, Retention, Migration, Einschränkungen) steht bereits in [01 Platform/02 Tables/07 Table Features/02 Change Data Feed.md](../../../../01%20Platform/02%20Tables/07%20Table%20Features/02%20Change%20Data%20Feed.md) — dieser Artikel dupliziert sie nicht, sondern behandelt nur die Einordnung von CDF **im CDC-/Pipeline-Kontext**.

## Konsum-Muster: Stream vs. Batch

Aus einer privaten Kursnotiz übernommen, nicht dokuverifiziert — beide Muster sind gängige Ansätze, um CDF-Ausgaben nachgelagert zu verarbeiten:

- **Stream-Modus:** Ein Structured-Streaming-Job verarbeitet den CDF fortlaufend als Micro-Batches ab dem letzten Checkpoint — ohne auf ein festes Zeitintervall zu warten. Treffen mehrere Änderungen (z. B. ein Insert und ein späteres Update desselben Datensatzes) innerhalb desselben Micro-Batches ein, muss die Verarbeitungslogik selbst den jeweils aktuellsten Stand auswählen.
- **Batch-Modus:** Der CDF wird alle X Minuten gemeinsam verarbeitet. Dafür muss die Logik selbst einen High-Watermark (letzte verarbeitete Version/Zeitstempel) führen und ab diesem Punkt weiterlesen.

## Anwendungsfälle im Pipeline-Kontext

- Inkrementelle Silver-/Gold-Updates, die nur geänderte Zeilen verarbeiten, statt teuer neu zu berechnen.
- Materialized Views ohne kostspielige Re-Aggregation über die gesamte Tabelle.
- Propagierung von Löschungen durch das gesamte Lakehouse (siehe Abgrenzung unten).

(Allgemeine Anwendungsfälle, Einschränkungen und die vollständige Funktionsreferenz: siehe verlinkte Vollreferenz oben.)

## Abgrenzung: CDF vs. `AUTO CDC INTO`

Aus einer privaten Kursnotiz übernommen, nicht dokuverifiziert — eine hilfreiche gedankliche Einordnung, keine offizielle Doku-Aussage: CDC (`AUTO CDC INTO`) und CDF lösen unterschiedliche Probleme und schließen sich nicht aus.

- **`AUTO CDC INTO`** wirkt **von außen nach innen** (Ingestion): Es nimmt Change-Records, die bereits als Insert/Update/Delete-Ereignisse von einer externen Quelle ankommen (z. B. ein CDC-Tool auf einer vorgelagerten Datenbank), und wendet sie auf **eine** Ziel-Delta-Tabelle an. Es wirkt nur auf diese eine Tabelle und weiß nichts davon, ob derselbe Datensatz bereits in weitere Tabellen kopiert wurde.
- **CDF** wirkt **von innen nach außen** (Propagation): Es beantwortet die Frage „Was hat sich in dieser Tabelle seit Version X geändert (inkl. Deletes)?" — unabhängig davon, wodurch die Änderung entstand (manuelles `DELETE`, `MERGE`, oder ein `AUTO CDC INTO`-Flow). Das macht CDF zum passenden Werkzeug, um eine Löschung durch das gesamte Lakehouse zu „durchreichen" (z. B. für DSGVO-/CCPA-„Recht auf Vergessenwerden"-Anfragen, die von einer Bronze-Tabelle bis in alle abgeleiteten Gold-Tabellen propagiert werden müssen — siehe [10 Governance und Zugriff/02 GDPR.md](../10%20Governance%20und%20Zugriff/02%20GDPR.md)).

Kurz: `AUTO CDC INTO` bringt eine Änderung an der Ingestion-Grenze **herein**, CDF trägt sie durch den Rest des Lakehouse **weiter**.

## Quellen

- https://docs.databricks.com/aws/en/delta/delta-change-data-feed
- Vollständige CDF-Referenz: [01 Platform/02 Tables/07 Table Features/02 Change Data Feed.md](../../../../01%20Platform/02%20Tables/07%20Table%20Features/02%20Change%20Data%20Feed.md)
