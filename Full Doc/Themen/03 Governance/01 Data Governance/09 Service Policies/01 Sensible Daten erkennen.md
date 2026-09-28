# Sensible Daten erkennen (`detect_sensitive_data`)

Eine eingebaute Service Policy zur Erkennung sensibler Daten (z. B. PII) in Anfragen und Antworten. Sie ist **deterministisch** und regelbasiert (nicht LLM-basiert) und fügt daher nur minimale Latenz hinzu.

## Aktionen bei Erkennung

| Aktion | Verhalten |
|---|---|
| **Block** | Verweigert die Interaktion; der Aufrufer erhält eine HTTP-200-Antwort mit den ausgelösten Kategorien. |
| **Redact** | Ersetzt erkannte Werte durch Platzhalter-Tokens (z. B. `[US_SSN]`), bevor der Inhalt weitergeleitet wird. |

Policies lassen sich auf Eingabe, Ausgabe oder beides anwenden.

## Unterstützte Kategorien (15 insgesamt)

| Region | Kategorien |
|---|---|
| **Global** (7) | E-Mail-Adresse, IP-Adresse, MAC-Adresse, VIN, Kreditkarte, IBAN, Telefonnummer |
| **USA** (4) | SSN, ITIN, Reisepass, Bankkontonummer |
| **UK** (2) | NHS-Nummer, National Insurance Number |
| **Indien** (2) | Permanent Account Number, Aadhaar-Nummer |

## Erkennungsmethoden

Kombination aus Regex-Musterabgleich, Prüfsummen (Luhn, ISO 7064, Mod-11, Verhoeff) und Kontext-Schlüsselwörtern zur Validierung der Treffer.

## Genauigkeit laut Benchmark

- Block-Präzision: **0,99** über alle 15 Kategorien.
- Redaction-Recall: **0,96**.
- Zusätzliche Latenz: **deutlich unter 50 ms** pro Request.

## Einschränkung

Die Policy erkennt keine Freitext-Entitäten wie Namen, Orte oder Organisationen — dafür wäre Sprachverständnis statt Musterabgleich nötig.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/service-policies/detect-sensitive-data
