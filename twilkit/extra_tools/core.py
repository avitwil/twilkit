
import datetime
import inspect
import os
import pathlib
import re
from typing import Any, Optional, Dict
from ADVfile_manager import TextFile


class PyTxt:
    """
    Lightweight text/file wrapper that lets you work with a string buffer
    or a bound `ADVfile_manager.TextFile` interchangeably.

    Behavior
    --------
    - If no file is bound (self.file is None), reading/writing uses the in-memory `__text`.
    - Once a file is bound (via setting `.file`), reading/writing goes to disk
      through `ADVfile_manager.TextFile`.

    Attributes
    ----------
    text : str | None
        Gets/sets the content. When a file is bound, this proxies to TextFile.read()/write().
    file : TextFile | None
        Gets/sets the underlying TextFile. Assigning a string path automatically creates a TextFile.
    read_only : bool
        When True, assignments to `.text` raise PermissionError.
    """

    def __init__(self, text: str | None = None, *, file: TextFile | None = None, read_only: bool = False):
        self.__text = text
        self.__file = file
        self.__ro = read_only

    @property
    def text(self) -> Optional[str]:
        """Return the current content (from memory if no file is bound, else from disk)."""
        if not self.__file:
            return self.__text
        return self.__file.read()

    @text.setter
    def text(self, text: str) -> None:
        """
        Set content (to memory if no file is bound, else write to disk).

        Raises
        ------
        PermissionError
            If `read_only` is True.
        """
        if self.__ro:
            raise PermissionError("PyTxt is read-only")
        if not self.__file:
            self.__text = text
        else:
            self.__file.write(text)

    @property
    def read_only(self) -> bool:
        """Whether this instance blocks writes to `.text`."""
        return self.__ro

    @read_only.setter
    def read_only(self, status: bool = True) -> None:
        """Enable/disable read-only mode."""
        self.__ro = status

    @property
    def file(self) -> Optional[TextFile]:
        """Return the bound TextFile (if any)."""
        return self.__file if self.__file else None

    @file.setter
    def file(self, file: TextFile | str) -> None:
        """
        Bind a TextFile. If a string path is given, construct TextFile(name, dirpath)
        using basename/dirname.

        Notes
        -----
        - If in-memory text exists, it will be flushed to the new file once bound.
        - If the file does not exist yet, an empty string is written to create it.
        """
        if isinstance(file, TextFile):
            self.__file = file
        else:
            self.__file = TextFile(os.path.basename(file), os.path.dirname(file))
            if self.__text is not None:
                self.__file.write(self.__text)
                self.__text = None
            else:
                try:
                    self.__file.read()
                except FileNotFoundError:
                    self.__file.write("")

    @file.deleter
    def file(self) -> None:
        """
        Unbind and remove the current file.

        - Reads the file content back into memory (`self.__text`)
        - Deletes the file on disk
        - Clears the bound TextFile
        """
        if self.__file:
            self.__text = self.__file.read()
            try:
                os.remove(self.__file.full_path)
            except FileNotFoundError:
                pass
            self.__file = None

    def __str__(self) -> str:
        return self.text or ""


class Return:
    """
    A simple, ergonomic result container: payload + success/error state.

    Design
    ------
    - `success` indicates operation state.
    - `values` (dict) holds named payload fields (always accessible).
    - `error` property exposes the error message when `success == False`.
    """

    def __init__(self, success: bool = True, /, **named_values: Any):
        """
        Parameters
        ----------
        success : bool, positional-only, default True
            Operation status flag. True = success, False = failure.
        **named_values : Any
            Named payload to carry with the result.
        """
        self.__values: Dict[str, Any] = dict(named_values)
        self.__success: bool = success
        self.__error_msg: Optional[str] = None

    @property
    def error(self) -> Optional[str]:
        """Error message if failed, else None."""
        return None if self.__success else self.__error_msg

    @error.setter
    def error(self, error_msg: str) -> None:
        """Mark as failed and store an error message."""
        self.__success = False
        self.__error_msg = error_msg

    @property
    def values(self) -> Dict[str, Any]:
        """A copy of the payload (dict), returned regardless of success state."""
        return dict(self.__values)

    @property
    def success(self) -> bool:
        """True if successful, else False."""
        return self.__success

    @property
    def ok(self) -> bool:
        """Alias for `success`."""
        return self.__success

    def get(self, key: str, default: Any = None) -> Any:
        """dict-like `get` on the payload."""
        return self.__values.get(key, default)

    def unwrap(self, key: str, default: Any = None) -> Any:
        """Convenience alias for `get`."""
        return self.get(key, default)

    def dict(self) -> Dict[str, Any]:
        """Return a shallow copy of the payload dictionary."""
        return dict(self.__values)

    def raise_for_error(self, exc_type: type[Exception] = RuntimeError) -> "Return":
        """
        Raise `exc_type` if this result represents a failure.

        Parameters
        ----------
        exc_type : Exception type, default RuntimeError
            Exception class to raise.

        Returns
        -------
        Return
            Self (useful for chaining).

        Raises
        ------
        exc_type
            If `success` is False.
        """
        if not self.__success:
            raise exc_type(self.error or "Operation failed")
        return self

    def __getitem__(self, key: str) -> Any:
        """dict-like key access on the payload."""
        return self.__values[key]

    def __bool__(self) -> bool:
        return self.__success

    def __repr__(self) -> str:
        if self.__success:
            return f"<Return success values={self.__values}>"
        else:
            return f"<Return failed error='{self.__error_msg}'>"

    @classmethod
    def fail(cls, error_msg: str, /, **named_values: Any) -> "Return":
        """Construct a failed result with an error message and optional payload."""
        r = cls(success=False, **named_values)
        r.error = error_msg
        return r


def copy_this_module(
    new_copy_file_path: str=os.getcwd(),
    copy_num: int = 0,
    *,
    new_name: str | None = None,
    include_main: bool = True,
) -> Return:
    """
    Create a copy of the current module into `new_copy_file_path`,
    with an auto-incremented suffix if the target exists.

    Naming
    ------
    - If `new_name` is provided:
        * If it has a suffix (e.g., ".py") → use as-is (with auto-increment when needed).
        * If it lacks a suffix → inherit the original module suffix.
    - Else:
        * Use original module's stem/suffix.
    - If `copy_num > 0` → start with `<stem><copy_num><suffix>`.
    - If `copy_num == 0` → start with `<stem><suffix>`.
    - If the candidate exists → increment numeric suffix until a free name is found.

    Header
    ------
    The copy begins with a small header:
      - original file name + source directory
      - copy number (if > 0)
      - timestamp

    Parameters
    ----------
    new_copy_file_path : str
        Directory path for the new copy (TextFile will create directories as needed).
    copy_num : int, default 0
        Initial copy number; if 0, try `<stem><suffix>` first.
    new_name : str | None
        Optional explicit name for the new copy. If it lacks a suffix, the original module’s
        suffix is used (e.g. passing `"backup"` becomes `"backup.py"` if the source is `.py`).
    include_main : bool, default True
        Whether to keep the `if __name__ == '__main__':` block in the copy.

    Returns
    -------
    Return
        success=True with payload:
        {
          "file_name": str,
          "file_path": str,
          "original_file_name": str,
          "original_file_path": str,
          "old": PyTxt,   # the source file bound to this module (read-only)
          "new": PyTxt    # the destination file (locked read-only after write)
        }
    """
    frame = inspect.stack()[1]
    src_path = os.path.abspath(frame.filename)
    # Source is read-only; destination must be writeable during creation.
    this = PyTxt(read_only=True)
    copy = PyTxt()

    # Resolve stem/suffix
    if new_name is None:
        stem = pathlib.Path(__file__).stem
        suffix = pathlib.Path(__file__).suffix
    else:
        p = pathlib.Path(new_name)
        stem = p.stem
        suffix = p.suffix or pathlib.Path(__file__).suffix  # inherit if missing

    # Initial candidate path
    if copy_num > 0:
        dest_path = os.path.join(new_copy_file_path, f"{stem}{copy_num}{suffix}")
    else:
        dest_path = os.path.join(new_copy_file_path, f"{stem}{suffix}")

    # Auto-increment if target exists
    n = copy_num
    if n > 0 or os.path.exists(dest_path):
        while os.path.exists(dest_path):
            n += 1
            dest_path = os.path.join(new_copy_file_path, f"{stem}{n}{suffix}")

    # Bind files (ADVfile_manager creates directories/files as needed)
    copy.file = dest_path
    this.file = src_path

    # Load source text
    source_text = this.text or ""

    # Optionally strip the __main__ block (robust regex for whitespace & end of file)
    if not include_main:
        source_text = re.sub(
            r"(?ms)^\s*if\s+__name__\s*==\s*['\"]__main__['\"]\s*:\s*.*\Z",
            "",
            source_text
        ).rstrip() + "\n"

    # Build header and write
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = [
        f"# a copy of {this.file.name} from {this.file.path}",
        *( [f"# copy number: {n}"] if n > 0 else [] ),
        f"# at {timestamp}",
        "",
    ]
    dont_run =rf"""
try:
    err  = '\033[91mERROR: THIS COPY WILL NOT RUN \n\033[92mThis is a copy of \033[94m' + r'{this.file.full_path}' + ' --\033[92m to run delete lines \033[91m1 - 8\033[0m'
    raise RuntimeError(err)
except RuntimeError as e:
    print(e)
    exit(1)
    
"""
    copy.text = dont_run + "\n".join(header) + source_text

    # Optionally lock destination after write
    copy.read_only = True

    return Return(
        file_name=copy.file.name,
        file_path=copy.file.path,
        original_file_name=this.file.name,
        original_file_path=this.file.path,
        old=this,
        new=copy,
    )


def _copy_me_print(*, path: str = os.getcwd(), new_name: str | None = None, keep_main: bool = True) -> None:
    """
    Convenience wrapper that copies this module and prints a colored summary to stdout.

    Parameters
    ----------
    path : str, default CWD
        Target directory for the copy.
    new_name : str | None
        Optional explicit file name for the copy (suffix optional; inherited if missing).
    keep_main : bool, default True
        Whether to keep the `if __name__ == '__main__':` block in the copy.
    """
    res = copy_this_module(path, new_name=new_name, include_main=keep_main)

    print()
    print()
    print(
        f"\033[92mCopy created:\033[94m {res['file_name']}\n"
        f"\033[92mPath:\033[94m {res['file_path']}\n"
        f"\033[92mFrom file:\033[94m {res['original_file_name']}\033[92m at\033[94m {res['original_file_path']}"
    )
    print()
    print()
    print(f"\033[93m---------- {res['file_name']} content ----------\033[95m")
    print()
    print(res['new'].text)
    print(f"\033[93m---------- {res['file_name']} End Of File ----------\033[0m")
