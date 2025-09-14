"""
ADVfile_manager
===============

Unified file abstractions for Python with safe writes, caching, backups,
context managers, exit-time cleanup, unified search, async variants,
and support for multiple formats:

- TextFile      : Plain text (.txt) with line-based helpers and search.
- JsonFile      : JSON (.json), dict or list root, append/merge, items().
- CsvFile       : CSV (.csv), DictReader/DictWriter, row helpers, search.
- YamlFile      : YAML (.yaml/.yml), requires PyYAML.
- IniFile       : INI (.ini), configparser-based read/write/search.
- TomlFile      : TOML (.toml), requires tomli/tomllib + tomli-w.
- XmlFile       : XML (.xml), ElementTree-based, tag/attr/text search.
- ExcelFile     : Excel (.xlsx), requires openpyxl.

Async Variants (A*):
- ATextFile, AJsonFile, ACsvFile, AYamlFile, AIniFile, ATomlFile, AXmlFile, AExcelFile.

Common features (all file types):
- Safe atomic writes
- In-memory cache with clear_cache()
- Backup/restore with retention policy
- Human-readable sizes
- Context manager safety (auto-backup + restore-on-error)
- Ephemeral backups auto-cleaned at exit
- Unified search() API across all formats (sync + async)

Author: Avi Twil
GitHub: https://github.com/avitwil/ADVfile_manager
"""

from .core import (
    # Base + sync classes
    File, TextFile, JsonFile, CsvFile, YamlFile,
    IniFile, TomlFile, XmlFile, ExcelFile,

    # Async classes
    ATextFile, AJsonFile, ACsvFile, AYamlFile,
    AIniFile, ATomlFile, AXmlFile, AExcelFile,

    # Utilities
    set_exit_cleanup, cleanup_backups_for_all,
)

__all__ = [
    # Base
    "File",

    # Sync classes
    "TextFile", "JsonFile", "CsvFile", "YamlFile",
    "IniFile", "TomlFile", "XmlFile", "ExcelFile",

    # Async classes
    "ATextFile", "AJsonFile", "ACsvFile", "AYamlFile",
    "AIniFile", "ATomlFile", "AXmlFile", "AExcelFile",

    # Utils
    "set_exit_cleanup", "cleanup_backups_for_all",
]

__author__ = "Avi Twil"
__version__ = "1.1.0"
__license__ = "MIT"
