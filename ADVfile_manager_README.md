
# ADVfile\_manager

**Author:** Avi Twil
**Repo:** [https://github.com/avitwil/ADVfile\_manager](https://github.com/avitwil/ADVfile_manager)

Unified file abstractions for Python with **safe writes, caching, backups, context managers, and exit-time cleanup** — all under a consistent API for **Text**, **JSON**, **CSV**, **YAML**, **INI**, **TOML**, **XML**, and **Excel** files. Includes **unified search** across formats and **async variants** of all classes.

* `TextFile` – read/write/append; line tools: `lines()`, `read_line()`.
* `JsonFile` – dict/list roots, `append()`, `get_item()`, `items()`.
* `CsvFile` – `DictReader`/`DictWriter`, `read_row()`, `rows()`, column order control.
* `YamlFile` – like `JsonFile` (requires `PyYAML`).
* `IniFile` – INI via `configparser`, dict-like write/append, search by section/key/value.
* `TomlFile` – TOML read/write/append (requires `tomli`/`tomli-w` or `tomllib`).
* `XmlFile` – XML via `xml.etree.ElementTree`, append elements, search by tag/attrs/text.
* `ExcelFile` – Excel via `openpyxl`, header-based rows, multi-sheet support.

The base class `File` adds **backups**, **restore**, **retention helpers**, **human-readable sizes**, **cache control**, a **context manager** that can auto-backup & restore on error, and **exit-time cleanup** for ephemeral backups. Each class implements a **unified `search()`** signature tailored to the format. Async wrappers (`ATextFile`, `AJsonFile`, …) expose `aread/awrite/aappend/asearch` and async context management.

---

## Table of Contents

* [Why ADVfile\_manager?](#why-advfile_manager)
* [Installation](#installation)
* [Quick Start](#quick-start)
* [ English Manual](./USAGE.md)
* [ מדריך בעברית](hebrew_guid.md)
* [Detailed Usage](#detailed-usage)

  * [Common Base: `File`](#common-base-file)
  * [`TextFile`](#textfile)
  * [`JsonFile`](#jsonfile)
  * [`CsvFile`](#csvfile)
  * [`YamlFile`](#yamlfile)
  * [`IniFile`](#inifile)
  * [`TomlFile`](#tomlfile)
  * [`XmlFile`](#xmlfile)
  * [`ExcelFile`](#excelfile)
  * [Unified Search (All Formats)](#unified-search-all-formats)
  * [Async API (A\* Classes)](#async-api-a-classes)
* [Backups, Retention & Exit Cleanup](#backups-retention--exit-cleanup)
* [Context Manager Safety](#context-manager-safety)
* [Advanced Notes](#advanced-notes)
* [Full Examples](#full-examples)
* [Feature-by-Feature: Explanation & Examples](#feature-by-feature-explanation--examples)
* [License](#license)

---

## Why ADVfile\_manager?

Typical file code ends up as a mix of ad-hoc helpers and repeated patterns.
**ADVfile\_manager** provides one consistent interface across many formats:

* **Safer writes**: temp file + atomic `os.replace()` where applicable.
* **Backups**: timestamped `.bak`; list, restore, and clear; exit-time cleanup if ephemeral.
* **Context safety**: `with` blocks can auto-backup and auto-restore on exceptions.
* **Unified search**: consistent `search()` signature per format.
* **Streaming helpers**: iterate lines/rows/items without loading everything.
* **Async Facade**: `aread/awrite/aappend/asearch`, `async with`.
* **Cache control**: in-memory cache with `clear_cache()`.

---

## Installation

```bash
pip install ADVfile_manager
```

Optional extras:

```bash
# YAML support
pip install pyyaml

# TOML reading on <3.11 and writing
pip install tomli tomli-w

# Excel support
pip install openpyxl
```

From source:

```bash
git clone https://github.com/avitwil/ADVfile_manager
cd ADVfile_manager
pip install -e .
```

---

# 🔎 Comparison: ADVfile\_manager vs Similar Tools

| Feature / Tool          | **ADVfile\_manager**                          | \[pathlib (stdlib)] | \[os/shutil (stdlib)] | \[pandas]        | \[ruamel.yaml]/\[PyYAML] |
| ----------------------- | --------------------------------------------- | ------------------- | --------------------- | ---------------- | ------------------------ |
| **Supported formats**   | TXT, JSON, CSV, YAML, INI, TOML, XML, Excel   | Paths only          | FS operations         | CSV/Excel/JSON/… | YAML only                |
| **Unified API**         | ✅ One interface across all formats            | ❌                   | ❌                     | ❌                | ❌                        |
| **Read/Write/Append**   | ✅ Consistent methods                          | Manual              | Manual                | ✅ DF ops         | ✅ YAML only              |
| **Cache system**        | ✅ In-memory + `clear_cache`                   | ❌                   | ❌                     | DF cache         | ❌                        |
| **Line/Row helpers**    | ✅ `lines/read_line`, `read_row/rows`, `items` | ❌                   | ❌                     | ✅ via DF         | ❌                        |
| **Backup & restore**    | ✅ `.bak`, restore, retention helpers          | ❌                   | ❌                     | ❌                | ❌                        |
| **Atomic writes**       | ✅ temp + `os.replace()`                       | ❌                   | ❌                     | ❌                | ❌                        |
| **Human-readable size** | ✅ `get_size_human()`                          | ❌                   | ❌                     | ❌                | ❌                        |
| **Context safety**      | ✅ auto-backup + restore-on-error              | ❌                   | ❌                     | ❌                | ❌                        |
| **Exit cleanup**        | ✅ atexit cleanup for ephemeral backups        | ❌                   | ❌                     | ❌                | ❌                        |
| **Unified search()**    | ✅ All formats                                 | ❌                   | ❌                     | Partial          | ❌                        |
| **Async variants**      | ✅ A\* classes (aread/awrite/aappend/asearch)  | ❌                   | ❌                     | ❌                | ❌                        |
| **Dependencies**        | Optional per-format                           | None                | None                  | Heavy            | Yes (YAML)               |

---

## 🎯 Example Use Cases

* **Config management**: JSON/YAML/TOML/INI safely edited with rollback.
* **Logs & reports**: append text/CSV rows with automatic backups/retention.
* **Transactional edits**: wrap risky edits in a context manager to auto-restore on failure.
* **Cross-format tools**: same patterns across TXT/CSV/Excel/XML/etc.
* **Search**: unify searching keys/values/cells/tags/text with one method.

---

## Quick Start

```python
from ADVfile_manager import TextFile, JsonFile, CsvFile, YamlFile

# Text
txt = TextFile("notes.txt", "data")
txt.write("first line")
txt.append("second line")
print(txt.read_line(2))     # "second line"
for i, line in txt.lines():
    print(i, line)

# JSON (dict root)
j = JsonFile("config.json", "data")
j.write({"users": [{"id": 1}]})
j.append({"active": True})
print(j.get_item("active")) # True

# CSV
c = CsvFile("table.csv", "data")
c.write([{"name":"Avi","age":30},{"name":"Dana","age":25}], fieldnames=["name","age"])
c.append({"name":"Noa","age":21})
print(c.read_row(2))        # {"name":"Dana","age":"25"}
for idx, row in c.rows():
    print(idx, row)

# YAML
y = YamlFile("config.yaml", "data")
y.write({"app":{"name":"demo"}, "features":["a"]})
y.append({"features":["b"]})
print(y.get_item("app"))
```

---

## Detailed Usage

### Common Base: `File`

Shared across all file types:

* `read()`, `write(data)`, `append(data)`
* `clear_cache()` — clear in-memory cache so next `read()` hits disk
* `get_size()` / `get_size_human()`
* Backups: `backup()`, `list_backups()`, `restore(backup_path=None)`, `clear_backups()`
* Context manager: `with File(...)(keep_backup=True) as f: ...`
* Exit cleanup (module-level):

  * `set_exit_cleanup(enabled: bool)`
  * `cleanup_backups_for_all()`

**Constructor**

```python
File(
  file_name: str,
  file_path: str | pathlib.Path | None = None,  # defaults to CWD
  keep_backup: bool = True                      # ephemeral backups if False
)
```

---

### `TextFile`

* `lines()` → generator of `(line_no, text)`
* `read_line(n)` → 1-based line access

```python
txt = TextFile("example.txt", "data")
txt.write("Hello")
txt.append("World")
print(txt.read())           # "Hello\nWorld"
print(txt.read_line(2))     # "World"
for i, line in txt.lines():
    print(i, line)
```

---

### `JsonFile`

* `append()` – list: append/extend; dict: shallow update
* `get_item(index_or_key)` – 1-based index for lists; key for dicts
* `items()` – iterate `(index,item)` or `(key,value)`

```python
j = JsonFile("conf.json", "data")
j.write({"users":[{"id":1}]})
j.append({"active": True})
print(j.get_item("active"))          # True

jl = JsonFile("list.json", "data")
jl.write([{"id":1}])
jl.append([{"id":2},{"id":3}])
print(jl.get_item(2))                # {"id":2}
for i, item in jl.items():
    print(i, item)
```

---

### `CsvFile`

* `write(data, fieldnames=None)` — control column order
* `read_row(n)` — 1-based rows
* `rows()` — generator `(row_no, row_dict)`

```python
c = CsvFile("table.csv", "data")
c.write([{"name":"Avi","age":30},{"name":"Dana","age":25}], fieldnames=["name","age"])
c.append({"name":"Noa","age":21})
print(c.read_row(2))                    # {"name":"Dana","age":"25"}
for i, row in c.rows():
    print(i, row)
```

---

### `YamlFile`

(Requires `PyYAML`)

* `append()` – list append/extend; dict shallow update
* `get_item(index_or_key)`, `items()`

```python
y = YamlFile("config.yaml", "data")
y.write({"app":{"name":"demo"}, "features":["a"]})
y.append({"features":["b"]})
print(y.get_item("app"))
for k, v in y.items():
    print(k, v)
```

---

### `IniFile`

* INI via `configparser`
* `write()` & `append()` with nested dicts: `{section: {key: value}}`

```python
from ADVfile_manager import IniFile

ini = IniFile("settings.ini", "data")
ini.write({"server": {"host": "127.0.0.1", "port": 8000}})
ini.append({"server": {"debug": "true"}, "auth": {"enabled": "yes"}})
cfg = ini.read()
print(cfg["server"]["host"])
```

---

### `TomlFile`

* Reads with `tomllib` (3.11+) or `tomli`
* Writes with `tomli-w`

```python
from ADVfile_manager import TomlFile

toml = TomlFile("config.toml", "data")
toml.write({"app": {"name": "demo"}, "features": {"b": True}})
print(toml.read()["app"]["name"])
toml.append({"features": {"c": 123}})
```

---

### `XmlFile`

* XML via `xml.etree.ElementTree`
* `write()` accepts an `Element` or XML string
* `append()` adds child Element(s)

```python
from ADVfile_manager import XmlFile
import xml.etree.ElementTree as ET

xmlf = XmlFile("books.xml", "data")
root = ET.Element("books")
root.append(ET.Element("book", attrib={"id": "1"}))
xmlf.write(root)

# Append another
xmlf.append(ET.Element("book", attrib={"id": "2"}))
print(ET.tostring(xmlf.read(), encoding="unicode"))
```

---

### `ExcelFile`

(Requires `openpyxl`)

* Header in the first row; reads into `List[Dict]`
* `write`, `append` rows (dicts); supports `sheet` and default sheet

```python
from ADVfile_manager import ExcelFile

xl = ExcelFile("report.xlsx", "data", default_sheet="Sheet1")
xl.write([{"name":"Avi","score":95},{"name":"Dana","score":88}])
xl.append({"name":"Noa","score":92})
rows = xl.read()
print(rows[0]["name"])
```

---

### Unified Search (All Formats)

Every class implements:

```python
search(
    pattern: Optional[str] = None,
    *,
    regex: bool = False,
    case: bool = False,
    key: Optional[str] = None,
    value: Any = None,
    columns: Optional[Sequence[str]] = None,
    tag: Optional[str] = None,
    attr: Optional[Dict[str, str]] = None,
    sheet: Optional[str] = None,
    limit: Optional[int] = None,
) -> Iterator[Dict[str, Any]]
```

Returned **hit** (dict) has keys like:
`path`, `value`, `line`, `row`, `col`, `sheet`, `context` (some may be `None`).

**Examples**

```python
# Text
for hit in TextFile("log.txt", "data").search("error", case=False):
    print(hit["path"], hit["value"])

# JSON by key/pattern
for hit in JsonFile("conf.json","data").search(pattern="admin", key="role"):
    print(hit)

# CSV (restrict to columns)
for hit in CsvFile("users.csv","data").search(pattern="@example.com", columns=["email"]):
    print(hit["row"], hit["col"], hit["value"])

# YAML exact value
for h in YamlFile("cfg.yaml","data").search(value=True):
    print(h)

# INI by key
for h in IniFile("settings.ini","data").search(key="debug", value="true"):
    print(h["context"])

# TOML by pattern
for h in TomlFile("app.toml","data").search(pattern="demo", regex=False):
    print(h)

# XML by tag/attrs
for h in XmlFile("books.xml","data").search(tag="book", attr={"id":"2"}):
    print(h["context"])

# Excel sheet & columns
for h in ExcelFile("report.xlsx","data").search(pattern="Avi", sheet="Sheet1", columns=["name"]):
    print(h["row"], h["col"], h["value"])
```

---

### Async API (A\* Classes)

Each format has an async variant: `ATextFile`, `AJsonFile`, `ACsvFile`, `AYamlFile`, `AIniFile`, `ATomlFile`, `AXmlFile`, `AExcelFile`.

Async methods:

* `aread()`, `awrite()`, `aappend()`, `asearch()` (returns list of hits)
* Async context: `async with ATextFile(...) as f: ...`

```python
import asyncio
from ADVfile_manager import ATextFile, AJsonFile, AExcelFile

async def main():
    async with ATextFile("notes.txt","data") as t:
        await t.awrite("hello")
        await t.aappend("world")
        print(await t.aread())

    aj = AJsonFile("conf.json","data")
    await aj.awrite({"users":[{"name":"Avi"}]})
    hits = await aj.asearch(pattern="Avi")
    print(hits)

    ax = AExcelFile("report.xlsx","data")
    await ax.awrite([{"name":"Avi","score":95}])
    res = await ax.asearch(pattern="Avi", columns=["name"])
    print(res)

asyncio.run(main())
```

---

## Backups, Retention & Exit Cleanup

* **Create**: `path = f.backup()` → `backups/<file>.<YYYYMMDD_HHMMSS_micro>.bak`
* **List**: `f.list_backups()` → sorted oldest→newest
* **Restore**:

  * latest: `f.restore()`
  * specific: `f.restore(path)`
* **Clear**: `f.clear_backups()` returns count removed
* **Ephemeral backups**: set `keep_backup=False` on the instance (or via `obj(keep_backup=False)`); they are auto-removed at interpreter exit.
* **Global controls**:

  ```python
  from ADVfile_manager import set_exit_cleanup, cleanup_backups_for_all
  set_exit_cleanup(True)              # enable (default)
  set_exit_cleanup(False)             # disable
  removed = cleanup_backups_for_all() # manual cleanup now
  ```

---

## Context Manager Safety

* `with` can **auto-backup on enter** (default `keep_backup=True`).
* On **exception**, file is **restored** from the latest backup.
* Cache is **always cleared** on exit.

```python
with TextFile("draft.txt", "data") as f:
    f.write("transactional edit")
    raise RuntimeError("oops!")  # file auto-restores to state at enter
```

Ephemeral within context:

```python
with TextFile("temp.txt", "data")(keep_backup=False) as f:
    f.write("temporary content")
# backups cleared on exit
```

---

## Advanced Notes

* **Atomic writes**: we use temp files + `os.replace()` where appropriate.
* **Pathlib**: `file_path` can be `str` or `pathlib.Path`.
* **Caching**: `read()` populates `self.content`. Call `clear_cache()` after external changes.
* **Append semantics**:

  * Text → newline if non-empty
  * JSON/YAML/TOML → dict: shallow update; list: append/extend
  * CSV/Excel → add row(s)
  * XML → append elements under root
  * INI → merge sections/keys
* **Excel**: first row is header; empty cells read as empty strings.
* **Python**: 3.8+ recommended; TOML writing needs `tomli-w`.

---

## Full Examples

### 1) Text + Backups + Restore Specific

```python
from ADVfile_manager import TextFile

txt = TextFile("example.txt", "example_data")
txt.write("v1"); b1 = txt.backup()
txt.write("v2"); b2 = txt.backup()
txt.write("v3"); b3 = txt.backup()

print("Backups:", txt.list_backups())
txt.restore(b2)
print("Restored content:", txt.read())  # "v2"
```

### 2) Ephemeral Backups + Exit Cleanup

```python
from ADVfile_manager import TextFile, cleanup_backups_for_all, set_exit_cleanup

with TextFile("temp.txt", "example_data")(keep_backup=False) as f:
    f.write("temporary content")

# Manual cleanup (or rely on atexit):
deleted = cleanup_backups_for_all()
print("Deleted backup files:", deleted)

# Disable/Enable the global atexit cleanup
set_exit_cleanup(False)
set_exit_cleanup(True)
```

### 3) CSV with Column Order Control

```python
from ADVfile_manager import CsvFile

rows = [{"name":"Avi","age":30},{"name":"Dana","age":25}]
c = CsvFile("table.csv", "example_data")
c.write(rows, fieldnames=["name","age"])
c.append({"name":"Noa","age":21})

print(c.read_row(2))      # {"name":"Dana","age":"25"}
for i, row in c.rows():
    print(i, row)
```

### 4) JSON/YAML/TOML Dict & List Behaviors

```python
from ADVfile_manager import JsonFile, YamlFile, TomlFile

# JSON dict
j = JsonFile("data.json", "example_data")
j.write({"users":[{"id":1}]})
j.append({"active": True})
print(j.get_item("active"))  # True

# JSON list
jl = JsonFile("list.json", "example_data")
jl.write([{"id":1}])
jl.append([{"id":2},{"id":3}])
print(jl.get_item(2))        # {"id":2}

# YAML dict
y = YamlFile("config.yaml", "example_data")
y.write({"app":{"name":"demo"},"features":["a"]})
y.append({"features":["b"]})
print(y.get_item("app"))

# TOML
t = TomlFile("cfg.toml", "example_data")
t.write({"app":{"name":"demo"}})
t.append({"features":{"x":True}})
print(t.read())
```

### 5) XML + Excel

```python
from ADVfile_manager import XmlFile, ExcelFile
import xml.etree.ElementTree as ET

# XML
xmlf = XmlFile("books.xml", "example_data")
root = ET.Element("books")
root.append(ET.Element("book", attrib={"id":"1"}))
xmlf.write(root)
xmlf.append(ET.Element("book", attrib={"id":"2"}))

for h in xmlf.search(tag="book", attr={"id":"2"}):
    print("Found:", h["context"])

# Excel
xl = ExcelFile("report.xlsx", "example_data", default_sheet="Sheet1")
xl.write([{"name":"Avi","score":95},{"name":"Dana","score":88}])
for h in xl.search(pattern="Avi", columns=["name"]):
    print(h["row"], h["col"], h["value"])
```

---

## Feature-by-Feature: Explanation & Examples

Below, each feature includes **what/why** and **how**, with **detailed examples**.

### 1) Safe Writes (Atomic)

**Why:** Prevent half-written files on crash/power loss.
**How:** Write to `*.tmp` then `os.replace(tmp, full_path)`.

**Example:** (built-in to write methods)

```python
JsonFile("data.json","data").write({"ok": True})
# Under the hood: writes to data.json.tmp then atomically replaces.
```

---

### 2) In-Memory Cache + `clear_cache()`

**Why:** Avoid redundant disk reads; but refresh easily after external changes.
**How:** `read()` fills `self.content`. Call `clear_cache()` to force re-read next time.

**Example:**

```python
txt = TextFile("notes.txt","data")
txt.write("one")
print(txt.read())   # pulls from disk and caches
# External edit happens here...
txt.clear_cache()
print(txt.read())   # re-reads from disk
```

---

### 3) Backups, Restore, Retention Helpers

**Why:** Safe rollback points; keep N most recent backups (by listing & pruning).
**How:** `backup()`, `list_backups()`, `restore(path=None)`, `clear_backups()`.

**Example:**

```python
t = TextFile("file.txt","data")
t.write("v1"); t.backup()
t.write("v2"); t.backup()
print(t.list_backups())
t.restore()                  # latest
removed = t.clear_backups()  # delete all backups now
```

---

### 4) Context Manager (Auto-Backup & Restore-On-Error)

**Why:** Transactional safety for risky edits.
**How:** `with File(...) as f:` backs up on enter (keep\_backup=True) and restores on exception.

**Example:**

```python
try:
    with JsonFile("conf.json","data") as j:
        j.write({"stage": "editing"})
        raise RuntimeError("boom")
except RuntimeError:
    pass
# conf.json restored to state at context entry
```

---

### 5) Exit-Time Cleanup for Ephemeral Backups

**Why:** Temporary edits don’t leave backup clutter.
**How:** Set `keep_backup=False` on the instance (or via call-chaining). Backups auto-delete via atexit.

**Example:**

```python
from ADVfile_manager import set_exit_cleanup, cleanup_backups_for_all

with TextFile("scratch.txt","data")(keep_backup=False) as f:
    f.write("temp")
# Backups cleared on exit.

set_exit_cleanup(False)      # disable global atexit cleanup
deleted = cleanup_backups_for_all()  # manual cleanup now
```

---

### 6) Human-Readable Sizes

**Why:** Friendly sizes for logs/UI.
**How:** `get_size_human()` returns e.g., `"12.3 KB"`.

**Example:**

```python
txt = TextFile("big.txt","data")
txt.write("x"*5000)
print(txt.get_size(), txt.get_size_human())  # 5000, "4.9 KB"
```

---

### 7) Text Helpers (`lines`, `read_line`)

**Why:** Work line-by-line without manual indexing.
**How:** `lines()` yields `(line_no, text)`, `read_line(n)` is 1-based.

**Example:**

```python
t = TextFile("notes.txt","data")
t.write("a\nb\nc")
print(t.read_line(2))    # "b"
for n, line in t.lines():
    print(n, line)
```

---

### 8) JSON/YAML/TOML Helpers

**Why:** Treat dict/list roots with one interface; shallow updates.
**How:** `get_item()`, `items()`, `append()`.

**Example (JSON):**

```python
j = JsonFile("conf.json","data")
j.write({"users":[{"id":1}]})
j.append({"active": True})
print(j.get_item("active"))  # True
for k, v in j.items():
    print(k, v)
```

**Example (YAML/TOML):** same semantics (YAML requires `pyyaml`; TOML requires `tomli`/`tomli-w` as needed).

---

### 9) CSV Helpers (`write(fieldnames=)`, `read_row`, `rows`)

**Why:** Control header order; read/iterate by row.
**How:** `write(..., fieldnames=...)`, `read_row(n)`, `rows()`.

**Example:**

```python
c = CsvFile("t.csv","data")
c.write([{"name":"Avi","age":30}], fieldnames=["name","age"])
c.append({"name":"Dana","age":25})
print(c.read_row(2))
for i, row in c.rows():
    print(i, row)
```

---

### 10) INI Merge (Sections/Keys)

**Why:** Simple config files need structured writes/updates.
**How:** `write({section:{k:v}})`, `append({section:{k:v}})`.

**Example:**

```python
ini = IniFile("settings.ini","data")
ini.write({"db":{"host":"localhost"}})
ini.append({"db":{"port":"5432"}})
```

---

### 11) XML Append & Search

**Why:** Build/extend XML trees; filter by tag/attrs/text.
**How:** `write(Element or xml_str)`, `append(Element or [Element])`, `search(tag=, attr=, pattern=)`.

**Example:**

```python
from ADVfile_manager import XmlFile
import xml.etree.ElementTree as ET

x = XmlFile("data.xml","data")
root = ET.Element("root")
x.write(root)
x.append(ET.Element("item", attrib={"kind":"a"}))

for h in x.search(tag="item", attr={"kind":"a"}):
    print(h["context"])
```

---

### 12) Excel Read/Write/Append + Search

**Why:** Spreadsheet data with header semantics.
**How:** `write(List[Dict], sheet=)`, `append(Dict|List[Dict], sheet=)`, `read(sheet=)`, `search(columns=, sheet=)`.

**Example:**

```python
xl = ExcelFile("r.xlsx","data", default_sheet="S1")
xl.write([{"name":"Avi","score":95},{"name":"Dana","score":88}])
xl.append({"name":"Noa","score":92})
for h in xl.search(pattern="Avi", columns=["name"]):
    print(h)
```

---

### 13) Unified Search Across All Formats

**Why:** One way to query text, keys, values, tags, attributes, columns, and sheets.
**How:** `search(pattern=, key=, value=, columns=, tag=, attr=, sheet=, regex=, case=, limit=)`.

**Examples already shown** above — they’re identical across file types, with format-specific options respected (e.g., `tag/attr` for XML, `columns`/`sheet` for Excel).

---

### 14) Async API (A\* Classes)

**Why:** Integrate with async apps (web servers, bots, pipelines).
**How:** `aread/awrite/aappend/asearch`, `async with`.

**Example:**

```python
import asyncio
from ADVfile_manager import ATextFile

async def work():
    async with ATextFile("async.txt","data") as t:
        await t.awrite("line1")
        await t.aappend("line2")
        print(await t.aread())

asyncio.run(work())
```

---

## License

**MIT License** — © 2025 Avi Twil.
See [`LICENSE`](./LICENSE) for details.

---

Questions or suggestions? Open an issue or PR:
**[https://github.com/avitwil/ADVfile\_manager](https://github.com/avitwil/ADVfile_manager)**
