# Deaktivierte Tasks in Lakeflow Jobs

Ein deaktivierter Task wird zur Laufzeit übersprungen, ohne aus dem Job entfernt zu werden — Konfiguration und Lauf-Historie bleiben erhalten, sodass er später ohne Neuaufbau reaktiviert werden kann.

## Verhalten nachgelagerter Tasks

Bei jedem Lauf wertet Lakeflow Jobs die **Run-if**-Bedingung jedes nachgelagerten Tasks gegen seine vorgelagerten Tasks aus, um zu entscheiden, ob er läuft, übersprungen oder deaktiviert wird. Deaktivierte Tasks schließen mit dem Terminierungscode `Disabled` ab. Kann die Run-if-Bedingung eines nachgelagerten Tasks wegen deaktivierter Elternteile nicht erfüllt werden, markiert Lakeflow Jobs auch ihn für diesen Lauf als deaktiviert — sichtbar über ein Icon oben rechts im DAG.

| Run-if-Bedingung | Verhalten bei deaktiviertem Elternteil | Beispiel |
|---|---|---|
| **All succeeded** (Standard) | Läuft nicht — ein deaktivierter Elternteil erfüllt „succeeded" nicht | `A (disabled) → B`: B läuft nicht |
| **At least one succeeded** | Läuft, wenn mindestens ein anderer Elternteil erfolgreich war | `A (disabled)` + `C (succeeded) → B`: B läuft |
| **None failed** | Läuft, wenn mindestens ein Elternteil ohne Fehlschlag abgeschlossen wurde | `A (disabled)` + `C (skipped) → B`: B läuft |
| **All done** | Läuft normal — ein deaktivierter Elternteil gilt als abgeschlossen | `A (disabled) → B`: B läuft |
| **At least one failed** | Läuft, wenn mindestens ein anderer Elternteil fehlschlug — ein deaktivierter Elternteil zählt nicht als Fehlschlag | `A (disabled)` + `C (failed) → B`: B läuft |
| **All failed** | Läuft nicht — ein deaktivierter Elternteil gilt nicht als Fehlschlag | `A (disabled) → B`: B läuft nicht |

**Hinweis:** Nur explizit deaktivierte Tasks tragen `disabled: true` in der Job-Definition. Die Deaktivierung nachgelagerter Tasks wird zur Lauf-Erstellungszeit ermittelt, nicht in den Job-Einstellungen gespeichert.

## Task deaktivieren

Über die UI: siehe `Task konfigurieren.md`, Abschnitt „Task deaktivieren".

Über API/Bundle: `disabled: true` auf dem Task setzen (Jobs REST API, CLI, SDK oder Declarative Automation Bundles):

```json
{
  "tasks": [
    {
      "task_key": "load_raw_data",
      "disabled": true,
      "notebook_task": {
        "notebook_path": "/Shared/etl/load_raw_data"
      }
    }
  ]
}
```

`jobs/get` und `jobs/list` liefern `disabled: true` nur für explizit deaktivierte Tasks — zur Laufzeit dynamisch deaktivierte Tasks erscheinen nicht in den gespeicherten Job-Einstellungen.

## Bei Repairs und Partial Runs

- **Repairs:** Lakeflow Jobs nutzt den Lauf-Status jedes Tasks zur Bestimmung, was repariert wird — nicht den Deaktivierungsstatus. Um einen deaktivierten Task im Rahmen eines Repairs zu erzwingen, in `rerun_tasks` der Repair-Anfrage aufnehmen.
- **Partial Runs:** Deaktivierte Tasks sind standardmäßig nicht vorausgewählt, lassen sich aber für einen einmaligen Lauf gezielt auswählen, ohne sie in den Job-Einstellungen zu reaktivieren. Bei `+`-Modifikatoren im `only`-Feld werden deaktivierte Tasks **nicht** automatisch mit eingeschlossen — sie müssen explizit hinzugefügt werden.

## Einschränkungen

- Ein **If/else**-Task schlägt fehl, wenn der vorgelagerte Task, der seinen Bedingungswert liefert, deaktiviert ist.
- Ein **For-each**-Task schlägt fehl, wenn der vorgelagerte Task, der seine Eingabewerte liefert, deaktiviert ist.
- Nur nutzerseitig deaktivierte Tasks erscheinen als `disabled: true` — die DAG-Ansicht in der Jobs-UI zeigt, welche nachgelagerten Tasks vor einem Lauf betroffen wären.

## Quelle

- https://docs.databricks.com/aws/en/jobs/disabled-tasks
