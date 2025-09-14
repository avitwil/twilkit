
# twilkit 
>**Version 2.0.0** - is here !! 

A lightweight toolkit for everyday Python work:

* **Validators** – clean, reusable descriptors for attribute validation
* **Colors** – simple ANSI color formatting for terminal output
* **Decorators** – exception handling and per-function logging
* **FlexVar** – a flexible, chainable dict-like container with a pretty `__str__`

---

## Table of Contents

* [Installation](#installation)
* [Quick Start](#quick-start)
* [API](#api)
  * [Validators](#validators)
    * [Start with](#startwithprefixes-str)
    * [End with](#endswithsuffixes-str)
    * [In between](#inbetweenminv-int--float-maxv-int--float)
    * [Less than](#lessthanvalue-int--float)
    * [More than](#morethanvalue-int--float)
    * [Colors](#colors)
    * [Decorators](#decorators)
      * [Catch Execptions](#catch_exceptions)
      * [Log Function](#log_function)
    * [FlexVar](#flexvar)
    * [Extra Tools new features from version 1.1.3](#extra-tools-pytxt-return-copy-helpers)
      * [Return](#return)
      * [PyTxt](#pytxt)
      * [Copy helper function](#copy-helpers)
* [Version 2.0 is here](#-version-200-)
  * [ADVfile_manager](#advfile_manager)
  * [pyproj_inspector](#pyproj_inspector)
* [Mini Project: “User Registry” CLI](#mini-project-user-registry-cli)
* [Contributing](#contributing)
* [License](#license)

---

## Installation

```bash
pip install twilkit
```
[back to menu](#table-of-contents)


---

> Supports Python 3.10+

---

## Quick Start

```python
from twilkit import validators, color, FlexVar, catch_exceptions, log_function

class User:
    name  = validators.StartWith("Mr ", "Ms ", "Dr ")
    email = validators.EndsWith("@example.com", "@corp.local")
    age   = validators.InBetween(0, 130)

@catch_exceptions
@log_function
def create_profile(name, email, age):
    u = User()
    u.name = name
    u.email = email
    u.age = age
    profile = FlexVar("Profile").add("name", name).add("email", email).add("age", age)
    print(color("User created").green)
    print(profile)
    return profile

create_profile("Dr Jane Doe", "jane@example.com", 34)
```
[back to menu](#table-of-contents)


---

## API

### Validators

Reusable data descriptors that enforce constraints on attributes when you set them.
Import them via the grouped namespace or directly:

```python
from twilkit import validators
# or:
from twilkit import StartWith, EndsWith, MoreThan, LessThan, InBetween
```
[back to menu](#table-of-contents)


---

#### `StartWith(*prefixes: str)`

Validate that a string starts with any of the provided prefixes.

```python
class Person:
    title = validators.StartWith("Mr ", "Ms ", "Dr ")

p = Person()
p.title = "Dr Alice"      # OK
# p.title = "Alice"       # raises ValidationError
```
[back to menu](#table-of-contents)


---

#### `EndsWith(*suffixes: str)`

Validate that a string ends with any of the provided suffixes.

```python
class Account:
    email = validators.EndsWith("@example.com", "@corp.local")

a = Account()
a.email = "dev@corp.local"  # OK
# a.email = "dev@gmail.com" # raises ValidationError
```
[back to menu](#table-of-contents)


---

#### `MoreThan(value: int | float)`

Validate that a number is strictly greater than `value`.

```python
class Metrics:
    height_cm = validators.MoreThan(0)

m = Metrics()
m.height_cm = 172  # OK
# m.height_cm = 0  # raises ValidationError
```
[back to menu](#table-of-contents)


---

#### `LessThan(value: int | float)`

Validate that a number is strictly less than `value`.

```python
class Bio:
    age = validators.LessThan(150)

b = Bio()
b.age = 42     # OK
# b.age = 200  # raises ValidationError
```
[back to menu](#table-of-contents)


---

#### `InBetween(minv: int | float, maxv: int | float)`

Validate that `minv <= value <= maxv`.

```python
class Exam:
    score = validators.InBetween(0, 100)

e = Exam()
e.score = 88    # OK
# e.score = -5  # raises ValidationError
```
[back to menu](#table-of-contents)


---

> All validators raise `twilkit.ValidationError` with a clear, colored message on failure.

---

### Colors

Minimal ANSI color helpers for terminals.

* `color(value)` → wraps the value and provides properties:

  * `.red`, `.light_green`, `.green`, `.yellow`, `.blue`, `.light_blue`, `.magenta`, `.cyan`, `.black`, `.purple`, `.orange`
* `Colors` enum → raw escape codes
* `Cprint` class → underlying helper

```python
from twilkit import color, Colors

print(color("Success").green)
print(color("Warning").yellow)
print(f"{Colors.RED.value}Error{Colors.RESET.value}")
```
[back to menu](#table-of-contents)


---



### Decorators

#### `@catch_exceptions`

Catch any exception, print a colored error (`<func> <error>`), return `None`.

```python
from twilkit import catch_exceptions, color

@catch_exceptions
def risky_div(a, b):
    return a / b

print(color("Result:").blue, risky_div(6, 3))  # 2.0
risky_div(1, 0)  # Prints colored error, returns None
```
[back to menu](#table-of-contents)


---

#### `@log_function`

Log function start, arguments, return values, and exceptions to `<func_name>.log`.

```python
from twilkit import log_function

@log_function
def compute_total(prices):
    return sum(prices)

compute_total([10, 20, 30])  # Logs to compute_total.log
```
[back to menu](#table-of-contents)


---



### FlexVar

A small, chainable dict-like container with a pretty string output.

```python
from twilkit import FlexVar

cfg = (
    FlexVar("Server Config")
      .add("host", "localhost")
      .add("port", 8080)
      .update("port", 9090)
)

print(cfg["host"])  # "localhost"
print(cfg.port)     # "9090"
print(cfg)          # Pretty formatted block

"host" in cfg       # True
del cfg["port"]     # Remove key
for key, val in cfg:
    print(key, val)
```

Error behavior:

* `.add(name, _)` → `KeyError` if attribute exists
* `.update(name, _)` / `.remove(name)` → `KeyError` if missing
* `.__getattr__(name)` → `AttributeError` if missing
* `.__getitem__` / `.__delitem__` → `KeyError` if missing

[back to menu](#table-of-contents)


---


## Mini Project: User Registry CLI

Combining validators, colors, decorators, and FlexVar.

```python
# file: user_registry.py
from twilkit import validators, color, log_function, catch_exceptions, FlexVar

class User:
    name  = validators.StartWith("Mr ", "Ms ", "Dr ")
    email = validators.EndsWith("@example.com", "@corp.local")
    age   = validators.InBetween(0, 130)

    def __init__(self, name: str, email: str, age: int):
        self.name = name
        self.email = email
        self.age = age

class Registry:
    def __init__(self):
        self._db = []

    @log_function
    @catch_exceptions
    def add_user(self, name: str, email: str, age: int):
        user = User(name, email, age)
        entry = (
            FlexVar("User")
            .add("name", user.name)
            .add("email", user.email)
            .add("age", user.age)
        )
        self._db.append(entry)
        print(color("User added").green)
        print(entry)
        return entry

    @log_function
    def list_users(self):
        if not self._db:
            print(color("No users found").yellow)
            return []
        print(color(f"Total users: {len(self._db)}").cyan)
        for i, entry in enumerate(self._db, start=1):
            print(color(f"[{i}]").purple)
            print(entry)
        return list(self._db)

    @log_function
    @catch_exceptions
    def update_email(self, index: int, new_email: str):
        entry = self._db[index]
        tmp = User(entry.name, new_email, entry.age)  # re-validation
        entry["email"] = tmp.email
        print(color("Email updated").light_green)
        print(entry)
        return entry

if __name__ == "__main__":
    reg = Registry()
    reg.add_user("Dr Alice", "alice@example.com", 34)
    reg.add_user("Ms Eve", "eve@gmail.com", 29)  # invalid -> ValidationError
    reg.list_users()
    reg.update_email(0, "alice@corp.local")
    reg.list_users()
```

This demonstrates:

* **Validation**: descriptors enforce constraints
* **Colors**: feedback messages
* **Logging**: each method logs to its own file
* **FlexVar**: flexible, human-readable data storage

[back to menu](#table-of-contents)


---

## Contributing

* Issues and PRs are welcome.
* Keep scope small, API tidy, docs clear.
* Include tests for new features .

---

## License

This project is licensed under the terms of the [MIT License](LICENSE).

[back to menu](#table-of-contents)


---

## Extra Tools (PyTxt, Return, Copy helpers)

> **New in 1.1.3** – Utility helpers under `twilkit.extra_tools` and re-exported at the top level.

[back to menu](#table-of-contents)


---

### PyTxt
A lightweight text/file wrapper that lets you work with an in-memory buffer or a bound file (via `ADVfile_manager.TextFile`).

    from twilkit import PyTxt
    p = PyTxt("hello")
    p.text                       # 'hello'
    p.file = "backups/example.txt"  # binds to a file (created if missing)
    p.text = "new content"          # writes to disk via ADVfile_manager

Key notes:
- `read_only=True` blocks writes and raises `PermissionError` when setting `.text`.
- Assigning `.file = <path>` auto-creates a `TextFile` using basename/dirname.
- Deleting `del p.file` pulls content back into memory and removes the file on disk.

[back to menu](#table-of-contents)


---

### Return
A tiny “result” object for returning a payload + success/error state.

    from twilkit import Return
    ok = Return(True, file="out.txt", size=123)
    if ok:
        print(ok["file"], ok.get("size"))

    err = Return.fail("not found", query="*.txt")
    if not err:
        print("Error:", err.error)

Conveniences: `.ok` (alias for `success`), `.dict()`, `.unwrap(key, default)`, and `.raise_for_error()`.

[back to menu](#table-of-contents)


---

### Copy helpers
Create a counted copy of a Python module with a header and optional removal of the `__main__` block.

    from twilkit import copy_this_module
    res = copy_this_module("backups", new_name="final.py", include_main=False)
    print("Created:", res["file_name"], "at", res["file_path"])



Parameters:
- `new_copy_file_path`: target folder.
- `copy_num`: start index for numbering; if the target exists, numbering auto-increments.
- `new_name`: optional output file name (suffix optional; source suffix is inherited if missing).
- `include_main`: keep or remove the `if __name__ == '__main__':` block in the copy.



> These helpers rely on **ADVfile_manager** for safe file operations. Install with extras: `pip install twilkit[extra_tools]`.

[back to menu](#table-of-contents)


---

# Version 2.0.0 

## include two new packages !!! 


### pyproj_inspector
**Repo:** [https://github.com/avitwil/pyproj_inspector](https://github.com/avitwil/pyproj_inspector)

`pyproj_inspector` ingests either a **single Python file** or a **project directory**, parses all `.py` files, and builds a structured view of your codebase:

- Built-in (stdlib) imports
- External imports (PyPI distributions mapped from import names)
- Internal modules (top-level packages/modules contained in your project)
- A map of `relative_path -> source_code` for every file
- An optional entry script when a single file is analyzed

It also ships with utilities to:

- Materialize the analyzed project into a temporary or target directory
- Create binaries via **PyInstaller** or **Nuitka**
- Generate a ready-to-edit **`pyproject.toml`** for packaging to PyPI
- Build a Debian `.deb` package (when `dpkg-deb` is available)

>Utility Analyze a Python script or project, classify imports, reconstruct sources, and quickly package into distributables.
```python
from twilkit.pyproj_inspector import PythonProject

proj = PythonProject("path/to/app.py")
print(proj.result.builtins)         # {'os', 'json', ...}
print(proj.result.external_imports) # {'requests': {'requests'}, ...}
print(proj.result.internal_modules) # {'app'}
print(proj.result.entry_relpath)    # 'app.py'

```
[pyproj_inspector](./pyproj_inspector_README.md)

[back to menu](#table-of-contents)


---


### ADVfile_manager
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


```python
from twilkit.ADVfile_manager import  File, TextFile, JsonFile, CsvFile, YamlFile,IniFile, TomlFile, XmlFile, ExcelFile
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

# INI
ini = IniFile("settings.ini", "data")
ini.write({"server": {"host": "127.0.0.1", "port": 8000}})
ini.append({"server": {"debug": "true"}, "auth": {"enabled": "yes"}})
cfg = ini.read()
print(cfg["server"]["host"])

# TOML
toml = TomlFile("config.toml", "data")
toml.write({"app": {"name": "demo"}, "features": {"b": True}})
print(toml.read()["app"]["name"])
toml.append({"features": {"c": 123}})

# XML

xmlf = XmlFile("books.xml", "data")
root = ET.Element("books")
root.append(ET.Element("book", attrib={"id": "1"}))
xmlf.write(root)

# Append another
xmlf.append(ET.Element("book", attrib={"id": "2"}))
print(ET.tostring(xmlf.read(), encoding="unicode"))

# EXEL

xl = ExcelFile("report.xlsx", "data", default_sheet="Sheet1")
xl.write([{"name":"Avi","score":95},{"name":"Dana","score":88}])
xl.append({"name":"Noa","score":92})
rows = xl.read()
print(rows[0]["name"])



```
[README](./ADVfile_manager_README.md)

[Usage Guide](./ADVfile_manager_USAGE.md)

[back to menu](#table-of-contents)


---


