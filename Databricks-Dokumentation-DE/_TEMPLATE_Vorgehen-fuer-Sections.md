# Template: Erstellung einer Section-Dokumentation

## 📋 Anforderungsvorlage (zum Kopieren, wenn du mir eine Section geben willst)

Ausfüllen und mir schicken (die Platzhalter in `[...]` ersetzen, Zeile 3 nur falls du eigenes Material lieferst — sonst weglassen):

```
Wende das Vorgehen aus "Databricks-Dokumentation-DE\_TEMPLATE_Vorgehen-fuer-Sections.md"
auf "Section [NUMMER] - [NAME]" an:

1. Vorhandene PDFs in diesem Ordner sichten.
2. Offizielle Exam-Guide-Ziele für "Section [NUMMER]: [NAME]" gegen die vorhandenen PDFs
   abgleichen (Exam Guide bei Bedarf neu von docs.databricks.com abrufen). Für jede echte
   Lücke ein neues PDF im etablierten Stil erstellen (deutsch, eigenständig formuliert,
   Code unverändert, docbox mit Quelle).
3. [Nur falls zutreffend:] Zusätzliches Kursmaterial liegt unter "[PFAD]" — zuerst
   Duplikat-Check gegen ALLE Sections, nur neue Unterthemen integrieren, Bilder aus
   Foliensatz-PDFs extrahieren, Kreuzverweise statt Wiederholungen.
4. Rückwärts-Ergänzung prüfen: stecken in ausgelassenen/nicht duplizierten Themen
   Einzelinfos, die bestehende PDFs dieser Section ergänzen?
5. Gezielte Vertiefungsrunde: pro bestehendem Thema 1-3 gezielte Websuchen gegen
   docs.databricks.com, Lücken einpflegen.
6. Qualitätssicherung (Klammer-Bug-Check, Stichproben per Read-Tool) + Abschlussbericht:
   was ergänzt, was bewusst ausgelassen und warum.

Bestehende Pipeline (_build/template.py, render_pdf()) weiterverwenden, keine neue
Vorlage bauen.
```

Die Punkte 1–6 sind unten in den Phasen A–F ausführlich erklärt (inkl. der Fallstricke in Abschnitt 3) — falls ich (oder ein späteres Modell) Details nachschlagen muss.

---

Dieses Dokument fasst das vollständige Vorgehen zusammen, mit dem `Section 1 - Databricks Intelligence Plattform` erstellt wurde. Es dient als wiederverwendbare Anleitung für die übrigen Section-Ordner (2–7).

## 0. Zielbild

Jede Section ist ein Ordner mit mehreren deutschsprachigen PDFs (ein PDF pro Unterthema/Kapitel), die zusammen ein Prüfungs-/Nachschlagewerk zum jeweiligen Exam-Guide-Abschnitt der "Databricks Certified Data Engineer Associate"-Zertifizierung bilden. Qualitätsmaßstab: klare, einfache deutsche Sprache; echte Codebeispiele; Bilder wo sinnvoll; keine thematischen Wiederholungen zwischen den Sections.

## 1. Technische Basis (einmalig vorhanden, wiederverwenden)

- **`_build/template.py`**: enthält die Funktion `render_pdf(out_pdf, title, subtitle, body_html, build_name)`. Baut aus `body_html` (reines HTML) plus einer festen CSS-Vorlage (Titelseite, Überschriften, Codeblöcke, Bild-Figuren, Info-Boxen) eine vollständige HTML-Datei und rendert sie per `msedge --headless --print-to-pdf` zu PDF. **Keine Neuentwicklung nötig** — für jede neue Section einfach importieren:
  ```python
  import sys, os, html
  sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
  from template import render_pdf

  def code(lang, text):
      return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'
  ```
- **CSS-Klassen im body_html**: `<h2>`/`<h3>` für Kapitel, `<pre class="code sql|python|yaml">` für Code, `<figure class="img"><img src="..."><figcaption>...</figcaption></figure>` für Bilder, `<table>` für Vergleiche, `<div class="docbox">...</div>` für den abschließenden "Ergänzt aus der offiziellen Databricks-Dokumentation"-Kasten mit Quellenlink.
- **Bilder-Ablage**: `_build/assets/<kürzel>/` (z. B. `assets/s1/...`), im HTML relativ referenziert (`assets/s1/bild.png`).
- **Build-Skript-Namenskonvention**: `_build/build_gap_s<N>_<thema>.py` für neu/nachträglich erstellte Themen (verhindert Kollisionen mit alten Nummern-Schemata aus früheren Ordnerstrukturen). Jedes Skript erzeugt genau ein PDF (Ausnahme: mehrere PDFs pro Skript sind möglich, siehe `build_07_all.py`, aber dann besonders auf Namenskollisionen und den Klammer-Bug achten, siehe Abschnitt 6).

## 2. Arbeitsphasen

### Phase A — Ausgangsmaterial sichten und Rohinhalt erstellen
1. Verfügbares Kursmaterial (Databricks-Academy-Notebooks, Udemy-Exporte, etc.) für das Thema der Section identifizieren.
2. Pro Unterthema den relevanten Quellinhalt lesen (Code-Zellen, Markdown-Text, Foliensätze).
3. **Eigenständigen deutschen Fließtext schreiben** (keine wörtliche Übersetzung) mit klarer, einfacher Sprache.
4. **Codebeispiele unverändert** aus der Quelle übernehmen (SQL/Python/YAML), mit `html.escape()` einbetten.
5. Falls keine Notebook-Quelle existiert (z. B. reine API-/Sprachreferenz-Themen): eigenes Fachwissen nutzen, aber per WebSearch gegen die aktuelle Databricks-Dokumentation verifizieren.

### Phase B — Abgleich mit dem offiziellen Exam Guide (Pflichtschritt pro Section)
1. Offiziellen Exam Guide (`databricks-certified-data-engineer-associate-exam-guide-*.pdf`, verlinkt auf `docs.databricks.com`) für den jeweiligen Abschnitt heranziehen — wortwörtliche Prüfungsziele extrahieren.
2. Jedes Prüfungsziel gegen die vorhandenen PDFs der Section abgleichen: abgedeckt / teilweise abgedeckt / fehlt.
3. Für jede echte Lücke: gezielte Websuche zur offiziellen Doku, neues PDF (oder neuer Abschnitt in bestehendem PDF) schreiben.
4. Für Ziele, die inhaltlich besser in eine **andere** Section passen (z. B. Monitoring-Aspekte, die schon in einer anderen Section stecken): **nicht duplizieren**, sondern im Text kurz kreuzverweisen ("siehe Section X, Kapitel Y").

### Phase C — Zusätzliches Nutzer-Material integrieren (falls vorhanden)
1. Vom Nutzer bereitgestellte Zusatzquellen (z. B. Udemy-Foliensätze + Video-Transkripte als Text/PDF-Paare) lokal auffinden (Downloads-Ordner o. ä. prüfen, nicht nur auf das im Chat eingefügte Preview verlassen).
2. **Duplikat-Check zuerst**: jedes Unterthema gegen bereits vorhandene PDFs (auch in anderen Sections!) prüfen. Inhaltlich deckungsgleiche Themen **bewusst auslassen** und das im Bericht an den Nutzer explizit benennen (nicht duplizieren, nur weil die Quelle es hergibt).
3. Für die verbleibenden, neuen Unterthemen: PDFs im etablierten Stil schreiben, mit Kreuzverweisen zu Themen, die andernorts bereits vertieft behandelt werden.
4. **Bilder aus Foliensätzen extrahieren** (falls als PDF vorhanden) statt neu zu zeichnen:
   ```python
   import fitz  # PyMuPDF
   doc = fitz.open(quelle_pdf)
   pix = doc[seite_index].get_pixmap(dpi=150)
   pix.save(zieldatei_png)
   ```
   Urheberzeile/Copyright-Vermerk im Bild **nicht wegschneiden** — dient der korrekten Quellenangabe bei Wiederverwendung urheberrechtlich geschützten Kursmaterials.

### Phase D — Rückwärts-Ergänzung prüfen (nach jeder größeren Content-Ergänzung)
Nach Phase B und C aktiv nachfragen bzw. selbst prüfen: *Gibt es unter den bewusst ausgelassenen/nicht duplizierten Themen Einzelinformationen, die bestehende PDFs der Section sinnvoll ergänzen (nicht duplizieren)?* Typische Fundstellen:
- Eine Tabelle/Vergleich in einem bestehenden PDF, der um eine zusätzliche Zeile/Spalte ergänzt werden kann (z. B. "Managed vs. External" um "Predictive-Optimization-Fähigkeit" ergänzt).
- Eine Erstellungssyntax, die analog zu einer bereits gezeigten existiert (z. B. `CLUSTER BY` neben `PARTITIONED BY`).
Solche Ergänzungen als gezielte `Edit`-Operationen in die bestehenden `build_gap_*.py`-Skripte einpflegen, danach neu rendern — **kein neues PDF** dafür anlegen.

### Phase E — Gezielte Vertiefungsrunde gegen die offizielle Doku
Kein pauschales "ganze Website studieren" (nicht möglich/sinnvoll — docs.databricks.com hat tausende Seiten, kein Crawling-Tool, kein Sinn für Vollarchivierung im Memory). Stattdessen **pro bestehendem Thema der Section** 1–3 gezielte WebSearches, um typische Lücken zu finden, etwa:
- Verwandte, aber nicht erwähnte SQL-Klauseln/Optionen (z. B. `INFORMATION_SCHEMA`, `PRIMARY KEY`/`FOREIGN KEY` als informationelle Constraints, `CREATE TABLE LIKE`).
- Aktuelle Best-Practice-Hinweise oder Deprecation-Hinweise der offiziellen Doku.
Gefundene, echte Lücken wieder als gezielte Edits in bestehende Skripte einpflegen (nicht als neue PDFs, außer der Umfang rechtfertigt ein eigenes Kapitel).

### Phase F — Qualitätssicherung
1. Nach jedem Render-Lauf: `grep -n "{{" build_*.py` — jedes Vorkommen prüfen (siehe Fallstrick in Abschnitt 6).
2. Mindestens 1–2 PDFs pro Batch mit dem `Read`-Tool visuell stichprobenprüfen: Umlaute korrekt, Codeblöcke lesbar, Bilder eingebettet, keine abgeschnittenen/leeren Seiten, Kreuzverweise zeigen auf die richtige Section/Kapitelnummer.
3. Dateigröße grob plausibilisieren (>20 KB pro PDF als Mindestindikator, dass Inhalt vorhanden ist).
4. Abschlussbericht an den Nutzer: was wurde ergänzt, was bewusst ausgelassen (mit Begründung), welche Lücken bestehen ggf. noch bewusst nicht geschlossen.

## 3. Bekannte Fallstricke

- **Doppelte geschweifte Klammern in f-strings**: `body = f"""...{code('python', '''{{...}}''')}..."""` — Klammern **innerhalb** des dreifach gequoteten String-Arguments von `code()` dürfen **nicht** verdoppelt werden (sie werden nicht vom äußeren f-string interpretiert und erscheinen sonst literal doppelt im PDF). Verdoppelung ist nur nötig für Text, der **direkt** im f-string-Body steht (z. B. `<code>{{{{job.run_id}}}}</code>` für literales `{{job.run_id}}` in einem Fließtext-Beispiel). Im Zweifel: kurzer Python-Test mit `print(f"{code(...)}")` vor dem Rendern.
- **Umlaute in Ordnernamen + Bash**: `find`/`grep` in Git-Bash können bei Ordnernamen mit Umlauten (z. B. "Überblick") unzuverlässig sein. Für Ordner-Operationen (anlegen, auflisten, verschieben, löschen) **PowerShell** verwenden, nicht Bash.
- **Doppelpunkt in Dateinamen**: Windows erlaubt keinen `:` in Dateinamen — bei Titeln mit Doppelpunkt (z. B. "DataFrame-Joins: Inner, ...") im Dateinamen durch " - " ersetzen, im PDF-Titel selbst darf der Doppelpunkt bleiben.
- **Build-Skript-Namenskollisionen**: vor dem Anlegen eines neuen `build_*.py` immer prüfen, ob der Dateiname schon von einer früheren Ordnerstruktur belegt ist (`ls _build | grep build_XX`). Neue/nachträgliche Skripte konsequent mit `build_gap_...` präfixen.
- **Agenten, die selbst delegieren statt zu arbeiten**: bei Einsatz von Hintergrund-Agenten explizit anweisen "erledige das SELBST, starte KEINE weiteren Subagenten" — sonst Gefahr von Doppelarbeit oder Stillstand ohne sichtbaren Fortschritt.
- **Session-/Rate-Limits bei Hintergrund-Agenten**: bei Ausfall eines Agenten den tatsächlichen Dateistand prüfen (nicht dem letzten Statusbericht vertrauen), fehlende Teile ggf. selbst direkt fertigstellen.

## 4. Anwendung auf Section 2–7

Für jede weitere Section (z. B. `Section 2 - Data Ingestion and Loading`) in dieser Reihenfolge vorgehen:
1. Phase A: vorhandene PDFs + Quellmaterial sichten.
2. Phase B: exam-guide-Ziele der jeweiligen Section (bereits im Exam Guide extrahiert, siehe frühere Gap-Analyse) nochmals gegenprüfen — ggf. hat sich der Exam Guide seither aktualisiert, kurz per WebFetch neu abrufen.
3. Falls Nutzer weiteres Kursmaterial (Udemy o. ä.) für diese Section liefert: Phase C.
4. Phase D: Rückwärts-Ergänzung prüfen.
5. Phase E: gezielte Vertiefungsrunde.
6. Phase F: Qualitätssicherung + Bericht.
