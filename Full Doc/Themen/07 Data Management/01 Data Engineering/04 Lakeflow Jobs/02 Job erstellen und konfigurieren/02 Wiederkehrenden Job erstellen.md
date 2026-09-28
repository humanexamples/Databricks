# Tutorial: Wiederkehrenden Job mit Backfill-Unterstützung erstellen

Voraussetzung: Zugriff auf System-Tabellen.

## Schritt 1: Query erstellen

Neues SQL-Notebook anlegen (z. B. „Query billing with parameters tutorial"). `<catalog>`/`<schema>` ersetzen:

```sql
USE CATALOG <catalog>;
USE SCHEMA <schema>;

CREATE TABLE IF NOT EXISTS tutorial_databricks_product_spend (
  billing_origin_product STRING,
  usage_date DATE,
  total_dollar_cost DECIMAL(12, 2)
);

-- Process the last N days specified by :lookback_days ending on :data_interval_end
INSERT INTO TABLE tutorial_databricks_product_spend
  REPLACE WHERE
    usage_date >= date_add(:data_interval_end, - CAST(:lookback_days AS INT))
    AND usage_date < :data_interval_end
  SELECT
    usage.billing_origin_product,
    usage.usage_date,
    SUM(usage.usage_quantity * list_prices.pricing.effective_list.default) AS total_dollar_cost
  FROM
    system.billing.usage AS usage
      JOIN system.billing.list_prices AS list_prices
        ON usage.sku_name = list_prices.sku_name
        AND usage.usage_end_time >= list_prices.price_start_time
        AND (
          list_prices.price_end_time IS NULL
          OR usage.usage_end_time < list_prices.price_end_time
        )
  WHERE
    usage.usage_date >=
      date_add(:data_interval_end, -CAST(:lookback_days AS INT))
    AND usage.usage_date <
      :data_interval_end
  GROUP BY
    usage.billing_origin_product,
    usage.usage_date
```

Parameter (**Edit** → **Add parameter**):

| Name | Standardwert |
|---|---|
| `lookback_days` | `1` |
| `data_interval_end` | *(keiner — immer erforderlich)* |

Testen: `data_interval_end` im Format `yyyy-mm-dd` angeben (z. B. `2025-10-02`), Compute verbinden, **Run all**.

## Schritt 2: Job zum Zeitplanen der Query erstellen

1. **Jobs & Pipelines** → **Create** → **Job** → Kachel **Notebook**.
2. Job umbenennen, Task-Namen vergeben (z. B. `tutorial-databricks-spend`).
3. Typ **Notebook**, Quelle **Workspace**, Pfad = obiges Notebook.
4. Parameter `lookback_days` = `1` hinzufügen.
5. Parameter `data_interval_end` hinzufügen — über **{ }** den Wert `{{job.trigger.time.iso_date}}` aus der Liste parametrisierter Werte wählen.
6. Task speichern.
7. Rechtes Panel → **Schedules & Triggers** → **Add trigger** → Typ **Scheduled**, Standardwerte (aktiv, täglich) belassen → **Save**.

**Hinweis:** Über **Pause** lässt sich der Zeitplan konfiguriert lassen, ohne tägliche Kosten zu verursachen.

## Schritt 3: Backfill für ältere Daten ausführen

1. Pfeil neben **Run now** → **Run backfill**.
2. **Start**: 7 Tage zuvor, 00:00 Uhr; **End**: heute, 00:00 Uhr (Beispiel: `09/14/2025, 12:00 AM` bis `09/21/2025, 12:00 AM`).
3. Zeitintervall: **Every** `1` `Day`.
4. Job-Parameter prüfen: `data_interval_end` = `{{backfill.iso_datetime}}`, `lookback_days` = `1`.
5. **Run** klicken.

## Quelle

- https://docs.databricks.com/aws/en/jobs/how-to/create-recurring-job
