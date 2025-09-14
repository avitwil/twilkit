"""
twilkit
=======

A lightweight Python toolkit providing:

- **validators** – data descriptors for attribute validation (start with, end with, ranges, etc.)
- **colors** – simple ANSI color printing via `color()` and `Cprint`
- **decorators** – error-catching and logging decorators for safer function execution
- **FlexVar** – a flexible, dict-like container with chainable add/update/remove

Features
--------
1. Centralized validation logic via descriptors:
   - StartWith, EndsWith, MoreThan, LessThan, InBetween
2. Quick and consistent colored output for CLI tools
3. Decorators for exception handling and logging to file
4. Dynamic attribute storage with pretty-printing

Examples
--------
Validation
~~~~~~~~~~
from twilkit import validators

class User:
    name = validators.StartWith("Mr ", "Ms ", "Dr ")
    email = validators.EndsWith("@example.com")

u = User()
u.name = "Dr Alice"        # valid
u.email = "alice@example.com"  # valid
# u.name = "Alice"          # raises ValidationError

Colors
~~~~~~
from twilkit import color
print(color("Success").green)
print(color("Warning").yellow)

Decorators
~~~~~~~~~~
from twilkit import catch_exceptions, log_function

@catch_exceptions
def safe_div(a, b):
    return a / b

@log_function
def add(a, b):
    return a + b

safe_div(4, 0)   # prints colored error, returns None
add(2, 3)        # logs to add.log

FlexVar
~~~~~~~
from twilkit import FlexVar

cfg = FlexVar("Config")
cfg.add("host", "localhost").add("port", 8080)
cfg.update("port", 9090)

print(cfg["host"])   # mapping-style access
print(cfg.port)      # attribute-style access
print(cfg)           # pretty formatted block
"""

from .core import (
    Colors, Cprint, color,
    ValidationError,
    StartWith, EndsWith, MoreThan, LessThan, InBetween,
    catch_exceptions, log_function,
    FlexVar,OfType, OptionalOfType, MatchesRegex
)
from .extra_tools import Return, PyTxt ,copy_this_module

from types import SimpleNamespace

# Namespace for grouped access to validators
validators = SimpleNamespace(
    StartWith=StartWith,
    EndsWith=EndsWith,
    MoreThan=MoreThan,
    LessThan=LessThan,
    InBetween=InBetween,
    OfType=OfType,
    OptionalOfType=OptionalOfType,
    MatchesRegex=MatchesRegex,
)

__all__ = [
    # validator namespace
    "validators",
    # validators also available at top-level
    "ValidationError",
    "StartWith", "EndsWith", "MoreThan", "LessThan", "InBetween","OfType", "OptionalOfType" ,    "MatchesRegex",

    # colors and helpers
    "Colors", "Cprint", "color",
    # decorators
    "catch_exceptions", "log_function",
    # dynamic container
    "FlexVar",
    "Return","PyTxt","copy_this_module"
]

# Re-exports: extra tools
from .extra_tools.core import PyTxt, Return, copy_this_module, copy_me_print

__all__ = [*globals().get('__all__', []), 'PyTxt', 'Return', 'copy_this_module']
