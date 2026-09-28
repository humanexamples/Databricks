# `DeltaTable` — Python-Referenz (Delta Lake)

## Abschnittsübersicht
1. [Zweck](#zweck)
2. [Instanziierung: forPath(), forName(), create(), createIfNotExists(), replace(), createOrReplace(), isDeltaTable()](#instanziierung)
3. [Lesen/Referenzieren: toDF(), alias()](#lesen)
4. [DML: delete(), update(), merge()](#dml)
5. [Wartung: vacuum(), optimize(), history(), detail()](#wartung)
6. [Versionierung: restoreToVersion(), restoreToTimestamp(), clone(), cloneAtVersion(), cloneAtTimestamp()](#versionierung)
7. [Protokoll/Features: convertToDelta(), upgradeTableProtocol(), addFeatureSupport(), dropFeatureSupport()](#protokoll)
8. [generate()](#generate)
9. [Quellen](#quellen)

## <a id="zweck">1. Zweck</a>
`delta.tables.DeltaTable` ist die zentrale Python-Klasse der Delta-Lake-API. Sie ist das programmatische Gegenstück zu SQL-Befehlen wie `MERGE`, `UPDATE`, `DELETE`, `VACUUM`, `OPTIMIZE`, `RESTORE` oder `CREATE TABLE`: statt SQL-Strings zu schreiben, erzeugt man ein `DeltaTable`-Objekt (z. B. über `forPath()` oder `forName()`) und ruft darauf Methoden auf. Ein Teil der Methoden (`create()`, `createIfNotExists()`, `replace()`, `createOrReplace()`) liefert einen `DeltaTableBuilder` zurück, `merge()` liefert einen `DeltaMergeBuilder`, `optimize()` einen `DeltaOptimizeBuilder` — diese Builder-Klassen werden in eigenen Dateien dieses Ordners behandelt, hier geht es nur um `DeltaTable` selbst.

## <a id="instanziierung">2. Instanziierung</a>

### `DeltaTable.forPath(sparkSession, path, hadoopConf={})`
Erzeugt ein `DeltaTable`-Objekt für die Daten am angegebenen Pfad. Wirft einen Fehler ("not a Delta table"), falls unter dem Pfad keine oder keine Delta-Tabelle existiert.
- `sparkSession` — die aktive `SparkSession`.
- `path` (str) — Pfad zur Delta-Tabelle.
- `hadoopConf` (Dict[str, str], optional, Default `{}`) — Hadoop-Konfiguration, die nur für diesen Zugriff verwendet wird, z. B. Cloud-Storage-Zugangsdaten.
```python
hadoopConf = {"fs.s3a.access.key": "<access-key>",
              "fs.s3a.secret.key": "secret-key"}
deltaTable = DeltaTable.forPath(spark, "/path/to/table", hadoopConf)
```

### `DeltaTable.forName(sparkSession, tableOrViewName)`
Erzeugt ein `DeltaTable`-Objekt über den (Metastore-)Tabellen- oder View-Namen statt über einen Pfad. Wirft ebenfalls einen "not a Delta table"-Fehler, wenn die Tabelle nicht existiert oder keine Delta-Tabelle ist.
- `sparkSession` — die aktive `SparkSession`.
- `tableOrViewName` (str) — Name der Tabelle oder View.
```python
deltaTable = DeltaTable.forName(spark, "tblName")
```

### `DeltaTable.create(sparkSession=None)`
Liefert einen `DeltaTableBuilder`, mit dem Tabellenname, Pfad, Spalten, Partitionierung, Kommentar und Tabellen-Properties festgelegt werden können — entspricht SQL `CREATE TABLE` und wirft einen Fehler, falls die Tabelle bereits existiert.
- `sparkSession` (optional) — aktive `SparkSession`; ohne Angabe wird die aktuelle Session verwendet.
```python
DeltaTable.create(spark) \
    .tableName("default.people") \
    .addColumn("id", "BIGINT") \
    .addColumn("name", "STRING") \
    .execute()
```

### `DeltaTable.createIfNotExists(sparkSession=None)`
Wie `create()`, entspricht aber SQL `CREATE TABLE IF NOT EXISTS`: kein Fehler, falls die Tabelle bereits existiert.
- `sparkSession` (optional) — aktive `SparkSession`; ohne Angabe wird die aktuelle Session verwendet.
```python
DeltaTable.createIfNotExists(spark) \
    .tableName("default.people") \
    .addColumn("id", "BIGINT") \
    .addColumn("name", "STRING") \
    .execute()
```

### `DeltaTable.replace(sparkSession=None)`
Liefert einen `DeltaTableBuilder`, der die bestehende Tabelle ersetzt — entspricht SQL `REPLACE TABLE`. Die Tabelle muss bereits existieren, sonst schlägt der Befehl fehl.
- `sparkSession` (optional) — aktive `SparkSession`; ohne Angabe wird die aktuelle Session verwendet.
```python
DeltaTable.replace(spark) \
    .tableName("default.people") \
    .addColumn("id", "BIGINT") \
    .addColumn("email", "STRING") \
    .execute()
```

### `DeltaTable.createOrReplace(sparkSession=None)`
Liefert einen `DeltaTableBuilder`, der die Tabelle anlegt, falls sie nicht existiert, oder ersetzt, falls sie existiert — entspricht SQL `CREATE OR REPLACE TABLE`. Anders als `replace()` führt ein fehlendes Vorkommen der Tabelle hier nicht zu einem Fehler.
- `sparkSession` (optional) — aktive `SparkSession`; ohne Angabe wird die aktuelle Session verwendet.
```python
DeltaTable.createOrReplace(spark) \
    .tableName("default.people") \
    .addColumn("id", "BIGINT") \
    .addColumn("email", "STRING") \
    .execute()
```

### `DeltaTable.isDeltaTable(sparkSession, identifier)`
Prüft, ob der übergebene Identifier (in der Praxis meist ein Dateipfad) die Wurzel einer Delta-Tabelle ist.
- `sparkSession` — die aktive `SparkSession`.
- `identifier` (str) — zu prüfender Pfad/Identifier.
```python
DeltaTable.isDeltaTable(spark, "/path/to/table")
```

## <a id="lesen">3. Lesen/Referenzieren</a>

### `deltaTable.toDF()`
Gibt eine `DataFrame`-Repräsentation der Delta-Tabelle zurück, mit der man wie mit jedem anderen Spark-DataFrame weiterarbeiten kann (Filter, Joins, Aggregationen …).
```python
deltaTable = DeltaTable.forPath(spark, "/path/to/table")
df = deltaTable.toDF()
df.show()
```

### `deltaTable.alias(aliasName)`
Vergibt einen Alias für die Delta-Tabelle. Wird vor allem bei `merge()` gebraucht, um Quelle und Ziel in der Bedingung eindeutig zu referenzieren.
- `aliasName` (str) — der zu vergebende Alias.
```python
deltaTable.alias("events").merge(
    source=updatesDF.alias("updates"),
    condition="events.eventId = updates.eventId"
)
```

## <a id="dml">4. DML</a>

### `deltaTable.delete(condition=None)`
Löscht alle Zeilen, die der Bedingung entsprechen. Ohne Bedingung werden alle Zeilen der Tabelle gelöscht.
- `condition` (str oder `Column`, optional, Default `None`) — SQL-Bedingung bzw. Spaltenausdruck; ohne Angabe sind alle Zeilen betroffen.
```python
deltaTable.delete("date < '2017-01-01'")
deltaTable.delete(col("date") < "2017-01-01")
```

### `deltaTable.update(condition=None, set)`
Aktualisiert Zeilen, die der Bedingung entsprechen, gemäß den in `set` angegebenen Regeln. Es gibt zwei Aufrufvarianten: mit `condition` positional/keyword für einen Teil der Zeilen, oder rein per Keyword `set=...` ohne `condition`, um alle Zeilen zu aktualisieren.
- `condition` (str oder `Column`, optional) — Bedingung, welche Zeilen betroffen sind; ohne Angabe werden alle Zeilen aktualisiert.
- `set` (Dict[str, str oder `Column`], erforderlich) — Mapping von Spaltennamen auf die neuen Werte/Ausdrücke.
```python
deltaTable.update(condition="eventType = 'clck'", set={"eventType": "'click'"})
deltaTable.update(condition=col("eventType") == "clck",
                   set={"eventType": lit("click")})
```

### `deltaTable.merge(source, condition)`
Führt Daten aus dem `source`-DataFrame anhand der Merge-Bedingung mit der Delta-Tabelle zusammen. Gibt einen `DeltaMergeBuilder` zurück, an dem anschließend `whenMatchedUpdate()`, `whenMatchedDelete()`, `whenNotMatchedInsert()` usw. sowie abschließend `execute()` aufgerufen werden (Details siehe eigene Datei zu `DeltaMergeBuilder`).
- `source` (`DataFrame`) — Quelldaten für den Merge.
- `condition` (str oder `Column`) — Bedingung, die Zeilen aus `source` und der Zieltabelle einander zuordnet.
```python
deltaTable.alias("events").merge(
    source=updatesDF.alias("updates"),
    condition="events.eventId = updates.eventId"
).whenMatchedUpdate(set={
    "data": "updates.data",
    "count": "events.count + 1"
}).whenNotMatchedInsert(values={
    "date": "updates.date",
    "eventId": "updates.eventId",
    "data": "updates.data",
    "count": "1"
}).execute()
```

## <a id="wartung">5. Wartung</a>

### `deltaTable.vacuum(retentionHours=None)`
Löscht rekursiv Dateien/Verzeichnisse der Tabelle, die für keine Version innerhalb der Aufbewahrungsschwelle mehr benötigt werden. Gibt bei Erfolg ein leeres `DataFrame` zurück.
- `retentionHours` (float, optional, Default `None`) — Aufbewahrungsschwelle in Stunden; ohne Angabe gilt der Standardwert der Tabelle (i. d. R. 7 Tage / 168 Stunden).
```python
deltaTable.vacuum()     # löscht Dateien, die älter als 7 Tage nicht mehr gebraucht werden
deltaTable.vacuum(100)  # löscht Dateien, die älter als 100 Stunden nicht mehr gebraucht werden
```

### `deltaTable.optimize()`
Optimiert das Datei-Layout der Tabelle. Gibt einen `DeltaOptimizeBuilder` zurück, mit dem ein Partitionsfilter gesetzt und anschließend eine Optimierungstechnik ausgeführt werden kann (z. B. Kompaktierung oder Z-Order) — Details siehe eigene Datei zu `DeltaOptimizeBuilder`.
```python
deltaTable.optimize().where("date='2021-11-18'").executeCompaction()
```

### `deltaTable.history(limit=None)`
Liefert die Commit-Historie der Tabelle als `DataFrame`, in umgekehrt chronologischer Reihenfolge (neuester Eintrag zuerst).
- `limit` (int, optional, Default `None`) — Anzahl der letzten Commits, die zurückgegeben werden; ohne Angabe wird die vollständige Historie geliefert.
```python
fullHistoryDF = deltaTable.history()    # komplette Historie
lastOperationDF = deltaTable.history(1) # nur die letzte Operation
```

### `deltaTable.detail()`
Liefert Detailinformationen zur Tabelle als `DataFrame`, u. a. Format, Name, Größe, Partitionsspalten und Anzahl Dateien.
```python
detailDF = deltaTable.detail()
```

## <a id="versionierung">6. Versionierung</a>

### `deltaTable.restoreToVersion(version)`
Setzt die Tabelle auf einen älteren Stand anhand der Versionsnummer zurück (entspricht SQL `RESTORE TABLE ... TO VERSION AS OF`).
- `version` (int) — Zielversion, auf die zurückgesetzt wird.
```python
deltaTable = DeltaTable.forPath(spark, "/path/to/table")
deltaTable.restoreToVersion(1)
```

### `deltaTable.restoreToTimestamp(timestamp)`
Setzt die Tabelle auf den Stand zu einem bestimmten Zeitpunkt zurück.
- `timestamp` (str) — Zielzeitpunkt im Format `yyyy-MM-dd` oder `yyyy-MM-dd HH:mm:ss`.
```python
deltaTable.restoreToTimestamp('2021-01-01')
deltaTable.restoreToTimestamp('2021-01-01 01:01:01')
```

### `deltaTable.clone(target, isShallow=False, replace=False, properties=None)`
Klont den aktuellen (neuesten) Stand der Tabelle in ein Ziel, das Daten und Metadaten der Quelltabelle zu diesem Zeitpunkt spiegelt.
- `target` (str) — Zielpfad, unter dem der Klon angelegt wird.
- `isShallow` (bool, Default `False`) — `True` für einen Shallow Clone (nur Metadaten, Daten werden per Referenz auf die Quelle genutzt), `False` für einen Deep Clone (Daten werden physisch kopiert).
- `replace` (bool, Default `False`) — `True`, um eine bereits am Ziel vorhandene Tabelle zu überschreiben; sonst wird ein Fehler geworfen, falls am Ziel schon eine Tabelle existiert.
- `properties` (Dict, optional, Default `None`) — benutzerdefinierte Tabellen-Properties, die Properties gleichen Namens aus der Quelltabelle überschreiben.
```python
deltaTable = DeltaTable.clone("/path/to/table", False, True)
```

### `deltaTable.cloneAtVersion(version, target, isShallow=False, replace=False, properties=None)`
Wie `clone()`, klont aber gezielt den Stand einer bestimmten Version.
- `version` (int) — Version der Quelltabelle, deren Daten/Metadaten geklont werden.
- `target`, `isShallow`, `replace`, `properties` — wie bei `clone()`.
```python
deltaTable = DeltaTable.cloneAtVersion(1, "/path/to/table", False)
```

### `deltaTable.cloneAtTimestamp(timestamp, target, isShallow=False, replace=False, properties=None)`
Wie `clone()`, klont aber gezielt den Stand zu einem bestimmten Zeitpunkt.
- `timestamp` (str) — Zeitpunkt der Quelltabelle, dessen Daten/Metadaten geklont werden.
- `target`, `isShallow`, `replace`, `properties` — wie bei `clone()`.
```python
deltaTable = DeltaTable.cloneAtTimestamp("2019-01-01", "/path/to/table", False)
```

## <a id="protokoll">7. Protokoll/Features</a>

### `DeltaTable.convertToDelta(sparkSession, identifier, partitionSchema=None)`
Wandelt eine bestehende Parquet-Tabelle in eine Delta-Tabelle um, indem im Basisverzeichnis der Tabelle ein Delta-Transaktionslog angelegt wird.
- `sparkSession` — die aktive `SparkSession`.
- `identifier` (str) — Identifier der Parquet-Tabelle, z. B. `` parquet.`path/to/table` ``.
- `partitionSchema` (`StructType` oder str, optional, Default `None`) — Partitionsschema, falls die Parquet-Tabelle partitioniert ist.
```python
deltaTable = DeltaTable.convertToDelta(spark, "parquet.`path/to/table`")
partitionedDeltaTable = DeltaTable.convertToDelta(
    spark, "parquet.`path/to/table`", "part int")
```

### `deltaTable.upgradeTableProtocol(readerVersion, writerVersion)`
Hebt die Protokollversion der Tabelle an, um neue Features nutzen zu können. Eine höhere Reader-Version verhindert den Zugriff für Clients mit älteren Delta-Lake-Versionen, eine höhere Writer-Version verhindert das Schreiben durch ältere Clients.
- `readerVersion` (int) — neue Reader-Protokollversion.
- `writerVersion` (int) — neue Writer-Protokollversion.
```python
deltaTable.upgradeTableProtocol(1, 3)
```

### `deltaTable.addFeatureSupport(featureName)`
Ergänzt das Protokoll um ein unterstütztes Feature. Falls die Tabelle noch keine Table Features nutzt, wird das Protokoll automatisch angehoben: bei einem reinen Writer-Feature auf Writer-Version 7, bei einem Reader-Writer-Feature auf (Reader 3, Writer 7).
- `featureName` (str) — Name des zu aktivierenden Features.
```python
deltaTable.addFeatureSupport("rowTracking")
```

### `deltaTable.dropFeatureSupport(featureName, truncateHistory=None)`
Entfernt ein unterstütztes Feature aus dem Protokoll. Das resultierende Protokoll wird dabei immer normalisiert (auf die schwächstmögliche Form reduziert).
- `featureName` (str) — Name des zu entfernenden Features.
- `truncateHistory` (bool, optional, Default `None`) — ob die Tabellenhistorie zusätzlich gekürzt werden soll (relevant für Features wie `rowTracking`, die u. U. historische Log-Einträge betreffen).
```python
deltaTable.dropFeatureSupport("rowTracking")
```

## <a id="generate">8. generate()</a>

### `deltaTable.generate(mode)`
Erzeugt Manifest-Dateien für die Delta-Tabelle, damit externe Engines ohne native Delta-Unterstützung die Tabelle lesen können.
- `mode` (str, nicht case-sensitiv) — Art des zu erzeugenden Manifests. In der Referenz ist als gültiger Wert dokumentiert: `"symlink_format_manifest"` — erzeugt Manifeste im Symlink-Format für den Lesezugriff durch Presto und Athena. Weitere Modi sind in der aktuell gefetchten Fassung der Referenzseite nicht aufgeführt (ungeklärt, ob es weitere gültige Werte gibt).
```python
deltaTable.generate("symlink_format_manifest")
```

## <a id="quellen">9. Quellen</a>
- DeltaTable — vollständige Klassenreferenz (Signaturen, Parameter, Beispiele): https://docs.delta.io/api/latest/python/spark/

**Stand:** 2026-09-21.
