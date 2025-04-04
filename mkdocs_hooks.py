"""Hooks for mkdocs."""
from __future__ import annotations

import glob
import json
import logging
import os
from pathlib import Path
from shutil import rmtree
from typing import TYPE_CHECKING, ClassVar, Literal

if TYPE_CHECKING:
    from logging import LogRecord

    from mkdocs import MkDocsConfig


TMP_FILE = "./missing_init_files.json"
NFILES = []

# -----------------------------------------------------------------------------


class ColorFormatter(logging.Formatter):
    """Custom logging formatter to add colors to log messages."""
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    fmt = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s "
        "(%(filename)s:%(lineno)d)"
    )

    FORMATS: ClassVar[dict[int, str]] = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: green + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset,
    }

    def format(self, record: LogRecord) -> str:
        """Format the log record with color.

        Args:
            record (LogRecord): The log record to format.

        Returns:
            str: The formatted log message with color.

        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


ch = logging.StreamHandler()
ch.setFormatter(ColorFormatter())

logging.basicConfig(
    level=logging.INFO,
    handlers=[ch],
)


# -----------------------------------------------------------------------------


def create_init_file(dirpath: str, msg: str) -> None:
    """Create an empty `__init__.py` file in the specified directory.

    Args:
        dirpath (str): The directory path where the `__init__.py` file will
            be created.
        msg (str): A message to log when the file is created.

    """
    ini_file = f"{dirpath}/__init__.py"
    Path(ini_file).touch()
    NFILES.append(ini_file)
    logging.info(  # noqa: LOG015
        "%s: created '%s'", msg, ini_file)


def create_parent_init_files(dirpath: str, rootpath: str, msg: str) -> None:
    """Create `__init__.py` files in parent directories.

    Args:
        dirpath (str): The directory path where the `__init__.py` file will
            be created.
        rootpath (str): The root directory path to stop at.
        msg (str): A message to log when the file is created.

    """
    parent_path = dirpath
    while parent_path != rootpath:
        parent_path = os.path.dirname(parent_path)
        parent_init = os.path.join(parent_path, "__init__.py")
        if not os.path.exists(parent_init):
            create_init_file(parent_path, msg)
        else:
            break


def add_missing_init_files(roots: tuple, msg: str = "") -> None:
    """Add temporary `__init__.py` files to directories.

    This function takes in one or more root directories as arguments and scans
    them for Python files without an `__init__.py` file. It generates a JSON
    file named `missing_init_files.json` containing the paths of these files.

    Args:
        roots: Variable number of root directories to scan.
        msg: An optional message to display during the process.

    """
    for root in roots:
        if not os.path.exists(root):
            continue
        rootpath = os.path.abspath(root)
        for dirpath, _, files in os.walk(rootpath):
            if "__init__.py" in files:
                continue

            if "." in dirpath:
                continue

            if not glob.glob(os.path.join(dirpath, "*.py")):
                continue

            create_init_file(dirpath, msg)
            create_parent_init_files(dirpath, rootpath, msg)

    with open(TMP_FILE, "w", encoding="utf-8") as f:
        json.dump(NFILES, f)


def remove_missing_init_files(msg: str = "") -> None:
    """Remove temporary `__init__.py` files.

    This function removes temporary `__init__.py` files created in the
    `add_missing_init_files()` function. It reads the paths of these files from
    a JSON file named `missing_init_files.json`.

    Args:
        msg: An optional message to display during the removal process.

    """
    global NFILES  # noqa: PLW0603
    nfiles = []
    if os.path.exists(TMP_FILE):
        with open(TMP_FILE, encoding="utf-8") as f:
            nfiles = json.load(f)
    else:
        nfiles = NFILES

    for file in nfiles:
        Path(file).unlink()
        logging.info("%s: removed %s", msg, file)  # noqa: LOG015

    os.remove(TMP_FILE)
    NFILES = []


def remove_pychache_dirs(msg: str = "") -> None:
    """Remove all existing '__pycache__' directories.

    This function walks the current directory and removes all existing
    '__pycache__' directories.

    Args:
        msg: An optional message to display during the removal process.

    """
    nremoved = 0

    for dirpath, dirs, _ in os.walk("."):
        if "__pycache__" in dirs:
            pydir = Path(f"{dirpath}/__pycache__")
            rmtree(pydir)
            nremoved += 1
            logging.info(  # noqa: LOG015
                "%s: removed '%s'", msg, pydir)

    if not nremoved:
        logging.info(  # noqa: LOG015
            "%s: no __pycache__ dirs found", msg)


# mkdocs hooks ----------------------------------------------------------------


def on_startup(
        command: Literal["build", "gh-deploy", "serve"], *,  # noqa: ARG001
        dirty: bool) -> None:  # noqa: ARG001
    """On statup hook for MkDocs."""
    remove_pychache_dirs(msg="HOOK    -  on_startup")


def on_pre_build(config: MkDocsConfig) -> None:  # noqa: ARG001
    """On pre-build hook for MkDocs.

    This function is called before the MkDocs build process begins. It adds
    temporary `__init__.py` files to directories that do not contain one, to
    make sure mkdocs doesn't ignore them.

    Args:
        config (MkDocsConfig): The MkDocs configuration object.

    Raises:
        RuntimeError: If an error occurs while
            adding the `__init__.py` files.

    """
    try:
        add_missing_init_files(
            ("client", "server", "services"),
            msg="HOOK    -  on_pre_build",
        )
    except BaseException as e:
        logging.exception("cleaning up error", exc_info=e)  # noqa: LOG015
        remove_missing_init_files(
            msg="HOOK    -  on_post_build: cleaning up on error !"
        )
        raise RuntimeError from e


def on_post_build(config: MkDocsConfig) -> None:  # noqa: ARG001
    """On post-build hook for MkDocs.

    Args:
        config (MkDocsConfig): The MkDocs configuration object.

    This function is called after the MkDocs build process ends. It removes
    temporary `__init__.py` files that were added in the `on_pre_build()`
    function.

    """
    remove_missing_init_files(msg="HOOK    -  on_post_build")
