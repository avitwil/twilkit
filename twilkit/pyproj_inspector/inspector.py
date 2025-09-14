
from __future__ import annotations
import ast
import os
import sys
import json
import tempfile
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

try:
    from importlib.metadata import packages_distributions, PackageNotFoundError  # py3.10+
except Exception:  # pragma: no cover
    packages_distributions = None  # type: ignore
    PackageNotFoundError = Exception  # type: ignore

_STDLIB: Set[str] = set(getattr(sys, "stdlib_module_names", set()))
if not _STDLIB:
    _STDLIB = {
        "abc", "argparse", "asyncio", "base64", "collections", "concurrent",
        "contextlib", "copy", "csv", "dataclasses", "datetime", "functools",
        "glob", "hashlib", "heapq", "http", "importlib", "inspect", "io",
        "itertools", "json", "logging", "math", "operator", "os", "pathlib",
        "pickle", "platform", "random", "re", "shutil", "site", "sqlite3",
        "statistics", "string", "subprocess", "sys", "tempfile", "textwrap",
        "threading", "time", "types", "typing", "unittest", "uuid", "venv",
        "zipfile",
    }

@dataclass
class ProjectParseResult:
    root: Path
    builtins: Set[str] = field(default_factory=set)
    external_imports: Dict[str, Set[str]] = field(default_factory=dict)
    internal_modules: Set[str] = field(default_factory=set)
    files_code: Dict[str, str] = field(default_factory=dict)
    entry_relpath: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps(
            {
                "root": str(self.root),
                "builtins": sorted(self.builtins),
                "external_imports": {k: sorted(v) for k, v in self.external_imports.items()},
                "internal_modules": sorted(self.internal_modules),
                "files": sorted(self.files_code.keys()),
                "entry": self.entry_relpath,
            },
            ensure_ascii=False,
            indent=2,
        )

class PythonProject:
    def __init__(self, path: str | os.PathLike):
        p = Path(path).resolve()
        if p.is_file() and p.suffix == ".py":
            root = p.parent
            entry_rel = p.name
            files = [p]
        elif p.is_dir():
            root = p
            entry_rel = None
            files = [q for q in root.rglob("*.py") if q.is_file()]
        else:
            raise ValueError("Path must be a .py file or a directory containing a project")

        files_code: Dict[str, str] = {}
        for fp in files:
            try:
                files_code[str(fp.relative_to(root))] = fp.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                files_code[str(fp.relative_to(root))] = fp.read_text(encoding="latin-1")

        builtins: Set[str] = set()
        top_level_imports: Set[str] = set()
        internal_modules: Set[str] = set()

        # Register internal modules from file paths (even if not imported)
        def _register_internal_from_path(relpath: str) -> None:
            parts = Path(relpath).with_suffix("").parts
            if parts and parts[-1] == "__init__":
                parts = parts[:-1]
            if parts:
                internal_modules.add(parts[0])

        for rel in files_code.keys():
            _register_internal_from_path(rel)

        # Parse AST to classify imports
        for relpath, src in files_code.items():
            try:
                tree = ast.parse(src, filename=relpath)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mod = alias.name.split(".")[0]
                        self._classify_module(mod, root, internal_modules, builtins, top_level_imports)
                elif isinstance(node, ast.ImportFrom):
                    if node.module is None:
                        internal_modules.add(self._rel_to_pkg(relpath))
                        continue
                    mod = node.module.split(".")[0]
                    self._classify_module(mod, root, internal_modules, builtins, top_level_imports)

        external_map: Dict[str, Set[str]] = self._map_imports_to_distributions(top_level_imports)

        self.result = ProjectParseResult(
            root=root,
            builtins=builtins,
            external_imports=external_map,
            internal_modules=internal_modules,
            files_code=files_code,
            entry_relpath=entry_rel,
        )

    @staticmethod
    def _rel_to_pkg(relpath: str) -> str:
        parts = Path(relpath).with_suffix("").parts
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts)

    @staticmethod
    def _classify_module(mod: str, root: Path, internal: Set[str], std: Set[str], top: Set[str]) -> None:
        mod_path_file = root / f"{mod}.py"
        mod_path_pkg = root / mod / "__init__.py"
        if mod_path_file.exists() or mod_path_pkg.exists():
            internal.add(mod)
            return
        if mod in _STDLIB:
            std.add(mod); return
        top.add(mod)

    @staticmethod
    def _map_imports_to_distributions(imports: Set[str]) -> Dict[str, Set[str]]:
        dist_map: Dict[str, Set[str]] = {}
        if packages_distributions:
            reverse = packages_distributions()
            for mod in sorted(imports):
                dists = reverse.get(mod, [])
                if dists:
                    for d in dists:
                        dist_map.setdefault(d, set()).add(mod)
        unmapped = [m for m in imports if all(m not in v for v in dist_map.values())]
        if unmapped:
            try:
                import urllib.request
                for name in unmapped:
                    url = f"https://pypi.org/simple/{name}/"
                    req = urllib.request.Request(url, method="HEAD")
                    try:
                        with urllib.request.urlopen(req, timeout=3) as resp:  # nosec
                            if 200 <= resp.status < 400:
                                dist_map.setdefault(name, set()).add(name)
                    except Exception:
                        pass
            except Exception:
                pass
        return dist_map

    def moduls(self) -> List[str]:
        return sorted(self.result.internal_modules)

    def restore_to(self, target: str | os.PathLike) -> Path:
        target = Path(target)
        target.mkdir(parents=True, exist_ok=True)
        for rel, code in self.result.files_code.items():
            out = target / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(code, encoding="utf-8")
        return target

    def run_in_tmp_env(self, entry: Optional[str] = None, *, install: bool = True, env: Optional[Dict[str, str]] = None,
                        args: Optional[List[str]] = None, python: Optional[str] = None) -> subprocess.CompletedProcess:
        entry_rel = entry or self.result.entry_relpath or ("__main__.py" if (self.result.root/"__main__.py").exists() else "main.py")
        if entry_rel not in self.result.files_code:
            raise FileNotFoundError(f"Entry script '{entry_rel}' was not found in parsed files")
        tmp = Path(tempfile.mkdtemp(prefix="pyproj_inspector_")).resolve()
        try:
            self.restore_to(tmp)
            venv_py = python or sys.executable
            venv_dir = tmp / ".venv"
            subprocess.check_call([venv_py, "-m", "venv", str(venv_dir)])
            bin_dir = "Scripts" if os.name == "nt" else "bin"
            py = venv_dir / bin_dir / ("python.exe" if os.name == "nt" else "python")
            pip = venv_dir / bin_dir / ("pip.exe" if os.name == "nt" else "pip")
            if install and self.result.external_imports:
                reqs = sorted(self.result.external_imports.keys())
                subprocess.check_call([str(py), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
                subprocess.check_call([str(pip), "install", *reqs])
            cmd = [str(py), str(tmp / entry_rel), *(args or [])]
            return subprocess.run(cmd, check=False, text=True, capture_output=True, env={**os.environ, **(env or {})})
        finally:
            pass
