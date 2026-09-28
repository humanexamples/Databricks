# Jobs automatisieren: Zeitpläne und Trigger

Lakeflow Jobs lassen sich in folgenden Situationen automatisch auslösen: zeitgesteuert, bei Updates von Quelltabellen, bei Ankunft neuer Dateien in einem Unity-Catalog-Speicherort, bei Erstellung/Update eines Unity-Catalog-Modells, oder kontinuierlich. Zusätzlich lassen sich Läufe manuell oder über externe Orchestrierungstools auslösen.

## Die sechs Trigger-Typen

| Trigger-Typ | Verhalten |
|---|---|
| **Scheduled** | Löst einen Job-Lauf zeitbasiert aus (siehe `Zeitgesteuert.md`) |
| **Table update** | Löst einen Lauf aus, wenn Quelltabellen aktualisiert werden (siehe `Tabellen-Update-Trigger.md`) |
| **File arrival** | Löst einen Lauf aus, wenn neue Dateien in einem überwachten Unity-Catalog-Speicherort eintreffen (siehe `Datei-Ankunfts-Trigger.md`) |
| **Model update** | Löst einen Lauf aus, wenn ein Unity-Catalog-Modell erstellt wird, eine Modellversion bereit ist, oder ein Modell-Alias gesetzt wird (Beta, siehe `Modell-Update-Trigger.md`) |
| **Continuous** | Hält den Job dauerhaft am Laufen — ein neuer Lauf startet, sobald der vorherige abschließt oder fehlschlägt (siehe `Continuous Jobs.md`) |
| **None (manuell)** | Läufe werden manuell über **Run now** oder programmatisch über andere Orchestrierungstools ausgelöst |

Standardmäßig kann nur ein Lauf eines Jobs gleichzeitig aktiv sein — dieses Limit lässt sich in den Advanced Settings erhöhen.

## Trigger konfigurieren

1. Job öffnen.
2. Im **Job details**-Panel zu **Schedules & Triggers** scrollen → **Add trigger**.
3. Trigger-Typ wählen und Optionen konfigurieren.
4. **Save** klicken.

## Bestehenden Trigger verwalten

- **Bearbeiten:** **Edit trigger**.
- **Pausieren:** **Pause**.
- **Entfernen:** **Delete**.

Beim Erstellen/Bearbeiten lässt sich der Trigger-Status zusätzlich direkt zwischen **Active** und **Paused** umschalten.

## Quelle

- https://docs.databricks.com/aws/en/jobs/triggers
