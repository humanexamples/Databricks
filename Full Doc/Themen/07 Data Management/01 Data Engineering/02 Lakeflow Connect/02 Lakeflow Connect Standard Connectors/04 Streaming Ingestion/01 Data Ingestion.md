# Streaming Ingestion

- Bei Streaming Ingestion werden Daten kontinuierlich geladen, sobald sie erzeugt werden, sodass sie nahezu in Echtzeit abgefragt werden können. Diese Methode eignet sich ideal zum Laden von Streaming-Daten aus Quellen wie Apache Kafka, Amazon Kinesis, Google Pub/Sub und Apache Pulsar.
- Streaming Ingestion verarbeitet Daten, sobald sie eintreffen, und ermöglicht so latenzarme Analysen und sofortige Reaktionen. Micro-Batch-Ingestion sammelt dagegen Daten über kurze, häufige Intervalle (Sekunden oder Minuten) und verarbeitet sie in kleinen Batches — ein Kompromiss zwischen Latenz und Systemeffizienz.
- **Daten kontinuierlich laden**, Zeilen oder Batches von Datenzeilen, sobald sie erzeugt werden, sodass sie nahezu in Echtzeit abgefragt werden können
- Micro-Batch verarbeitet kleine Batches in sehr **kurzen, häufigen Intervallen**
- Gängige Techniken:
  - `spark.readStream` (Auto Loader mit kontinuierlichem Trigger)
  - Declarative Pipelines (Trigger-Modus continuous)




<table style="width: 100%; border-collapse: collapse; line-height: 1.5;">
  <thead>
    <tr style="background: #1B5162; color: white;">
      <th style="padding: 10px 14px; text-align: left; border: 1px solid #EEEDE9; width: 140px;">MERKMAL</th>
      <th style="padding: 10px 14px; text-align: left; border: 1px solid #EEEDE9;">CREATE TABLE AS (CTAS) + spark.read</th>
      <th style="padding: 10px 14px; text-align: left; border: 1px solid #EEEDE9;">COPY INTO</th>
      <th style="padding: 10px 14px; text-align: left; border: 1px solid #EEEDE9;">Auto Loader</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background: #F9F7F4;">
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Ingestion-Typ</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Batch</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Incremental Batch</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Inkrementell (Batch oder Streaming)</td>
    </tr>
    <tr>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Anwendungsfälle</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Am besten für kleinere Datensätze</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Ideal für Tausende von Dateien</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Skaliert auf Millionen+ Dateien pro Stunde, Backfills mit Milliarden von Dateien</td>
    </tr>
    <tr style="background: #F9F7F4;">
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Syntax/Schnittstelle</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">
        <ul style="margin: 0; padding-left: 16px;">
          <li>Python (spark.read)</li>
          <li>SQL (CTAS)</li>
        </ul>
      </td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">SQL</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">
        <ul style="margin: 0; padding-left: 16px;">
          <li>Python (spark.readStream)</li>
          <li>SQL mit Declarative Pipelines (CREATE OR REFRESH STREAMING TABLES)</li>
          <li>Streaming Tables in Databricks SQL</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Idempotenz</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Nein</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Ja</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Ja</td>
    </tr>
    <tr style="background: #F9F7F4;">
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Schema-Evolution</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Manuell oder beim Lesen abgeleitet</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Mit Optionen unterstützt</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Auto Loader erkennt und entwickelt Schemas automatisch weiter. Behandelt neue Spalten, sobald sie auftauchen.</td>
    </tr>
    <tr>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Latenz</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Hoch</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Moderat (geplant)</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Niedrig oder hoch, abhängig von der Konfiguration</td>
    </tr>
    <tr style="background: #F9F7F4;">
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Benutzerfreundlichkeit</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Einfach</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Einfach und SQL-basiert</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Mittel bis fortgeschritten, abhängig von der Implementierung</td>
    </tr>
    <tr>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Zusammenfassung</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Am besten für einmalige, ad hoc Ingestion. Kann so geplant werden, dass stets alle Daten gelesen und verarbeitet werden.</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Einfach und wiederholbar für inkrementelle Datei-Ingestion. Gut geeignet für geplante Jobs oder Pipelines.</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Am besten für nahezu Echtzeit-Streaming oder inkrementelle Ingestion, mit hoher Automatisierung und Skalierbarkeit.</td>
    </tr>
  </tbody>
</table>
