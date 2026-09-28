# Event Hooks — Custom Monitoring von Pipelines

**Wichtig:** Event Hooks befinden sich in der Public Preview.

Event Hooks erlauben, benutzerdefinierte Python-Callback-Funktionen zu definieren, die ausgeführt werden, wenn Ereignisse im Event Log einer Pipeline persistiert werden — etwa für eigene Monitoring- und Alerting-Lösungen. Jede Aussage und jedes Code-Beispiel wurde per `WebFetch` gegen `docs.databricks.com/aws/en/ldp/event-hooks` verifiziert.

## Abschnittsübersicht

1. [Grundprinzip](#grundprinzip)
2. [Event-Hook-Verarbeitung überwachen](#ueberwachen)
3. [Einen Event Hook definieren](#definieren)
4. [Beispiel: Bestimmte Ereignisse gezielt verarbeiten](#beispiel-selektiv)
5. [Beispiel: Alle Ereignisse an einen Slack-Channel senden](#beispiel-slack)
6. [Beispiel: Event Hook nach vier aufeinanderfolgenden Fehlschlägen deaktivieren](#beispiel-deaktivieren)
7. [Beispiel: Pipeline mit einem Event Hook](#beispiel-vollstaendig)
8. [Quellen](#quellen)

---

## <a id="grundprinzip">1. Grundprinzip</a>

Ein Event Hook wird über eine Python-Funktion definiert, die genau ein Argument entgegennimmt — dieses Argument ist ein Dictionary, das ein Ereignis repräsentiert. Die Event Hooks werden anschließend als Teil des Pipeline-Quellcodes eingebunden. Alle in einer Pipeline definierten Event Hooks versuchen, sämtliche während jedes Pipeline-Updates erzeugten Ereignisse zu verarbeiten. Besteht die Pipeline aus mehreren Quellcode-Dateien, gelten definierte Event Hooks für die gesamte Pipeline. Obwohl Event Hooks Teil des Pipeline-Quellcodes sind, erscheinen sie **nicht** im Pipeline-Graph.

Event Hooks lassen sich sowohl mit Pipelines nutzen, die in den Hive Metastore veröffentlichen, als auch mit solchen, die nach Unity Catalog veröffentlichen.

**Weitere Hinweise:**

- Python ist die einzige unterstützte Sprache zur Definition von Event Hooks. Um benutzerdefinierte Python-Funktionen zur Ereignisverarbeitung in einer über das SQL-Interface implementierten Pipeline zu nutzen, müssen die Funktionen in einer separaten Python-Quelldatei ergänzt werden, die als Teil der Pipeline läuft — sie gelten dann für die gesamte Pipeline.
- Event Hooks werden nur für Ereignisse ausgelöst, deren `maturity_level` gleich `STABLE` ist (siehe `Event-Log-Schema.md`).
- Event Hooks laufen asynchron zu Pipeline-Updates, aber synchron zueinander — es läuft also stets nur ein einzelner Event Hook gleichzeitig, andere warten, bis der aktuell laufende Hook abgeschlossen ist. Läuft ein Event Hook unbegrenzt weiter, blockiert er alle anderen Event Hooks.
- Lakeflow-Pipelines versuchen, jeden Event Hook auf jedes während eines Pipeline-Updates emittierte Ereignis anzuwenden. Um nachhinkenden Event Hooks Zeit zu geben, alle wartenden Ereignisse zu verarbeiten, wartet die Pipeline vor dem Beenden ihrer Compute eine nicht konfigurierbare feste Zeitspanne. Es ist jedoch **nicht garantiert**, dass alle Hooks für alle Ereignisse ausgelöst werden, bevor die Compute beendet wird.

---

## <a id="ueberwachen">2. Event-Hook-Verarbeitung überwachen</a>

Der Event-Typ `hook_progress` im Pipeline-Event-Log dient dazu, den Status der Event Hooks eines Updates zu überwachen. Um zirkuläre Abhängigkeiten zu vermeiden, werden Event Hooks für `hook_progress`-Ereignisse selbst nicht ausgelöst.

---

## <a id="definieren">3. Einen Event Hook definieren</a>

Zur Definition dient der Decorator `on_event_hook`:

```python
@dp.on_event_hook(max_allowable_consecutive_failures=None)
def user_event_hook(event):
  # Python code defining the event hook
```

`max_allowable_consecutive_failures` beschreibt die maximale Anzahl aufeinanderfolgender Fehlschläge, bevor der Event Hook deaktiviert wird. Ein Fehlschlag liegt vor, wenn der Event Hook eine Exception wirft. Ist ein Event Hook deaktiviert, verarbeitet er keine neuen Ereignisse mehr, bis die Pipeline neu gestartet wird.

`max_allowable_consecutive_failures` muss eine Ganzzahl größer oder gleich `0` sein, oder `None`. Der Standardwert `None` bedeutet, dass die Anzahl aufeinanderfolgender Fehlschläge nicht begrenzt ist und der Event Hook niemals deaktiviert wird.

Fehlschläge und Deaktivierungen von Event Hooks lassen sich im Event Log als `hook_progress`-Ereignisse überwachen.

Die Event-Hook-Funktion muss eine Python-Funktion sein, die genau einen Parameter akzeptiert — ein Dictionary, das das auslösende Ereignis repräsentiert. Ein Rückgabewert der Funktion wird ignoriert.

---

## <a id="beispiel-selektiv">4. Beispiel: Bestimmte Ereignisse gezielt verarbeiten</a>

Dieses Beispiel wartet auf `STOPPING`-Ereignisse der Pipeline und gibt dann eine Nachricht in den Driver-Logs (`stdout`) aus:

```python
@dp.on_event_hook
def my_event_hook(event):
  if (
    event['event_type'] == 'update_progress' and
    event['details']['update_progress']['state'] == 'STOPPING'
  ):
    print('Received notification that update is stopping: ', event)
```

---

## <a id="beispiel-slack">5. Beispiel: Alle Ereignisse an einen Slack-Channel senden</a>

Dieses Beispiel implementiert einen Event Hook, der alle empfangenen Ereignisse über die Slack-API an einen Slack-Channel sendet. Es nutzt ein Databricks Secret, um ein Token zur Authentifizierung bei der Slack-API sicher zu speichern.

```python
from pyspark import pipelines as dp
import requests

# Get a Slack API token from a Databricks secret scope.
API_TOKEN = dbutils.secrets.get(scope="<secret-scope>", key="<token-key>")

@dp.on_event_hook
def write_events_to_slack(event):
  res = requests.post(
    url='https://slack.com/api/chat.postMessage',
    headers={
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + API_TOKEN,
    },
    json={
      'channel': '<channel-id>',
      'text': 'Received event:\n' + event,
    }
  )
```

---

## <a id="beispiel-deaktivieren">6. Beispiel: Event Hook nach vier aufeinanderfolgenden Fehlschlägen deaktivieren</a>

```python
from pyspark import pipelines as dp
import random

def run_failing_operation():
   raise Exception('Operation has failed')

# Allow up to 3 consecutive failures. After a 4th consecutive
# failure, this hook is disabled.
@dp.on_event_hook(max_allowable_consecutive_failures=3)
def non_reliable_event_hook(event):
  run_failing_operation()
```

---

## <a id="beispiel-vollstaendig">7. Beispiel: Pipeline mit einem Event Hook</a>

Ein einfaches, aber vollständiges Beispiel für die Nutzung von Event Hooks innerhalb einer Pipeline:

```python
from pyspark import pipelines as dp
import requests
import json
import time

API_TOKEN = dbutils.secrets.get(scope="<secret-scope>", key="<token-key>")
SLACK_POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'
DEV_CHANNEL = 'CHANNEL'
SLACK_HTTPS_HEADER_COMMON = {
 'Content-Type': 'application/json',
 'Authorization': 'Bearer ' + API_TOKEN
}

# Create a single dataset.
@dp.table
def test_dataset():
 return spark.range(5)

# Definition of event hook to send events to a Slack channel.
@dp.on_event_hook
def write_events_to_slack(event):
  res = requests.post(url=SLACK_POST_MESSAGE_URL, headers=SLACK_HTTPS_HEADER_COMMON, json = {
    'channel': DEV_CHANNEL,
    'text': 'Event hook triggered by event: ' + event['event_type'] + ' event.'
  })
```

---

## <a id="quellen">8. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/event-hooks

**Stand:** 2026-08-19
