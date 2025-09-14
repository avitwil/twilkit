from enum import Enum
from functools import wraps
from typing import Callable, Any, Iterable
import logging
import re


# ---------- Colors / helpers ----------

class Colors(Enum):
    """
    ANSI color escape codes enumeration.

    Members
    -------
    RESET, RED, LIGHT_GREEN, GREEN, YELLOW, BLUE, LIGHT_BLUE, MAGENTA,
    CYAN, BLACK, PURPLE, ORANGE
        String escape codes that can be prefixed to text to colorize terminal output.

    Examples
    --------
    text = f"{Colors.RED.value}Error{Colors.RESET.value}"
    """

    RESET = "\033[0m"
    RED = "\33[91m"
    LIGHT_GREEN = "\33[92m"
    GREEN = "\33[32m"
    YELLOW = "\33[93m"
    BLUE = "\33[38;2;0;51;255m"
    LIGHT_BLUE = "\33[94m"
    MAGENTA = "\33[95m"
    CYAN = "\33[96m"
    BLACK = "\33[30m"
    PURPLE = "\33[35m"
    ORANGE = "\033[38;2;255;165;0m"


class Cprint:
    """
    Lightweight colorizer wrapper around a value.

    Provides properties that render the wrapped value with ANSI colors.
    Intended for quick inline formatting in f-strings.

    Parameters
    ----------
    value : Any
        The value to be rendered (converted to string) with color.

    Examples
    --------
    msg = Cprint("Hello").green
    # print(msg) -> green "Hello" in a supporting terminal
    """

    def __init__(self, value: Any):
        self.__value = value

    @property
    def red(self) -> str:
        """Return the value colored red."""
        return f"\33[91m{self.__value}\033[0m"

    @property
    def light_green(self) -> str:
        """Return the value colored light green."""
        return f"\33[92m{self.__value}\033[0m"

    @property
    def green(self) -> str:
        """Return the value colored green."""
        return f"\33[32m{self.__value}\033[0m"

    @property
    def yellow(self) -> str:
        """Return the value colored yellow."""
        return f"\33[93m{self.__value}\033[0m"

    @property
    def blue(self) -> str:
        """Return the value colored RGB(0,51,255)."""
        return f"\33[38;2;0;51;255m{self.__value}\033[0m"

    @property
    def light_blue(self) -> str:
        """Return the value colored light blue."""
        return f"\33[94m{self.__value}\033[0m"

    @property
    def magenta(self) -> str:
        """Return the value colored magenta."""
        return f"\33[95m{self.__value}\033[0m"

    @property
    def cyan(self) -> str:
        """Return the value colored cyan."""
        return f"\33[96m{self.__value}\033[0m"

    @property
    def black(self) -> str:
        """Return the value colored black."""
        return f"\33[30m{self.__value}\033[0m"

    @property
    def purple(self) -> str:
        """Return the value colored purple."""
        return f"\33[35m{self.__value}\033[0m"

    @property
    def orange(self) -> str:
        """Return the value colored orange."""
        return f"\033[38;2;255;165;0m{self.__value}\033[0m"


def color(value: Any) -> Cprint:
    """
    Convenience factory for Cprint.

    Parameters
    ----------
    value : Any
        Value to be wrapped.

    Returns
    -------
    Cprint
        A colorizer wrapper.

    Examples
    --------
    print(f"{color('OK').green}")
    """
    return Cprint(value)


# ---------- Exceptions ----------

class ValidationError(Exception):
    """
    Exception raised by validation descriptors when a constraint fails.

    Parameters
    ----------
    name : str
        The validated attribute name (unmangled).
    *values : Any
        Expected value(s) used in the failed validation (e.g., allowed prefixes).
    msg : str
        Human-readable message describing the violated rule.

    Attributes
    ----------
    name : str
        Colored attribute name for display.
    value : str
        Colored string representation of expected value(s).
    msg : str
        Colored message.

    Examples
    --------
    # Raised internally by descriptors like StartWith / EndsWith / InBetween
    """

    def __init__(self, name: str, *values: Any, msg: str):
        self.name = color(name).light_green

        parts = [color(v).yellow for v in values]
        sep = f" {color('or').red} "
        self.value = sep.join(parts) if parts else ""

        self.msg = color(msg).red
        super().__init__(f"{self.name} {self.msg} {self.value}".strip())


# ---------- Descriptors ----------

class StartWith:
    """
    Data descriptor validating that a string starts with any of the given prefixes.

    Usage: define as a class attribute and assign on instances.

    Parameters
    ----------
    *value : str
        One or more allowed prefixes. Passed directly to str.startswith.

    Raises
    ------
    ValidationError
        If the assigned value is not a string or does not start with any prefix.

    Examples
    --------
    class User:
        name = StartWith("Mr ", "Ms ", "Dr ")

    u = User()
    u.name = "Dr Alice"   # OK
    # u.name = "Alice"    # -> ValidationError
    """

    def __init__(self, *value: str):
        self.value = value

    def __set_name__(self, owner, name):
        self.name = f"__{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name, None)

    def __set__(self, instance, value: str):
        if not isinstance(value, str) or not value.startswith(self.value):
            raise ValidationError(self.name.lstrip("__"), *self.value, msg="must start with")
        setattr(instance, self.name, value)


class EndsWith:
    """
    Data descriptor validating that a string ends with any of the given suffixes.

    Parameters
    ----------
    *value : str
        One or more allowed suffixes.

    Raises
    ------
    ValidationError
        If the assigned value is not a string or does not end with any suffix.

    Examples
    --------
    class User:
        email = EndsWith("@example.com", "@corp.local")

    u = User()
    u.email = "alice@example.com"   # OK
    # u.email = "alice@gmail.com"   # -> ValidationError
    """

    def __init__(self, *value: str):
        self.value = value

    def __set_name__(self, owner, name):
        self.name = f"__{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name, None)

    def __set__(self, instance, value: str):
        if not isinstance(value, str) or not value.endswith(self.value):
            raise ValidationError(self.name.lstrip("__"), *self.value, msg="must end with")
        setattr(instance, self.name, value)


class MoreThan:
    """
    Data descriptor validating that a numeric value is strictly greater than a threshold.

    Parameters
    ----------
    value : float | int
        Strict lower bound.

    Raises
    ------
    ValidationError
        If the assigned value is not greater than the threshold.

    Examples
    --------
    class Metrics:
        height_cm = MoreThan(0)

    m = Metrics()
    m.height_cm = 170     # OK
    # m.height_cm = 0     # -> ValidationError
    """

    def __init__(self, value: float | int):
        self.value = value

    def __set_name__(self, owner, name):
        self.name = f"__{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name, None)

    def __set__(self, instance, value: float | int):
        if not value > self.value:
            raise ValidationError(self.name.lstrip("__"), self.value, msg="must be more than")
        setattr(instance, self.name, value)


class LessThan:
    """
    Data descriptor validating that a numeric value is strictly less than a threshold.

    Parameters
    ----------
    value : float | int
        Strict upper bound.

    Raises
    ------
    ValidationError
        If the assigned value is not less than the threshold.

    Examples
    --------
    class Person:
        age = LessThan(150)

    p = Person()
    p.age = 42        # OK
    # p.age = 200     # -> ValidationError
    """

    def __init__(self, value: float | int):
        self.value = value

    def __set_name__(self, owner, name):
        self.name = f"__{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name, None)

    def __set__(self, instance, value: float | int):
        if not value < self.value:
            raise ValidationError(self.name.lstrip("__"), self.value, msg="must be less than")
        setattr(instance, self.name, value)


class InBetween:
    """
    Data descriptor validating that a numeric value lies within a closed interval.

    Condition: min <= value <= max

    Parameters
    ----------
    minv : float | int
        Lower bound (inclusive).
    maxv : float | int
        Upper bound (inclusive).

    Raises
    ------
    ValidationError
        If the assigned value is outside the [minv, maxv] interval.

    Examples
    --------
    class Exam:
        score = InBetween(0, 100)

    e = Exam()
    e.score = 88       # OK
    # e.score = -5     # -> ValidationError
    """

    def __init__(self, minv: float | int, maxv: float | int):
        self.min = minv
        self.max = maxv

    def __set_name__(self, owner, name):
        self.name = f"__{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name, None)

    def __set__(self, instance, value: float | int):
        if not (self.min <= value <= self.max):
            raise ValidationError(self.name.lstrip("__"), self.min, self.max, msg="must be between")
        setattr(instance, self.name, value)


# ---------- Decorators ----------

def catch_exceptions(func: Callable):
    """
    Decorator that catches exceptions from the wrapped function,
    prints a colored error summary, and returns None on failure.

    Intended for lightweight CLI utilities where exceptions should be
    surfaced to the console without crashing the program.

    Parameters
    ----------
    func : Callable
        The function to wrap.

    Returns
    -------
    Callable
        Wrapped function that returns the original result, or None if an exception occurred.

    Examples
    --------
    @catch_exceptions
    def div(a, b):
        return a / b

    result_ok = div(6, 3)     # -> 2.0
    result_err = div(1, 0)    # prints colored message, returns None
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"{color(func.__name__).green} {e}")
            return None
    return wrapper


def log_function(func: Callable):
    """
    Decorator that logs function start, arguments, successful return,
    and exceptions to a dedicated <func_name>.log file.

    Each decorated function gets its own logger and file handler,
    avoiding repeated global logging configuration.

    Parameters
    ----------
    func : Callable
        The function to wrap.

    Returns
    -------
    Callable
        Wrapped function that logs execution details.

    Log format
    ----------
    LEVEL (DD/MM/YY HH:MM:SS): message (Line: <lineno> [<filename>])

    Examples
    --------
    @log_function
    def compute(x, y):
        return x + y

    val = compute(2, 3)  # writes entries to compute.log

    Error Handling
    --------------
    On exception, the error is logged with traceback and the wrapper returns None.
    """
    logger_name = f"{func.__module__}.{func.__name__}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fh = logging.FileHandler(f"{func.__name__}.log", encoding="utf-8", mode="a")
        fmt = logging.Formatter(
            "%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d [%(filename)s])",
            datefmt="%d/%m/%y %I:%M:%S"
        )
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("starting '%s' with args=%s kwargs=%s", func.__name__, list(args), dict(kwargs))
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger.exception("'%s' crashed. args=%s kwargs=%s error=%s", func.__name__, list(args), dict(kwargs), e)
            return None
        else:
            logger.info("'%s' finished successfully. returned=%r", func.__name__, result)
            return result
    return wrapper


# ---------- FlexVar ----------

class FlexVar:
    """
    Chainable, dict-like container with a pretty string representation.

    Useful for collecting named attributes dynamically with simple validation
    and ergonomic access via both attribute and mapping syntax.

    Parameters
    ----------
    title : str
        Title header used by the string representation.

    Examples
    --------
    info = (
        FlexVar("User")
        .add("name", "Alice")
        .add("age", 30)
        .update("age", 31)
    )
    x = info["name"]        # mapping access
    y = info.name           # attribute-like access
    s = str(info)           # formatted block with title and key/value pairs

    Error Handling
    --------------
    - add(name, value): raises KeyError if the attribute already exists.
    - update(name, value): raises KeyError if the attribute does not exist.
    - remove(name): raises KeyError if the attribute does not exist.
    - __getattr__(name): raises AttributeError if the attribute does not exist.
    - __getitem__/__delitem__: raise KeyError for unknown keys (standard mapping behavior).
    """

    def __init__(self, title: str):
        self.__attr: dict[str, Any] = {}
        self.__title = title

    def add(self, name: str, value: Any):
        """
        Add a new attribute.

        Parameters
        ----------
        name : str
            Attribute name (must not already exist).
        value : Any
            Value to store.

        Returns
        -------
        FlexVar
            Self, to allow chaining.

        Raises
        ------
        KeyError
            If the attribute already exists.

        Examples
        --------
        FlexVar("Config").add("host", "localhost").add("port", 8080)
        """
        if name in self.__attr:
            raise KeyError(f"attribute {name} already exists")
        self.__attr[name] = value
        return self

    def update(self, name: str, value: Any):
        """
        Update an existing attribute.

        Parameters
        ----------
        name : str
            Existing attribute name.
        value : Any
            New value.

        Returns
        -------
        FlexVar
            Self, to allow chaining.

        Raises
        ------
        KeyError
            If the attribute does not exist.

        Examples
        --------
        FlexVar("User").add("age", 20).update("age", 21)
        """
        if name not in self.__attr:
            raise KeyError(f"attribute {name} does not exist")
        self.__attr[name] = value
        return self

    def remove(self, name: str):
        """
        Remove an existing attribute.

        Parameters
        ----------
        name : str
            Existing attribute name.

        Returns
        -------
        FlexVar
            Self, to allow chaining.

        Raises
        ------
        KeyError
            If the attribute does not exist.

        Examples
        --------
        FlexVar("Bag").add("x", 1).remove("x")
        """
        if name not in self.__attr:
            raise KeyError(f"attribute {name} does not exist")
        del self.__attr[name]
        return self

    def __getattr__(self, name: str) -> Any:
        """
        Attribute-style access to stored values.

        Parameters
        ----------
        name : str
            Attribute name.

        Returns
        -------
        Any
            Stored value.

        Raises
        ------
        AttributeError
            If the attribute does not exist.

        Examples
        --------
        v = FlexVar("Env").add("mode", "prod")
        mode = v.mode
        """
        if name not in self.__attr:
            raise AttributeError(f"attribute {name} does not exist")
        return self.__attr[name]

    def __str__(self) -> str:
        """
        Multiline, human-friendly representation.

        Returns
        -------
        str
            A block with title, separator lines, and key/value pairs.

        Examples
        --------
        str(FlexVar("User").add("name","Alice"))
        """
        lines = [f"{self.__title}", "---------------"]
        lines += [f"{k}: {v}" for k, v in self.__attr.items()]
        lines += ["---------------"]
        return "\n".join(lines)

    def __getitem__(self, key: str) -> Any:
        """
        Mapping access for reading.

        Parameters
        ----------
        key : str
            Existing attribute name.

        Returns
        -------
        Any
            Stored value.

        Raises
        ------
        KeyError
            If the key is not present.

        Examples
        --------
        v = FlexVar("Cfg").add("host", "127.0.0.1")
        host = v["host"]
        """
        return self.__attr[key]

    def __setitem__(self, key: str, value: Any):
        """
        Mapping access for writing (create or overwrite).

        Parameters
        ----------
        key : str
            Attribute name.
        value : Any
            Value to set.

        Examples
        --------
        v = FlexVar("Cfg")
        v["timeout"] = 5
        """
        self.__attr[key] = value

    def __contains__(self, key: str) -> bool:
        """
        Membership test.

        Parameters
        ----------
        key : str
            Attribute name.

        Returns
        -------
        bool
            True if present, else False.

        Examples
        --------
        "port" in FlexVar("Net").add("port", 8080)
        """
        return key in self.__attr

    def __delitem__(self, key: str):
        """
        Delete an attribute via mapping syntax.

        Parameters
        ----------
        key : str
            Existing attribute name.

        Raises
        ------
        KeyError
            If the key is not present.

        Examples
        --------
        v = FlexVar("Bag").add("x", 1)
        del v["x"]
        """
        del self.__attr[key]

    def __iter__(self) -> Iterable[tuple[str, Any]]:
        """
        Iterate over (key, value) pairs.

        Returns
        -------
        Iterable[tuple[str, Any]]
            Iterator over items.

        Examples
        --------
        for k, v in FlexVar("Data").add("a", 1).add("b", 2):
            pass
        """
        return iter(self.__attr.items())

class OfType:
    """
    Data descriptor that validates an attribute is an instance of one (or more)
    specific Python types.

    Validation rule
    ----------------
    `isinstance(value, types) == True`

    Parameters
    ----------
    *types : type
        One or more Python types (e.g., `int`, `float`, `str`, custom classes).

    Examples
    --------
    class Config:
        port = OfType(int)
        ratio = OfType(int, float)     # allow either int or float
        name = OfType(str)

    c = Config()
    c.port = 8080        # OK
    c.ratio = 0.75       # OK (float allowed)
    # c.port = "8080"    # raises ValidationError: must be of type int
    # c.name = 123       # raises ValidationError: must be of type str

    Raises
    ------
    ValidationError
        If the assigned value is not an instance of any of the allowed types.
    """

    def __init__(self, *types: type):
        if not types:
            raise TypeError("OfType requires at least one type")
        self.types = types

    def __set_name__(self, owner, name):
        self.name = f"__{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name, None)

    def __set__(self, instance, value):
        if not isinstance(value, self.types):
            # build a friendly list of expected type names
            type_names = tuple(t.__name__ for t in self.types)
            raise ValidationError(self.name.lstrip("__"), *type_names, msg="must be of type")
        setattr(instance, self.name, value)


class OptionalOfType:
    """
    Data descriptor that validates an attribute is either `None` or an instance
    of one (or more) specific Python types.

    Validation rule
    ----------------
    `value is None or isinstance(value, types) == True`

    Parameters
    ----------
    *types : type
        One or more Python types (e.g., `str`, `int`, custom classes).

    Examples
    --------
    class Profile:
        nickname = OptionalOfType(str)     # str or None
        score    = OptionalOfType(int, float)

    p = Profile()
    p.nickname = None      # OK
    p.nickname = "Avi"     # OK
    p.score = 100          # OK
    p.score = 99.5         # OK
    # p.score = "100"      # raises ValidationError: must be of type int or float

    Raises
    ------
    ValidationError
        If the assigned value is not None and not an instance of the allowed types.
    """

    def __init__(self, *types: type):
        if not types:
            raise TypeError("OptionalOfType requires at least one type")
        self.types = types

    def __set_name__(self, owner, name):
        self.name = f"__{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name, None)

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, self.types):
            type_names = tuple(t.__name__ for t in self.types)
            raise ValidationError(self.name.lstrip("__"), *type_names, msg="must be of type or None")
        setattr(instance, self.name, value)


class MatchesRegex:
    """
    Data descriptor that validates a string against a regular expression (full match).

    Validation rule
    ----------------
    `pattern.fullmatch(value) is not None`

    Parameters
    ----------
    pattern : str | Pattern[str]
        A regular-expression pattern string (compiled with re.compile) or an
        already compiled regex object. If a plain string is provided, it is
        compiled with `re.compile(pattern)` without flags.

    Notes
    -----
    - Uses `fullmatch`, not `search`, to ensure the entire value conforms.
    - For case-insensitive matches or other behaviors, pre-compile your pattern
      with flags and pass the compiled object:
        `MatchesRegex(re.compile(r"^abc$", re.IGNORECASE))`

    Examples
    --------
    Email (simple)
    --------------
    class User:
        email = MatchesRegex(r"^[\\w\\.-]+@[\\w\\.-]+\\.[A-Za-z]{2,}$")

    u = User()
    u.email = "alice@example.com"    # valid
    # u.email = "bad-email"          # raises ValidationError

    Israeli phone
    -------------
    class Contact:
        phone = MatchesRegex(r"^05\\d-\\d{7}$")  # e.g., 052-1234567

    c = Contact()
    c.phone = "052-1234567"          # valid
    # c.phone = "12345"              # raises ValidationError

    Username (3–15, letters/digits/_)
    ----------------------------------
    class Account:
        username = MatchesRegex(r"^[A-Za-z0-9_]{3,15}$")

    a = Account()
    a.username = "avi_twil"          # valid
    # a.username = "a!"              # raises ValidationError

    Strong-ish password (example policy)
    ------------------------------------
    # at least 8 chars, one upper, one lower, one digit
    pwd_re = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).{8,}$"

    class Secret:
        password = MatchesRegex(pwd_re)

    s = Secret()
    s.password = "Aa123456"          # valid
    # s.password = "password"        # raises ValidationError

    Raises
    ------
    ValidationError
        If the assigned value fails to fully match the given pattern.
    TypeError
        If a non-string value is assigned (this descriptor validates strings).
    """

    def __init__(self, pattern: str | re.Pattern[str]):
        if isinstance(pattern, str):
            self.pattern = re.compile(pattern)
        elif isinstance(pattern, re.Pattern):
            self.pattern = pattern
        else:
            raise TypeError("pattern must be a str or compiled regex (re.Pattern)")
        self._pattern_str = getattr(self.pattern, "pattern", str(pattern))

    def __set_name__(self, owner, name):
        self.name = f"__{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name, None)

    def __set__(self, instance, value: str):
        if not isinstance(value, str):
            raise TypeError(f"{self.name.lstrip('__')} must be a string")
        if self.pattern.fullmatch(value) is None:
            raise ValidationError(
                self.name.lstrip("__"),
                self._pattern_str,
                msg="must match regex"
            )
        setattr(instance, self.name, value)

