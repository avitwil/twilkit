
from __future__ import annotations
import sys
import os
import subprocess
from pathlib import Path
from typing import Literal, Optional

BuildMode = Literal["pyinstaller", "nuitka"]

def create_binary(project_root: str | os.PathLike, entry: str, *, mode: BuildMode = "pyinstaller",
                  onefile: bool = True, output_dir: Optional[str | os.PathLike] = None,
                  extra_args: Optional[list[str]] = None) -> Path:
    project_root = Path(project_root).resolve()
    output_dir = Path(output_dir or project_root / "dist")
    output_dir.mkdir(parents=True, exist_ok=True)

    entry_path = project_root / entry
    if not entry_path.exists():
        raise FileNotFoundError(entry)

    if mode == "pyinstaller":
        args = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--name", Path(entry).stem,
            "--distpath", str(output_dir),
            "--workpath", str(project_root / ".build"),
        ]
        if onefile:
            args.append("--onefile")
        args += extra_args or []
        args.append(str(entry_path))
        subprocess.check_call(args)
        artifact = output_dir / (Path(entry).stem + (".exe" if os.name == "nt" else ""))
        if not artifact.exists():
            for child in output_dir.iterdir():
                if child.name.startswith(Path(entry).stem):
                    artifact = child
                    break
        return artifact

    elif mode == "nuitka":
        args = [
            sys.executable, "-m", "nuitka",
            f"--output-dir={str(output_dir)}",
            "--remove-output",
            "--assume-yes-for-downloads",
        ]
        if onefile:
            args.append("--onefile")
        args += extra_args or []
        args.append(str(entry_path))
        subprocess.check_call(args)
        candidates = sorted(output_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
        return candidates[0] if candidates else output_dir

    else:
        raise ValueError("mode must be 'pyinstaller' or 'nuitka'")
