## Rescued Data

Ingestion-Techniken wie **`read_files()`**, **`spark.read`** oder **Auto Loader** stellen während der Ingestion eine Rescued-Data-Spalte bereit:

- Die Rescued-Data-Spalte stellt sicher, dass Spalten, die nicht zum Schema passen, **gerettet statt verworfen** werden
- Nicht passende Werte werden als **JSON-formatierte Strings** in der Spalte `_rescued_data` gespeichert
- Wenn eine Zeile keine Schema-Abweichungen aufweist, ist die Spalte `_rescued_data` `null`
- So bleiben alle Eingabedaten erhalten und ein unbemerkter Datenverlust wird verhindert

In dieser Lektion haben Sie gelernt, wie die Rescued-Data-Spalte bei der Daten-Ingestion funktioniert:

- Wenn Eingabedaten nicht dem erwarteten Schema entsprechen, **werden nicht passende Werte in der Spalte `_rescued_data`** als JSON-formatierte Strings erfasst, anstatt verworfen zu werden.
- Die Rescued-Data-Spalte ist bei Verwendung von **`read_files()`**, **`spark.read`** oder **Auto Loader** verfügbar.
- Werte, die zum Schema passen, werden normal ingestiert, und `_rescued_data` ist für diese Zeilen `null`.
- Diese Funktion verhindert unbemerkten Datenverlust und ermöglicht es Ihnen, Schema-Abweichungen nach der Ingestion zu untersuchen und zu beheben.
