
# pyproj_inspector

Analyze a Python script or project, classify imports, reconstruct sources, and quickly package into distributables.
Authored by **Avi Twil**.

> Version: `0.1.2` • License: MIT • Python: 3.8+ • OS: Windows, macOS, Linux

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [Analyze a single script](#analyze-a-single-script)
  - [Analyze a project directory](#analyze-a-project-directory)
- [Python API](#python-api)
  - [`PythonProject`](#pythonproject)
  - [`ProjectParseResult`](#projectparseresult)
  - [High-level Methods](#high-level-methods)
    - [`moduls()`](#moduls)
    - [`restore_to(target)`](#restore_totarget)
    - [`run_in_tmp_env(...)`](#run_in_tmp_env)
  - [Build Utilities](#build-utilities)
    - [`create_binary(...)`](#create_binary)
  - [Packaging Utilities](#packaging-utilities)
    - [`create_pypi_package(...)`](#create_pypi_package)
    - [`plan_pypi_version(...)`](#plan_pypi_version)
    - [`create_debian_package(...)`](#create_debian_package)
- [CLI Usage](#cli-usage)
- [How it works (Design Notes)](#how-it-works-design-notes)
- [Limitations & Notes](#limitations--notes)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
  - [Project Layout](#project-layout)
  - [Run Tests](#run-tests)
- [Changelog](#changelog)
- [Author](#author)
- [License](#license)

---

## Overview

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

---

## Key Features

- ⚙️ **Static analysis** via `ast` – resilient even if some files have syntax errors
- 🏷️ **Import classification**:
  - **Builtins** using `sys.stdlib_module_names` (fallback list included)
  - **External** mapped via `importlib.metadata.packages_distributions()` with a fallback **PyPI Simple** `HEAD` probe per import
  - **Internal** detected from **actual files** (even if not imported) and from relative imports
- 🧳 **Rehydration** – write all sources back to disk with original relative paths
- 🚀 **Ephemeral execution** – run your entry script in a fresh venv, optionally installing external deps
- 📦 **Packaging helpers** – binary via **PyInstaller**/**Nuitka**, **PyPI** metadata scaffold, **Debian** packages
- 🧪 **Comprehensive tests** – unit & edge-case coverage

---

## Installation

```bash

pip install pyproj_inspector

```

> For **binary creation**, ensure you have the chosen tool installed in your environment:
> - PyInstaller: `pip install pyinstaller`
> - Nuitka: `pip install nuitka`
>
> For **Debian packaging**, you need `dpkg-deb` available on your system.

---

## Quick Start

### Analyze a single script

```python
from pyproj_inspector import PythonProject

proj = PythonProject("path/to/app.py")
print(proj.result.builtins)         # {'os', 'json', ...}
print(proj.result.external_imports) # {'requests': {'requests'}, ...}
print(proj.result.internal_modules) # {'app'}
print(proj.result.entry_relpath)    # 'app.py'
```

### Analyze a project directory

```python
from pyproj_inspector import PythonProject

proj = PythonProject("path/to/project_dir")
print(sorted(proj.moduls()))        # e.g. ['pkg', 'utils']
print(len(proj.result.files_code))  # number of .py files discovered
```

---

## Python API

### `PythonProject`

```python
PythonProject(path: str | os.PathLike)
```
- **`path`**: A `.py` file or a project directory.
- If a single file is passed, `entry_relpath` is set to its filename.

> Parsing is robust: files with syntax errors are still captured in `files_code` and simply skipped for AST import extraction.

### `ProjectParseResult`

```python
@dataclass
class ProjectParseResult:
    root: Path
    builtins: Set[str]
    external_imports: Dict[str, Set[str]]  # distribution -> {import names}
    internal_modules: Set[str]
    files_code: Dict[str, str]             # 'relative/path.py' -> source
    entry_relpath: Optional[str]           # when analyzing a single file
```
- **Builtins**: stdlib modules detected via `sys.stdlib_module_names` or a curated fallback set.
- **External imports**: resolved via `packages_distributions()`. Any unmapped names are *probingly* tested against PyPI’s simple index (`HEAD`) to guess a matching distribution (best effort).
- **Internal modules**: determined by the project’s file layout (top-level names from `*.py` and package dirs) + relative-import hints. For packages, `pkg/__init__.py` is reported as `pkg`.

### High-level Methods

#### `moduls()`

```python
proj.moduls() -> List[str]
```
Returns a **sorted** list of internal module names. This reflects the top-level modules/packages detected in your project’s tree (e.g., `['app', 'utils']`).

#### `restore_to(target)`

```python
proj.restore_to("out/dir") -> pathlib.Path
```
Writes every captured file from `files_code` to the given directory, preserving relative paths. It **overwrites** existing files.

#### `run_in_tmp_env(...)`

```python
proj.run_in_tmp_env(
    entry: Optional[str] = None,
    install: bool = True,
    env: Optional[Dict[str, str]] = None,
    args: Optional[List[str]] = None,
    python: Optional[str] = None,
) -> subprocess.CompletedProcess
```
- Creates a temp directory, restores all sources, bootstraps a virtual environment and **optionally installs external distributions** (keys from `external_imports`).
- **`entry`**: by default uses `entry_relpath` (if analyzing a single file). If missing, falls back to `__main__.py` or `main.py` when present.
- Returns a `CompletedProcess` with `stdout`, `stderr`, and `returncode`.

> Useful for quick smoke tests in isolation.

### Build Utilities

#### `create_binary(...)`

```python
from pyproj_inspector import create_binary

create_binary(
    project_root: str | os.PathLike,
    entry: str,
    mode: Literal["pyinstaller", "nuitka"] = "pyinstaller",
    onefile: bool = True,
    output_dir: Optional[str | os.PathLike] = None,
    extra_args: Optional[list[str]] = None,
) -> pathlib.Path
```
- Builds a standalone binary of `entry` using **PyInstaller** or **Nuitka**.
- Returns the path to the produced artifact.
- **Requirements**: the chosen backend must be installed and available in the current Python environment.

### Packaging Utilities

#### `create_pypi_package(...)`

```python
from pyproj_inspector import create_pypi_package

create_pypi_package(
    project_root: str | Path,
    package_name: str,
    version: Optional[str] = None,
    new: bool = True,
    creator_name: str = "Unknown",
    description: str = "Auto-generated package",
    homepage: str = "",
) -> Path
```
- Writes a **`pyproject.toml`** scaffold (PEP 621) and creates a package directory with `__init__.py`.
- When `new=True`, checks PyPI for name availability; if taken, raises `ValueError`.
- When `new=False`, fetches the latest published version and **bumps the patch** (e.g., `1.0.0 -> 1.0.1`), unless you pass a **higher** `version`, which takes precedence.

> The template is rendered using `string.Template` to avoid brace-related issues.

#### `plan_pypi_version(...)`

```python
from pyproj_inspector.packaging_utils import plan_pypi_version

plan = plan_pypi_version(name, version, new)
print(plan.name, plan.version, plan.is_new_project)
```
- Returns the chosen name/version and whether this is treated as a new project.

#### `create_debian_package(...)`

```python
from pyproj_inspector import packaging_utils
packaging_utils.create_debian_package(
    project_root: str | Path,
    package_name: str,
    version: str = "0.1.0",
    creator_name: str = "Unknown",
    entry: Optional[str] = None,
) -> Path
```
- Produces a Debian `.deb` by staging the project under `/usr/local/lib/<name>` with a basic `DEBIAN/control` file.
- If `entry` is provided, a launcher script is placed under `/usr/local/bin/<name>`.
- **Requirement**: `dpkg-deb` must be available.

---

## CLI Usage

```bash
# Print JSON analysis (builtins/external/internal/files)
pyproj_inspector <PATH> --json

# Build a binary
pyproj_inspector <PATH> binary --entry main.py --mode pyinstaller --onefile

# Scaffold PyPI packaging (pyproject.toml)
pyproj_inspector <PATH> pypi --name my_project --new --creator "Avi Twil"

# Build a Debian package
pyproj_inspector <PATH> deb --name my_project --version 0.1.0 --creator "Avi Twil" --entry main.py
```

> On Windows via PyCharm’s terminal, ensure the active interpreter has the required backend (e.g., `pip install pyinstaller`).

---

## How it works (Design Notes)

1. **Discovery**  
   - If `path` is a file: analyze just that file; set `entry_relpath` to its name.
   - If `path` is a directory: recursively collect `*.py` files.

2. **File capture**  
   - Read each file as UTF‑8, falling back to Latin‑1 when needed. All sources are stored in `files_code`.

3. **Internal modules**  
   - Derived from file layout (**top-level** names of `*.py` and package directories).  
   - `pkg/__init__.py` normalizes to `pkg`.  
   - Relative imports (e.g. `from . import x`) mark the current package as internal too.

4. **Import classification**  
   - Parse each file’s AST; collect top-level import names.  
   - Classify priority: **internal (if a file/dir exists)** → **stdlib** → **external**.

5. **External mapping**  
   - Use `packages_distributions()` when available.  
   - For unmapped names, probe **PyPI Simple** `HEAD` (`https://pypi.org/simple/<name>/`) to infer a plausible distribution name.

6. **Execution sandbox**  
   - `run_in_tmp_env()` creates an isolated venv, installs external distributions (if any), and executes the chosen entry script.

---

## Limitations & Notes

- **Namespace packages (PEP 420)**: currently not fully supported. A top-level directory without `__init__.py` may not always be recognized as a package.  
  _Planned_: heuristic support to treat existing directories as internal packages when imported.
- **External mapping is best-effort**: PyPI probing is a heuristic; unusual naming may require manual intervention.
- **Binary size/behavior**: depends on the chosen backend (PyInstaller/Nuitka) and your project’s specifics.
- **Network access**: PyPI checks require connectivity unless you inject your own mapping logic.

---

## Troubleshooting

- **`ValueError: Project name 'X' already exists on PyPI`**  
  Use a different `--name` or set `new=False` and pass a higher `--version`.
- **`FileNotFoundError` when running**  
  Ensure `entry` exists **in the analyzed sources** (`files_code`); if you analyze a directory, add the script first.
- **Binary build fails**  
  Verify the backend is installed: `pip show pyinstaller` / `pip show nuitka`. Check platform-specific notes of those tools.
- **Imports misclassified**  
  If you intentionally shadow stdlib (e.g., `json.py`), the tool prioritizes **internal** over stdlib—this is by design.

---

## Development

### Project Layout

```
pyproj_inspector/
  __init__.py
  inspector.py         # analysis core
  build_utils.py       # binary builders
  packaging_utils.py   # PyPI/DEB helpers
  cli.py               # command-line interface
tests/
  ...                  # unit & edge-case tests
pyproject.toml
README.md
```

### Run Tests

```bash
python -m pip install -U pip pytest
pytest -q
# or on Windows:
run_tests.bat
```

---

## Changelog

### 0.1.2
- Fix `pyproject.toml` template rendering using `string.Template`
- Normalize `pkg/__init__.py` → `pkg`
- Prefer **internal** over stdlib for shadowed names (e.g., local `json.py`)
- Register internal modules from file layout (even if not imported)
- CLI imports modules for easier monkeypatching in tests

---

## Author

**Avi Twil**

---

## License

MIT © Avi Twil
