
from __future__ import annotations
import argparse
from .inspector import PythonProject
from . import build_utils, packaging_utils

def main(argv=None):
    ap = argparse.ArgumentParser(prog="pyproj_inspector", description="Analyze and package Python projects")
    ap.add_argument("path", help="Path to a .py file or a project folder")
    ap.add_argument("--json", action="store_true", help="Print JSON summary and exit")

    sub = ap.add_subparsers(dest="cmd")

    sb = sub.add_parser("binary", help="Build a binary with PyInstaller or Nuitka")
    sb.add_argument("--entry", required=True)
    sb.add_argument("--mode", choices=["pyinstaller", "nuitka"], default="pyinstaller")
    sb.add_argument("--onefile", action="store_true", default=True)

    sp = sub.add_parser("pypi", help="Write pyproject.toml for PyPI packaging")
    sp.add_argument("--name", required=True)
    sp.add_argument("--version")
    sp.add_argument("--new", action="store_true", default=False)
    sp.add_argument("--creator", default="Unknown")

    sd = sub.add_parser("deb", help="Create a .deb using dpkg-deb")
    sd.add_argument("--name", required=True)
    sd.add_argument("--version", default="0.1.0")
    sd.add_argument("--creator", default="Unknown")
    sd.add_argument("--entry")

    args = ap.parse_args(argv)

    proj = PythonProject(args.path)

    if args.cmd is None:
        if args.__dict__["json"]:
            print(proj.result.to_json())
            return 0
        else:
            print("Loaded project at:", proj.result.root)
            print("Built-ins:", ", ".join(sorted(proj.result.builtins)))
            print("External dists:")
            for d, mods in sorted(proj.result.external_imports.items()):
                print("  ", d, "<-", ", ".join(sorted(mods)))
            print("Internal modules:", ", ".join(sorted(proj.result.internal_modules)))
            print("Files:", len(proj.result.files_code))
            return 0

    if args.cmd == "binary":
        out = build_utils.create_binary(proj.result.root, args.entry, mode=args.mode, onefile=args.onefile)
        print(out)
        return 0

    if args.cmd == "pypi":
        pt = packaging_utils.create_pypi_package(proj.result.root, args.name, version=args.version, new=args.new, creator_name=args.creator)
        print(pt)
        return 0

    if args.cmd == "deb":
        deb = packaging_utils.create_debian_package(proj.result.root, args.name, version=args.version, creator_name=args.creator, entry=args.entry)
        print(deb)
        return 0

    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
