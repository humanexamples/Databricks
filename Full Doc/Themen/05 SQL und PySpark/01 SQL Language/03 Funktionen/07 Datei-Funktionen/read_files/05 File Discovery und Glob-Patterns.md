# `read_files` — File Discovery und Glob-Patterns

`read_files` liest eine einzelne Datei oder alle Dateien unter einem Verzeichnis. Ohne Glob durchsucht es das Verzeichnis **rekursiv**. Mit Glob steigt es nur in die Verzeichnisse ab, die zum Muster passen.

## Glob-Patterns

Globs im `path` filtern Verzeichnisse und Dateien.

| Muster | Bedeutung |
|---|---|
| `?` | Genau ein beliebiges Zeichen |
| `*` | Null oder mehr Zeichen |
| `[abc]` | Ein Zeichen aus der Menge `{a,b,c}` |
| `[a-z]` | Ein Zeichen aus dem Bereich `{a…z}` |
| `[^a]` | Ein Zeichen, das **nicht** aus der Menge/dem Bereich stammt. `^` muss direkt nach der öffnenden Klammer stehen. |
| `{ab,cd}` | Ein String aus der Menge `{ab, cd}` |
| `{ab,c{de,fh}}` | Ein String aus der Menge `{ab, cde, cfh}` |

## Strikter Globber (`useStrictGlobber`)

`read_files` nutzt beim Globben standardmäßig den **strikten Globber** (`useStrictGlobber => true`, ab DBR 12.2 LTS). Bei Auto Loader ist der Default umgekehrt.

Ist der strikte Globber **aus**:

- werden abschließende Slashes (`/`) ignoriert,
- kann `*` über mehrere Verzeichnisebenen hinweg passen.

Fälle, in denen sich beide Modi unterscheiden (nicht strikt: Treffer, strikt: kein Treffer):

```text
Muster        Dateipfad
/a/*/d/       /a/b/c/d/file.txt
/a/*/c/       /a/b/x/y/c/file.txt
/a/*/c        /a/b/c_file.txt
/a/*/c/       /a/b/c_file.txt
/a/*/c        /a/b/cookie/file.txt
```

Fälle, in denen beide Modi gleich reagieren:

```text
Muster            Dateipfad              Treffer
/a/b              /a/b/c/file.txt        ja
/a/b              /a/b_dir/c/file.txt    nein
/a/b              /a/b.txt               nein
/a/b/             /a/b.txt               nein
/a/*/c/           /a/b/c/file.txt        ja
/a/*/c/           /a/b/c/d/file.txt      ja
/a/b*             /a/b.txt               ja
/a/b*             /a/b/file.txt          ja
/a/{0.txt,1.txt}  /a/0.txt               ja
/a/*/{0.txt,1.txt} /a/0.txt              nein
/a/b/[cde-h]/i/   /a/b/c/i/file.txt      ja
```
