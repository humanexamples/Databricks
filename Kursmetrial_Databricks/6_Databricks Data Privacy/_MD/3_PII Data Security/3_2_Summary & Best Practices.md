## 3_2_Zusammenfassung & Best Practices

Hier ist eine Zusammenfassung der verschiedenen Schutztechniken, die wir besprochen haben, zum ausführlichen Nachlesen.

Gängige Datenschutztechniken: Hier ist eine Zusammenfassung der verschiedenen Schutztechniken, die wir besprochen haben, zum ausführlichen Nachlesen.

| Technik                  | Beschreibung                                                 | Beispiel          | Beispiel-Use-Case                                            | Vorteile                                                     | Nachteile                                                    | Schutz           |
| ------------------------ | ----------------------------------------------------------- | ----------------- | ---------------------------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------- | ---------------- |
| **Data Masking**         | Verbirgt Originaldaten durch modifizierten Inhalt. Dynamisches Masking in Databricks erlaubt das Definieren von Masking-Regeln. | gXXX.dXXXX@gmx.de | Sensible Daten schützen und dabei die operative Nutzbarkeit erhalten. | - Erhält das Datenformat; - Ein Teil der Information kann erhalten bleiben, während die Privatsphäre erhöht wird. | - Die Verteilung der Daten wird verändert.; - Daten sind evtl. über Informationen aus verwandten Spalten wiederherstellbar.; - Kann nicht zum Verknüpfen von Daten verwendet werden. | Gering bis mittel |
| **Pseudo-Anonymisierung** | Ersetzt Werte durch Pseudonyme oder andere künstliche Werte. | charles@gmx.de    | Medizinische Studien, in denen der Patient über die Zeit verfolgt werden muss, die Identität aber geschützt sein muss. | - Statistische Verteilung bleibt erhalten.; - Verknüpfung mehrerer Datensätze möglich. | - Aus der Verteilung der pseudo-anonymisierten Werte lassen sich evtl. tatsächliche Werte ableiten; - Daten sind evtl. über Informationen aus verwandten Spalten wiederherstellbar.; - Die Zuordnung zu den Originalwerten muss sicher gespeichert werden. | Gering bis mittel |
| **Hashing**              | Wandelt Daten in eine irreversible Zeichenkette um.          | cf35ddff242..     | Speicherung von Passwörtern                                  | - Sicher und irreversibel; - Datenverknüpfung möglich; - Erhält die Datenverteilung | - Aus der Verteilung der Hash-Werte lassen sich evtl. tatsächliche Werte ableiten; - Datenrückgewinnung nicht möglich | Mittel bis hoch  |
| **Column Encryption**    | Verschlüsselt Daten auf Spaltenebene. In Databricks werden sensible Daten vor der Speicherung verschlüsselt. | skjrk42ndd..      | Absicherung bestimmter sensibler Datenspalten.               | - Hohe Sicherheit; - Berücksichtigt einzelne Werte und Verteilungen | - Erfordert Key Management.; - Erhöht die Datengröße erheblich.; - Datenverknüpfung ist schwierig.; - Verteilung wird verändert. | Hoch             |
| **Tokenisierung**        | Ersetzt sensible Daten durch Tokens.                         | fik52tklhn2..     | Kreditkartentransaktionen                                    | - Token kann echte Daten für Operationen ersetzen.          | - Erfordert ein robustes Tokenisierungssystem.; - Alle Daten sind wiederherstellbar, wenn das Token-System kompromittiert wird. | Hoch             |

------

**Best Practices für den Umgang mit PII-Daten**

1. Kein PII zu haben ist immer besser, als PII zu haben
2. Anonymisierung ist immer > als Pseudo-Anonymisierung ist immer > als
  Klartext
3. Versuche stets, eine gesunde Paranoia gegenüber den angewendeten Schutzmaßnahmen zu bewahren
4. Wende stets die 3-Fakten-Regel an
5. Berücksichtige stets, wie Datensätze kombiniert werden könnten, um eine Re-Identifikation zu ermöglichen
6. Stelle stets sicher, dass deine Datenteams angemessen zu den geltenden Datenschutzgesetzen geschult sind
7. Nicht jedes PII ist gleich sensibel
8. Führe PIA-Reviews (Privacy Impact Assessments) durch
9. Isoliere stets Umgebungen, die PII verarbeiten
10. Dein Leben ist am einfachsten, wenn du die Umgebung isolierst, die PII schützt

- https://arxiv.org/abs/cs/0610105
- https://edps.europa.eu/system/files/2021-04/21-04-27_aepd-edps-anonymisation-en-5.pdf
- https://www.cs.utexas.edu/~shmat/shmat_oak08netflix.pdf
- https://courses.csail.mit.edu/6.857/2018/project/Archie-Gershon-Katchoff-Zeng-Netflix.pdf
