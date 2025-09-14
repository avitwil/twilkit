
# ADVfile_manager — Usage Guide (v1.3.0)


**Author:** Avi Twil
**Repo:** [https://github.com/avitwil/ADVfile\_manager](https://github.com/avitwil/ADVfile_manager)

Unified file abstractions for Python with **safe I/O patterns**, **in-memory caching**, **timestamped backups**, **context-manager safety (auto-backup & restore-on-error)**, **exit-time cleanup of ephemeral backups**, and a **single, unified search() signature** — across **Text, JSON, CSV, YAML, INI, TOML, XML, and Excel** files. Includes **async facades** (`ATextFile`, `AJsonFile`, …) for non-blocking workflows.

---

## Why ADVfile\_manager?

* **One API, many formats** – Read/Write/Append/Search the same way for TXT/JSON/CSV/YAML/INI/TOML/XML/Excel.
* **Safer workflows** – Context manager takes a backup on enter and restores on exceptions.
* **Backups you control** – `backup()`, `list_backups()`, `restore()`, `clear_backups()`.
* **Ephemeral edits** – Mark a file instance `keep_backup=False` and its backups auto-delete at interpreter exit.
* **Unified search** – One method signature (`search(pattern=..., key=..., value=..., columns=..., tag=..., attr=..., sheet=...)`) adapted per format.
* **In-memory cache** – Fast `read()` re-uses cached content; `clear_cache()` when you need a fresh disk read.
* **Async ready** – `aread/awrite/aappend/asearch` and `async with` on the `A*` classes.
* **Practical safety** – Uses temp-file + `os.replace()` where appropriate (e.g., TOML/XML/Excel) to reduce corruption risk.

> Note: Full atomic writes aren’t possible for every format in every environment. ADVfile\_manager uses best-effort safe patterns per format.

---

## Table of Contents

1. [Why ADVfile_manager?](#why-advfile_manager)
2. [Installation](#installation)
3. [Feature Comparison](#feature-comparison)
   - [ADVfile_manager vs. common alternatives](#comparison-vs-others)
   - [ADVfile_manager vs. ATmulti_file_handler](#comparison-vs-atmulti_file_handler)
4. [Quick Start](#quick-start)
5. [Base Class: `File` (applies to all formats)](#base-file)
   - [Constructor & Attributes](#file-constructor)
   - [Context Manager & Ephemeral Backups](#file-context)
   - [Backups / Restore / Clear / List](#file-backups)
   - [Caching & File Size Helpers](#file-cache-and-size)
   - [Unified `search()` Contract (format-specific behavior)](#file-search-contract)
   - [Exit-Time Cleanup Controls (module-level)](#file-exit-cleanup)
6. [TextFile (TXT) — Complete Guide](#textfile)
   - [Constructor](#textfile)  <!-- jumps to section top (constructor right below) -->
   - [Core I/O & Line helpers](#textfile)  <!-- same section; methods just below -->
   - [Search](#textfile)  <!-- same section -->
   - [Backups & Context Safety (TextFile)](#textfile)  <!-- same section -->
7. [JsonFile (JSON) — Complete Guide](#jsonfile-json--complete-guide)
   - [Constructor](#jsonfile-json--complete-guide)
   - [Core I/O, Accessors (`get_item`, `items`)](#jsonfile-json--complete-guide)
   - [Search](#jsonfile-json--complete-guide)
8. [CsvFile (CSV) — Complete Guide](#csvfile-csv--complete-guide)
   - [Constructor](#csvfile-csv--complete-guide)
   - [write / read / append / read_row / rows](#csvfile-csv--complete-guide)
   - [Search](#csvfile-csv--complete-guide)
9. [YamlFile (YAML) — Complete Guide](#yamlfile-yaml--complete-guide)
   - [Constructor](#yamlfile-yaml--complete-guide)
   - [Core I/O, Accessors (`get_item`, `items`)](#yamlfile-yaml--complete-guide)
   - [Search](#yamlfile-yaml--complete-guide)
10. [IniFile (INI) — Complete Guide](#inifile-ini--complete-guide)
    - [Constructor](#inifile-ini--complete-guide)
    - [write / read / append](#inifile-ini--complete-guide)
    - [Search](#inifile-ini--complete-guide)
11. [TomlFile (TOML) — Complete Guide](#tomlfile-toml--complete-guide)
    - [Constructor](#tomlfile-toml--complete-guide)
    - [write / read / append](#tomlfile-toml--complete-guide)
    - [Search](#tomlfile-toml--complete-guide)
12. [XmlFile (XML) — Complete Guide](#xmlfile-xml--complete-guide)
    - [Constructor](#xmlfile-xml--complete-guide)
    - [write / read / append](#xmlfile-xml--complete-guide)
    - [Search](#xmlfile-xml--complete-guide)
13. [ExcelFile (XLSX via openpyxl) — Complete Guide](#excelfile-xlsx-via-openpyxl--complete-guide)
    - [Constructor](#excelfile-xlsx-via-openpyxl--complete-guide)
    - [write / read / append](#excelfile-xlsx-via-openpyxl--complete-guide)
    - [Search](#excelfile-xlsx-via-openpyxl--complete-guide)
14. [Async A* Classes — Complete Guide](#async-a-classes--complete-guide)
    - [ATextFile](#async-a-classes--complete-guide)
    - [AJsonFile](#async-a-classes--complete-guide)
    - [ACsvFile](#async-a-classes--complete-guide)
    - [AYamlFile](#async-a-classes--complete-guide)
    - [AIniFile](#async-a-classes--complete-guide)
    - [ATomlFile](#async-a-classes--complete-guide)
    - [AXmlFile](#async-a-classes--complete-guide)
    - [AExcelFile](#async-a-classes--complete-guide)
15. [Backups, Restore & Context Safety — Deep Dive](#backups-restore--context-safety--deep-dive)
16. [Global Utilities](#global-utilities)
17. [Unified `search(...)` Cheatsheet](#unified-search-cheatsheet)
18. [Installation (v1.3.0)](#installation-v130)
19. [Comparison Tables](#comparison-tables)
    - [ADVfile_manager vs. Popular Libraries](#advfile_manager-vs-popular-libraries)
    - [ADVfile_manager vs. Your ATmulti_file_handler](#advfile_manager-vs-your-atmulti_file_handler-hypothetical-prior-tool)
20. [Sample Project — End-to-End](#sample-project--end-to-end)
21. [Roadmap (next iterations)](#roadmap-next-iterations)



---

## Installation

```bash
pip install ADVfile_manager
```

**Optional dependencies (install only if you need the format):**

* YAML: `pip install pyyaml`
* TOML (read): Python 3.11+ (builtin `tomllib`) — or `pip install tomli`
* TOML (write): `pip install tomli-w`
* Excel (XLSX): `pip install openpyxl`

Python **3.8+** recommended.

---

## Feature Comparison

### <a id="comparison-vs-others"></a>ADVfile\_manager vs. common alternatives

| Capability / Tool                               | **ADVfile\_manager**                 | `pathlib` (stdlib) | `os`/`shutil` (stdlib) | `json`/`csv`/`configparser`/`xml.etree` (stdlib) | `pandas`                       | `PyYAML`/`ruamel.yaml` | `openpyxl`       |
| ----------------------------------------------- | ------------------------------------ | ------------------ | ---------------------- | ------------------------------------------------ | ------------------------------ | ---------------------- | ---------------- |
| Supported formats                               | TXT/JSON/CSV/YAML/INI/TOML/XML/Excel | Paths only         | Filesystem ops         | Parsing per format (fragmented)                  | CSV/JSON/Excel/… as DataFrames | YAML only              | Excel only       |
| Unified API (read/write/append/search)          | **Yes**                              | No                 | No                     | No (each module different)                       | Partially (DF centric)         | No                     | No               |
| Context safety (auto backup + restore on error) | **Yes**                              | No                 | No                     | No                                               | No                             | No                     | No               |
| Backups utilities                               | **Yes**                              | No                 | No                     | No                                               | No                             | No                     | No               |
| Ephemeral backups (atexit cleanup)              | **Yes**                              | No                 | No                     | No                                               | No                             | No                     | No               |
| In-memory cache + `clear_cache()`               | **Yes**                              | No                 | No                     | No                                               | DF caching model               | No                     | No               |
| Unified search signature                        | **Yes**                              | No                 | No                     | No                                               | DataFrame ops                  | No                     | No               |
| Async facade                                    | **Yes**                              | No                 | No                     | No                                               | No (needs extra libs)          | No                     | No               |
| Extra safety writes (temp + replace)            | TOML/XML/Excel                       | N/A                | N/A                    | Usually no                                       | No                             | N/A                    | Depends on usage |
| Learning curve                                  | **Low**                              | Low                | Low                    | **High** (inconsistent)                          | Medium/High                    | Low                    | Low              |

### <a id="comparison-vs-atmulti_file_handler"></a>ADVfile\_manager vs. **ATmulti\_file\_handler** (my other tool)

| Area                                   | **ADVfile\_manager 1.3.0**                             | **ATmulti\_file\_handler**       |
| -------------------------------------- | ------------------------------------------------------ | -------------------------------- |
| Unified search across formats          | **Yes** (`search()` signature works everywhere)        | Partial/Absent                   |
| Async (`A*` classes)                   | **Yes** (`aread/awrite/aappend/asearch`, `async with`) | Partial/Absent                   |
| Formats                                | TXT/JSON/CSV/**YAML/INI/TOML/XML/Excel**               | Likely subset (TXT/JSON/CSV/…)\* |
| Context safety (auto backup + restore) | **Yes**                                                | Partial/Absent                   |
| Ephemeral backups (atexit cleanup)     | **Yes**                                                | Absent                           |
| Safe writes (temp+replace)             | TOML/XML/Excel                                         | Varies                           |
| Docs & teaching focus                  | **Very high (this README)**                            | Varies                           |

\* If your previous tool already supports some of these, the main upgrade here is **the unified search API, async facade, and the broader format coverage (YAML/INI/TOML/XML/Excel) with consistent ergonomics and safety patterns.**

---

## Quick Start

```python
from ADVfile_manager import TextFile, JsonFile

base = "example_data"

# Text
txt = TextFile("notes.txt", base)
txt.write("first line")
txt.append("second line")
print(txt.read())           # "first line\nsecond line"
print(txt.read_line(2))     # "second line"
for i, line in txt.lines():
    print(i, line)

# Safe edit with automatic backup/restore
with TextFile("notes.txt", base) as safe:
    safe.append("inside context")
    # raise Exception("boom")  # uncomment to see auto-restore in action

# JSON
j = JsonFile("config.json", base)
j.write({"users": [{"id": 1}]})
j.append({"active": True})
print(j.read())             # {'users': [{'id': 1}], 'active': True}

# Unified search (examples later in doc)
hits = list(txt.search(pattern="second"))
print(hits[0]["value"])     # matched line text
```

---

## <a id="base-file"></a>Base Class: `File` (applies to all formats)

Every concrete class (`TextFile`, `JsonFile`, …) inherits from `File`, so the features here are **universal**.

### <a id="file-constructor"></a>Constructor & Attributes

```python
from ADVfile_manager import TextFile  # any subclass has the same base behavior

# file_path is created if missing; status reflects file existence
f = TextFile("example.txt", file_path="example_data")  # keep_backup=True by default

print(f.name)       # "example.txt"
print(f.path)       # "example_data"
print(f.full_path)  # "example_data/example.txt"
print(f.status)     # False initially (until you write)
print(f.content)    # None (cache empty)
```

**Notes & exceptions**

* If the `file_path` directory does not exist, it is created automatically.
* `status` reflects on-disk existence of `full_path`.
* `content` is an internal cache. It’s `None` until a successful `read()` or `write()` populates it.

---

### <a id="file-context"></a>Context Manager & Ephemeral Backups

**Why:** To protect against partial writes or runtime errors.
**How it works:**

* On `__enter__`: if `keep_backup=True`, a backup is taken automatically (if file exists).
* On `__exit__`: if an exception occurred and `keep_backup=True`, the file is restored from the latest backup.
* Cache is always cleared on exit.
* If `keep_backup=False`, backups for that file are cleared on exit (and also at interpreter shutdown).

```python
from ADVfile_manager import TextFile

# Default: keep_backup=True
with TextFile("plan.txt", "example_data") as t:
    t.write("v1")
    # If an exception happens now, restore() is called for you.

# Mark an existing instance as ephemeral just for this context:
ephemeral = TextFile("temp.txt", "example_data")
with ephemeral(keep_backup=False) as t:
    t.write("temporary value")
# On exit: backups for this file are removed
```

**Exceptions**

* If the file did not exist at `__enter__`, no backup is created (no error).
* If restore is attempted but no backups exist (rare), it’s simply skipped.

---

### <a id="file-backups"></a>Backups / Restore / Clear / List

**Why:** Safe rollback points and manual recovery.

```python
from ADVfile_manager import TextFile

t = TextFile("story.txt", "example_data")
t.write("v1"); b1 = t.backup()
t.write("v2"); b2 = t.backup()

print(t.list_backups())   # [ "...story.txt.2025..._..._...bak", "...v2....bak" ]

t.restore()               # restore latest (v2)
t.restore(b1)             # restore a specific backup (v1)
removed = t.clear_backups()
print("removed backups:", removed)
```

**Exceptions**

* `backup()` raises `FileNotFoundError` if the file doesn’t exist yet.
* `restore()` raises `FileNotFoundError` if no backups are found (only when you call it manually without any backups).

---

### <a id="file-cache-and-size"></a>Caching & File Size Helpers

```python
f = TextFile("data.txt", "example_data")
f.write("hello")
print(f.read())            # cached
print(f.get_size())        # bytes
print(f.get_size_human())  # e.g. "6.0 B"
f.clear_cache()
# Next read() will re-open from disk:
print(f.read())
```

---

### <a id="file-search-contract"></a>Unified `search()` Contract (format-specific behavior)

Every subclass implements `search()` with the **same signature**:

```python
search(
    pattern: str | None = None,
    *,
    regex: bool = False,
    case: bool = False,
    key: str | None = None,            # mapping-like formats (JSON/YAML/INI/TOML)
    value: Any = None,                 # exact value match
    columns: Sequence[str] | None = None,  # CSV/Excel column filter
    tag: str | None = None,            # XML tag filter
    attr: dict[str,str] | None = None, # XML attributes equals filter
    sheet: str | None = None,          # Excel sheet filter
    limit: int | None = None,
) -> Iterator[dict]
```

**Return value:** an **iterator of hit dicts**. Keys vary by format but follow this baseline:

* `path`: string (`/full/path.ext` with location info for row/line/col when relevant)
* `value`: the matched value (string or native)
* `line` / `row` / `col` / `sheet`: location hints where applicable
* `context`: short string or object to understand the match (**e.g.** full line for text, row dict for CSV/Excel, element for XML).
* Some formats add keys like `key` (JSON/YAML/TOML dict key) or `section` (INI).

You’ll see practical examples under each file type.

---

### <a id="file-exit-cleanup"></a>Exit-Time Cleanup Controls (module-level)

**Why:** When you open files in ephemeral mode (`keep_backup=False`), their backups are registered to be deleted automatically when the interpreter exits. You can control this behavior globally.

```python
from ADVfile_manager import set_exit_cleanup, cleanup_backups_for_all, TextFile

# enable/disable atexit cleanup globally (enabled by default)
set_exit_cleanup(True)
set_exit_cleanup(False)

# manual cleanup (removes backups for all ephemeral-registered files)
removed_total = cleanup_backups_for_all()
print(removed_total)
```

---

## <a id="textfile"></a>TextFile (TXT) — Complete Guide

`TextFile` is for plain UTF-8 text. It supports **full CRUD** and **line-level helpers**.

### Constructor

```python
from ADVfile_manager import TextFile

txt = TextFile("log.txt", "example_data")
```

* Creates `example_data/` if it doesn’t exist.
* `status` indicates if `log.txt` exists already.
* `keep_backup=True` by default (context manager will auto-backup).

---

### Methods Overview

* **Core I/O**

  * `write(data: str) -> None`
  * `read() -> str`
  * `append(data: str) -> None`
* **Line helpers**

  * `lines() -> Generator[tuple[int, str], None, None]`
  * `read_line(line_number: int) -> str`
* **Search**

  * `search(pattern, regex=False, case=False, limit=None) -> Iterator[dict]`
* **Inherited from `File`**

  * `backup()`, `list_backups()`, `restore(backup_path=None)`, `clear_backups()`
  * `clear_cache()`
  * `get_size()`, `get_size_human()`
  * Context manager & ephemeral control (`with ...`, `obj(keep_backup=False)`)

Below, each method has **Why / How / Example / Exceptions**.

---

### `write(data: str) -> None`

**Why:** Replace the entire file content in one go.

**How:** Opens in text mode, writes `data`, updates in-memory cache and `status=True`.

```python
txt = TextFile("a.txt", "example_data")
txt.write("Hello\nWorld")
print(txt.status)   # True
```

**Exceptions**

* If the directory is not writable, the OS will raise (e.g. `PermissionError`).

---

### `read() -> str`

**Why:** Get the entire file content (cached after first read).

**How:** Reads from disk once, caches result in `txt.content`.

```python
txt = TextFile("a.txt", "example_data")
txt.write("Hello\nWorld")
print(txt.read())       # "Hello\nWorld"
print(txt.read())       # cached (no disk I/O)
txt.clear_cache()
print(txt.read())       # re-read from disk
```

**Exceptions**

* If the file does not exist, `open(..., "rt")` raises `FileNotFoundError`.
  Create it with `write()` first or guard with `txt.status`.

---

### `append(data: str) -> None`

**Why:** Add content to the end; preserves line semantics.

**How:** If file already has bytes (`size > 0`), a leading newline is inserted automatically.

```python
txt = TextFile("log.txt", "example_data")
txt.write("first")
txt.append("second")
txt.append("third")
print(txt.read())
# first
# second
# third
```

**Exceptions**

* Same as `write()` (filesystem errors).

---

### `lines() -> Generator[(line_number, line_text)]`

**Why:** Stream large files without loading all content.

**How:** Yields `(1, "first line")`, `(2, "second line")`, … (no trailing `\n`).

```python
for num, line in TextFile("a.txt", "example_data").lines():
    print(f"{num}: {line}")
```

**Exceptions**

* `FileNotFoundError` if the file does not exist at open time.

---

### `read_line(line_number: int) -> str`

**Why:** Random access to a specific line (1-based index).

**How:** Streams until the requested line, returns the text without trailing newline.

```python
txt = TextFile("a.txt", "example_data")
txt.write("first\nsecond\nthird")
print(txt.read_line(2))       # "second"
```

**Exceptions**

* `IndexError` if the requested line does not exist.
* `FileNotFoundError` if the file is missing.

---

### `search(pattern, *, regex=False, case=False, limit=None)`

**Why:** Quickly find lines that contain a substring or match a regex.

**How:** Iterates over lines and yields hit dicts:

```python
txt = TextFile("grep.txt", "example_data")
txt.write("Alpha\nbeta\nALPHA BETA\nGamma")

# Case-insensitive substring (default)
hits = list(txt.search(pattern="alpha"))
print([h["line"] for h in hits])    # [1, 3]

# Case-sensitive
hits = list(txt.search(pattern="Alpha", case=True))
print([h["line"] for h in hits])    # [1]

# Regex
hits = list(txt.search(pattern=r"^A.*BETA$", regex=True))
print([h["line"] for h in hits])    # [3]

# Limit results
hits = list(txt.search(pattern="a", limit=2))
print(len(hits))                    # 2
```

**Hit schema (TextFile)**

```python
{
  "path":   "/abs/path/grep.txt:line[3]",
  "value":  "ALPHA BETA",  # the matching line
  "line":   3,
  "row":    None,
  "col":    None,
  "sheet":  None,
  "context":"ALPHA BETA"
}
```

**Exceptions**

* None (returns an empty iterator if `pattern` is `None`).

---

### Backups & Context Safety with TextFile (practical)

```python
t = TextFile("edit.txt", "example_data")
t.write("v1")
b1 = t.backup()
t.write("v2")
b2 = t.backup()

print(t.list_backups())  # two backups now
t.restore(b1)            # roll back to "v1"
print(t.read())          # "v1"
removed = t.clear_backups()

# Context safety demo
try:
    with TextFile("edit.txt", "example_data") as safe:
        safe.write("draft")
        raise RuntimeError("oops")   # triggers restore of previous version
except RuntimeError:
    pass
print(t.read())  # back to "v1"
```

---

### Putting it together: Text log utility (mini demo)

```python
from ADVfile_manager import TextFile

base = "example_data"
log  = TextFile("app.log", base)

# Start a log (safe transactional edit)
with log:
    log.write("[start] app booting")
    log.append("user=avi")
    # ... if a crash occurs, previous content (if any) is restored

# Searching logs
for hit in log.search(pattern="user"):
    print(f"line {hit['line']}: {hit['value']}")

# Backups lifecycle
b = log.backup()
print("backup:", b)
print("backups:", log.list_backups())
log.restore()          # latest
log.clear_backups()
```

# JsonFile (JSON) — Complete Guide

`JsonFile` handles JSON files with either a **dict root** or a **list root**.
Supports append semantics for both types, item accessors, iteration, and unified `search()`.

---

### Constructor

```python
from ADVfile_manager import JsonFile

j = JsonFile("data.json", "example_data")
```

* Creates `example_data/data.json` if missing when you `write()`.
* Auto-loads into memory on first `read()` or if already exists.

---

### Methods Overview

* **Core I/O**

  * `write(data: Any)`
  * `read() -> Any`
  * `append(data: Any)`
* **Accessors**

  * `get_item(index_or_key)`
  * `items() -> Iterable`
* **Search**

  * `search(pattern=..., key=..., value=..., regex=False, case=False, limit=None)`

Inherited methods: backups, cache, size helpers, context, etc.

---

### `write(data: dict | list)`

**Why:** Overwrite with a Python dict or list as JSON.
**How:** Dumps JSON with indentation (default indent=2).

```python
j = JsonFile("d.json", "example_data")
j.write({"users": [{"id": 1}]})
print(j.read())   # {'users': [{'id': 1}]}

jl = JsonFile("l.json", "example_data")
jl.write([{"id": 1}, {"id": 2}])
```

**Exceptions**

* If `data` isn’t JSON-serializable, `TypeError` from `json.dump`.

---

### `read() -> dict | list`

**Why:** Get file content into Python objects.
**How:** Uses `json.load`, caches result in `self.content`.

```python
print(j.read())   # dict
print(jl.read())  # list
```

**Exceptions**

* Raises `FileNotFoundError` if file missing.
* Raises `json.JSONDecodeError` if the file is invalid JSON.

---

### `append(data: Any)`

**Why:** Add new content without rewriting the whole file.
**How:**

* Dict root: requires a dict → shallow merge (`dict.update`).
* List root: appends an element, or extends with an iterable.

```python
j = JsonFile("d.json", "example_data")
j.write({"users": [{"id": 1}]})
j.append({"active": True})
print(j.read())  # {'users':[{'id':1}], 'active':True}

jl = JsonFile("l.json", "example_data")
jl.write([{"id": 1}])
jl.append({"id": 2})
jl.append([{"id": 3}, {"id": 4}])
print(jl.read()) # [{'id':1}, {'id':2}, {'id':3}, {'id':4}]
```

**Exceptions**

* If root is dict but you append non-dict → `TypeError`.
* If root is neither list nor dict → `TypeError`.

---

### `get_item(index_or_key)`

**Why:** Convenient random access.
**How:**

* If root is list → expects 1-based integer index.
* If root is dict → expects string key.

```python
jl = JsonFile("l.json", "example_data")
jl.write([{"id": 10}, {"id": 20}])
print(jl.get_item(2))  # {'id': 20}

j = JsonFile("d.json", "example_data")
j.write({"x": 42})
print(j.get_item("x"))  # 42
```

**Exceptions**

* `TypeError` if wrong type used.
* `IndexError` if index out of range.
* `KeyError` if dict key not present.

---

### `items()`

**Why:** Iterate root contents directly.
**How:**

* Dict root → yields `(key, value)`.
* List root → yields `(1-based index, item)`.

```python
j = JsonFile("d.json", "example_data")
j.write({"a": 1, "b": 2})
for k, v in j.items():
    print(k, v)   # 'a' 1, 'b' 2

jl = JsonFile("l.json", "example_data")
jl.write([{"id": 1}, {"id": 2}])
for i, item in jl.items():
    print(i, item)  # 1 {'id':1}, 2 {'id':2}
```

---

### `search(pattern=..., key=..., value=..., regex=False, case=False, limit=None)`

**Why:** Inspect nested JSON structures with a unified API.
**How:** Walks dicts/lists recursively, matches keys, values, and string patterns.

```python
j = JsonFile("u.json", "example_data")
j.write({"users":[{"id":1,"name":"Avi"},{"id":2,"name":"Dana"}], "active":True})

# Find by key name
hits = list(j.search(pattern="name"))
print([h["value"] for h in hits])  # ["Avi","Dana"]

# Find by exact key
hits = list(j.search(key="active"))
print(hits[0]["value"])            # True

# Find by regex in values
hits = list(j.search(pattern="^A", regex=True))
print([h["value"] for h in hits])  # ["Avi"]
```

**Hit schema (JSON)**

```python
{"path": "/abs/path/u.json", "key": "name", "value": "Avi"}
```

**Exceptions**

* None (invalid key/value just yields no results).

---

# CsvFile (CSV) — Complete Guide

`CsvFile` manages CSVs with headers, using `csv.DictReader`/`DictWriter`.

---

### Constructor

```python
from ADVfile_manager import CsvFile

c = CsvFile("table.csv", "example_data")
```

---

### Methods Overview

* `write(rows, fieldnames=None)`
* `read() -> list[dict[str,str]]`
* `append(row_or_rows)`
* `read_row(n)`
* `rows() -> generator`
* `search(pattern=..., columns=..., value=...)`

---

### `write(rows, fieldnames=None)`

**Why:** Overwrite CSV.
**How:** Writes headers first, then rows.

```python
c = CsvFile("t.csv", "example_data")
c.write([{"name":"Avi","age":30},{"name":"Dana","age":25}])
print(c.read())
```

**Exceptions**

* `ValueError` if rows empty and no fieldnames provided.

---

### `read() -> list[dict]`

**Why:** Load CSV into list of dicts.
**How:** Keys = headers, values = strings.

```python
rows = c.read()
print(rows[0])  # {"name":"Avi","age":"30"}
```

---

### `append(row_or_rows)`

**Why:** Add new rows without overwriting.
**How:** Accepts dict or list of dicts. Infers headers if needed.

```python
c.append({"name":"Noa","age":21})
c.append([{"name":"Lior","age":28},{"name":"Omri","age":33}])
print(c.read())
```

**Exceptions**

* Raises `TypeError` if argument isn’t dict or list of dicts.

---

### `read_row(n)`

**Why:** Access specific row (1-based, excluding header).
**How:** Iterates until that row.

```python
print(c.read_row(2))   # {"name":"Dana","age":"25"}
```

**Exceptions**

* `IndexError` if row doesn’t exist.

---

### `rows()`

**Why:** Stream rows lazily.
**How:** Yields `(row_number, row_dict)`.

```python
for i, row in c.rows():
    print(i, row)
```

---

### `search(pattern=..., columns=None, value=None, regex=False, case=False, limit=None)`

**Why:** Find cells by substring or exact match.
**How:** Iterates through rows/columns.

```python
hits = list(c.search(pattern="Avi"))
print(hits[0]["value"])   # "Avi"

hits = list(c.search(value="21"))
print(hits[0]["row"], hits[0]["col"])   # 3 "age"

hits = list(c.search(pattern="^D", regex=True, columns=["name"]))
print([h["value"] for h in hits])  # ["Dana"]
```

**Hit schema (CSV)**

```python
{
  "path": "/abs/path/table.csv:row[2].name",
  "value": "Dana",
  "row": 2,
  "col": "name",
  "context": "{'name':'Dana','age':'25'}"
}
```

**Exceptions**

* None (just yields no results if no matches).



# YamlFile (YAML) — Complete Guide

`YamlFile` manages YAML configs (requires `PyYAML`).
Behaves like `JsonFile`, with dict/list roots, append semantics, and unified search.

---

### Constructor

```python
from ADVfile_manager import YamlFile

y = YamlFile("config.yaml", "example_data")
```

* Raises `ImportError` if `pyyaml` is not installed.

---

### Methods Overview

* `write(data)`
* `read() -> Any`
* `append(data)`
* `get_item(index_or_key)`
* `items()`
* `search(pattern=..., key=..., value=...)`

---

### `write(data)`

**Why:** Store Python dict/list as YAML.
**How:** Uses `yaml.safe_dump`.

```python
y.write({"app":{"name":"demo"}, "features":["a"]})
print(y.read())
```

**Exceptions**

* `ImportError` if PyYAML missing.
* `yaml.YAMLError` if dump fails.

---

### `read() -> Any`

**Why:** Load YAML into Python structures.
**How:** Uses `yaml.safe_load`.

```python
print(y.read())   # {'app': {'name': 'demo'}, 'features': ['a']}
```

**Exceptions**

* `yaml.YAMLError` if invalid YAML.

---

### `append(data)`

**Why:** Update config easily.
**How:**

* Dict root → shallow merge.
* List root → append or extend.

```python
y.append({"features":["b"]})
print(y.read())  # {'app': {'name':'demo'}, 'features':['a','b']}
```

**Exceptions**

* If root is dict but append non-dict → `TypeError`.
* If root is list but append wrong type → `TypeError`.

---

### `get_item(index_or_key)`

**Why:** Random access.
**How:**

* List root → 1-based index.
* Dict root → key.

```python
print(y.get_item("app"))  # {'name': 'demo'}
```

**Exceptions**

* `TypeError` if wrong accessor type.
* `KeyError` / `IndexError` if missing.

---

### `items()`

**Why:** Iterate over YAML root.
**How:**

* Dict → `(key, value)`
* List → `(index, value)`

```python
for k, v in y.items():
    print(k, v)
```

---

### `search(...)`

**Why:** Inspect YAML recursively (like JSON).
**How:** Uses `_walk_jsonlike`.

```python
hits = list(y.search(pattern="demo"))
print(hits[0]["value"])  # 'demo'
```

---

# IniFile (INI) — Complete Guide

`IniFile` wraps Python’s `configparser`.
Sections and keys are case-insensitive (normalized to lowercase internally).

---

### Constructor

```python
from ADVfile_manager import IniFile

ini = IniFile("settings.ini", "example_data")
```

---

### Methods Overview

* `write(data)`
* `read() -> dict`
* `append(data)`
* `search(pattern=..., key=..., value=...)`

---

### `write(data)`

**Why:** Save INI config from dict.
**How:** Dict → ConfigParser → file.

```python
ini.write({"server": {"host": "127.0.0.1", "port": "8000"}})
```

**Exceptions**

* If `data` not dict-of-dicts → `TypeError`.

---

### `read() -> dict`

**Why:** Load INI into Python dict with lowercase keys.
**How:** Reads via ConfigParser, normalizes.

```python
cfg = ini.read()
print(cfg["server"]["host"])  # "127.0.0.1"
```

---

### `append(data)`

**Why:** Merge more sections/keys.
**How:** Shallow merge, writes back.

```python
ini.append({"server": {"debug": "true"}, "auth": {"enabled": "yes"}})
print(ini.read()["auth"]["enabled"])  # "yes"
```

**Exceptions**

* If `data` not dict-of-dicts → `TypeError`.

---

### `search(...)`

**Why:** Find keys/values by substring or regex.
**How:** Iterates dict.

```python
hits = list(ini.search(pattern="127"))
print(hits[0]["value"])  # "127.0.0.1"

hits = list(ini.search(key="port"))
print(hits[0]["value"])  # "8000"
```

---

# TomlFile (TOML) — Complete Guide

`TomlFile` manages TOML configs (requires Python 3.11+ `tomllib`, or `tomli/tomli-w`).

---

### Constructor

```python
from ADVfile_manager import TomlFile

t = TomlFile("cfg.toml", "example_data")
```

---

### Methods Overview

* `write(data)`
* `read() -> dict`
* `append(data)`
* `search(pattern=..., key=..., value=...)`

---

### `write(data)`

**Why:** Store dict as TOML.
**How:** Requires `tomli-w`.

```python
t.write({"app":{"name":"demo"}, "flags":{"x":True}})
```

**Exceptions**

* `ImportError` if no writer installed.

---

### `read() -> dict`

**Why:** Load TOML into Python dict.
**How:** Uses `tomllib`/`tomli`.

```python
cfg = t.read()
print(cfg["app"]["name"])  # "demo"
```

**Exceptions**

* `ImportError` if no TOML reader.

---

### `append(data)`

**Why:** Extend config safely.
**How:** Deep merge (dicts merged recursively).

```python
t.append({"flags":{"y":False}})
print(t.read()["flags"])  # {"x":True,"y":False}
```

**Exceptions**

* `TypeError` if root/data not dict.

---

### `search(...)`

**Why:** Explore TOML deeply.
**How:** Uses `_walk_jsonlike`.

```python
hits = list(t.search(pattern="demo"))
print(hits[0]["value"])  # "demo"
```


# XmlFile (XML) — Complete Guide

`XmlFile` wraps `xml.etree.ElementTree` for reading/writing/augmenting XML trees and running structured searches by **tag**, **attributes**, and **text**.

> **When to use:** configs, data exports, and interoperable machine documents where hierarchical structure matters.

---

## Constructor

```python
from ADVfile_manager import XmlFile
import xml.etree.ElementTree as ET

x = XmlFile("data.xml", "example_data")
```

* If `data.xml` already exists, its root is lazily loaded upon first `read()` (or automatically after `__init__` if your previous run wrote content).

---

## Methods Overview

* `write(data: Element | str) -> None`
* `read() -> xml.etree.ElementTree.Element`
* `append(data: Element | Sequence[Element]) -> None`
* `search(pattern=None, *, regex=False, case=False, tag=None, attr=None, value=None, limit=None) -> Iterator[dict]`

---

## `write(data)`

**Why:** Persist an XML document to disk.

**How:**

* Accepts either a fully-built `Element` (root) or a raw XML string.
* Writes with UTF-8 and XML declaration.
* Uses a temp file and `os.replace()` for atomicity.

```python
root = ET.Element("books")
root.append(ET.Element("book", attrib={"id": "1"}))
root.append(ET.Element("book", attrib={"id": "2"}))

x = XmlFile("books.xml", "example_data")
x.write(root)       # or: x.write('<books><book id="1"/></books>')
```

**Exceptions**

* `ET.ParseError` if given an invalid XML string.
* `OSError`/`IOError` on disk errors.

---

## `read() -> Element`

**Why:** Load the XML tree for programmatic access.

**How:**

* Parses the file and returns the **root `Element`**.
* Caches the tree root for this instance.

```python
root = x.read()
print(root.tag)    # "books"
for el in root.iter("book"):
    print(el.get("id"))
```

**Exceptions**

* `ET.ParseError` if file contents are malformed XML.
* `FileNotFoundError` if file missing.

---

## `append(data)`

**Why:** Add elements under the root in-place.

**How:**

* Accepts a single `Element` or a sequence of `Element` objects.
* Appends to current root and writes back.

```python
# Add one
x.append(ET.Element("book", attrib={"id": "3"}))

# Add many
more = [ET.Element("book", attrib={"id": "4"}),
        ET.Element("book", attrib={"id": "5"})]
x.append(more)
```

**Exceptions**

* `TypeError` if `data` is not an `Element` or a sequence of `Element`s.
* `ET.ParseError` if file unreadable; fix by re-writing valid root.

---

## `search(...)`

**Why:** Query XML by **tag**, **attributes**, **text**, or combined criteria.

**How (matching rules):**

* `tag="book"` → only elements with that tag.
* `attr={"id":"2"}` → element must have all listed attributes with exact values.
* `value="Some text"` → element’s **text** (stripped) must equal that value.
* `pattern="sale"` + `regex`/`case` → substring or regex match on element text.
* `limit=N` → stop after N hits.

**Yielded hit dict:**
`{"path": file_path, "value": element_text, "context": element}`

```python
# 1) Find by tag:
hits = list(x.search(tag="book"))
print(len(hits))

# 2) By attribute:
hits = list(x.search(tag="book", attr={"id": "3"}))
print(hits[0]["context"].tag, hits[0]["value"])  # 'book', element text ('' if None)

# 3) By exact text value:
chapter = XmlFile("chapter.xml", "example_data")
chapter.write('<chapter><title>Intro</title><title>Advanced</title></chapter>')
hits = list(chapter.search(tag="title", value="Intro"))
print(hits[0]["value"])  # "Intro"

# 4) By pattern (case-insensitive substring):
hits = list(chapter.search(tag="title", pattern="adv", case=False))
print([h["value"] for h in hits])  # ["Advanced"]

# 5) Combined + limit:
hits = list(x.search(tag="book", attr={"category":"Fiction"}, limit=2))
for h in hits:
    el = h["context"]
    print(el.tag, el.attrib)
```

**Exceptions**

* None specific from `search()`; ensure file reads/parsed successfully first.

---

# ExcelFile (XLSX via openpyxl) — Complete Guide

`ExcelFile` provides simple, safe interaction with `.xlsx` files via `openpyxl`:
**read/write/append** with dict rows (first row is header), multi-sheet support, and unified cell search.

> **When to use:** lightweight Excel export/import; incremental logging; merging sheets without pulling in heavy data tools.

---

## Dependencies

* Requires `openpyxl`:

```bash
pip install openpyxl
```

---

## Constructor

```python
from ADVfile_manager import ExcelFile

xls = ExcelFile("report.xlsx", "example_data", default_sheet="Sheet1")
```

* `default_sheet` is used when you don’t specify a `sheet=` in methods.
* If the workbook or sheet is missing, appropriate structures are created as needed.

---

## Methods Overview

* `read(*, sheet=None) -> List[Dict[str, Any]]`
* `write(rows, *, sheet=None) -> None`
* `append(row_or_rows, *, sheet=None) -> None`
* `search(pattern=None, *, regex=False, case=False, columns=None, value=None, sheet=None, limit=None) -> Iterator[dict]`

**Row shape:** every row is a `dict`, keys are column headers, values are cell values.
**Headers rule:** first row of the sheet is the header; created automatically when writing to an empty sheet.

---

## `write(rows, *, sheet=None)`

**Why:** Create/replace content in a sheet with **specified header order**.

**How:**

* Accepts a list/iterable of dict rows.
* Header order is inferred from the first occurrence of keys across rows.
* Clears/recreates target sheet, writes headers and rows.
* Uses temp+replace for atomicity.

```python
rows = [
    {"name": "Avi",  "score": 100},
    {"name": "Dana", "score":  90},
]
xls.write(rows, sheet="S1")

# Create a second sheet:
xls.write([{"name": "Noa", "score": 95}], sheet="S2")
```

**Exceptions**

* `ImportError` if `openpyxl` not installed.
* `TypeError` if `rows` are not dict-like.
* `OSError` on disk errors.

---

## `read(*, sheet=None) -> List[Dict[str, Any]]`

**Why:** Load sheet into a list of dict rows.

**How:**

* Reads headers from row 1.
* Creates dict per row (row 2..N).
* Coerces missing cells to `""` to keep stable column sets.

```python
data = xls.read(sheet="S1")
print(data)
# [{'name': 'Avi', 'score': 100}, {'name': 'Dana', 'score': 90}]
```

**Exceptions**

* `FileNotFoundError` if workbook not found.
* `KeyError` only if the sheet name resolution fails internally (we create sheets on write/append, but read expects a present sheet; ensure it exists).

---

## `append(row_or_rows, *, sheet=None)`

**Why:** Add rows to existing (or new) sheet while keeping header consistency.

**How:**

* Accepts dict or iterable of dicts.
* If the sheet is empty, headers inferred from the appended rows and written first.
* If headers exist, any missing keys in a particular row are written as `""`.

```python
# Append one row to S1:
xls.append({"name": "Lior", "score": 88}, sheet="S1")

# Append multiple rows to S2 (new column appears → blank where missing):
xls.append([{"name": "Omri", "score": 84},
            {"name": "Noa"}],            # 'score' missing → "" in that row
          sheet="S2")

print(xls.read(sheet="S2"))
# [{'name': 'Noa', 'score': 95}, {'name': 'Omri', 'score': 84}, {'name': 'Noa', 'score': ''}]
```

**Exceptions**

* `TypeError` if row is not dict or a list of dicts.
* `ImportError` if `openpyxl` missing.

---

## `search(pattern=None, *, regex=False, case=False, columns=None, value=None, sheet=None, limit=None)`

**Why:** Find cells by **substring/regex** or exact **value** across columns and sheets.

**How:**

* Internally calls `read(sheet=...)` → list of dict rows.
* `columns=["colA","colB"]` to limit search scope.
* `value=...` for exact value match (stringified), `pattern="..."` for substring/regex.
* Returns hit dicts:
  `{"path", "value", "row", "col", "sheet", "context"}`

```python
# Pattern search (case-insensitive by default):
hits = list(xls.search(pattern="noa", sheet="S2"))
print([(h["row"], h["col"], h["value"]) for h in hits])

# Exact-match value search:
hits = list(xls.search(value=90, columns=["score"], sheet="S1"))
print(hits[0]["value"])  # "90" or 90 depending on cell typing → we stringify for comparison

# Regex (case-sensitive):
hits = list(xls.search(pattern=r"^A..$", regex=True, case=True, columns=["name"], sheet="S1"))
for h in hits:
    print(h["row"], h["col"], h["value"])

# Limit results:
hits = list(xls.search(pattern="o", sheet="S2", limit=2))
print(len(hits))  # 2
```

**Exceptions**

* None specific beyond what `read()` might raise if file/sheet invalid.

---

## End-to-End Example (Excel + Backups + Search)

```python
from ADVfile_manager import ExcelFile

x = ExcelFile("grades.xlsx", "example_data", default_sheet="ClassA")

# Write a fresh sheet:
x.write([{"name":"Avi", "score": 100},
         {"name":"Dana","score":  90}])

# Backup before risky changes:
bpath = x.backup()

# Append rows:
x.append({"name":"Noa","score":95})
x.append([{"name":"Lior","score":88},{"name":"Omri"}])  # 'score' missing -> ""

# Search:
print("Find 90:", list(x.search(value=90, columns=["score"])))
print("Names with 'o':", [h["value"] for h in x.search(pattern="o", columns=["name"])])

# Restore if needed:
# x.restore(bpath)
```

# Async A\* Classes — Complete Guide

The async façade mirrors the sync API using `asyncio.to_thread(...)`. You get the same semantics, but non-blocking. Each async class corresponds 1:1 to its sync sibling:

* `ATextFile` ↔ `TextFile`
* `AJsonFile` ↔ `JsonFile`
* `ACsvFile` ↔ `CsvFile`
* `AYamlFile` ↔ `YamlFile`
* `AIniFile` ↔ `IniFile`
* `ATomlFile` ↔ `TomlFile`
* `AXmlFile` ↔ `XmlFile`
* `AExcelFile` ↔ `ExcelFile`

All provide:

* `await aread(...)`
* `await awrite(...)`
* `await aappend(...)`
* `await asearch(...)` → returns a **list** of hits (not an iterator)
* `async with ...` context manager (auto-backup on enter, restore on exception, clear cache on exit — same as sync)

> ⚠️ **Notes / Exceptions**
> • You must run under an event loop (e.g., `pytest-asyncio`, `asyncio.run(...)`).
> • Exceptions mirror the sync versions (e.g., `FileNotFoundError`, `ET.ParseError`, `ImportError`).

---

## ATextFile

### Constructor

```python
from ADVfile_manager import ATextFile

t = ATextFile("notes.txt", "example_data")
```

### Methods & Examples

#### `await awrite(text: str) -> None`

```python
await t.awrite("hello async")
```

#### `await aread() -> str`

```python
content = await t.aread()
print(content)
```

#### `await aappend(text: str) -> None`

```python
await t.aappend("another line")
```

#### `await asearch(pattern: str, *, regex=False, case=False, limit=None) -> list[dict]`

```python
hits = await t.asearch(pattern="hello")
print(len(hits), hits[0]["line"], hits[0]["value"])
```

#### `async with ATextFile(...)`

```python
try:
    async with ATextFile("draft.txt", "example_data") as f:
        await f.awrite("temp edit")
        raise RuntimeError("boom")
except RuntimeError:
    pass
# file auto-restored from backup; cache cleared
```

---

## AJsonFile

### Constructor

```python
from ADVfile_manager import AJsonFile

j = AJsonFile("data.json", "example_data")
```

### Methods & Examples

#### `await awrite(obj: Any) -> None`

```python
await j.awrite({"users": [{"id": 1}]})
```

#### `await aread() -> Any`

```python
obj = await j.aread()
print(obj["users"][0]["id"])
```

#### `await aappend(data: Any) -> None`

* list-root → append/extend
* dict-root → shallow `update(...)`
* raises `TypeError` if wrong type for dict-root

```python
# dict root
await j.awrite({"users": [{"id": 1}]})
await j.aappend({"active": True})     # ok
# wrong type:
try:
    await j.aappend(["not", "a", "dict"])  # raises TypeError on dict root
except TypeError:
    ...
```

#### `await asearch(pattern=None, *, key=None, value=None, regex=False, case=False, limit=None) -> list[dict]`

```python
await j.awrite({"users":[{"id":1, "name":"Dana"},{"id":2,"name":"Noa"}], "active": True})

# 1) by key name + pattern over value
hits = await j.asearch(key="name", pattern="no", case=False)
print([h["value"] for h in hits])  # ['Noa']

# 2) by exact value anywhere
hits = await j.asearch(value=True)
print(hits)  # at least one hit for "active": True
```

#### `async with AJsonFile(...)`

```python
try:
    async with AJsonFile("risky.json", "example_data") as jf:
        await jf.awrite({"state": "bad"})
        raise RuntimeError("oops")
except RuntimeError:
    pass
# restored from latest backup if existed
```

---

## ACsvFile

```python
from ADVfile_manager import ACsvFile

c = ACsvFile("table.csv", "example_data")
await c.awrite([{"name":"Avi","age":30},{"name":"Dana","age":25}])  # writes header
await c.aappend({"name":"Noa"})   # 'age' missing -> "" in file

rows = await c.aread()
print(rows)

hits = await c.asearch(pattern="avi", case=False, columns=["name"])
print(hits[0]["row"], hits[0]["col"], hits[0]["value"])
```

---

## AYamlFile

> Requires `pyyaml` (`pip install pyyaml`)

```python
from ADVfile_manager import AYamlFile

y = AYamlFile("conf.yaml","example_data")
await y.awrite({"app":{"name":"demo"},"features":["a"]})
await y.aappend({"features":["b"]})  # shallow update for dict
hits = await y.asearch(key="app")
print(hits[0]["value"])
```

---

## AIniFile

```python
from ADVfile_manager import AIniFile

ini = AIniFile("settings.ini","example_data")
await ini.awrite({"Server":{"Host":"127.0.0.1","Port":"8000"}})
await ini.aappend({"Server":{"Debug":"true"}})

cfg = await ini.aread()
print(cfg["server"]["debug"])  # 'true' (lower-cased keys in memory)

hits = await ini.asearch(key="host")
print(hits[0]["value"])  # "127.0.0.1"
```

---

## ATomlFile

> Reading: Python 3.11+ (`tomllib`) or `tomli`; Writing: `tomli-w`

```python
from ADVfile_manager import ATomlFile

t = ATomlFile("cfg.toml","example_data")
await t.awrite({"app":{"name":"demo","ver":1}, "flags":{"x":True}})
await t.aappend({"flags":{"y":False}})   # deep-merge dicts
hits = await t.asearch(key="y", value=False)
print(hits)
```

---

## AXmlFile

```python
from ADVfile_manager import AXmlFile
import xml.etree.ElementTree as ET

x = AXmlFile("data.xml","example_data")
root = ET.Element("books")
root.append(ET.Element("book", attrib={"id":"1"}))
await x.awrite(root)

await x.aappend(ET.Element("book", attrib={"id":"2"}))

hits = await x.asearch(tag="book", attr={"id":"2"})
print(hits[0]["context"].tag, hits[0]["value"])   # 'book', ''
```

---

## AExcelFile

> Requires `openpyxl`

```python
from ADVfile_manager import AExcelFile

xls = AExcelFile("grades.xlsx","example_data", default_sheet="ClassA")
await xls.awrite([{"name":"Avi","score":100},{"name":"Dana","score":90}])
await xls.aappend({"name":"Noa"})  # missing 'score' -> "" in file

rows = await xls.aread()
print(rows[-1])   # {'name': 'Noa', 'score': ''}

hits = await xls.asearch(pattern="no", columns=["name"])
print([(h["row"], h["value"]) for h in hits])
```

---

# Backups, Restore & Context Safety — Deep Dive

These features live in the **base `File`** class and are inherited by all concrete types.

## Why

* **Rollback**: if a write goes wrong, you can restore the last known good state.
* **Transactional editing**: context manager protects against partial writes.
* **Automation**: non-retained (“ephemeral”) backups are auto-cleared at interpreter exit.

## API & Examples

### `backup() -> str`

Create a timestamped `.bak` under `<path>/backups`.

```python
txt = TextFile("file.txt","example_data")
txt.write("v1")
b = txt.backup()
print("Backup:", b)
```

**Raises:** `FileNotFoundError` if the source file doesn’t exist.

---

### `list_backups() -> list[str]`

Sorted (oldest → newest) absolute paths.

```python
for b in txt.list_backups():
    print(b)
```

---

### `restore(backup_path: str | None = None) -> str`

Restore from a specific backup path, or the **latest** if `None`.

```python
# latest
txt.restore()

# specific
backups = txt.list_backups()
txt.restore(backups[-2])
```

**Raises:** `FileNotFoundError` if no backups exist.

---

### `clear_backups() -> int`

Delete all .bak files for this file; returns count.

```python
removed = txt.clear_backups()
print("Removed backups:", removed)
```

---

### Context Manager Safety (`with ... as f:`)

* **On enter**: auto-backup (if `keep_backup=True`, the default).
* **On exception**: auto-restore from latest backup.
* **On exit**: cache cleared.
* **Ephemeral**: if `keep_backup=False`, backups are cleared on exit.

```python
# default transactional safety
try:
    with JsonFile("conf.json","example_data") as jf:
        jf.write({"ok": 1})
        raise RuntimeError()
except RuntimeError:
    pass

# ephemeral backups (no retention)
with TextFile("temp.txt","example_data")(keep_backup=False) as f:
    f.write("temporary")
# backups auto-cleared here
```

---

# Global Utilities

### `set_exit_cleanup(enabled: bool) -> None`

Enable/disable automatic cleanup of **ephemeral** backups on interpreter exit. Default: **enabled**.

```python
from ADVfile_manager import set_exit_cleanup
set_exit_cleanup(False)  # disable auto cleanup
set_exit_cleanup(True)   # enable again
```

---

### `cleanup_backups_for_all() -> int`

Manually clear backups for all registered **ephemeral** files; returns total removed.

```python
from ADVfile_manager import cleanup_backups_for_all
removed = cleanup_backups_for_all()
print("Removed ephemeral backups:", removed)
```

---

# Unified `search(...)` Cheatsheet

All file classes implement the same signature. Not all parameters apply to every format, but the interface is consistent:

```python
search(
  pattern: str | None = None,
  *,
  regex: bool = False,
  case: bool = False,
  key: str | None = None,       # mapping key / field (JSON/YAML/INI/TOML)
  value: Any = None,            # exact value match
  columns: Sequence[str] | None = None,  # CSV/Excel columns
  tag: str | None = None,       # XML element tag
  attr: dict[str,str] | None = None,     # XML attributes
  sheet: str | None = None,     # Excel sheet name
  limit: int | None = None,     # max hits
) -> Iterator[dict]
```

* **TextFile**: `pattern`, `regex`, `case`, `limit`
* **JsonFile/YamlFile/TomlFile**: `pattern`, `key`, `value`, `regex`, `case`, `limit`
* **IniFile**: `pattern`, `key`, `value`, `regex`, `case`, `limit` (sections/keys case-normalized in memory)
* **CsvFile**: `pattern`, `columns`, `value`, `regex`, `case`, `limit`
* **XmlFile**: `tag`, `attr`, `pattern`, `value`, `regex`, `case`, `limit`
* **ExcelFile**: `sheet`, `columns`, `pattern`, `value`, `regex`, `case`, `limit`

**Returned hit dict** may contain:
`{"path","value","line","row","col","sheet","context", ...}`
(Only relevant keys are set; others are `None`.)

---

# Installation (v1.3.0)

**Base install (core formats: Text/JSON/CSV/INI/XML):**

```bash
pip install ADVfile_manager
```

**YAML support:**

```bash
pip install pyyaml
```

**TOML support:**

* Read (Python ≥3.11): built-in `tomllib`
* Read (Python 3.8–3.10):

  ```bash
  pip install tomli
  ```
* Write (all versions):

  ```bash
  pip install tomli-w
  ```

**Excel support:**

```bash
pip install openpyxl
```

**Async testing helpers (optional for tests):**

```bash
pip install pytest pytest-asyncio
```

**Python version:** 3.8+ recommended.

---

# Comparison Tables

## ADVfile\_manager vs. Popular Libraries

| Capability / Tool              | **ADVfile\_manager**       | pathlib (stdlib) | os/shutil (stdlib) | pandas              | PyYAML / ruamel.yaml | configparser | tomli/tomllib + tomli-w | xml.etree  | openpyxl |
| ------------------------------ | -------------------------- | ---------------- | ------------------ | ------------------- | -------------------- | ------------ | ----------------------- | ---------- | -------- |
| Unified API across formats     | ✅                          | ❌                | ❌                  | ❌                   | ❌                    | ❌            | ❌                       | ❌          | ❌        |
| Text                           | ✅                          | Path ops only    | File ops only      | DF-centric          | ❌                    | ❌            | ❌                       | ❌          | ❌        |
| JSON                           | ✅                          | ❌                | ❌                  | via read\_json (DF) | ❌                    | ❌            | ❌                       | ❌          | ❌        |
| CSV                            | ✅                          | ❌                | ❌                  | ✅ (heavy)           | ❌                    | ❌            | ❌                       | ❌          | ❌        |
| YAML                           | ✅ (PyYAML)                 | ❌                | ❌                  | ❌                   | ✅                    | ❌            | ❌                       | ❌          | ❌        |
| INI                            | ✅                          | ❌                | ❌                  | ❌                   | ❌                    | ✅            | ❌                       | ❌          | ❌        |
| TOML                           | ✅ (tomli/tomllib, tomli-w) | ❌                | ❌                  | ❌                   | ❌                    | ❌            | ✅                       | ❌          | ❌        |
| XML                            | ✅                          | ❌                | ❌                  | ❌                   | ❌                    | ❌            | ❌                       | ✅          | ❌        |
| Excel                          | ✅ (openpyxl)               | ❌                | ❌                  | ✅ (heavy)           | ❌                    | ❌            | ❌                       | ❌          | ✅        |
| Atomic writes (temp + replace) | ✅                          | ❌                | ❌                  | depends             | n/a                  | n/a          | n/a                     | depends    | depends  |
| Backups / Restore              | ✅                          | ❌                | ❌                  | ❌                   | ❌                    | ❌            | ❌                       | ❌          | ❌        |
| Context manager auto-restore   | ✅                          | ❌                | ❌                  | ❌                   | ❌                    | ❌            | ❌                       | ❌          | ❌        |
| Unified search() API           | ✅                          | ❌                | ❌                  | ❌                   | ❌                    | ❌            | ❌                       | ❌          | ❌        |
| Async API                      | ✅                          | ❌                | ❌                  | ❌                   | ❌                    | ❌            | ❌                       | ❌          | ❌        |
| Weight / deps                  | Light, opt-in              | Very light       | Very light         | Heavy               | Light                | Very light   | Light                   | Very light | Medium   |

**Bottom line:** ADVfile\_manager is the only one that **ties everything together** with one consistent, safety-first API (I/O + backups + search + async). Use pandas only if you *need* data analysis.

---

## ADVfile\_manager vs. *Your* `ATmulti_file_handler` (hypothetical prior tool)

| Area                      | **ADVfile\_manager (1.3.0)**                 | ATmulti\_file\_handler                       |
| ------------------------- | -------------------------------------------- | -------------------------------------------- |
| Formats                   | Text, JSON, CSV, YAML, INI, TOML, XML, Excel | Typically fewer formats (often no Excel/XML) |
| Unified search            | ✅ single signature across all                | ❌/Partial (per-format helpers)               |
| Context manager safety    | ✅ auto-backup + restore                      | Partial or manual                            |
| Async façade              | ✅ A\* classes for all formats                | Partial / none                               |
| Ephemeral backups cleanup | ✅ (atexit + manual)                          | ❌                                            |
| Excel handling            | ✅ header-first, robust append with blanks    | ❌/Partial                                    |
| XML attribute/tag search  | ✅                                            | ❌/Partial                                    |
| Tests coverage            | Extensive (sync + async)                     | Partial                                      |
| Docs (this README)        | Deep, per-method examples                    | Limited                                      |

**Upgrade value:** modernized async API, broader format coverage, unified search, consistent safety features, and stronger testing.

---

# Sample Project — End-to-End

A realistic mini-pipeline that touches multiple formats, uses backups, context safety, unified search, and async where useful.

```python
"""
Goal:
- Load settings (INI + TOML)
- Read a source CSV, enrich from JSON reference data
- Emit results to both JSON and Excel
- Provide quick search queries across outputs
- Use transactional safety + backups
- Demonstrate async steps
"""

import asyncio
from ADVfile_manager import (
    IniFile, TomlFile, JsonFile, CsvFile, ExcelFile,
    AJsonFile, AExcelFile, set_exit_cleanup
)

BASE = "project_data"

def load_settings():
    ini = IniFile("settings.ini", BASE)
    if not ini.status:
        ini.write({"Server":{"Host":"127.0.0.1","Port":"8000"}})
    cfg = ini.read()

    toml = TomlFile("feature_flags.toml", BASE)
    try:
        flags = toml.read()
    except Exception:
        flags = {"features":{"excel_export": True}}
        toml.write(flags)

    return cfg, flags

def enrich_rows_from_json(rows):
    ref = JsonFile("ref.json", BASE)
    if not ref.status:
        ref.write({"vip_users": ["Avi"]})
    vip_list = ref.read().get("vip_users", [])
    out = []
    for r in rows:
        r = dict(r)
        r["vip"] = r.get("name") in vip_list
        out.append(r)
    return out

def process_sync():
    # 1) Read CSV
    src = CsvFile("source.csv", BASE)
    if not src.status:
        src.write([{"name":"Avi","score":100},{"name":"Dana","score":90},{"name":"Noa","score":95}])
    rows = src.read()

    # 2) Enrich with JSON reference
    enriched = enrich_rows_from_json(rows)

    # 3) Transactional write with backup
    out_json = JsonFile("result.json", BASE)
    with out_json as jf:
        jf.write({"rows": enriched})

    # 4) Search: find VIP
    hits = list(out_json.search(pattern="True", key="vip"))
    print("VIP hits:", hits)

async def async_exports():
    # Async Excel export
    aex = AExcelFile("result.xlsx", BASE, default_sheet="Report")
    await aex.awrite([{"name":"Avi","score":100,"vip":True},
                      {"name":"Dana","score":90,"vip":False},
                      {"name":"Noa","score":95,"vip":False}])
    # Append
    await aex.aappend({"name":"Omri","score":84,"vip":False})
    # Search by pattern
    hits = await aex.asearch(pattern="o", columns=["name"])
    print("Excel pattern hits:", [(h["row"], h["value"]) for h in hits])

def main():
    set_exit_cleanup(True)

    cfg, flags = load_settings()
    print("INI:", cfg)
    print("Flags:", flags)

    process_sync()
    asyncio.run(async_exports())

if __name__ == "__main__":
    main()
```

**What this shows:**

* INI + TOML loading and writing.
* JSON ref data & CSV ingestion.
* Transactional JSON write with context manager.
* Async Excel write/append/search.
* Unified search queries (`pattern`, `key`, `columns`, …).

---

# Roadmap (next iterations)

Only the items you requested:

* 🔐 **File encryption/decryption**
  Per-file opt-in encryption (likely AES-GCM) with key material management hooks, seamless within `read`/`write`/`append` and transparent backups.

* 🧾 **Hash-based change detection**
  Maintain and expose SHA-256 (and optionally MD5) digests; detect external changes and optionally auto-invalidate cache or raise on stale reads.
