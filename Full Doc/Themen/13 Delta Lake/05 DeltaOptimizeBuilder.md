# `DeltaOptimizeBuilder` — Python-Referenz (Delta Lake)

## Abschnittsübersicht
1. [Zweck](#zweck)
2. [`where()`](#where)
3. [`executeCompaction()`](#executecompaction)
4. [`executeZOrderBy()`](#executezorderby)
5. [Quellen](#quellen)

## <a id="zweck">1. Zweck</a>

`DeltaOptimizeBuilder` ist das Builder-Objekt für den `OPTIMIZE`-Befehl auf einer Delta-Tabelle: Kompaktierung kleiner Dateien und/oder Z-Order-Clustering. Man erhält eine Instanz über `DeltaTable.optimize()` und hängt optional `where()` sowie genau eine der Ausführungsmethoden (`executeCompaction()` oder `executeZOrderBy()`) an.

## <a id="where">2. `where()`</a>

- Schränkt den Optimize-Vorgang über einen Partitionsfilter auf ausgewählte Partitionen ein.
- Parameter:
  - `partitionFilter` (str) — Partitionsfilter-Ausdruck, z. B. `"date='2021-11-18'"`.
- Rückgabe: `DeltaOptimizeBuilder` (Chaining).

```python
deltaTable.optimize().where("date='2021-11-18'").executeCompaction()
```

## <a id="executecompaction">3. `executeCompaction()`</a>

- Kompaktiert kleine Dateien in den ausgewählten Partitionen (Bin-Packing) zu größeren Dateien.
- Parameter: keine.
- Rückgabe: `DataFrame` mit den Ausführungs-Metriken des OPTIMIZE-Vorgangs.

```python
deltaTable.optimize().where("date='2021-11-18'").executeCompaction()
```

## <a id="executezorderby">4. `executeZOrderBy()`</a>

- Ordnet die Daten in den ausgewählten Partitionen per Z-Order nach den angegebenen Spalten neu an, um die Datei-Skip-Effizienz bei Filtern auf diese Spalten zu verbessern.
- Parameter:
  - `*cols` (str) — Spaltennamen als Einzelargumente, **oder** eine Liste/Tuple von Spaltennamen (`List[str]` bzw. `Tuple[str, ...]`).
- Rückgabe: `DataFrame` mit den Ausführungs-Metriken des OPTIMIZE-Vorgangs.

```python
deltaTable.optimize().where("date='2021-11-18'").executeZOrderBy("eventType")

# mit mehreren Spalten:
deltaTable.optimize().executeZOrderBy("eventType", "userId")
```

## <a id="quellen">5. Quellen</a>
- `DeltaOptimizeBuilder` — vollständige Klassenreferenz (Signaturen, Parameter, Beispiele): https://docs.delta.io/api/latest/python/spark/

**Stand:** 2026-09-21.
