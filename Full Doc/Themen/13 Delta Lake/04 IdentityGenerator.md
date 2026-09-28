# `IdentityGenerator` — Python-Referenz (Delta Lake)

## Abschnittsübersicht
1. [Zweck](#zweck)
2. [Konstruktor und Attribute](#konstruktor)
3. [Verwendung mit `addColumn()`](#verwendung)
4. [Quellen](#quellen)

## <a id="zweck">1. Zweck</a>

`IdentityGenerator` (aus `delta.tables`) beschreibt die Konfiguration einer Identity-Spalte (automatisch generierte, fortlaufende Werte) für eine Delta-Tabelle. Man übergibt eine Instanz als Wert für `generatedAlwaysAs` oder `generatedByDefaultAs` beim Aufruf von `DeltaTableBuilder.addColumn()` — siehe [03 DeltaTableBuilder.md](03%20DeltaTableBuilder.md).

## <a id="konstruktor">2. Konstruktor und Attribute</a>

- Konstruktor: `IdentityGenerator(start: int = 1, step: int = 1)`.
- Attribute:
  - `start` (int, Default `1`) — Startwert der Identity-Spalte, also der Wert der ersten generierten Zeile.
  - `step` (int, Default `1`) — Schrittweite zwischen aufeinanderfolgenden generierten Werten (auch negative Werte möglich, für absteigende Sequenzen).

```python
from delta.tables import IdentityGenerator

gen = IdentityGenerator(start=100, step=5)
gen.start  # 100
gen.step   # 5
```

## <a id="verwendung">3. Verwendung mit `addColumn()`</a>

- `generatedAlwaysAs=IdentityGenerator(...)` — die Datenbank generiert bei jedem Insert immer selbst den Wert; ein vom Nutzer mitgegebener Wert für diese Spalte führt zu einem Fehler.
- `generatedByDefaultAs=IdentityGenerator(...)` — die Datenbank generiert den Wert nur, wenn der Nutzer für diese Spalte keinen eigenen Wert angibt.

```python
from delta.tables import DeltaTable, IdentityGenerator

deltaTable = DeltaTable.create(spark) \
    .tableName("events") \
    .addColumn("id", dataType="BIGINT", generatedAlwaysAs=IdentityGenerator(start=1, step=1)) \
    .addColumn("payload", dataType="STRING") \
    .execute()
```

## <a id="quellen">4. Quellen</a>
- `IdentityGenerator` — vollständige Klassenreferenz (Signaturen, Parameter, Beispiele): https://docs.delta.io/api/latest/python/spark/

**Stand:** 2026-09-21.
